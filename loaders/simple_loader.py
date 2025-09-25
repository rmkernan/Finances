#!/usr/bin/env python3
"""
Simple Financial Data Loader

Created: 09/23/25 2:25PM
Updated: 09/23/25 2:43PM - Added document_accounts table population for proper document-account linking
Updated: 09/23/25 3:56PM - Fixed for updated schema (removed entity_id from institutions, added institution_name to accounts)
Updated: 09/23/25 4:03PM - Added all orphaned fields (sec_subtype, estimated_ann_inc, est_yield, cusip, reference, account_type, transaction, balance, doc_level_data)
Updated: 09/23/25 4:23PM - Complete loader refactor to handle ALL attributes from JSON specifications:
  - Added bond-specific fields (maturity_date, coupon_rate, accrued_int, agency_ratings, call info, etc.)
  - Added income_summary and realized_gains support as flexible key-value pairs
  - Enhanced activity loading with cost_basis, transaction_cost, payee fields, ytd_payments
  - Added trades_pending_settlement section support
  - Full extraction metadata preservation (extraction_type, timestamp, version, pages, notes)
Updated: 09/23/25 6:08PM - Enhanced source field to capture document section lineage:
  - Transactions: source = section name (e.g., "securities_bought_sold", "dividends_interest_income")
  - Positions: source = sec_type (e.g., "Mutual Funds", "Bonds", "Options")
Updated: 09/23/25 6:17PM - Added options symbol extraction from security descriptions:
  - Extract underlying symbol from option descriptions like "PUT (TSLA)" → symbol = "TSLA"
  - Handles both PUT and CALL options with regex pattern matching
Updated: 09/23/25 7:16PM - Added configuration-driven mapping system and sec_class support:
  - Replaced hardcoded ACTIVITY_SECTIONS with dynamic database-driven mappings
  - Added sec_class column population for options classification (call, put)
  - Enhanced transaction_subtype with security pattern overrides (opening_transaction, closing_transaction, assignment)
  - Comprehensive mapping priority: security patterns > description mapping > section mapping
Updated: 09/23/25 10:10PM - Fixed doc_level_data loading to match actual schema columns:
Updated: 09/24/25 11:52AM - Updated JSON metadata attribute names to align with new schema: source_pdf_filepath, json_output_md5_hash
Updated: 09/24/25 1:54PM - Added complete security_types mapping integration to load_positions function for full data_mappings table coverage
Updated: 09/24/25 1:57PM - Fixed entity lookup logic to get entity_id from account records instead of direct entity name matching
Updated: 09/24/25 2:29PM - Prepared for incremental JSON loading support with database schema updates for activities_loaded/positions_loaded timestamps and JSON hash tracking
Updated: 09/24/25 2:33PM - Implemented complete incremental JSON loading capability with helper functions, JSON hash calculation, and enhanced create_document logic
Updated: 09/24/25 3:23PM - Integrated three-table mapping rule engine: extracted rule evaluation to separate module, added rule-based transaction classification with fallback to legacy system
Updated: 09/24/25 3:26PM - Completed migration to three-table mapping system: removed legacy data_mappings table and fallback logic, fully functional rule-based classification
Updated: 09/24/25 3:57PM - Fixed remaining legacy data_mappings references and security type mapping calls to use three-table rule engine only
Updated: 09/24/25 4:01PM - Added three-table mapping rule engine support to load_positions function for future holdings classification rules
Updated: 09/25/25 5:35PM - Fixed mapping rules engine integration: added transaction field support for core_fund_activity patterns
  - Changed from key-value pairs to direct column mapping for portfolio_summary, income_summary, realized_gains
  - Single row per account with all summary fields populated from JSON
Purpose: Pure transcription system to load JSON extractions into PostgreSQL database

Design Principles:
- Table-driven activity processing
- No inference - loads exactly what extractor determined
- Handles activities and/or holdings from same accounts array
- Auto-moves files to loaded directory on success
- Populates document_accounts junction table for consolidated statements
- Loads ALL attributes defined in JSON specifications
- Ready for incremental loading: same PDF can load activities first, then positions later
- JSON hash duplicate prevention for data integrity

Usage:
    python3 simple_loader.py path/to/extraction.json
"""

import json
import sys
import uuid
import shutil
import hashlib
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

# Legacy mapping functions removed - using three-table rule engine only

# Import the separate rule engine module
from mapping_rules_engine import apply_mapping_rules

