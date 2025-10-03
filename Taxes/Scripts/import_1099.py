#!/usr/bin/env python3
"""
1099 Tax Form Import Script

Created: 2025-01-02
Updated: 2025-01-02 - Initial script creation with Fidelity CSV parsing and Google Sheets import
Updated: 2025-10-01 4:00PM - Completed main processing loop and command-line interface
Updated: 2025-10-01 4:25PM - Implemented Google Sheets API integration for duplicate checking and data writing
Updated: 2025-10-01 4:27PM - Added global duplicate checking, column consistency validation, and all-or-nothing import policy
Updated: 2025-10-01 5:30PM - Implemented 1099-B breakdown by reporting category (5 categories × 6 metrics)
Updated: 2025-10-01 5:40PM - Fixed Total Proceeds offset, added Account Name row extraction from filename
Updated: 2025-10-01 5:45PM - Adjusted for blank row 16: DATA_START_ROW now 18, updated all row references
Updated: 2025-10-01 5:51PM - Changed default for missing values from empty to "-"
Updated: 2025-10-01 6:17PM - Smart handling: checkboxes/text fields empty, numeric fields show "-" when missing
Updated: 2025-10-01 6:23PM - Fixed: only write "-" to data box rows, leave structural/separator rows blank
Updated: 2025-10-01 6:27PM - Adjusted 1099-B for extra blank row 18: data now starts at row 20 (not 18)

Purpose:
    Extract 1099 tax form data from Fidelity CSV files and import into consolidated
    Google Sheets worksheet. Handles deduplication, data validation, and preserves
    user formatting.

Usage:
    python3 import_1099.py --csv <path_to_csv> [--check-duplicates] [--dry-run]

Arguments:
    --csv           Path to Fidelity 1099 CSV file
    --check-duplicates  Check for existing account before import (default: True)
    --dry-run       Show what would be imported without actually importing
    --account       Specific account number to import (if CSV has multiple)

Requirements:
    - pandas
    - Google Sheets API credentials (see documentation)

Reference Documentation:
    /Users/richkernan/Projects/Finances/Taxes/Docs/1099-import-map.md
"""

import pandas as pd
import argparse
import sys
from typing import Dict, List, Optional, Tuple

# ============================================================================
# CONFIGURATION - Update these if spreadsheet structure changes
# ============================================================================

SPREADSHEET_ID = "1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0"

# Sheet names for each form type
SHEET_NAMES = {
    'INT': '1099-INT',
    'DIV': '1099-DIV',
    'MISC': '1099-MISC',
    'B': '1099-B'
}

# Row numbers for different data sections (1-indexed to match Google Sheets)
PAYER_NAME_ROW = 6
PAYER_EIN_ROW = 7
PAYER_ADDRESS_ROW = 8
RECIPIENT_NAME_ROW = 11
RECIPIENT_TIN_ROW = 12
RECIPIENT_ADDRESS_ROW = 13
ACCOUNT_NUMBER_ROW = 14
ACCOUNT_NAME_ROW = 15  # Account friendly name derived from filename
DATA_START_ROW = 18  # Box 1 starts at row 18 (row 16 is blank, row 17 is section header)

# Column mapping for data columns (C=3, D=4, E=5, F=6, G=7)
DATA_COLUMNS = ['C', 'D', 'E', 'F', 'G']
COLUMN_INDICES = {col: idx for idx, col in enumerate(DATA_COLUMNS, start=3)}

# Default payer information
FIDELITY_PAYER = {
    'name': 'Fidelity Investments',
    'ein': '77-0196742',
    'address': '100 Salem Street, Smithfield, RI 02917'
}

# Default recipient address (if not in CSV)
DEFAULT_RECIPIENT_ADDRESS = "210 SCOTNEY GLEN CIR, ALPHARETTA, GA 30022"


# ============================================================================
# CSV COLUMN MAPPINGS - Maps CSV columns to spreadsheet box numbers
# ============================================================================

