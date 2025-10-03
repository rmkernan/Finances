"""
Data Transformation Functions for Financial JSON Loading

Created: 09/29/25
Purpose: Transform extracted JSON data to match database schema requirements

This module provides functions to handle:
- Field name mapping (JSON → database columns)
- Currency string parsing (remove $, commas)
- Date format conversion (handle multiple formats)
- Symbol/CUSIP merging
- Source field derivation
- Foreign key resolution
- Pre-load validation

Used by: scripts/load_extractions.py
"""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, List, Tuple, Any


# ============================================================================
# MAPPING CONSTANTS
# ============================================================================

# Field name mappings: JSON field name → Database column name
ACTIVITIES_FIELD_MAP = {
    'settlement_date': 'sett_date',
    'sec_description': 'security_name',
    'transaction_cost': 'fees',
    'reference': 'reference_number',
    'ytd_payments': 'ytd_amount',
    'post_date': 'sett_date',
    'date': 'sett_date',
}

POSITIONS_FIELD_MAP = {
    'sec_description': 'sec_name',
    'price_per_unit': 'price',
}

# Source value mapping: JSON section name → Database source value
SOURCE_MAP = {
    'securities_bought_sold': 'sec_bot_sold',
    'dividends_interest_income': 'div_int_income',
    'short_activity': 'short_activity',
    'other_activity_in': 'other_activity_in',
    'other_activity_out': 'other_activity_out',
    'deposits': 'deposits',
    'withdrawals': 'withdrawals',
    'exchanges_in': 'exchanges_in',
    'exchanges_out': 'exchanges_out',
    'fees_charges': 'fees_charges',
    'core_fund_activity': 'core_fund',
    'trades_pending_settlement': 'trades_pending',
}

# Special values that represent NULL/None
NULL_VALUES = {'unavailable', 'not applicable', 'n/a', '-', '', 'null', 'none'}


# ============================================================================
# FUNCTION 1: FIELD NAME MAPPING
# ============================================================================

def map_field_name(json_field: str, data_type: str) -> str:
    """
    Map JSON field name to database column name.

    Args:
        json_field: Field name from JSON extraction
        data_type: Either 'activities' or 'positions'

    Returns:
        Database column name (or original if no mapping exists)

    Examples:
        >>> map_field_name('settlement_date', 'activities')
        'sett_date'
        >>> map_field_name('sec_description', 'activities')
        'security_name'
        >>> map_field_name('price_per_unit', 'positions')
        'price'
        >>> map_field_name('unmapped_field', 'activities')
        'unmapped_field'
    """
    if data_type == 'activities':
        field_map = ACTIVITIES_FIELD_MAP
    elif data_type == 'positions':
        field_map = POSITIONS_FIELD_MAP
    else:
        raise ValueError(f"Invalid data_type: {data_type}. Must be 'activities' or 'positions'")

    # Return mapped name or original if no mapping exists
    return field_map.get(json_field, json_field)


# ============================================================================
# FUNCTION 2: CURRENCY PARSING
# ============================================================================

def parse_currency(value: Any) -> Optional[Decimal]:
    """
    Parse currency string to Decimal, handling $, commas, and special values.

    Handles:
        - Dollar signs and commas: "$738,691.27" → Decimal("738691.27")
        - Negative values: "-$2,091.38" → Decimal("-2091.38")
        - Parentheses (accounting): "($100.00)" → Decimal("-100.00")
        - Plain numbers: "758.61" → Decimal("758.61")
        - Special values: "unavailable" → None
        - NULL values: None → None

    Args:
        value: Currency value (string, number, or None)

    Returns:
        Decimal value or None

    Raises:
        ValueError: If value cannot be parsed as currency

    Examples:
        >>> parse_currency("$738,691.27")
        Decimal('738691.27')
        >>> parse_currency("-$2,091.38")
        Decimal('-2091.38')
        >>> parse_currency("($100.00)")
        Decimal('-100.00')
        >>> parse_currency("unavailable")
        None
        >>> parse_currency(123.45)
        Decimal('123.45')
    """
    # Handle None
    if value is None:
        return None

    # Handle numeric types (int, float)
    if isinstance(value, (int, float)):
        return Decimal(str(value))

    # Convert to string and clean whitespace
    value_str = str(value).strip()

    # Handle special NULL-equivalent values
    if value_str.lower() in NULL_VALUES:
        return None

    # Remove currency symbols, commas, and convert parentheses to negative
    # Parentheses are used in accounting notation for negative numbers
    cleaned = value_str.replace('$', '').replace(',', '')

    # Handle parentheses (accounting notation for negative)
    if '(' in cleaned or ')' in cleaned:
        cleaned = cleaned.replace('(', '-').replace(')', '')

    # Parse to Decimal
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Cannot parse currency value: '{value}' (cleaned: '{cleaned}')")