# Legacy mapping functions removed - now using three-table rule engine

# Security type mapping removed - now handled by three-table rule engine in load_positions

def connect_db():
    """Get database connection"""
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def parse_amount(amount_str):
    """Convert amount string to Decimal, handle None"""
    if not amount_str:
        return None
    # Remove currency symbols and commas, handle parentheses as negative
    clean = str(amount_str).replace('$', '').replace(',', '')
    if '(' in clean and ')' in clean:
        clean = '-' + clean.replace('(', '').replace(')', '')
    try:
        return Decimal(clean)
    except:
        return None

def parse_date(date_str, tax_year):
    """Parse date string, add year if missing"""
    if not date_str:
        return None
    try:
        if '/' in date_str and len(date_str.split('/')[2]) == 2:
            # MM/DD/YY format
            return datetime.strptime(f"{date_str.split('/')[0]}/{date_str.split('/')[1]}/{tax_year}", "%m/%d/%Y").date()
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def extract_option_symbol(sec_description, sec_symbol):
    """Extract underlying symbol from options security description if sec_symbol is null"""
    if sec_symbol:
        return sec_symbol

    if not sec_description:
        return None

    # Pattern for options: "PUT (SYMBOL)" or "CALL (SYMBOL)"
    import re
    match = re.search(r'(?:PUT|CALL)\s*\(([A-Z]+)\)', sec_description)
    if match:
        return match.group(1)

    return sec_symbol

def lookup_entity(name, conn):
    """Lookup existing entity by name - fail if not found"""
    cur = conn.cursor()
    cur.execute("SELECT id FROM entities WHERE entity_name = %s", (name,))
    result = cur.fetchone()
    if not result:
        raise ValueError(f"Entity '{name}' not found in database. Reference data must be loaded first via process-inbox command.")
    return result['id']

def lookup_institution(name, conn):
    """Lookup existing institution by name - fail if not found"""
    cur = conn.cursor()
    cur.execute("SELECT id FROM institutions WHERE institution_name = %s", (name,))
    result = cur.fetchone()
    if not result:
        raise ValueError(f"Institution '{name}' not found in database. Reference data must be loaded first via process-inbox command.")
    return result['id']

def lookup_account(account_number, institution_id, conn):
    """Lookup existing account by number and institution - fail if not found"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, entity_id FROM accounts
        WHERE account_number = %s AND institution_id = %s
    """, (account_number, institution_id))
    result = cur.fetchone()
    if not result:
        raise ValueError(f"Account '{account_number}' not found at institution. Reference data must be loaded first via process-inbox command.")
    return result['id'], result['entity_id']

def get_existing_document(doc_hash, conn):
    """Lookup existing document by PDF hash - returns document record or None"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, activities_loaded, activities_json_md5_hash,
               positions_loaded, positions_json_md5_hash,
               file_name, processed_at
        FROM documents
        WHERE doc_md5_hash = %s
    """, (doc_hash,))
    return cur.fetchone()

def check_extraction_status(existing_doc, extraction_type, json_md5_hash):
    """Check if extraction already loaded and determine action"""
    if extraction_type == 'activities':
        if existing_doc['activities_json_md5_hash'] == json_md5_hash:
            return 'SKIP_DUPLICATE'  # Same JSON already loaded
        elif existing_doc['activities_loaded']:
            return 'WARN_REPROCESS'  # Different JSON for same type
        else:
            return 'PROCEED'  # Not yet loaded

    elif extraction_type == 'holdings':
        if existing_doc['positions_json_md5_hash'] == json_md5_hash:
            return 'SKIP_DUPLICATE'  # Same JSON already loaded
        elif existing_doc['positions_loaded']:
            return 'WARN_REPROCESS'  # Different JSON for same type
        else:
            return 'PROCEED'  # Not yet loaded

    return 'PROCEED'  # Unknown extraction type, proceed

# handle_reprocessing_scenario() function removed - fail-fast approach never auto-reprocesses
# Financial data conflicts must be resolved manually before reloading

def update_document_loading_status(doc_id, extraction_type, json_md5_hash, conn):
    """Update document with loading timestamp and JSON hash"""
    cur = conn.cursor()
    now = datetime.now()

    if extraction_type == 'activities':
        cur.execute("""
            UPDATE documents
            SET activities_loaded = %s, activities_json_md5_hash = %s, updated_at = %s
            WHERE id = %s
        """, (now, json_md5_hash, now, doc_id))
    elif extraction_type == 'holdings':
        cur.execute("""
            UPDATE documents
            SET positions_loaded = %s, positions_json_md5_hash = %s, updated_at = %s
            WHERE id = %s
        """, (now, json_md5_hash, now, doc_id))

    return True

