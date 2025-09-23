"""
Core Loading Module for Database Loader

Created: 09/23/25 11:05AM
Purpose: Load positions and activities data into database
Updates:
  - 09/23/25 11:05AM: Initial implementation
  - 09/23/25 12:49PM: Added unified account-centric loader supporting both activities and holdings per account
  - 09/23/25 1:01PM: Removed all value substitutions - loader now preserves source data exactly as-is
  - 09/23/25 1:15PM: Converted to pure transcription system - no inference, only loads what extractor determined

Core logic for loading financial data into database tables.
PURE TRANSCRIPTION: Loads only what the extractor determined and wrote to JSON.
NO INFERENCE: All interpretation should be done by extractor agents, not loader.
"""

import uuid
from typing import Dict, Any, List
from decimal import Decimal
from . import transform
from . import entities

def load_positions(data: Dict[str, Any], doc_id: str, conn, config: Dict[str, Any]) -> int:
    """
    Load position records into database.

    Args:
        data: Positions JSON data
        doc_id: Document ID for foreign key
        conn: Database connection
        config: Configuration dictionary

    Returns:
        Number of positions loaded
    """
    cursor = conn.cursor()
    count = 0
    account_ids_used = []

    # Get institution from metadata
    institution_name = data.get("extraction_metadata", {}).get("institution")

    # Process each account's holdings - handle both top-level holdings and accounts with holdings
    accounts_to_process = data.get("holdings", data.get("accounts", []))

    for account_data in accounts_to_process:
        account_number = account_data.get("account_number")
        account_holder = account_data.get("account_holder_name",
                                         account_data.get("account_holder", "Unknown"))

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity
        entity_id = entities.get_or_create_entity(account_holder, conn, config)

        # Get or create institution
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Get or create account
        account_type = account_data.get("account_type")
        if not account_type:
            raise ValueError(f"Missing required account_type for account {account_number}. Extractor should have determined this.")
        account_id = entities.get_or_create_account(
            account_number, entity_id, institution_id, account_type, conn, config
        )

        account_ids_used.append(account_id)

        # Load each position - handle both positions and holdings arrays
        positions_to_process = account_data.get("positions", account_data.get("holdings", []))
        for position in positions_to_process:
            position_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO positions (
                    id, document_id, account_id, entity_id,
                    position_date, account_number,
                    sec_ticker, cusip, sec_name, sec_type,
                    quantity, price, end_market_value,
                    cost_basis, unrealized_gain_loss
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                position_id, doc_id, account_id, entity_id,
                transform.parse_date(
                    data.get("extraction_metadata", {}).get("statement_date"),
                    config["defaults"]["tax_year"]
                ),
                account_number,
                position.get("symbol"),
                position.get("cusip"),
                position.get("sec_description"),
                position.get("sec_type"),
                transform.parse_amount(position.get("quantity")),
                transform.parse_amount(position.get("price")),
                transform.parse_amount(position.get("market_value")),
                transform.parse_amount(position.get("cost_basis")),
                transform.parse_amount(position.get("unrealized_gain_loss"))
            ))

            count += 1

    cursor.close()
    print(f"Loaded {count} positions")

    # Return account IDs for document linking
    return count, account_ids_used