# Maps CSV column names to (row_offset, box_number)
# row_offset is relative to DATA_START_ROW

INT_BOX_MAP = {
    '1099-INT-1 Interest Income': (0, '1'),
    '1099-INT-2 Early Withdrawal Penalty': (1, '2'),
    '1099-INT-3 Interest on U.S. Savings Bonds and Treas. Obligations': (2, '3'),
    '1099-INT-4 Federal Income Tax Withheld': (3, '4'),
    '1099-INT-5 Investment Expenses': (4, '5'),
    '1099-INT-6 Foreign Tax Paid': (5, '6'),
    '1099-INT-7 Foreign Country or U.S. Possession': (6, '7'),
    '1099-INT-8 Tax-Exempt Interest': (7, '8'),
    '1099-INT-9 Specified Private Activity Bond Interest': (8, '9'),
    '1099-INT-10 Market Discount': (9, '10'),
    '1099-INT-11 Bond Premium': (10, '11'),
    '1099-INT-12 Bond premium on U.S. Treasury Obligations': (11, '12'),
    '1099-INT-13 Bond Premium on Tax-Exempt Bond': (12, '13'),
    '1099-INT-14 Tax-Exempt Bond CUSIP No.': (13, '14'),
    '1099-INT-15 State': (16, '15'),
    '1099-INT-16 State Identification No.': (17, '16'),
    '1099-INT-17 State Tax Withheld': (18, '17'),
}

DIV_BOX_MAP = {
    '1099-DIV-1A Total Ordinary Dividends': (0, '1a'),
    '1099-DIV-1B Qualified Dividends': (1, '1b'),
    '1099-DIV-2A Total Capital Gain Distributions': (2, '2a'),
    '1099-DIV-2B Unrecap. Sec 1250 Gain': (3, '2b'),
    '1099-DIV-2C Section 1202 Gain': (4, '2c'),
    '1099-DIV-2D Collectibles (28%) Gain': (5, '2d'),
    '1099-DIV-2E SECTION 897 ORDINARY DIVIDENDS': (6, '2e'),
    '1099-DIV-2F SECTION 897 CAPITAL GAIN': (7, '2f'),
    '1099-DIV-3 Nondividend Distributions': (8, '3'),
    '1099-DIV-4 Federal Income Tax Withheld': (9, '4'),
    '1099-DIV-5 Section 199A Dividends': (10, '5'),
    '1099-DIV-6 Investment Expenses': (11, '6'),
    '1099-DIV-7 Foreign Tax Paid': (12, '7'),
    '1099-DIV-8 Foreign Country or U.S. Possession': (13, '8'),
    '1099-DIV-9 Cash Liquidation Distributions': (14, '9'),
    '1099-DIV-10 Non-Cash Liquidation Distributions': (15, '10'),
    '1099-DIV-12 Exempt Interest Dividends': (17, '12'),
    '1099-DIV-13 Specified Private Activity Bond Interest Dividends': (18, '13'),
    '1099-DIV-14 State': (21, '14'),
    '1099-DIV-15 State Identification No.': (22, '15'),
    '1099-DIV-16 State Tax Withheld': (23, '16'),
}

MISC_BOX_MAP = {
    '1099-MISC-2 Royalties': (1, '2'),
    '1099-MISC-3 Other Income': (2, '3'),
    '1099-MISC-4 Federal Income Tax Withheld': (3, '4'),
    '1099-MISC-8 Substitute Payments In Lieu of Dividends and Interest': (7, '8'),
    '1099-MISC-16 State Tax Withheld': (16, '16'),
    "1099-MISC-17 State/Payer's State No.": (17, '17'),
    '1099-MISC-18 State Income': (18, '18'),
}