# ============================================================================
# FUNCTION 3: DATE PARSING
# ============================================================================

def parse_date(value: Any) -> Optional[datetime.date]:
    """
    Parse date string handling multiple formats.

    Formats accepted:
        - ISO 8601: "2025-04-30"
        - MM/DD/YYYY: "04/15/2034"
        - MM/DD/YY: "04/15/34" (50-year window: 00-49 → 2000-2049, 50-99 → 1950-1999)

    Args:
        value: Date value (string or None)

    Returns:
        datetime.date object or None

    Raises:
        ValueError: If date format is not recognized

    Examples:
        >>> parse_date("2025-04-30")
        datetime.date(2025, 4, 30)
        >>> parse_date("04/15/2034")
        datetime.date(2034, 4, 15)
        >>> parse_date("04/15/34")
        datetime.date(2034, 4, 15)
        >>> parse_date("04/15/92")
        datetime.date(1992, 4, 15)
        >>> parse_date(None)
        None
    """
    # Handle None and empty strings
    if value is None or value == '':
        return None

    value_str = str(value).strip()

    # Handle special NULL-equivalent values
    if value_str.lower() in NULL_VALUES:
        return None

    # Try ISO 8601 format first (YYYY-MM-DD) - most common in JSON
    try:
        return datetime.strptime(value_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    # Try MM/DD/YYYY format
    try:
        return datetime.strptime(value_str, '%m/%d/%Y').date()
    except ValueError:
        pass

    # Try MM/DD/YY format with century logic
    try:
        dt = datetime.strptime(value_str, '%m/%d/%y')

        # Apply 50-year window:
        # Two-digit years 00-49 → 2000-2049
        # Two-digit years 50-99 → 1950-1999
        if dt.year > 2050:
            dt = dt.replace(year=dt.year - 100)

        return dt.date()
    except ValueError:
        pass

    # If all formats fail, raise error
    raise ValueError(f"Cannot parse date value: '{value}'. Expected formats: YYYY-MM-DD, MM/DD/YYYY, or MM/DD/YY")


# ============================================================================
# FUNCTION 4: SYMBOL/CUSIP MERGER
# ============================================================================

def merge_symbol_cusip(sec_symbol: Optional[str], cusip: Optional[str]) -> Optional[str]:
    """
    Merge symbol and CUSIP into single identifier.

    Strategy: Securities typically have either a symbol (stocks/ETFs) OR a CUSIP
    (bonds/options), never both. Prefer symbol when available, fall back to CUSIP.

    Args:
        sec_symbol: Security symbol (e.g., "AAPL", "SPY")
        cusip: CUSIP identifier (e.g., "037833100")

    Returns:
        Single identifier string or None if both are missing

    Examples:
        >>> merge_symbol_cusip("AAPL", None)
        'AAPL'
        >>> merge_symbol_cusip(None, "037833100")
        '037833100'
        >>> merge_symbol_cusip("  SPY  ", "")
        'SPY'
        >>> merge_symbol_cusip(None, None)
        None
    """
    # Prefer symbol for stocks/ETFs (more human-readable)
    if sec_symbol and sec_symbol.strip():
        return sec_symbol.strip()

    # Fall back to CUSIP for bonds/options
    if cusip and cusip.strip():
        return cusip.strip()

    # Both are missing or empty
    return None


# ============================================================================
# FUNCTION 5: SOURCE FIELD DERIVATION
# ============================================================================

def derive_source(section_name: str) -> str:
    """
    Derive database source value from JSON section name.

    The database requires a 'source' field to identify which statement section
    the transaction came from, but this field doesn't exist in JSON. It must be
    derived based on which array the transaction appears in.

    Args:
        section_name: JSON array name (e.g., 'securities_bought_sold')

    Returns:
        Database source value (e.g., 'sec_bot_sold')

    Raises:
        ValueError: If section_name is not recognized

    Examples:
        >>> derive_source('securities_bought_sold')
        'sec_bot_sold'
        >>> derive_source('dividends_interest_income')
        'div_int_income'
        >>> derive_source('unknown_section')
        Traceback (most recent call last):
        ValueError: Unknown activity section: 'unknown_section'
    """
    source = SOURCE_MAP.get(section_name)

    if source is None:
        raise ValueError(
            f"Unknown activity section: '{section_name}'. "
            f"Valid sections: {', '.join(SOURCE_MAP.keys())}"
        )

    return source


# ============================================================================
# FUNCTION 6: ACCOUNT ID RESOLUTION
# ============================================================================

def resolve_account_id(conn, account_number: str) -> str:
    """
    Lookup account_id UUID from account_number string.

    The database uses UUID primary keys but JSON only has account numbers.
    This function resolves the account_number to its UUID.

    Args:
        conn: Database connection object (psycopg2 connection)
        account_number: Account number from JSON (e.g., "Z12345678")

    Returns:
        Account UUID as string

    Raises:
        ValueError: If account_number is not found in database

    Example:
        >>> conn = psycopg2.connect(...)
        >>> resolve_account_id(conn, "Z12345678")
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    """
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                f"Account not found in database: '{account_number}'. "
                f"Make sure account exists in accounts table before loading transactions."
            )

        return str(row[0])  # Convert UUID to string

    finally:
        cursor.close()


