#!/usr/bin/env python3
"""
CSV to Holdings JSON Converter for Fidelity Statements
Created: 09/26/25 - Hybrid CSV+LLM extraction workflow
Updated: 09/26/25 2:20PM - Complete implementation based on CSV_Mapping_Fid_Positions.md
Updated: 09/26/25 2:37PM - Fixed account mapping lookup and holdings parsing logic
Updated: 09/26/25 4:16PM - Added TODO index generation for efficient LLM augmentation

Purpose: Extract ~75% of holdings data from Fidelity CSV exports to create
         base JSON structure for LLM augmentation with PDF-only fields.
         Also generates a TODO index file listing all null fields that need
         PDF extraction, reducing LLM processing from 2000+ lines to ~100.
"""

import csv
import json
import hashlib
import sys
import re
from datetime import datetime
from pathlib import Path


def load_account_mappings():
    """Load account mappings for label generation"""
    mapping_file = Path("/Users/richkernan/Projects/Finances/config/account-mappings.json")
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            return json.load(f)
    return {}


def get_account_label(account_num, mappings):
    """Get mapped account label or last 4 digits"""
    if not isinstance(mappings, dict):
        return account_num[-4:] if len(account_num) > 4 else account_num

    # Navigate the nested structure: accounts -> fidelity -> {last4digits} -> metadata
    fidelity_accounts = mappings.get("accounts", {}).get("fidelity", {})

    # Extract last 4 digits from account number for lookup
    # Z27-375656 -> 5656, Z24-527872 -> 7872
    if len(account_num) >= 4:
        last_4 = account_num[-4:]  # Get last 4 characters
        if last_4 in fidelity_accounts:
            return fidelity_accounts[last_4].get("filename_label", last_4)

    # Fallback to last 4 digits
    return account_num[-4:] if len(account_num) > 4 else account_num


def parse_security_type(section_name):
    """Map CSV section headers to standard security types"""
    type_map = {
        "Stocks": "Stocks",
        "Bonds": "Bonds",
        "Mutual Funds": "Mutual Funds",
        "Options": "Options",
        "Core Account": "Core Account",
        "Other": "Other",
        "Exchange Traded Products": "Exchange Traded Products"
    }
    return type_map.get(section_name, "Other")


def parse_options_description(description):
    """Extract options details from description if applicable"""
    # Example: "CALL (AAPL) APPLE INC JAN 17 25 $180"
    options_data = {}

    # Check if it's an option
    if "CALL" in description or "PUT" in description:
        # Extract underlying symbol from parentheses
        symbol_match = re.search(r'\(([A-Z]+)\)', description)
        if symbol_match:
            options_data["underlying_symbol"] = symbol_match.group(1)

        # Extract strike price (preceded by $)
        strike_match = re.search(r'\$(\d+(?:\.\d+)?)', description)
        if strike_match:
            options_data["strike_price"] = f"{float(strike_match.group(1)):.2f}"

        # Extract expiration date (simplified - would need more logic for full parsing)
        # This is where LLM augmentation will provide accurate dates

    return options_data


def clean_currency(value):
    """Clean currency values for JSON"""
    if not value or value == "" or value == "not applicable":
        return None
    # Remove commas and convert to string with 2 decimals
    try:
        cleaned = value.replace(',', '')
        return f"{float(cleaned):.2f}"
    except:
        return None


def clean_quantity(value):
    """Clean quantity values for JSON"""
    if not value or value == "":
        return None
    try:
        # Preserve up to 6 decimal places as per spec
        return f"{float(value):.6f}".rstrip('0').rstrip('.')
    except:
        return None


