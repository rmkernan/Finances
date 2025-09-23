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
Purpose: Pure transcription system to load JSON extractions into PostgreSQL database

Design Principles:
- Table-driven activity processing
- No inference - loads exactly what extractor determined
- Handles activities and/or holdings from same accounts array
- Auto-moves files to loaded directory on success
- Populates document_accounts junction table for consolidated statements
- Loads ALL attributes defined in JSON specifications

Usage:
    python3 simple_loader.py path/to/extraction.json
"""

import json
import sys
import uuid
import shutil
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

# Cache for mapping lookups to avoid repeated database queries
_mapping_cache = {}

def get_mapping(mapping_type, source_value, conn):
    """Get type and subtype mapping from database with caching"""
    cache_key = f"{mapping_type}:{source_value}"

    if cache_key not in _mapping_cache:
        cur = conn.cursor()
        cur.execute("""
            SELECT target_type, target_subtype
            FROM data_mappings
            WHERE mapping_type = %s AND source_value = %s
        """, (mapping_type, source_value))

        result = cur.fetchone()
        if result:
            _mapping_cache[cache_key] = {
                'type': result['target_type'],
                'subtype': result['target_subtype']
            }
        else:
            # Fallback for unmapped values - store null to avoid repeated lookups
            _mapping_cache[cache_key] = None

    return _mapping_cache[cache_key]

def get_transaction_type_and_subtype(section_name, description, security_name, conn):
    """
    Get transaction type and subtype using cascading mapping logic.

    Priority order (highest to lowest):
    1. Security patterns (CLOSING TRANSACTION, OPENING TRANSACTION, ASSIGNED PUTS/CALLS)
    2. Description-based mapping (Muni Exempt Int → interest/muni_exempt)
    3. Section-based mapping (dividends_interest_income → income/investment)
    4. Raw section name as fallback

    Args:
        section_name: JSON section where transaction was found (e.g., 'dividends_interest_income')
        description: Transaction description (e.g., 'Muni Exempt Int')
        security_name: Security description (e.g., 'PUT (COIN) COINBASE... CLOSING TRANSACTION')
        conn: Database connection

    Returns:
        tuple: (transaction_type, transaction_subtype)
    """

    # Start with description-based mapping for precise categorization
    # This handles cases like "Muni Exempt Int" → interest/muni_exempt vs "Dividend Received" → dividend/received
    if description:
        desc_mapping = get_mapping('transaction_descriptions', description, conn)
        if desc_mapping:
            transaction_type = desc_mapping['type']
            transaction_subtype = desc_mapping['subtype']
        else:
            # Fall back to section-based mapping for type
            section_mapping = get_mapping('activity_sections', section_name, conn)
            if section_mapping:
                transaction_type = section_mapping['type']
                transaction_subtype = section_mapping['subtype']
            else:
                transaction_type = section_name
                transaction_subtype = None
    else:
        # Fall back to section-based mapping when no description available
        section_mapping = get_mapping('activity_sections', section_name, conn)
        if section_mapping:
            transaction_type = section_mapping['type']
            transaction_subtype = section_mapping['subtype']
        else:
            transaction_type = section_name
            transaction_subtype = None

    # Security pattern overrides have highest priority for subtypes
    # This handles options lifecycle: OPENING TRANSACTION, CLOSING TRANSACTION, ASSIGNED PUTS/CALLS
    if security_name:
        cur = conn.cursor()
        cur.execute("""
            SELECT source_value, target_subtype
            FROM data_mappings
            WHERE mapping_type = 'security_patterns'
            ORDER BY LENGTH(source_value) DESC  -- Longer patterns first (e.g., "ASSIGNED PUTS" before "PUTS")
        """)
        patterns = cur.fetchall()

        for pattern_row in patterns:
            pattern = pattern_row['source_value']
            if pattern in security_name:
                transaction_subtype = pattern_row['target_subtype']  # Override any previous subtype
                break

    return transaction_type, transaction_subtype

def get_security_classification(security_name, conn):
    """
    Get security classification from security name patterns.

    Currently handles options classification:
    - "CALL (" → 'call'
    - "PUT (" → 'put'
    - "ASSIGNED CALLS" → 'call'
    - "ASSIGNED PUTS" → 'put'

    Args:
        security_name: Security description from transaction data
        conn: Database connection

    Returns:
        str: Security class ('call', 'put') or None if no pattern matches

    Examples:
        "CALL (COIN) COINBASE..." → 'call'
        "PUT (CRWV) COREWEAVE..." → 'put'
        "TESLA INC COM ASSIGNED PUTS" → 'put'
        "AT&T INC COM USD1" → None
    """
    if not security_name:
        return None

    # Get all security classification patterns, ordered by length for specificity
    # This ensures "ASSIGNED PUTS" matches before "PUT ("
    cur = conn.cursor()
    cur.execute("""
        SELECT source_value, target_subtype
        FROM data_mappings
        WHERE mapping_type = 'security_classification'
        ORDER BY LENGTH(source_value) DESC
    """)
    patterns = cur.fetchall()

    # Check each pattern against the security name
    for pattern_row in patterns:
        pattern = pattern_row['source_value']
        if pattern in security_name:
            return pattern_row['target_subtype']

    return None

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
        SELECT id FROM accounts
        WHERE account_number = %s AND institution_id = %s
    """, (account_number, institution_id))
    result = cur.fetchone()
    if not result:
        raise ValueError(f"Account '{account_number}' not found at institution. Reference data must be loaded first via process-inbox command.")
    return result['id']