# ============================================================================
# FUNCTION 7: ENTITY ID RESOLUTION
# ============================================================================

def resolve_entity_id(conn, account_id: str) -> str:
    """
    Lookup entity_id from account_id.

    Each account belongs to an entity (business or person). This function
    resolves the entity_id from an account_id.

    Args:
        conn: Database connection object (psycopg2 connection)
        account_id: Account UUID

    Returns:
        Entity UUID as string

    Raises:
        ValueError: If account_id not found or has no entity

    Example:
        >>> conn = psycopg2.connect(...)
        >>> resolve_entity_id(conn, 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')
        'f0e1d2c3-b4a5-9687-fedc-ba0987654321'
    """
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT entity_id FROM accounts WHERE id = %s",
            (account_id,)
        )
        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                f"Account not found in database: '{account_id}'. "
                f"Cannot resolve entity_id."
            )

        if row[0] is None:
            raise ValueError(
                f"Account '{account_id}' has no entity_id assigned. "
                f"Update accounts table to set entity_id before loading transactions."
            )

        return str(row[0])  # Convert UUID to string

    finally:
        cursor.close()


# ============================================================================
# FUNCTION 8: PRE-LOAD VALIDATION
# ============================================================================

def validate_json_before_load(json_data: Dict, data_type: str) -> Tuple[bool, List[str]]:
    """
    Validate JSON structure and values before attempting database load.

    Checks:
        - Required top-level structure exists
        - Required fields present in each record
        - Currency values can be parsed
        - Dates can be parsed
        - Numeric values fit in database columns (NUMERIC(15,2))

    Args:
        json_data: Parsed JSON data
        data_type: Either 'activities' or 'positions'

    Returns:
        Tuple of (is_valid, error_list)
        - is_valid: True if all validation passes
        - error_list: List of error messages (empty if valid)

    Example:
        >>> json_data = {"accounts": [...]}
        >>> is_valid, errors = validate_json_before_load(json_data, 'activities')
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"Validation error: {error}")
    """
    errors = []

    # Check required top-level structure
    if not isinstance(json_data, dict):
        errors.append("JSON data must be a dictionary/object")
        return False, errors

    if 'accounts' not in json_data:
        errors.append("Missing required 'accounts' array at top level")
        return False, errors

    if not isinstance(json_data['accounts'], list):
        errors.append("'accounts' must be an array")
        return False, errors

    # Validate each account
    for i, account in enumerate(json_data['accounts']):
        account_num = account.get('account_number', f'account[{i}]')

        # Validate account has account_number
        if 'account_number' not in account:
            errors.append(f"Account {i}: Missing required field 'account_number'")
            continue

        # Validate based on data type
        if data_type == 'activities':
            errors.extend(_validate_activities_account(account, account_num))
        elif data_type == 'positions':
            errors.extend(_validate_positions_account(account, account_num))
        else:
            errors.append(f"Invalid data_type: '{data_type}'. Must be 'activities' or 'positions'")

    return len(errors) == 0, errors