def create_document(data, institution_id, loaded_path, extraction_type, json_md5_hash, conn):
    """
    FAIL-FAST document validation and loading strategy.

    Design Philosophy:
    - Document records should be created during /process-inbox, not /load-extractions
    - Never autonomously overwrite existing financial data
    - Fail immediately with clear error messages when workflow is incorrect
    - Only proceed when: document exists AND extraction type not yet loaded

    This approach ensures:
    1. Data safety - no accidental overwrites
    2. Workflow integrity - catches process-inbox skips
    3. Error transparency - clear guidance for resolution
    4. Simplicity - eliminates complex conflict resolution logic
    """
    cur = conn.cursor()

    metadata = data.get('extraction_metadata', {})
    doc_data = data.get('document_data', {})

    # Get MD5 hash for duplicate detection
    doc_hash = metadata.get('doc_md5_hash')
    if not doc_hash:
        raise ValueError("Missing doc_md5_hash in extraction metadata")

    # Check if document exists by PDF hash
    existing_doc = get_existing_document(doc_hash, conn)

    if existing_doc:
        # Document exists - check if this extraction type already loaded
        status = check_extraction_status(existing_doc, extraction_type, json_md5_hash)

        if status == 'SKIP_DUPLICATE':
            print(f"  Skipping - {extraction_type} already loaded with identical JSON content")
            return existing_doc['id']

        elif status == 'WARN_REPROCESS':
            # FAIL-FAST: Never automatically reprocess financial data
            old_hash = (existing_doc['activities_json_md5_hash'] if extraction_type == 'activities'
                       else existing_doc['positions_json_md5_hash'])
            raise ValueError(
                f"DUPLICATE DATA CONFLICT:\n"
                f"  Document: {existing_doc['file_name']}\n"
                f"  Extraction type: {extraction_type}\n"
                f"  Already loaded: {existing_doc['processed_at']}\n"
                f"  Existing hash: {old_hash}\n"
                f"  New hash: {json_md5_hash}\n\n"
                f"This means {extraction_type} data already exists but with different content.\n"
                f"Resolution required: Determine if this is a duplicate extraction, \n"
                f"corrected data, or extraction bug before proceeding.\n\n"
                f"To reprocess: Delete existing {extraction_type} data first, then reload."
            )

        # PROCEED: Document exists, extraction type not yet loaded
        update_document_loading_status(existing_doc['id'], extraction_type, json_md5_hash, conn)
        return existing_doc['id']

    else:
        # FAIL-FAST: Document should exist from process-inbox step
        file_name = Path(metadata.get('source_pdf_filepath', 'unknown.pdf')).name
        raise ValueError(
            f"MISSING DOCUMENT RECORD:\n"
            f"  PDF file: {file_name}\n"
            f"  PDF hash: {doc_hash}\n\n"
            f"Document record not found in database. This indicates the PDF was not\n"
            f"processed through /process-inbox workflow first.\n\n"
            f"Resolution required: Run /process-inbox command to create document\n"
            f"structure before loading extractions.\n\n"
            f"Workflow: /process-inbox → /load-extractions"
        )

# create_new_document() function removed - no longer needed with fail-fast approach
# Document creation now handled exclusively by /process-inbox workflow

def link_document_account(doc_id, account_id, conn):
    """Link document to account in junction table"""
    cur = conn.cursor()

    # Check if link already exists
    cur.execute("""
        SELECT 1 FROM document_accounts
        WHERE document_id = %s AND account_id = %s
    """, (doc_id, account_id))

    if not cur.fetchone():
        cur.execute("""
            INSERT INTO document_accounts (document_id, account_id)
            VALUES (%s, %s)
        """, (doc_id, account_id))

    return True