B_BOX_MAP = {
    '1099-B-Total Proceeds': (36, 'total_proceeds'),  # Row 56 (offset 36: 20+36=56)
    '1099-B-Total Cost Basis': (37, 'total_cost'),     # Row 57
    '1099-B-Total Market Discount': (38, 'total_market'), # Row 58
    '1099-B-Total Wash Sales': (39, 'total_wash'),     # Row 59
    '1099-B-Realized Gain/Loss': (40, 'total_gain'),   # Row 60
    '1099-B-Federal Income Tax Withheld': (41, 'total_tax'), # Row 61
}

# 1099-B breakdown by category (each category starts at these offsets from row 20)
B_CATEGORY_OFFSETS = {
    'SHORT TERM_COVERED': 0,      # Row 20-25 (offset 0-5)
    'SHORT TERM_NONCOVERED': 7,   # Row 27-32 (offset 7-12)
    'LONG TERM_COVERED': 14,      # Row 34-39 (offset 14-19)
    'LONG TERM_NONCOVERED': 21,   # Row 41-46 (offset 21-26)
    'UNKNOWN': 28,                # Row 48-53 (offset 28-33)
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_account_name_from_filename(csv_path: str) -> str:
    """
    Extract friendly account name from CSV filename.

    Pattern: 2024_1099_Joint-Brokerage-7872.csv → Joint-Brokerage

    Args:
        csv_path: Full path to CSV file

    Returns:
        Account name string, or empty string if pattern doesn't match
    """
    import os
    import re

    filename = os.path.basename(csv_path)

    # Pattern: YYYY_1099_<account-name>-<digits>.csv
    # Extract account-name without trailing digits
    match = re.search(r'\d{4}_1099_(.+?)-?\d+\.csv$', filename)
    if match:
        return match.group(1)

    return ""


def clean_csv_value(value) -> float:
    """
    Clean and convert CSV numeric values to float.
    Fidelity CSVs have leading zeros and sometimes formulas like ="Z12345"
    
    Args:
        value: Raw value from CSV
        
    Returns:
        float: Cleaned numeric value, or 0.0 if cannot convert
    """
    if pd.isna(value):
        return 0.0
    
    # Handle string values with formulas like ="Z12345"
    if isinstance(value, str):
        # Remove formula markers
        value = value.replace('="', '').replace('"', '').strip()
        
        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            # If it's text (like CUSIP), return as-is
            return value
    
    return float(value)


def extract_summary_row(df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Extract the '1099 Summary' row from Fidelity CSV.
    This row contains all the aggregated 1099 data.
    
    Args:
        df: DataFrame loaded from Fidelity CSV
        
    Returns:
        Series containing the summary row, or None if not found
    """
    # Find row where first column equals "1099 Summary"
    summary_mask = df.iloc[:, 0].str.strip() == "1099 Summary"
    summary_rows = df[summary_mask]
    
    if summary_rows.empty:
        print("ERROR: No '1099 Summary' row found in CSV")
        return None
    
    if len(summary_rows) > 1:
        print("WARNING: Multiple summary rows found, using first one")
    
    return summary_rows.iloc[0]


def extract_account_info(row: pd.Series) -> Dict[str, str]:
    """
    Extract account information from summary row.
    
    Args:
        row: Summary row from CSV
        
    Returns:
        Dict with account, customer_name, and ssn_tin
    """
    return {
        'account': clean_csv_value(row.iloc[1]),  # Column 2: Account
        'customer_name': clean_csv_value(row.iloc[2]),  # Column 3: Customer Name
        'ssn_tin': clean_csv_value(row.iloc[3])  # Column 4: SSN/TIN
    }


def extract_b_breakdown(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Extract 1099-B breakdown by reporting category from CSV.

    Args:
        df: Full DataFrame from CSV

    Returns:
        Dict with structure: {
            'SHORT TERM_COVERED': {proceeds: X, cost: Y, ...},
            'LONG TERM_COVERED': {...},
            ...
        }
    """
    breakdown = {}

    # Find all section total rows
    section_rows = df[df.iloc[:, 0].str.strip() == '1099-B-Total-by-section']

    for idx, row in section_rows.iterrows():
        term = str(row.iloc[21]).strip().upper()  # Column 21 is Term
        coverage = str(row.iloc[22]).strip().upper()  # Column 22 is Covered/Noncovered

        if not term or term in ['TERM', 'NAN']:
            continue

        # Create category key
        category_key = f"{term}_{coverage}"

        # Extract values (convert from string with leading zeros)
        proceeds = clean_csv_value(row.iloc[13])
        cost = clean_csv_value(row.iloc[14])
        market_disc = clean_csv_value(row.iloc[15])
        wash_sales = clean_csv_value(row.iloc[16])
        gain = clean_csv_value(row.iloc[17])
        loss = clean_csv_value(row.iloc[18])
        fed_tax = clean_csv_value(row.iloc[19])

        # Calculate realized gain/loss
        realized = gain + loss  # loss is negative

        breakdown[category_key] = {
            'proceeds': proceeds,
            'cost': cost,
            'market_disc': market_disc,
            'wash_sales': wash_sales,
            'realized': realized,
            'fed_tax': fed_tax
        }

    return breakdown


def extract_form_data(row: pd.Series, form_type: str) -> Dict[str, any]:
    """
    Extract all box values for a specific form type from the summary row.

    Args:
        row: Summary row from CSV
        form_type: One of 'INT', 'DIV', 'MISC', 'B'

    Returns:
        Dict mapping box numbers to values, or None for truly missing columns
    """
    # Select the appropriate box mapping
    box_maps = {
        'INT': INT_BOX_MAP,
        'DIV': DIV_BOX_MAP,
        'MISC': MISC_BOX_MAP,
        'B': B_BOX_MAP
    }

    box_map = box_maps.get(form_type)
    if not box_map:
        raise ValueError(f"Unknown form type: {form_type}")

    form_data = {}

    # Iterate through all columns in the row
    for col_name, (row_offset, box_num) in box_map.items():
        if col_name in row.index:
            value = clean_csv_value(row[col_name])
            form_data[box_num] = value
        else:
            # Column not found - mark as None so we can handle it specially
            form_data[box_num] = None

    return form_data


def format_for_sheet(form_data: Dict, form_type: str, b_breakdown: Dict = None) -> List[List]:
    """
    Format extracted form data into rows for Google Sheets import.
    Creates the complete column of data from row 6 to end.

    Args:
        form_data: Dict of box_number -> value
        form_type: One of 'INT', 'DIV', 'MISC', 'B'
        b_breakdown: For 1099-B only, the breakdown by category

    Returns:
        List of lists, each inner list is a single cell value
    """
    # Get the box map to determine row ordering
    box_maps = {
        'INT': INT_BOX_MAP,
        'DIV': DIV_BOX_MAP,
        'MISC': MISC_BOX_MAP,
        'B': B_BOX_MAP
    }

    box_map = box_maps[form_type]

    # Calculate how many rows we need (max row offset + some buffer)
    max_row_offset = max(offset for offset, _ in box_map.values())
    num_rows = max_row_offset + 5  # Add buffer for state info

    # Initialize with empty strings (we'll fill in "-" only for actual data boxes)
    column_data = [[""]] * num_rows

    # Special handling for 1099-B with breakdown
    if form_type == 'B' and b_breakdown:
        # Fill in breakdown by category (rows 18-51)
        for category_key, offset in B_CATEGORY_OFFSETS.items():
            if category_key in b_breakdown:
                data = b_breakdown[category_key]
                column_data[offset] = [data['proceeds']]      # Proceeds
                column_data[offset + 1] = [data['cost']]      # Cost Basis
                column_data[offset + 2] = [data['market_disc']] # Market Discount
                column_data[offset + 3] = [data['wash_sales']] # Wash Sales
                column_data[offset + 4] = [data['realized']]  # Realized Gain/Loss
                column_data[offset + 5] = [data['fed_tax']]   # Fed Tax Withheld
            else:
                # Category not in breakdown, write "-" for the 6 metric rows
                column_data[offset] = ["-"]
                column_data[offset + 1] = ["-"]
                column_data[offset + 2] = ["-"]
                column_data[offset + 3] = ["-"]
                column_data[offset + 4] = ["-"]
                column_data[offset + 5] = ["-"]

    # Define checkbox/special fields that should be empty (not "-") when missing
    # These are non-numeric fields like checkboxes, country codes, CUSIPs
    EMPTY_FIELDS = {
        '7', '8', '11', '14',  # INT/DIV: Foreign country, CUSIP, FATCA checkbox
        '2e', '2f',  # DIV: Section 897 fields (may have text)
    }

    # Fill in the box values at their appropriate offsets
    for box_num, value in form_data.items():
        # Find the row offset for this box
        matching_items = [(offset, bn) for csv_col, (offset, bn) in box_map.items() if bn == box_num]
        if matching_items:
            row_offset, _ = matching_items[0]

            if value is None:
                # Column missing from CSV
                if box_num in EMPTY_FIELDS:
                    column_data[row_offset] = [""]  # Checkboxes/special fields: truly empty
                else:
                    column_data[row_offset] = ["-"]  # Numeric fields: show "-" for missing
            else:
                # Value exists in CSV (could be 0, text, or number)
                column_data[row_offset] = [value]

    return column_data


# ============================================================================
# GOOGLE SHEETS INTERACTION
# ============================================================================

def check_account_exists(account_number: str, form_type: str) -> Optional[str]:
    """
    Check if an account number already exists in the spreadsheet.

    Args:
        account_number: Account number to check
        form_type: Form type ('INT', 'DIV', 'MISC', 'B')

    Returns:
        Column letter (C-G) if found, None if not found
    """
    from googleapiclient.discovery import build
    from google.auth import default

    print(f"  Checking for account {account_number} in {form_type}...")

    try:
        creds, _ = default()
        service = build('sheets', 'v4', credentials=creds)

        sheet_name = SHEET_NAMES[form_type]
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!C{ACCOUNT_NUMBER_ROW}:G{ACCOUNT_NUMBER_ROW}"
        ).execute()

        values = result.get('values', [])
        if values and values[0]:
            for i, account in enumerate(values[0]):
                if account and str(account).strip() == str(account_number).strip():
                    col_letter = chr(67 + i)  # C=67, D=68, etc.
                    print(f"  → Found in column {col_letter}")
                    return col_letter

        return None

    except Exception as e:
        print(f"  ERROR checking for account: {e}")
        return None


def find_next_column(form_type: str) -> Optional[str]:
    """
    Find the next available column (C-G) for a form type.

    Args:
        form_type: Form type ('INT', 'DIV', 'MISC', 'B')

    Returns:
        Next available column letter (C-G), or None if all full
    """
    from googleapiclient.discovery import build
    from google.auth import default

    print(f"  Finding next available column in {form_type}...")

    try:
        creds, _ = default()
        service = build('sheets', 'v4', credentials=creds)

        sheet_name = SHEET_NAMES[form_type]
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!C{ACCOUNT_NUMBER_ROW}:G{ACCOUNT_NUMBER_ROW}"
        ).execute()

        values = result.get('values', [])
        accounts = values[0] if values else []

        # Find first empty column
        for i in range(5):  # C through G (5 columns)
            col_letter = chr(67 + i)  # C=67, D=68, etc.
            if i >= len(accounts) or not accounts[i] or not str(accounts[i]).strip():
                print(f"  → Next available: {col_letter}")
                return col_letter

        print(f"  → All columns full (C-G)")
        return None

    except Exception as e:
        print(f"  ERROR finding next column: {e}")
        return None