def generate_todo_index(json_data, output_path):
    """Generate TODO index file listing all null fields that need PDF extraction"""
    todo = {
        "source_json": str(output_path),
        "pdf_required_fields": {
            "document_data": [],
            "accounts": {}
        },
        "summary": {
            "total_null_fields": 0,
            "holdings_with_nulls": 0,
            "bonds_needing_details": 0,
            "options_needing_dates": 0,
            "document_fields": 0,
            "account_summary_fields": 0
        }
    }

    # Check document_data nulls
    for field, value in json_data["document_data"].items():
        if value is None:
            todo["pdf_required_fields"]["document_data"].append(field)
            todo["summary"]["total_null_fields"] += 1
            todo["summary"]["document_fields"] += 1

    # Process each account
    for acc_idx, account in enumerate(json_data["accounts"]):
        account_num = account["account_number"]
        todo["pdf_required_fields"]["accounts"][account_num] = {
            "account_index": acc_idx,
            "net_account_value": [],
            "income_summary": [],
            "realized_gains": [],
            "holdings_needing_pdf": []
        }

        # Check net_account_value nulls
        for field, value in account["net_account_value"].items():
            if value is None:
                todo["pdf_required_fields"]["accounts"][account_num]["net_account_value"].append(field)
                todo["summary"]["total_null_fields"] += 1
                todo["summary"]["account_summary_fields"] += 1

        # Check income_summary nulls
        for field, value in account["income_summary"].items():
            if value is None:
                todo["pdf_required_fields"]["accounts"][account_num]["income_summary"].append(field)
                todo["summary"]["total_null_fields"] += 1
                todo["summary"]["account_summary_fields"] += 1

        # Check realized_gains nulls (all fields are null from CSV)
        for field, value in account["realized_gains"].items():
            if value is None:
                todo["pdf_required_fields"]["accounts"][account_num]["realized_gains"].append(field)
                todo["summary"]["total_null_fields"] += 1
                todo["summary"]["account_summary_fields"] += 1

        # Process holdings
        for hold_idx, holding in enumerate(account["holdings"]):
            fields_needed = []

            # Basic fields that might be null
            basic_fields = ["unrealized_gain_loss", "estimated_ann_inc", "est_yield"]
            for field in basic_fields:
                if holding.get(field) is None:
                    fields_needed.append(field)
                    todo["summary"]["total_null_fields"] += 1

            # Bond-specific fields
            if holding["sec_type"] == "Bonds":
                bond_fields = ["maturity_date", "coupon_rate", "accrued_int",
                              "agency_ratings", "next_call_date", "call_price",
                              "payment_freq", "bond_features"]
                for field in bond_fields:
                    if holding.get(field) is None:
                        fields_needed.append(field)
                        todo["summary"]["total_null_fields"] += 1
                if fields_needed:
                    todo["summary"]["bonds_needing_details"] += 1

            # Options-specific fields
            if holding["sec_type"] == "Options" or "underlying_symbol" in holding:
                if holding.get("expiration_date") is None:
                    fields_needed.append("expiration_date")
                    todo["summary"]["total_null_fields"] += 1
                    todo["summary"]["options_needing_dates"] += 1

            # Add to TODO if any fields need extraction
            if fields_needed:
                todo["pdf_required_fields"]["accounts"][account_num]["holdings_needing_pdf"].append({
                    "index": hold_idx,
                    "symbol_or_cusip": holding.get("sec_symbol") or holding.get("cusip") or "N/A",
                    "description": holding.get("sec_description", "")[:50] + "...",  # Truncate for readability
                    "fields": fields_needed
                })
                todo["summary"]["holdings_with_nulls"] += 1

    return todo


def extract_statement_period(csv_path):
    """Extract statement period from filename or default to current month"""
    # Try to extract from filename like "KernanStatement4302025.csv" -> "2025-04"
    filename = csv_path.stem
    match = re.search(r'(\d{1,2})(\d{2})(\d{4})', filename)
    if match:
        month = match.group(1).zfill(2)
        day = match.group(2)
        year = match.group(3)
        return f"{year}-{month}"
    # Default to current year-month
    return datetime.now().strftime("%Y-%m")