def load_positions(account_data, doc_id, account_id, entity_id, statement_date, conn):
    """Load holdings/positions for one account"""
    if 'holdings' not in account_data:
        return 0

    cur = conn.cursor()
    count = 0

    for position in account_data['holdings']:
        position_id = str(uuid.uuid4())

        # Parse percentages - handle both decimal and percentage formats
        coupon_rate = position.get('coupon_rate')
        if coupon_rate:
            coupon_rate = parse_amount(coupon_rate)

        # Apply three-table mapping rules for position classification
        # Prepare position data for rule evaluation
        position_data = {
            'sec_description': position.get('sec_description'),
            'sec_type': position.get('sec_type'),
            'sec_subtype': position.get('sec_subtype'),
            'sec_symbol': position.get('sec_symbol'),
            'cusip': position.get('cusip'),
            'source': position.get('sec_type'),  # Use sec_type as source for position rules
            'quantity': position.get('quantity', ''),
            'end_market_value': position.get('end_market_value', '')
        }

        # Apply mapping rules to get field updates
        rule_updates = apply_mapping_rules(position_data, conn)

        # Use rule engine results or fall back to original values
        mapped_sec_type = rule_updates.get('sec_type') or position.get('sec_type')
        mapped_sec_subtype = rule_updates.get('sec_subtype') or position.get('sec_subtype')

        cur.execute("""
            INSERT INTO positions (
                id, document_id, account_id, entity_id, position_date,
                account_number, sec_ticker, cusip, sec_name, sec_type, sec_subtype,
                quantity, price, beg_market_value, end_market_value, cost_basis, unrealized_gain_loss,
                estimated_ann_inc, est_yield, underlying_symbol, strike_price, exp_date, option_type,
                maturity_date, coupon_rate, accrued_int, agency_ratings, next_call_date,
                call_price, payment_freq, bond_features, source
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            position_id, doc_id, account_id, entity_id, statement_date,
            account_data.get('account_number'),
            position.get('sec_symbol'),
            position.get('cusip'),
            position.get('sec_description'),
            mapped_sec_type,
            mapped_sec_subtype,
            parse_amount(position.get('quantity')),
            parse_amount(position.get('price_per_unit')) or Decimal('0'),
            parse_amount(position.get('beg_market_value')),
            parse_amount(position.get('end_market_value')) or Decimal('0'),
            parse_amount(position.get('cost_basis')),
            parse_amount(position.get('unrealized_gain_loss')),
            parse_amount(position.get('estimated_ann_inc')),
            parse_amount(position.get('est_yield')),
            position.get('underlying_symbol'),  # Options field
            parse_amount(position.get('strike_price')),  # Options field
            parse_date(position.get('expiration_date'), datetime.now().year),  # Options field
            position.get('sec_subtype') if position.get('sec_type') == 'Options' else None,  # Use subtype as option_type for options
            # Bond-specific fields
            parse_date(position.get('maturity_date'), datetime.now().year),
            coupon_rate,
            parse_amount(position.get('accrued_int')),
            position.get('agency_ratings'),
            parse_date(position.get('next_call_date'), datetime.now().year),
            parse_amount(position.get('call_price')),
            position.get('payment_freq'),
            position.get('bond_features'),
            # Source from sec_type (document section)
            position.get('sec_type')
        ))
        count += 1

    return count

def load_activities(account_data, doc_id, account_id, entity_id, conn):
    """Load activities/transactions for one account"""
    cur = conn.cursor()
    count = 0

    # Load activities from all known sections
    activity_sections = [
        'dividends_interest_income', 'deposits', 'withdrawals', 'core_fund_activity',
        'securities_bought_sold', 'other_activity_in', 'other_activity_out',
        'exchanges_in', 'exchanges_out', 'fees_charges', 'billpay', 'trades_pending_settlement'
    ]

    for section_name in activity_sections:
        activities = account_data.get(section_name, [])

        # Handle None values - convert to empty list
        if activities is None:
            activities = []

        for activity in activities:
            transaction_id = str(uuid.uuid4())

            # Handle dates - use appropriate field based on section
            trans_date = None
            settle_date = None

            if section_name == 'billpay':
                trans_date = parse_date(activity.get('post_date'), datetime.now().year)
                settle_date = trans_date
            elif section_name == 'trades_pending_settlement':
                trans_date = parse_date(activity.get('trade_date'), datetime.now().year)
                settle_date = parse_date(activity.get('settlement_date'), datetime.now().year)
            else:
                # Standard handling
                trans_date = parse_date(activity.get('date') or activity.get('settlement_date'), datetime.now().year)
                settle_date = parse_date(activity.get('settlement_date') or activity.get('date'), datetime.now().year)

            # Apply three-table mapping rules for classification
            # This replaces the old hardcoded mapping with the flexible rule engine
            description = activity.get('description') or activity.get('sec_description', 'Unknown')
            security_name = activity.get('sec_description')

            # Prepare transaction data for rule evaluation
            transaction_data = {
                'description': description,
                'transaction': activity.get('transaction', ''),
                'section': section_name,
                'source': section_name,
                'sec_description': security_name,
                'amount': activity.get('amount', ''),
                'quantity': activity.get('quantity', '')
            }

            # Apply mapping rules to get field updates
            rule_updates = apply_mapping_rules(transaction_data, conn)


            # Extract classification fields from rule engine
            transaction_type = rule_updates.get('transaction_type')
            transaction_subtype = rule_updates.get('transaction_subtype')
            sec_class = rule_updates.get('sec_class')

            # Override subtype with activity-specific data if available
            if not transaction_subtype and activity.get('transaction'):
                transaction_subtype = activity.get('transaction')

            cur.execute("""
                INSERT INTO transactions (
                    id, entity_id, document_id, account_id,
                    transaction_date, settlement_date, transaction_type, transaction_subtype,
                    description, amount, security_name, security_identifier, sec_cusip,
                    quantity, price_per_unit, cost_basis, reference_number, source, payee, sec_class
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                transaction_id, entity_id, doc_id, account_id,
                trans_date,
                settle_date,
                transaction_type,
                transaction_subtype,
                description,
                parse_amount(activity.get('amount')) or Decimal('0'),
                activity.get('sec_description'),
                extract_option_symbol(activity.get('sec_description'), activity.get('sec_symbol')),
                activity.get('cusip'),
                parse_amount(activity.get('quantity')),
                parse_amount(activity.get('price_per_unit')),
                parse_amount(activity.get('cost_basis')),
                activity.get('reference'),
                section_name,  # Use actual section name as source
                activity.get('payee'),
                sec_class
            ))
            count += 1

    return count