def load_activities(data: Dict[str, Any], doc_id: str, conn, config: Dict[str, Any]) -> int:
    """
    Load transaction records into database.

    Args:
        data: Activities JSON data
        doc_id: Document ID for foreign key
        conn: Database connection
        config: Configuration dictionary

    Returns:
        Number of transactions loaded
    """
    cursor = conn.cursor()
    count = 0
    account_ids_used = []

    # Get institution from metadata
    institution_name = data.get("extraction_metadata", {}).get("institution")

    # Process each account's activities
    for account_data in data.get("activities", []):
        account_number = account_data.get("account_number")
        # Require account holder name - fail if missing
        account_holder = account_data.get("account_holder")
        if not account_holder:
            raise ValueError(f"Missing required account_holder for account {account_number}")

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity
        entity_id = entities.get_or_create_entity(account_holder, conn, config)

        # Get or create institution
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Get or create account
        account_type = account_data.get("account_type")
        if not account_type:
            raise ValueError(f"Missing required account_type for account {account_number}. Extractor should have determined this.")
        account_id = entities.get_or_create_account(
            account_number, entity_id, institution_id, account_type, conn, config
        )

        account_ids_used.append(account_id)

        # Load each transaction
        for activity in account_data.get("transactions", []):
            transaction_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO transactions (
                    id, entity_id, document_id, account_id,
                    transaction_date, settlement_date,
                    transaction_type, description, amount,
                    security_name, security_identifier,
                    quantity, price_per_unit, fees,
                    source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                transaction_id, entity_id, doc_id, account_id,
                transform.parse_date(
                    activity.get("transaction_date"),
                    config["defaults"]["tax_year"]
                ),
                transform.parse_date(
                    activity.get("settlement_date"),
                    config["defaults"]["tax_year"]
                ),
                transaction_type,  # Use section-determined type, not inferred from description
                activity.get("description"),
                transform.parse_amount(activity.get("amount")),
                activity.get("security_name"),
                activity.get("symbol"),
                transform.parse_amount(activity.get("quantity")),
                transform.parse_amount(activity.get("price")),
                transform.parse_amount(activity.get("fees")),
                'statement'
            ))

            count += 1

    cursor.close()
    print(f"Loaded {count} transactions")

    return count, account_ids_used