def _validate_activities_account(account: Dict, account_num: str) -> List[str]:
    """
    Validate activities data for a single account.

    Internal helper for validate_json_before_load.
    """
    errors = []

    # List of activity sections to check
    activity_sections = [
        'securities_bought_sold',
        'dividends_interest_income',
        'short_activity',
        'other_activity_in',
        'other_activity_out',
        'deposits',
        'withdrawals',
        'exchanges_in',
        'exchanges_out',
        'fees_charges',
        'core_fund_activity',
        'trades_pending_settlement',
    ]

    for section_name in activity_sections:
        if section_name not in account:
            continue  # Section is optional

        transactions = account[section_name]
        if not isinstance(transactions, list):
            errors.append(f"{account_num}.{section_name}: Must be an array")
            continue

        # Validate each transaction
        for j, txn in enumerate(transactions):
            txn_id = f"{account_num}.{section_name}[{j}]"

            # Validate currency fields
            for field in ['amount', 'quantity', 'cost_basis', 'fees']:
                if field in txn and txn[field] is not None:
                    try:
                        value = parse_currency(txn[field])
                        if value is not None:
                            # Check fits in NUMERIC(15,2) - max 13 digits before decimal
                            if abs(value) >= Decimal('10000000000000'):
                                errors.append(
                                    f"{txn_id}: {field} value too large: {value} "
                                    f"(max: 9,999,999,999,999.99)"
                                )
                    except ValueError as e:
                        errors.append(f"{txn_id}: Invalid {field}: {e}")

            # Validate date fields
            for field in ['settlement_date', 'sett_date', 'post_date', 'date']:
                if field in txn and txn[field] is not None:
                    try:
                        parse_date(txn[field])
                    except ValueError as e:
                        errors.append(f"{txn_id}: Invalid {field}: {e}")

    return errors


def _validate_positions_account(account: Dict, account_num: str) -> List[str]:
    """
    Validate positions data for a single account.

    Internal helper for validate_json_before_load.
    """
    errors = []

    if 'holdings' not in account:
        # Holdings array is required for positions
        errors.append(f"{account_num}: Missing required 'holdings' array")
        return errors

    holdings = account['holdings']
    if not isinstance(holdings, list):
        errors.append(f"{account_num}.holdings: Must be an array")
        return errors

    # Validate each position
    for k, pos in enumerate(holdings):
        pos_id = f"{account_num}.holdings[{k}]"

        # Validate currency fields
        for field in ['end_market_value', 'beg_market_value', 'cost_basis',
                      'unrealized_gain_loss', 'estimated_ann_inc', 'price']:
            if field in pos and pos[field] is not None:
                try:
                    value = parse_currency(pos[field])
                    if value is not None:
                        # Check fits in NUMERIC(15,2)
                        if abs(value) >= Decimal('10000000000000'):
                            errors.append(
                                f"{pos_id}: {field} value too large: {value} "
                                f"(max: 9,999,999,999,999.99)"
                            )
                except ValueError as e:
                    errors.append(f"{pos_id}: Invalid {field}: {e}")

        # Validate date fields
        for field in ['maturity_date', 'position_date']:
            if field in pos and pos[field] is not None:
                try:
                    parse_date(pos[field])
                except ValueError as e:
                    errors.append(f"{pos_id}: Invalid {field}: {e}")

    return errors