def extract_holdings_from_csv(csv_path, output_dir):
    """Extract holdings data from Fidelity CSV export following CSV_Mapping_Fid_Positions.md"""

    csv_path = Path(csv_path)
    output_dir = Path(output_dir)

    # Load account mappings
    mappings = load_account_mappings()

    # Extract statement period
    statement_period = extract_statement_period(csv_path)

    # Initialize output structure per JSON_Stmnt_Fid_Positions.md
    timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M") + "ET"

    output = {
        "extraction_metadata": {
            "json_output_id": f"fid_stmnt_{statement_period.lower()}_csv_extract",
            "source_pdf_filepath": str(csv_path.with_suffix('.pdf')),  # PDF path for reference
            "source_csv_filepath": str(csv_path),
            "json_output_md5_hash": "",  # Will calculate after JSON creation
            "doc_md5_hash": None,  # Will be added by orchestrator
            "extraction_type": "holdings",
            "extraction_timestamp": timestamp,
            "extractor_version": "csv_1.0",
            "extraction_notes": ["CSV extraction completed - awaiting LLM augmentation for PDF-only fields"]
        },
        "document_data": {
            "institution": "Fidelity",
            "statement_date": None,  # LLM will extract from PDF
            "period_start": None,    # LLM will extract from PDF
            "period_end": None       # LLM will extract from PDF
        },
        "accounts": []
    }

    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        lines = list(reader)

    # Parse account summary section (lines 1-2 typically)
    if len(lines) < 2:
        raise ValueError("CSV file too short - missing account summary")

    headers = lines[0]
    account_summaries = {}
    account_labels = []

    # Process each account summary row
    for row in lines[1:]:
        if len(row) < 2 or not row[1]:  # Need at least account number
            break
        if row[0] == "":  # Empty first column signals end of summaries
            break

        account_type = row[0]
        account_num = row[1].strip()

        if account_num and account_num[0].isalpha():  # Valid account number
            account_label = get_account_label(account_num, mappings)
            account_labels.append(account_label)

            account_data = {
                "account_number": account_num,
                "account_name": account_type,
                "account_holder_name": None,  # LLM will extract from PDF
                "account_type": "brokerage",  # Default - LLM may update

                # Net Account Value section (partial - LLM will complete)
                "net_account_value": {
                    "beg_net_acct_val_period": clean_currency(row[2]) if len(row) > 2 else None,
                    "beg_net_acct_val_ytd": None,  # PDF only
                    "additions_period": None,  # PDF only
                    "additions_ytd": None,  # PDF only
                    "deposits_period": None,  # PDF only
                    "deposits_ytd": None,  # PDF only
                    "exchanges_in_period": None,  # PDF only
                    "exchanges_in_ytd": None,  # PDF only
                    "subtractions_period": None,  # PDF only
                    "subtractions_ytd": None,  # PDF only
                    "withdrawals_period": None,  # PDF only
                    "withdrawals_ytd": None,  # PDF only
                    "exchanges_out_period": None,  # PDF only
                    "exchanges_out_ytd": None,  # PDF only
                    "transaction_costs_period": None,  # PDF only
                    "transaction_costs_ytd": None,  # PDF only
                    "taxes_withheld_period": None,  # PDF only
                    "taxes_withheld_ytd": None,  # PDF only
                    "change_in_inc_val_period": clean_currency(row[3]) if len(row) > 3 else None,
                    "change_in_inc_val_ytd": None,  # PDF only
                    "ending_net_acct_val_period": clean_currency(row[6]) if len(row) > 6 else clean_currency(row[4]) if len(row) > 4 else None,
                    "ending_net_acct_val_ytd": None,  # PDF only
                    "accrued_interest": None,  # PDF only
                    "ending_net_acct_val_incl_ai": None  # PDF only
                },

                # Income Summary section (partial - only taxable from CSV)
                "income_summary": {
                    "taxable_total_period": clean_currency(row[11]) if len(row) > 11 else None,
                    "taxable_total_ytd": clean_currency(row[12]) if len(row) > 12 else None,
                    "divs_taxable_period": clean_currency(row[7]) if len(row) > 7 else None,
                    "divs_taxable_ytd": clean_currency(row[8]) if len(row) > 8 else None,
                    "stcg_taxable_period": None,  # PDF only
                    "stcg_taxable_ytd": None,  # PDF only
                    "int_taxable_period": clean_currency(row[9]) if len(row) > 9 else None,
                    "int_taxable_ytd": clean_currency(row[10]) if len(row) > 10 else None,
                    "ltcg_taxable_period": None,  # PDF only
                    "ltcg_taxable_ytd": None,  # PDF only
                    "tax_exempt_total_period": None,  # PDF only
                    "tax_exempt_total_ytd": None,  # PDF only
                    "divs_tax_exempt_period": None,  # PDF only
                    "divs_tax_exempt_ytd": None,  # PDF only
                    "stcg_tax_ex_period": None,  # PDF only
                    "stcg_tax_ex_ytd": None,  # PDF only
                    "int_tax_exempt_period": None,  # PDF only
                    "int_tax_exempt_ytd": None,  # PDF only
                    "ltcg_tax_ex_period": None,  # PDF only
                    "ltcg_tax_ex_ytd": None,  # PDF only
                    "roc_period": None,  # PDF only
                    "roc_ytd": None,  # PDF only
                    "incsumm_total_period": clean_currency(row[11]) if len(row) > 11 else None,
                    "incsumm_total_ytd": clean_currency(row[12]) if len(row) > 12 else None
                },

                # Realized Gains section (all PDF only)
                "realized_gains": {
                    "netstgl_period": None,
                    "netstgl_ytd": None,
                    "stg_period": None,
                    "stg_ytd": None,
                    "netltgl_period": None,
                    "netltgl_ytd": None,
                    "ltg_period": None,
                    "ltg_ytd": None,
                    "net_gl_period": None,
                    "net_gl_ytd": None
                },

                "holdings": []
            }

            account_summaries[account_num] = account_data

    # Parse holdings detail section
    current_account = None
    current_sec_type = None
    current_sec_subtype = None

    # Find where holdings start - look for "Symbol/CUSIP" header
    holdings_start = -1
    for i, row in enumerate(lines):
        if len(row) > 0 and row[0] == "Symbol/CUSIP":
            holdings_start = i + 1  # Start from next line after header
            break

    if holdings_start == -1:
        print("Warning: Could not find holdings section in CSV")
    else:
        # Process holdings
        for row in lines[holdings_start:]:
            # Skip completely empty rows
            if not row or len(row) == 0:
                continue

            # Get first cell for analysis
            first_cell = row[0].strip() if row[0] else ""

            # Check for account number line (single cell or with empty second cell)
            # Account numbers are like Z27375656, Z24527872, Z40394067
            if first_cell and len(first_cell) >= 8:
                # Check if it looks like an account number
                if first_cell[0] in ['Z', '2', '3'] and any(c.isdigit() for c in first_cell):
                    # Verify it's a standalone account number line (not a CUSIP in holdings)
                    if len(row) == 1 or (len(row) > 1 and not row[1].strip()):
                        current_account = first_cell
                        continue

            # Check for section headers
            section_headers = ["Stocks", "Bonds", "Mutual Funds", "Options", "Core Account",
                             "Other", "Exchange Traded Products"]
            if first_cell in section_headers:
                current_sec_type = parse_security_type(first_cell)
                current_sec_subtype = first_cell
                continue

            # Skip subtotal lines
            if first_cell.startswith("Subtotal"):
                continue

            # Skip separator/empty lines
            if first_cell == "," or first_cell == "":
                continue

            # Parse position data - must have account and enough columns
            if current_account and current_account in account_summaries and len(row) >= 6:
                # Get position data
                symbol_cusip = row[0].strip() if row[0] else None
                description = row[1].strip() if len(row) > 1 and row[1] else None

                # Must have a description to be valid holding
                if not description or description in [",", ""]:
                    continue

                # Determine if symbol or CUSIP
                sec_symbol = None
                cusip = None
                if symbol_cusip and symbol_cusip not in [",", ""]:
                    # CUSIP is typically 9 characters alphanumeric
                    if len(symbol_cusip) == 9 and any(c.isdigit() for c in symbol_cusip):
                        cusip = symbol_cusip
                    else:
                        sec_symbol = symbol_cusip

                # Create holding entry
                holding = {
                    "sec_type": current_sec_type,
                    "sec_subtype": current_sec_subtype,
                    "sec_symbol": sec_symbol,
                    "cusip": cusip,
                    "sec_description": description,
                    "beg_market_value": clean_currency(row[4]) if len(row) > 4 else None,
                    "quantity": clean_quantity(row[2]) if len(row) > 2 else None,
                    "price_per_unit": clean_currency(row[3]) if len(row) > 3 else None,
                    "end_market_value": clean_currency(row[5]) if len(row) > 5 else None,
                    "cost_basis": clean_currency(row[6]) if len(row) > 6 and row[6] != "not applicable" else None,
                    "unrealized_gain_loss": None,  # PDF only
                    "estimated_ann_inc": None,  # PDF only
                    "est_yield": None  # PDF only
                }

                # Add bond-specific fields if applicable
                if current_sec_type == "Bonds":
                    holding.update({
                        "maturity_date": None,  # PDF only
                        "coupon_rate": None,  # PDF only
                        "accrued_int": None,  # PDF only
                        "agency_ratings": None,  # PDF only
                        "next_call_date": None,  # PDF only
                        "call_price": None,  # PDF only
                        "payment_freq": None,  # PDF only
                        "bond_features": None  # PDF only
                    })

                # Add options-specific fields if applicable
                if current_sec_type == "Options" or (description and ("CALL" in description or "PUT" in description)):
                    options_data = parse_options_description(description)
                    holding.update({
                        "underlying_symbol": options_data.get("underlying_symbol"),
                        "strike_price": options_data.get("strike_price"),
                        "expiration_date": None  # LLM will extract accurate date
                    })

                account_summaries[current_account]["holdings"].append(holding)

    # Add accounts to output
    output["accounts"] = list(account_summaries.values())

    # Generate filename
    account_labels_str = "+".join(account_labels) if account_labels else "Unknown"
    output_filename = f"Fid_Stmnt_{statement_period}_{account_labels_str}_holdings_{timestamp}.json"
    output_path = output_dir / output_filename

    # Calculate MD5 hash of JSON content
    json_str = json.dumps(output, indent=2, sort_keys=True)
    output["extraction_metadata"]["json_output_md5_hash"] = hashlib.md5(json_str.encode()).hexdigest()

    # Save JSON file
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Generate TODO index file for LLM augmentation
    todo_output = generate_todo_index(output, output_path)

    # Save TODO file
    todo_path = output_path.with_suffix('.TODO.json')
    with open(todo_path, 'w') as f:
        json.dump(todo_output, f, indent=2)

    # Print summary
    total_accounts = len(output["accounts"])
    total_holdings = sum(len(acc["holdings"]) for acc in output["accounts"])
    total_nulls = todo_output["summary"]["total_null_fields"]

    print(f"✅ CSV Extraction Complete!")
    print(f"📊 Extracted: {total_accounts} accounts, {total_holdings} holdings")
    print(f"📄 Output: {output_path}")
    print(f"📋 TODO: {todo_path} ({total_nulls} fields need PDF extraction)")
    print(f"🔄 Ready for LLM augmentation with PDF-only fields")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_holdings_json.py <csv_file> <output_dir>")
        print("Example: python csv_to_holdings_json.py /path/to/statement.csv /documents/4extractions/")
        sys.exit(1)

    csv_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not csv_file.exists():
        print(f"❌ Error: CSV file not found: {csv_file}")
        sys.exit(1)

    if not output_dir.exists():
        print(f"❌ Error: Output directory not found: {output_dir}")
        sys.exit(1)

    try:
        extract_holdings_from_csv(csv_file, output_dir)
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        sys.exit(1)