def load_accounts_activities(data: Dict[str, Any], doc_id: str, conn, config: Dict[str, Any]) -> tuple:
    """
    Load transaction records from accounts structure.

    Args:
        data: JSON data with accounts array containing activities
        doc_id: Document ID for foreign key
        conn: Database connection
        config: Configuration dictionary

    Returns:
        Tuple of (count, account_ids_used)
    """
    cursor = conn.cursor()
    count = 0
    account_ids_used = []

    # Get institution from metadata or document_data
    institution_name = data.get("extraction_metadata", {}).get("institution") or \
                      data.get("document_data", {}).get("institution")

    # Process each account
    for account_data in data.get("accounts", []):
        account_number = account_data.get("account_number")
        # Require account holder name - fail if missing
        account_holder = account_data.get("account_holder_name") or account_data.get("account_name")
        if not account_holder:
            raise ValueError(f"Missing required account_holder_name for account {account_number}")

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity
        entity_id = entities.get_or_create_entity(account_holder, conn, config)

        # Get or create institution
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Get or create account
        account_type = account_data.get("account_type")
        if not account_type:
            raise ValueError(f"Missing required account_type for account {account_number}. Extractor should have determined this.")
        account_id = entities.get_or_create_account(
            account_number, entity_id, institution_id, account_type, conn, config
        )

        account_ids_used.append(account_id)

        # Process different types of activities
        activity_sections = [
            ('dividends_interest_income', 'dividend'),
            ('deposits', 'deposit'),
            ('withdrawals', 'withdrawal'),
            ('core_fund_activity', 'core_fund'),
            ('securities_bought_sold', 'trade'),
            ('other_activity_in', 'other_in'),
            ('other_activity_out', 'other_out'),
            ('exchanges_in', 'exchange_in'),
            ('exchanges_out', 'exchange_out'),
            ('fees_charges', 'fee'),
            ('billpay', 'billpay')
        ]

        for section_name, transaction_type in activity_sections:
            activities = account_data.get(section_name, [])

            for activity in activities:
                transaction_id = str(uuid.uuid4())

                # Parse transaction data based on section
                if section_name == 'dividends_interest_income':
                    trans_date = transform.parse_date(activity.get("settlement_date"), config["defaults"]["tax_year"])
                    settlement_date = trans_date
                    description = activity.get("description")
                    amount = transform.parse_amount(activity.get("amount"))
                    security_name = activity.get("sec_description")
                    security_identifier = activity.get("sec_symbol")
                    quantity = transform.parse_amount(activity.get("quantity"))
                    price_per_unit = transform.parse_amount(activity.get("price_per_unit"))

                elif section_name in ['deposits', 'withdrawals']:
                    trans_date = transform.parse_date(activity.get("date"), config["defaults"]["tax_year"])
                    settlement_date = trans_date
                    description = activity.get("description")
                    amount = transform.parse_amount(activity.get("amount"))
                    security_name = None
                    security_identifier = None
                    quantity = None
                    price_per_unit = None

                elif section_name == 'core_fund_activity':
                    trans_date = transform.parse_date(activity.get("settlement_date"), config["defaults"]["tax_year"])
                    settlement_date = trans_date
                    description = activity.get('description')
                    amount = transform.parse_amount(activity.get("amount"))
                    security_name = activity.get("sec_description")
                    security_identifier = activity.get("sec_symbol")
                    quantity = transform.parse_amount(activity.get("quantity"))
                    price_per_unit = transform.parse_amount(activity.get("price_per_unit"))

                else:
                    # Generic handling for other sections
                    trans_date = transform.parse_date(
                        activity.get("date") or activity.get("settlement_date"),
                        config["defaults"]["tax_year"]
                    )
                    settlement_date = trans_date
                    description = activity.get("description")
                    amount = transform.parse_amount(activity.get("amount"))
                    security_name = activity.get("sec_description")
                    security_identifier = activity.get("sec_symbol") or activity.get("symbol")
                    quantity = transform.parse_amount(activity.get("quantity"))
                    price_per_unit = transform.parse_amount(activity.get("price_per_unit") or activity.get("price"))

                cursor.execute("""
                    INSERT INTO transactions (
                        id, entity_id, document_id, account_id,
                        transaction_date, settlement_date,
                        transaction_type, description, amount,
                        security_name, security_identifier,
                        quantity, price_per_unit, fees,
                        source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    transaction_id, entity_id, doc_id, account_id,
                    trans_date, settlement_date,
                    transaction_type, description, amount,
                    security_name, security_identifier,
                    quantity, price_per_unit, None,  # fees not in this structure
                    'statement'
                ))

                count += 1

    cursor.close()
    print(f"Loaded {count} transactions from accounts structure")

    return count, account_ids_used

def load_accounts_data(data: Dict[str, Any], doc_id: str, conn, config: Dict[str, Any]) -> tuple:
    """
    Unified loader that processes each account and loads whatever data is present.

    Args:
        data: JSON data with accounts array
        doc_id: Document ID for foreign key
        conn: Database connection
        config: Configuration dictionary

    Returns:
        Tuple of (total_records_loaded, account_ids_used)
    """
    total_records = 0
    all_account_ids = []

    # Get institution from metadata or document_data
    institution_name = data.get("extraction_metadata", {}).get("institution") or \
                      data.get("document_data", {}).get("institution")

    # Process each account
    for account_data in data.get("accounts", []):
        account_number = account_data.get("account_number")
        # Require account holder name - fail if missing
        account_holder = account_data.get("account_holder_name") or account_data.get("account_name")
        if not account_holder:
            raise ValueError(f"Missing required account_holder_name for account {account_number}")

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity, institution, and account
        entity_id = entities.get_or_create_entity(account_holder, conn, config)
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)
        account_type = account_data.get("account_type")
        if not account_type:
            raise ValueError(f"Missing required account_type for account {account_number}. Extractor should have determined this.")
        account_id = entities.get_or_create_account(
            account_number, entity_id, institution_id, account_type, conn, config
        )
        all_account_ids.append(account_id)

        # Check for holdings/positions data
        if "holdings" in account_data:
            positions_loaded = load_account_positions(
                account_data, doc_id, account_id, entity_id, data, conn, config
            )
            total_records += positions_loaded
            print(f"Loaded {positions_loaded} positions for account {account_number}")

        # Check for activities data
        activities_loaded = load_account_activities(
            account_data, doc_id, account_id, entity_id, conn, config
        )
        total_records += activities_loaded
        if activities_loaded > 0:
            print(f"Loaded {activities_loaded} transactions for account {account_number}")

    return total_records, all_account_ids

def load_account_positions(account_data: Dict[str, Any], doc_id: str, account_id: str,
                          entity_id: str, full_data: Dict[str, Any], conn, config: Dict[str, Any]) -> int:
    """Load positions for a single account."""
    cursor = conn.cursor()
    count = 0

    # Get statement date from document metadata
    statement_date = full_data.get("document_data", {}).get("statement_date")

    for position in account_data.get("holdings", []):
        position_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO positions (
                id, document_id, account_id, entity_id,
                position_date, account_number,
                sec_ticker, cusip, sec_name, sec_type,
                quantity, price, end_market_value,
                cost_basis, unrealized_gain_loss
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            position_id, doc_id, account_id, entity_id,
            transform.parse_date(statement_date, config["defaults"]["tax_year"]),
            account_data.get("account_number"),
            position.get("sec_symbol"),
            position.get("cusip"),
            position.get("sec_description"),
            position.get("sec_type"),
            transform.parse_amount(position.get("quantity")),
            transform.parse_amount(position.get("price_per_unit")),
            transform.parse_amount(position.get("end_market_value")),
            transform.parse_amount(position.get("cost_basis")),
            transform.parse_amount(position.get("unrealized_gain_loss"))
        ))
        count += 1

    cursor.close()
    return count

def load_account_activities(account_data: Dict[str, Any], doc_id: str, account_id: str,
                           entity_id: str, conn, config: Dict[str, Any]) -> int:
    """Load activities/transactions for a single account."""
    cursor = conn.cursor()
    count = 0

    # Process different types of activities (same logic as load_accounts_activities)
    activity_sections = [
        ('dividends_interest_income', 'dividend'),
        ('deposits', 'deposit'),
        ('withdrawals', 'withdrawal'),
        ('core_fund_activity', 'core_fund'),
        ('securities_bought_sold', 'trade'),
        ('other_activity_in', 'other_in'),
        ('other_activity_out', 'other_out'),
        ('exchanges_in', 'exchange_in'),
        ('exchanges_out', 'exchange_out'),
        ('fees_charges', 'fee'),
        ('billpay', 'billpay')
    ]

    for section_name, transaction_type in activity_sections:
        activities = account_data.get(section_name, [])

        for activity in activities:
            transaction_id = str(uuid.uuid4())

            # Parse transaction data based on section (same parsing logic)
            if section_name == 'dividends_interest_income':
                trans_date = transform.parse_date(activity.get("settlement_date"), config["defaults"]["tax_year"])
                settlement_date = trans_date
                description = activity.get("description")
                amount = transform.parse_amount(activity.get("amount"))
                security_name = activity.get("sec_description")
                security_identifier = activity.get("sec_symbol")
                quantity = transform.parse_amount(activity.get("quantity"))
                price_per_unit = transform.parse_amount(activity.get("price_per_unit"))

            elif section_name in ['deposits', 'withdrawals']:
                trans_date = transform.parse_date(activity.get("date"), config["defaults"]["tax_year"])
                settlement_date = trans_date
                description = activity.get("description")
                amount = transform.parse_amount(activity.get("amount"))
                security_name = None
                security_identifier = None
                quantity = None
                price_per_unit = None

            elif section_name == 'core_fund_activity':
                trans_date = transform.parse_date(activity.get("settlement_date"), config["defaults"]["tax_year"])
                settlement_date = trans_date
                description = activity.get('description')
                amount = transform.parse_amount(activity.get("amount"))
                security_name = activity.get("sec_description")
                security_identifier = activity.get("sec_symbol")
                quantity = transform.parse_amount(activity.get("quantity"))
                price_per_unit = transform.parse_amount(activity.get("price_per_unit"))

            else:
                # Generic handling for other sections
                trans_date = transform.parse_date(
                    activity.get("date") or activity.get("settlement_date"),
                    config["defaults"]["tax_year"]
                )
                settlement_date = trans_date
                description = activity.get("description")
                amount = transform.parse_amount(activity.get("amount"))
                security_name = activity.get("sec_description")
                security_identifier = activity.get("sec_symbol") or activity.get("symbol")
                quantity = transform.parse_amount(activity.get("quantity"))
                price_per_unit = transform.parse_amount(activity.get("price_per_unit") or activity.get("price"))

            cursor.execute("""
                INSERT INTO transactions (
                    id, entity_id, document_id, account_id,
                    transaction_date, settlement_date,
                    transaction_type, description, amount,
                    security_name, security_identifier,
                    quantity, price_per_unit, fees,
                    source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                transaction_id, entity_id, doc_id, account_id,
                trans_date, settlement_date,
                transaction_type, description, amount,
                security_name, security_identifier,
                quantity, price_per_unit, None,  # fees not in this structure
                'statement'
            ))

            count += 1

    cursor.close()
    return count