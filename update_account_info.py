#!/usr/bin/env python3
"""
Update Account Information in JSON Files

Created: 09/23/25 4:26PM
Purpose: Updates all JSON extraction files with correct account information from account-mappings.json

This script ensures consistency across all extracted JSON files by:
- Applying correct account_holder_name from mappings
- Adding missing account_type field where needed
- Ensuring account names and numbers are consistent
"""

import json
import glob
from pathlib import Path

def load_account_mappings(mapping_file):
    """Load the account mappings configuration"""
    with open(mapping_file, 'r') as f:
        return json.load(f)

def get_account_info(account_number, mappings):
    """Get account information from mappings based on account number"""
    # Extract last 4 digits from account number (e.g., Z24-527872 -> 7872)
    last_4 = account_number.split('-')[-1][-4:] if '-' in account_number else account_number[-4:]

    # Look up in mappings
    fidelity_accounts = mappings['accounts']['fidelity']

    for key, info in fidelity_accounts.items():
        if key == last_4:
            # Get the corresponding entity information
            entity_key = info['entity_key']
            entity_info = mappings['entities'][entity_key]

            # Return account info with proper entity name from mappings
            result = info.copy()
            result['entity_name'] = entity_info['entity_name']  # Use canonical entity name
            return result

    return None

def update_json_file(file_path, mappings):
    """Update a single JSON file with correct account information"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    modified = False

    # Update each account in the file
    if 'accounts' in data:
        for account in data['accounts']:
            account_number = account.get('account_number')
            if not account_number:
                continue

            # Get correct info from mappings
            correct_info = get_account_info(account_number, mappings)

            if correct_info:
                # Update account information
                old_holder = account.get('account_holder_name')
                old_name = account.get('account_name')
                old_type = account.get('account_type')

                # Apply updates using canonical entity name from mappings
                account['account_holder_name'] = correct_info['entity_name']  # Use canonical entity name
                account['account_name'] = correct_info['account_name']

                # Add account_type if missing or incorrect
                if 'account_type' not in account or account['account_type'] != correct_info['account_type']:
                    account['account_type'] = correct_info['account_type']
                    modified = True

                # Check if we made changes
                if (old_holder != account['account_holder_name'] or
                    old_name != account['account_name'] or
                    old_type != account.get('account_type')):
                    modified = True
                    print(f"  Updated {account_number}:")
                    if old_holder != account['account_holder_name']:
                        print(f"    account_holder_name: {old_holder} -> {account['account_holder_name']}")
                    if old_name != account['account_name']:
                        print(f"    account_name: {old_name[:50]}... -> {account['account_name']}")
                    if old_type != account.get('account_type'):
                        print(f"    account_type: {old_type} -> {account['account_type']}")

    # Save if modified
    if modified:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  ✅ Saved updates to {file_path}")
    else:
        print(f"  ✓ No changes needed for {file_path}")

    return modified

def main():
    """Main function to update all JSON files"""
    # Load account mappings
    mappings_file = Path('/Users/richkernan/Projects/Finances/config/account-mappings.json')
    mappings = load_account_mappings(mappings_file)

    print("Loading account mappings...")
    print(f"Found {len(mappings['accounts']['fidelity'])} Fidelity accounts in mappings")
    print()

    # Find all JSON files to update
    directories = [
        '/Users/richkernan/Projects/Finances/documents/4extractions',
        '/Users/richkernan/Projects/Finances/documents/5loaded'
    ]

    total_files = 0
    modified_files = 0

    for directory in directories:
        print(f"Processing directory: {directory}")
        json_files = sorted(glob.glob(f"{directory}/*.json"))

        for json_file in json_files:
            print(f"\nProcessing: {Path(json_file).name}")
            total_files += 1
            if update_json_file(json_file, mappings):
                modified_files += 1

    print("\n" + "="*60)
    print(f"Summary: Updated {modified_files} of {total_files} files")
    print("="*60)

if __name__ == "__main__":
    main()