def load_doc_level_data(account_data, doc_id, account_id, statement_date, conn):
    """Load account-level summary data to doc_level_data table"""
    cur = conn.cursor()
    account_number = account_data.get('account_number')

    # Combine all summary data
    portfolio = account_data.get('portfolio_summary', {})
    income = account_data.get('income_summary', {})
    gains = account_data.get('realized_gains', {})

    # Only insert if we have data
    if not (portfolio or income or gains):
        return 0

    doc_data_id = str(uuid.uuid4())

    # Map JSON fields to database columns
    cur.execute("""
        INSERT INTO doc_level_data (
            id, document_id, account_id, account_number, doc_section, as_of_date,
            -- Portfolio summary fields
            net_acct_value, beg_value, end_value,
            -- Income summary fields
            taxable_total_period, taxable_total_ytd,
            divs_taxable_period, divs_taxable_ytd,
            stcg_taxable_period, stcg_taxable_ytd,
            int_taxable_period, int_taxable_ytd,
            ltcg_taxable_period, ltcg_taxable_ytd,
            tax_exempt_total_period, tax_exempt_total_ytd,
            divs_tax_exempt_period, divs_tax_exempt_ytd,
            int_tax_exempt_period, int_tax_exempt_ytd,
            roc_period, roc_ytd,
            grand_total_period, grand_total_ytd,
            -- Realized gains fields
            st_gain_period, st_loss_period,
            lt_gain_ytd, lt_loss_ytd
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """, (
        doc_data_id, doc_id, account_id, account_number, 'combined', statement_date,
        # Portfolio values
        parse_amount(portfolio.get('net_account_value')),
        parse_amount(portfolio.get('beginning_value')),
        parse_amount(portfolio.get('ending_value')),
        # Income values
        parse_amount(income.get('taxable_total_period')),
        parse_amount(income.get('taxable_total_ytd')),
        parse_amount(income.get('divs_taxable_period')),
        parse_amount(income.get('divs_taxable_ytd')),
        parse_amount(income.get('stcg_taxable_period')),
        parse_amount(income.get('stcg_taxable_ytd')),
        parse_amount(income.get('int_taxable_period')),
        parse_amount(income.get('int_taxable_ytd')),
        parse_amount(income.get('ltcg_taxable_period')),
        parse_amount(income.get('ltcg_taxable_ytd')),
        parse_amount(income.get('tax_exempt_total_period')),
        parse_amount(income.get('tax_exempt_total_ytd')),
        parse_amount(income.get('divs_tax_exempt_period')),
        parse_amount(income.get('divs_tax_exempt_ytd')),
        parse_amount(income.get('int_tax_exempt_period')),
        parse_amount(income.get('int_tax_exempt_ytd')),
        parse_amount(income.get('roc_period')),
        parse_amount(income.get('roc_ytd')),
        parse_amount(income.get('grand_total_period')),
        parse_amount(income.get('grand_total_ytd')),
        # Gains values
        parse_amount(gains.get('st_gain_period') if gains else None),
        parse_amount(gains.get('st_loss_period') if gains else None),
        parse_amount(gains.get('lt_gain_ytd') if gains else None),
        parse_amount(gains.get('lt_loss_ytd') if gains else None)
    ))

    return 1

