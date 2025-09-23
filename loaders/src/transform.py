"""
Data Transformation Module for Database Loader

Created: 09/23/25 11:05AM
Purpose: Transform extracted data into database-ready formats
Updates:
  - 09/23/25 11:05AM: Initial implementation
  - 09/23/25 1:03PM: Updated infer_account_type to handle None values without substitution

Handles date parsing, amount conversion, and type inference.
Preserves source data integrity - returns None instead of default values when data missing.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import re

def parse_date(date_str: str, tax_year: int = None) -> Optional[date]:
    """
    Parse various date formats into date object.

    Args:
        date_str: Date string to parse
        tax_year: Year to use for MM/DD format

    Returns:
        date object or None if unparseable
    """
    if not date_str:
        return None

    # Clean the string
    date_str = date_str.strip()

    # Try different formats
    formats = [
        "%Y-%m-%d",    # ISO format
        "%m/%d/%Y",    # MM/DD/YYYY
        "%m/%d/%y",    # MM/DD/YY
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Try MM/DD format with tax year
    if tax_year and "/" in date_str:
        try:
            month, day = date_str.split("/")
            return date(tax_year, int(month), int(day))
        except:
            pass

    return None

def parse_amount(amount_str: str) -> Optional[Decimal]:
    """
    Convert string amounts to Decimal.

    Args:
        amount_str: Amount string like "$1,234.56" or "(1,234.56)"

    Returns:
        Decimal or None if unparseable
    """
    if not amount_str:
        return None

    # Remove currency symbols and commas
    clean = re.sub(r'[$,]', '', str(amount_str))

    # Handle parentheses as negative
    if '(' in clean and ')' in clean:
        clean = '-' + re.sub(r'[()]', '', clean)

    try:
        return Decimal(clean)
    except:
        return None

def infer_transaction_type(description: str) -> str:
    """
    Determine transaction type from description.

    Args:
        description: Transaction description

    Returns:
        Transaction type string
    """
    if not description:
        return 'other'  # Cannot infer type without description

    desc_upper = description.upper()

    # Check for specific types
    if 'DIVIDEND' in desc_upper:
        return 'dividend'
    elif 'INTEREST' in desc_upper:
        return 'interest'
    elif 'BUY' in desc_upper or 'BOUGHT' in desc_upper:
        return 'buy'
    elif 'SELL' in desc_upper or 'SOLD' in desc_upper:
        return 'sell'
    elif 'FEE' in desc_upper or 'CHARGE' in desc_upper:
        return 'fee'
    elif 'TRANSFER' in desc_upper:
        if 'IN' in desc_upper:
            return 'transfer_in'
        elif 'OUT' in desc_upper:
            return 'transfer_out'
    elif 'DEPOSIT' in desc_upper:
        return 'transfer_in'  # Deposits are incoming transfers

    return 'other'

def infer_account_type(account_name: str) -> str:
    """
    Infer account type from name or description.

    Args:
        account_name: Account name or description (can be None)

    Returns:
        Account type string or None if no name provided
    """
    if not account_name:
        return None

    name_upper = account_name.upper()

    if 'IRA' in name_upper:
        if 'ROTH' in name_upper:
            return 'roth_ira'
        return 'ira'
    elif '401' in name_upper:
        return '401k'
    elif 'CASH' in name_upper or 'CMA' in name_upper:
        return 'cash_management'
    elif 'CHECKING' in name_upper:
        return 'checking'
    elif 'SAVINGS' in name_upper:
        return 'savings'

    return 'brokerage'  # Default when type cannot be determined from name