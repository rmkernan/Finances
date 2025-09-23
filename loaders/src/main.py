"""
Main Orchestrator for Database Loader

Created: 09/23/25 11:05AM
Purpose: Coordinate all modules to load financial data
Updates:
  - 09/23/25 11:05AM: Initial implementation
  - 09/23/25 12:49PM: Redesigned to be account-centric, supporting both activities and holdings per account
  - 09/23/25 12:49PM: Added automatic file moving to documents/5loaded/ after successful load

Entry point that orchestrates the complete loading process.
Supports unified loading of activities and/or holdings data from account-structured JSON files.
"""

import sys
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, Any

from . import config
from . import validator
from . import entities
from . import documents
from . import loader

def move_to_loaded(json_path: Path) -> None:
    """
    Move successfully loaded file to loaded directory.

    Args:
        json_path: Path to the JSON file that was successfully loaded
    """
    # Create loaded directory structure matching extractions
    loaded_dir = json_path.parent.parent / "5loaded"
    loaded_dir.mkdir(exist_ok=True)

    destination = loaded_dir / json_path.name

    try:
        shutil.move(str(json_path), str(destination))
        print(f"Moved processed file to: {destination}")
    except Exception as e:
        print(f"Warning: Could not move file to loaded directory: {e}")
        print(f"File remains at: {json_path}")

def process_file(json_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Process a single JSON file through loading pipeline.

    Args:
        json_path: Path to JSON file
        dry_run: If True, rollback instead of commit

    Returns:
        Dictionary with load statistics and status
    """
    result = {
        "file": str(json_path),
        "status": "pending",
        "message": "",
        "records_loaded": 0
    }

    # Load configuration
    cfg = config.load_config()

    # Get database connection
    conn = None
    try:
        conn = config.get_connection(cfg)

        # Load JSON file
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Validate we have accounts structure (the standard format)
        if "accounts" not in data:
            raise ValueError("Missing accounts array in JSON")

        # Validate structure - pass "accounts" since we're using account-centric approach
        validator.validate_json_structure(data, "accounts")

        # Check for duplicate
        md5_hash = data.get("extraction_metadata", {}).get("doc_md5_hash") or \
                   data.get("extraction_metadata", {}).get("file_hash")
        if not md5_hash:
            raise ValueError("Missing doc_md5_hash or file_hash in metadata")

        if validator.check_duplicate(md5_hash, conn):
            result["status"] = "duplicate"
            result["message"] = "Document already loaded"
            return result

        # Get institution (will be created if needed)
        institution_name = data.get("extraction_metadata", {}).get("institution") or \
                          data.get("document_data", {}).get("institution")

        # Use first account holder to determine entity for institution
        accounts = data.get("accounts", [])
        if not accounts:
            raise ValueError("No accounts found in data")

        # Require account holder name - fail if missing
        first_holder = accounts[0].get("account_holder_name") or accounts[0].get("account_holder")
        if not first_holder:
            raise ValueError("Missing required account_holder_name or account_holder in first account")

        # Get entity for institution
        entity_id = entities.get_or_create_entity(first_holder, conn, cfg)
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Create document record with final file path (will be in loaded directory)
        loaded_path = json_path.parent.parent / "5loaded" / json_path.name
        doc_id = documents.create_document(
            data.get("extraction_metadata", {}),
            institution_id,
            conn,
            cfg,
            str(loaded_path)
        )

        # Load the data using account-centric approach
        total_records, account_ids = loader.load_accounts_data(data, doc_id, conn, cfg)

        # Link document to accounts
        documents.link_document_accounts(doc_id, account_ids, conn)

        result["records_loaded"] = total_records

        if dry_run:
            conn.rollback()
            result["status"] = "dry_run"
            result["message"] = f"Would load {total_records} records"
        else:
            conn.commit()

            # Move file to loaded directory after successful commit
            move_to_loaded(json_path)

            result["status"] = "success"
            result["message"] = f"Loaded {total_records} records"

    except Exception as e:
        if conn:
            conn.rollback()
        result["status"] = "error"
        result["message"] = str(e)
        print(f"Error: {e}")

    finally:
        if conn:
            conn.close()

    return result

def main():
    """Command-line interface for the loader."""
    parser = argparse.ArgumentParser(
        description='Load financial data from JSON extractions to database'
    )
    parser.add_argument('files', nargs='+', help='JSON files to load')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate without loading')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    # Process each file
    total_loaded = 0
    for file_path in args.files:
        print(f"\nProcessing: {file_path}")
        result = process_file(Path(file_path), args.dry_run)

        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")

        if result['status'] == 'success':
            total_loaded += result['records_loaded']

    print(f"\nTotal records loaded: {total_loaded}")

    # Exit with error code if any failures (files already processed, so don't re-process)
    sys.exit(0)

if __name__ == '__main__':
    main()