def write_to_sheet(form_type: str, column: str, account_info: Dict,
                   form_data: Dict, payer_info: Dict = None, b_breakdown: Dict = None,
                   account_name: str = "") -> bool:
    """
    Write 1099 data to Google Sheet (values only, preserves formatting).

    Args:
        form_type: Form type ('INT', 'DIV', 'MISC', 'B')
        column: Target column (C-G)
        account_info: Dict with account, customer_name, ssn_tin
        form_data: Dict of box_number -> value
        payer_info: Optional payer info, defaults to Fidelity
        b_breakdown: For 1099-B only, breakdown by category
        account_name: Friendly account name derived from filename

    Returns:
        True if successful, False otherwise
    """
    if payer_info is None:
        payer_info = FIDELITY_PAYER

    sheet_name = SHEET_NAMES[form_type]

    # Build the complete column data
    # Rows 6-8: Payer info
    payer_data = [
        [payer_info['name']],           # Row 6
        [payer_info['ein']],             # Row 7
        [payer_info['address']],         # Row 8
        [""],                            # Row 9: empty
        [""],                            # Row 10: empty
        # Rows 11-15: Recipient info
        [account_info['customer_name']], # Row 11
        [account_info['ssn_tin']],       # Row 12
        [DEFAULT_RECIPIENT_ADDRESS],     # Row 13
        [account_info['account']],       # Row 14
        [account_name],                  # Row 15: Account Name (derived from filename)
        [""],                            # Row 16: blank row
        [""],                            # Row 17: section header (leave empty)
    ]

    # 1099-B has an extra blank row (row 18) before data starts at row 19
    if form_type == 'B':
        payer_data.append([""])          # Row 18: blank row (1099-B only)

    # Rows 18+ (or 19+ for 1099-B): Form data
    form_values = format_for_sheet(form_data, form_type, b_breakdown)

    # Combine all data
    all_data = payer_data + form_values
    
    # Calculate the range (starting at row 6, column specified)
    start_cell = f"{column}{PAYER_NAME_ROW}"
    
    print(f"  Writing to {sheet_name}!{start_cell}")
    print(f"  Total rows to write: {len(all_data)}")

    try:
        from googleapiclient.discovery import build
        from google.auth import default

        creds, _ = default()
        service = build('sheets', 'v4', credentials=creds)

        body = {
            'values': all_data
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!{start_cell}",
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        updated_cells = result.get('updatedCells', 0)
        print(f"  → Updated {updated_cells} cells")
        return True

    except Exception as e:
        print(f"  ERROR writing to sheet: {e}")
        return False


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_global_duplicate(account_number: str) -> Dict[str, str]:
    """
    Check if account number exists in ANY of the four tabs.

    Args:
        account_number: Account number to check

    Returns:
        Dict mapping form_type -> column_letter for tabs where account exists
    """
    from googleapiclient.discovery import build
    from google.auth import default

    print(f"\n🔍 Checking for account {account_number} across all tabs...")

    duplicates = {}
    form_types = ['INT', 'DIV', 'MISC', 'B']

    try:
        creds, _ = default()
        service = build('sheets', 'v4', credentials=creds)

        for form_type in form_types:
            sheet_name = SHEET_NAMES[form_type]
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!C{ACCOUNT_NUMBER_ROW}:G{ACCOUNT_NUMBER_ROW}"
            ).execute()

            values = result.get('values', [])
            if values and values[0]:
                for i, account in enumerate(values[0]):
                    if account and str(account).strip() == str(account_number).strip():
                        col_letter = chr(67 + i)
                        duplicates[form_type] = col_letter
                        print(f"   Found in 1099-{form_type} column {col_letter}")

        if not duplicates:
            print(f"   ✓ Account not found in any tab (safe to import)")

        return duplicates

    except Exception as e:
        print(f"   ERROR during global duplicate check: {e}")
        return {}