def create_document(data, institution_id, loaded_path, conn):
    """Create document record with full extraction metadata"""
    cur = conn.cursor()

    metadata = data.get('extraction_metadata', {})
    doc_data = data.get('document_data', {})

    # Get MD5 hash for duplicate detection
    doc_hash = metadata.get('doc_md5_hash')
    if not doc_hash:
        raise ValueError("Missing doc_md5_hash in extraction metadata")

    # Check for duplicate
    cur.execute("SELECT id FROM documents WHERE doc_md5_hash = %s", (doc_hash,))
    if cur.fetchone():
        raise ValueError(f"Document with hash {doc_hash} already exists")

    # Create document
    doc_id = str(uuid.uuid4())
    file_name = Path(metadata.get('file_path', 'unknown.pdf')).name

    # Store extraction metadata as JSON in a metadata column
    extraction_metadata = {
        'extraction_type': metadata.get('extraction_type'),
        'extraction_timestamp': metadata.get('extraction_timestamp'),
        'extractor_version': metadata.get('extractor_version'),
        'pages_processed': metadata.get('pages_processed'),
        'extraction_notes': metadata.get('extraction_notes', []),
        'file_hash': metadata.get('file_hash')
    }

    cur.execute("""
        INSERT INTO documents (
            id, institution_id, tax_year, document_type,
            file_path, file_name, doc_md5_hash,
            period_start, period_end, processed_at, extraction_notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        doc_id, institution_id,
        datetime.now().year,  # Tax year
        'statement',  # Document type
        str(loaded_path), file_name, doc_hash,
        parse_date(doc_data.get('period_start'), datetime.now().year),
        parse_date(doc_data.get('period_end'), datetime.now().year),
        datetime.now(),
        json.dumps(extraction_metadata)  # Store extraction metadata as JSON in notes
    ))

    return doc_id

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
            position.get('sec_type'),
            position.get('sec_subtype'),
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

            # Get transaction type and subtype using dynamic mapping system
            # This replaces the old hardcoded ACTIVITY_SECTIONS mapping with flexible database-driven rules
            description = activity.get('description') or activity.get('sec_description', 'Unknown')
            security_name = activity.get('sec_description')
            transaction_type, transaction_subtype = get_transaction_type_and_subtype(section_name, description, security_name, conn)

            # Get security classification (call, put, etc.) for options tracking
            # This enables matching opening/closing transactions and proper options categorization
            sec_class = get_security_classification(security_name, conn)

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
    count = 0
    account_number = account_data.get('account_number')

    # Load portfolio summary
    if 'portfolio_summary' in account_data:
        portfolio = account_data['portfolio_summary']
        for field, value in portfolio.items():
            if value is not None:
                doc_data_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO doc_level_data (id, document_id, account_id, account_number, doc_section,
                                                field_name, field_value, as_of_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (doc_data_id, doc_id, account_id, account_number,
                      'portfolio_summary', field, str(value), statement_date))
                count += 1

    # Load income_summary
    if 'income_summary' in account_data:
        income = account_data['income_summary']
        for field, value in income.items():
            if value is not None:
                doc_data_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO doc_level_data (id, document_id, account_id, account_number, doc_section,
                                                field_name, field_value, as_of_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (doc_data_id, doc_id, account_id, account_number,
                      'income_summary', field, str(value), statement_date))
                count += 1

    # Load realized_gains
    if 'realized_gains' in account_data:
        gains = account_data['realized_gains']
        for field, value in gains.items():
            if value is not None:
                doc_data_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO doc_level_data (id, document_id, account_id, account_number, doc_section,
                                                field_name, field_value, as_of_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (doc_data_id, doc_id, account_id, account_number,
                      'realized_gains', field, str(value), statement_date))
                count += 1

    return count

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

    # Get institution
    institution = data.get('extraction_metadata', {}).get('institution') or \
                 data.get('document_data', {}).get('institution')
    if not institution:
        raise ValueError("Missing institution in JSON")

    with connect_db() as conn:
        try:
            # Process first account to get entity and institution
            accounts = data.get('accounts', [])
            if not accounts:
                raise ValueError("No accounts found in JSON")

            first_account = accounts[0]
            entity_name = first_account.get('account_holder_name')
            if not entity_name:
                raise ValueError("Missing account_holder_name in first account")

            # Lookup existing entities and institutions
            entity_id = lookup_entity(entity_name, conn)
            institution_id = lookup_institution(institution, conn)

            # Create document (checks for duplicates)
            loaded_path = move_to_loaded(json_path)
            doc_id = create_document(data, institution_id, loaded_path, conn)

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

                # Lookup existing account
                account_id = lookup_account(account_number, institution_id, conn)

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