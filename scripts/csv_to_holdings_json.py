#!/usr/bin/env python3
"""
CSV to Holdings JSON Converter
Created: 09/26/25 - Quick CSV holdings extraction
"""
import csv
import json
import hashlib
from datetime import datetime
from pathlib import Path

def extract_holdings_from_csv(csv_path):
    """Extract holdings data from Fidelity CSV export"""

    # Initialize output structure
    output = {
        "extraction_metadata": {
            "json_output_id": f"csv_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source_csv_filepath": str(csv_path),
            "extraction_type": "holdings",
            "extraction_timestamp": datetime.now().strftime("%Y.%m.%d_%H.%M") + "ET",
            "extractor_version": "csv_1.0"
        },
        "accounts": []
    }

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)

    # Parse account summary (first 2 lines)
    headers = lines[0]
    account_data = {}

    for row in lines[1:3]:
        if len(row) > 2:
            account_type = row[0]  # "Joint CMA" or "Joint Brokerage"
            account_num = row[1]    # Account number
            if account_num:
                account_data[account_num] = {
                    "account_number": account_num,
                    "account_name": account_type,
                    "portfolio_summary": {
                        "beginning_value": row[2] if len(row) > 2 else None,
                        "ending_value": row[4] if len(row) > 4 else None,
                        "dividends_period": row[7] if len(row) > 7 else None,
                        "dividends_ytd": row[8] if len(row) > 8 else None,
                        "interest_period": row[9] if len(row) > 9 else None,
                        "interest_ytd": row[10] if len(row) > 10 else None
                    },
                    "positions": []
                }

    # Parse positions (starting after headers)
    current_account = None
    current_section = None

    for i, row in enumerate(lines[5:], 5):
        if not row or not row[0]:
            continue

        # Check for account number line
        if len(row[0]) > 5 and row[0][0] == 'Z' and not row[1]:
            current_account = row[0].strip()
            continue

        # Check for section headers
        if row[0] in ['Stocks', 'Bonds', 'Mutual Funds', 'Options', 'Other', 'Core Account']:
            current_section = row[0]
            continue

        # Skip subtotal lines
        if row[0].startswith('Subtotal'):
            continue

        # Parse position data
        if current_account and len(row) >= 7:
            symbol = row[0]
            if symbol and not symbol.startswith('Account'):
                position = {
                    "symbol": symbol if symbol != ',' else None,
                    "description": row[1],
                    "security_type": current_section.lower().replace(' ', '_') if current_section else 'unknown',
                    "quantity": row[2],
                    "price": row[3],
                    "beginning_value": row[4],
                    "ending_value": row[5],
                    "cost_basis": row[6] if len(row) > 6 and row[6] != 'not applicable' else None
                }

                if current_account in account_data:
                    account_data[current_account]["positions"].append(position)

    # Add accounts to output
    output["accounts"] = list(account_data.values())

    # Calculate MD5 hash of JSON content
    json_str = json.dumps(output, indent=2)
    output["extraction_metadata"]["json_output_md5_hash"] = hashlib.md5(json_str.encode()).hexdigest()

    return output

# Example usage
if __name__ == "__main__":
    csv_file = Path("/Users/richkernan/Projects/Finances/documents/1inbox/Statement8312025.csv")
    holdings = extract_holdings_from_csv(csv_file)

    # Save to extractions folder
    output_file = Path("/Users/richkernan/Projects/Finances/documents/4extractions") / \
                  f"csv_holdings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(holdings, f, indent=2)

    print(f"✅ Extracted {sum(len(acc['positions']) for acc in holdings['accounts'])} positions")
    print(f"📄 Saved to: {output_file}")