def check_column_consistency(column: str) -> Dict[str, bool]:
    """
    Check if a column is empty across all four tabs.

    Args:
        column: Column letter (C-G) to check

    Returns:
        Dict mapping form_type -> True if column has data, False if empty
    """
    from googleapiclient.discovery import build
    from google.auth import default

    print(f"\n🔍 Checking column {column} consistency across all tabs...")

    column_status = {}
    form_types = ['INT', 'DIV', 'MISC', 'B']

    try:
        creds, _ = default()
        service = build('sheets', 'v4', credentials=creds)

        for form_type in form_types:
            sheet_name = SHEET_NAMES[form_type]
            # Check if account number row in this column has data
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!{column}{ACCOUNT_NUMBER_ROW}"
            ).execute()

            values = result.get('values', [])
            has_data = bool(values and values[0] and str(values[0][0]).strip())
            column_status[form_type] = has_data

            status = "HAS DATA" if has_data else "empty"
            print(f"   1099-{form_type}: {status}")

        return column_status

    except Exception as e:
        print(f"   ERROR during column consistency check: {e}")
        return {}


# ============================================================================
# MAIN PROCESSING FUNCTIONS
# ============================================================================

def process_csv(csv_path: str, check_duplicates: bool = True,
                dry_run: bool = False) -> bool:
    """
    Main function to process a Fidelity 1099 CSV file.
    
    Args:
        csv_path: Path to CSV file
        check_duplicates: Whether to check for existing accounts
        dry_run: If True, show what would be done without actually doing it
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Processing: {csv_path}")
    print(f"{'='*70}\n")
    
    # Read CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded CSV with {len(df)} rows")
    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        return False
    
    # Extract summary row
    summary_row = extract_summary_row(df)
    if summary_row is None:
        return False
    
    # Extract account info
    account_info = extract_account_info(summary_row)
    account_name = extract_account_name_from_filename(csv_path)
    print(f"\n📋 Account Information:")
    print(f"   Account: {account_info['account']}")
    print(f"   Account Name: {account_name}")
    print(f"   Customer: {account_info['customer_name']}")
    print(f"   SSN/TIN: {account_info['ssn_tin']}")

    # SAFETY CHECK 1: Global duplicate check across all tabs
    duplicates = {}
    if check_duplicates:
        duplicates = check_global_duplicate(account_info['account'])
        if duplicates:
            print(f"\n⚠️  WARNING: Account {account_info['account']} already imported!")
            print(f"   Found in: {', '.join([f'1099-{k} col {v}' for k, v in duplicates.items()])}")
            if not dry_run:
                response = input(f"\n   Overwrite existing data? (y/n): ")
                if response.lower() != 'y':
                    print(f"\n   Aborting import.")
                    return False
                print(f"\n   Proceeding with overwrite...")

    # Extract all form data first (before any writes)
    form_types = ['INT', 'DIV', 'MISC', 'B']
    all_form_data = {}

    print(f"\n{'='*70}")
    print(f"EXTRACTING DATA FROM CSV")
    print(f"{'='*70}")

    # Also extract 1099-B breakdown if present
    b_breakdown = None
    if 'B' in form_types:
        b_breakdown = extract_b_breakdown(df)
        if b_breakdown:
            print(f"\n1099-B Breakdown:")
            for category_key, data in b_breakdown.items():
                print(f"  {category_key}: ${data['proceeds']:,.2f} proceeds")

    for form_type in form_types:
        print(f"\n1099-{form_type}:")
        form_data = extract_form_data(summary_row, form_type)
        non_zero = [v for v in form_data.values() if isinstance(v, (int, float)) and v != 0]
        print(f"  ✓ Extracted {len(form_data)} boxes ({len(non_zero)} non-zero)")
        all_form_data[form_type] = form_data

    # Determine target column (must be same for all tabs)
    target_column = None
    if check_duplicates and duplicates:
        # Use existing column if overwriting
        target_column = list(duplicates.values())[0]  # Should be same for all
        print(f"\n→ Will overwrite existing column: {target_column}")
    else:
        # Find next available column (check first tab, verify others match)
        target_column = find_next_column('INT')
        if target_column is None:
            print(f"\n✗ ERROR: No available columns")
            return False
        print(f"\n→ Target column for import: {target_column}")

    # SAFETY CHECK 2: Verify column consistency across all tabs
    column_status = check_column_consistency(target_column)

    # All tabs should have same status (all empty or all with data)
    has_data_count = sum(column_status.values())
    if has_data_count > 0 and has_data_count < 4:
        print(f"\n⚠️  CRITICAL ERROR: Column {target_column} is INCONSISTENT!")
        print(f"   {has_data_count} tabs have data, {4 - has_data_count} are empty")
        print(f"\n   This violates the all-or-nothing rule.")
        print(f"   Please manually review and fix the spreadsheet before importing.")
        return False

    # Process each form type (all-or-nothing)
    print(f"\n{'='*70}")
    print(f"IMPORTING TO COLUMN {target_column}")
    print(f"{'='*70}")

    results = {}

    for form_type in form_types:
        print(f"\n1099-{form_type}:")
        form_data = all_form_data[form_type]

        # Write to sheet (or show what would be written)
        if dry_run:
            non_zero = [v for v in form_data.values() if isinstance(v, (int, float)) and v != 0]
            print(f"  → Would write {len(non_zero)} non-zero values to column {target_column}")
            if form_data:
                first_val = list(form_data.values())[0]
                print(f"     Sample: {first_val}")
            results[form_type] = 'dry_run'
        else:
            # Pass b_breakdown for 1099-B only
            breakdown_param = b_breakdown if form_type == 'B' else None
            success = write_to_sheet(form_type, target_column, account_info, form_data,
                                    b_breakdown=breakdown_param, account_name=account_name)
            if success:
                results[form_type] = 'success'
            else:
                print(f"  ✗ Failed to write data")
                results[form_type] = 'failed'
                # If any write fails, abort (all-or-nothing)
                print(f"\n✗ IMPORT FAILED - aborting to maintain consistency")
                return False

    # Print summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    for form_type, result in results.items():
        status_icon = {
            'success': '✓',
            'skipped': '⊘',
            'failed': '✗',
            'dry_run': '→'
        }.get(result, '?')
        print(f"  {status_icon} 1099-{form_type}: {result}")

    print(f"\n")
    return all(r in ['success', 'skipped', 'dry_run'] for r in results.values())


def main():
    """
    Main entry point for command-line execution.
    """
    parser = argparse.ArgumentParser(
        description='Import Fidelity 1099 data from CSV to Google Sheets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be imported
  python3 import_1099.py --csv file.csv --dry-run

  # Import without checking for duplicates
  python3 import_1099.py --csv file.csv --no-check-duplicates

  # Import with duplicate checking (default)
  python3 import_1099.py --csv file.csv
        """
    )

    parser.add_argument('--csv', required=True,
                        help='Path to Fidelity 1099 CSV file')
    parser.add_argument('--check-duplicates', dest='check_duplicates',
                        action='store_true', default=True,
                        help='Check for existing accounts before import (default)')
    parser.add_argument('--no-check-duplicates', dest='check_duplicates',
                        action='store_false',
                        help='Skip duplicate checking')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be imported without actually importing')
    parser.add_argument('--account', type=str,
                        help='Specific account number to import (if CSV has multiple)')

    args = parser.parse_args()

    # Validate CSV file exists
    import os
    if not os.path.exists(args.csv):
        print(f"ERROR: CSV file not found: {args.csv}")
        sys.exit(1)

    # Process the CSV
    success = process_csv(
        csv_path=args.csv,
        check_duplicates=args.check_duplicates,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