def move_to_loaded(json_path):
    """Move file to loaded directory"""
    loaded_dir = json_path.parent.parent / "5loaded"
    loaded_dir.mkdir(exist_ok=True)
    destination = loaded_dir / json_path.name
    shutil.move(str(json_path), str(destination))
    return destination

def load_document(json_path):
    """Main loader function - process entire document"""
    json_path = Path(json_path)
    print(f"Loading: {json_path}")

    # Load JSON
    with open(json_path) as f:
        data = json.load(f)

    # Calculate JSON file hash before any database operations
    json_content = json.dumps(data, sort_keys=True)
    json_md5_hash = hashlib.md5(json_content.encode()).hexdigest()

    # Determine extraction type from JSON content
    extraction_type = None
    if any('holdings' in account_data for account_data in data.get('accounts', [])):
        extraction_type = 'holdings'
    elif any(section in account_data for account_data in data.get('accounts', [])
            for section in ['dividends_interest_income', 'securities_bought_sold', 'deposits', 'withdrawals']):
        extraction_type = 'activities'
    else:
        # Fallback to metadata extraction_type
        extraction_type = data.get('extraction_metadata', {}).get('extraction_type', 'unknown')

    # Get institution
    institution = data.get('extraction_metadata', {}).get('institution') or \
                 data.get('document_data', {}).get('institution')
    if not institution:
        raise ValueError("Missing institution in JSON")

    with connect_db() as conn:
        try:

            # Process first account to get institution
            accounts = data.get('accounts', [])
            if not accounts:
                raise ValueError("No accounts found in JSON")

            # Lookup institution first
            institution_id = lookup_institution(institution, conn)

            # Create document with incremental loading support
            loaded_path = move_to_loaded(json_path)
            doc_id = create_document(data, institution_id, loaded_path, extraction_type, json_md5_hash, conn)

            total_positions = 0
            total_transactions = 0

            # Parse statement date once for all accounts
            statement_date = parse_date(
                data.get('document_data', {}).get('statement_date'),
                datetime.now().year
            )

            # Process each account
            for account_data in accounts:
                account_number = account_data.get('account_number')

                if not account_number:
                    print(f"Warning: Skipping account missing number")
                    continue

                # Lookup existing account - now returns both account_id and entity_id
                account_id, entity_id = lookup_account(account_number, institution_id, conn)

                # Link document to account
                link_document_account(doc_id, account_id, conn)

                # Load positions if present
                if 'holdings' in account_data:
                    positions_loaded = load_positions(
                        account_data, doc_id, account_id, entity_id, statement_date, conn
                    )
                    total_positions += positions_loaded
                    if positions_loaded > 0:
                        print(f"  Loaded {positions_loaded} positions for account {account_number}")

                # Load activities if present
                transactions_loaded = load_activities(
                    account_data, doc_id, account_id, entity_id, conn
                )
                total_transactions += transactions_loaded
                if transactions_loaded > 0:
                    print(f"  Loaded {transactions_loaded} transactions for account {account_number}")

                # Load document-level summary data if present
                doc_data_loaded = load_doc_level_data(
                    account_data, doc_id, account_id, statement_date, conn
                )
                if doc_data_loaded > 0:
                    print(f"  Loaded {doc_data_loaded} summary data fields for account {account_number}")

            conn.commit()
            print(f"Success: {total_positions} positions, {total_transactions} transactions")
            print(f"Moved to: {loaded_path}")

        except Exception as e:
            import traceback
            print(f"Error during processing: {e}")
            traceback.print_exc()
            conn.rollback()
            # Move file back if it was moved
            if 'loaded_path' in locals():
                shutil.move(str(loaded_path), str(json_path))
            raise e

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 simple_loader.py path/to/extraction.json")
        sys.exit(1)

    try:
        load_document(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)