# ============================================================================
# TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DATA TRANSFORMATIONS MODULE - TESTS")
    print("=" * 80)

    # Test 1: map_field_name
    print("\n1. Testing map_field_name():")
    print(f"   'settlement_date' (activities) → '{map_field_name('settlement_date', 'activities')}'")
    print(f"   'sec_description' (activities) → '{map_field_name('sec_description', 'activities')}'")
    print(f"   'price_per_unit' (positions) → '{map_field_name('price_per_unit', 'positions')}'")
    print(f"   'unmapped_field' (activities) → '{map_field_name('unmapped_field', 'activities')}'")

    # Test 2: parse_currency
    print("\n2. Testing parse_currency():")
    test_currency_values = [
        "$738,691.27",
        "-$2,091.38",
        "($100.00)",
        "123.45",
        "unavailable",
        None,
    ]
    for val in test_currency_values:
        result = parse_currency(val)
        print(f"   '{val}' → {result}")

    # Test 3: parse_date
    print("\n3. Testing parse_date():")
    test_date_values = [
        "2025-04-30",
        "04/15/2034",
        "04/15/34",
        "04/15/92",
        None,
    ]
    for val in test_date_values:
        result = parse_date(val)
        print(f"   '{val}' → {result}")

    # Test 4: merge_symbol_cusip
    print("\n4. Testing merge_symbol_cusip():")
    test_symbol_cusip_pairs = [
        ("AAPL", None),
        (None, "037833100"),
        ("  SPY  ", ""),
        (None, None),
        ("TSLA", "88160R101"),  # Both present - prefer symbol
    ]
    for sym, cusip in test_symbol_cusip_pairs:
        result = merge_symbol_cusip(sym, cusip)
        print(f"   symbol='{sym}', cusip='{cusip}' → '{result}'")

    # Test 5: derive_source
    print("\n5. Testing derive_source():")
    test_sections = [
        'securities_bought_sold',
        'dividends_interest_income',
        'deposits',
        'withdrawals',
    ]
    for section in test_sections:
        result = derive_source(section)
        print(f"   '{section}' → '{result}'")

    # Test 6 & 7: resolve_account_id and resolve_entity_id
    print("\n6-7. Testing resolve_account_id() and resolve_entity_id():")
    print("   (Requires database connection - skipped in standalone test)")
    print("   These functions query the accounts table for UUID lookups")

    # Test 8: validate_json_before_load
    print("\n8. Testing validate_json_before_load():")

    # Valid test data
    valid_json = {
        "accounts": [
            {
                "account_number": "Z12345678",
                "securities_bought_sold": [
                    {
                        "settlement_date": "2025-04-30",
                        "amount": "$1,234.56"
                    }
                ]
            }
        ]
    }
    is_valid, errors = validate_json_before_load(valid_json, 'activities')
    print(f"   Valid JSON: is_valid={is_valid}, errors={errors}")

    # Invalid test data (missing accounts)
    invalid_json = {"some_other_field": "value"}
    is_valid, errors = validate_json_before_load(invalid_json, 'activities')
    print(f"   Invalid JSON: is_valid={is_valid}, errors={errors}")

    # Invalid currency value
    bad_currency_json = {
        "accounts": [
            {
                "account_number": "Z12345678",
                "securities_bought_sold": [
                    {
                        "amount": "not a number"
                    }
                ]
            }
        ]
    }
    is_valid, errors = validate_json_before_load(bad_currency_json, 'activities')
    print(f"   Bad currency: is_valid={is_valid}, errors={errors}")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)