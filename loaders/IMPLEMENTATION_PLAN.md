# Database Loader Implementation Plan

**Created:** 09/23/25 11:05AM ET
**Purpose:** Standalone implementation guide for building database loaders for financial data
**Target Developer:** Any Claude instance or developer implementing from scratch

## Overview

This document provides complete specifications for implementing a database loader system that takes JSON files extracted from financial statements and loads them into a PostgreSQL database. The loader follows a "lazy creation" pattern where entities, institutions, and accounts are created on-demand as they're encountered.

## Prerequisites

Before starting implementation, ensure you have:

1. **Database Schema Created**
   - Schema file: `/docs/Design/02-Technical/schema.md`
   - Migration script: `/database-migration-plan.md`
   - Database must be running at: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`

2. **JSON Extraction Files**
   - Positions format: `/config/institution-guides/JSON_Stmnt_Fid_Positions.md`
   - Activities format: `/config/institution-guides/JSON_Stmnt_Fid_Activities.md`

3. **Configuration Files**
   - Account mappings: `/config/database-account-mappings.json`
   - Database connection: Create `/loaders/config/loader_config.json` (template below)

## Project Structure to Create

```
/loaders/
├── IMPLEMENTATION_PLAN.md    # This file
├── README.md                 # User documentation (create from template below)
├── requirements.txt          # Python dependencies
├── config/
│   ├── loader_config.json   # Database settings
│   └── test_config.json     # Test database settings
├── src/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── validator.py         # Input validation
│   ├── entities.py          # Entity/Institution/Account creation
│   ├── documents.py         # Document record management
│   ├── transform.py         # Data transformation
│   ├── loader.py            # Core loading logic
│   └── main.py              # Main orchestrator
├── tests/
│   ├── __init__.py
│   ├── test_validator.py
│   ├── test_entities.py
│   ├── test_transform.py
│   ├── test_loader.py
│   └── test_integration.py
└── test_data/
    ├── sample_positions.json
    ├── sample_activities.json
    └── invalid_data.json
```

## Configuration Files

### `/loaders/config/loader_config.json`
```json
{
  "database": {
    "host": "127.0.0.1",
    "port": 54322,
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
  },
  "mappings": {
    "account_mappings_path": "../../config/database-account-mappings.json"
  },
  "defaults": {
    "tax_year": 2024,
    "institution": "Fidelity Investments",
    "georgia_resident": true
  },
  "processing": {
    "batch_size": 500,
    "fail_on_duplicate": true,
    "create_missing_accounts": true
  }
}
```

### `/loaders/requirements.txt`
```
psycopg2-binary==2.9.9
python-dateutil==2.8.2
```

## Module Implementations

### Module 1: `src/config.py`
```python
"""
Configuration Module for Database Loader

Created: 09/23/25
Purpose: Manage database connections and configuration settings
Updates:
  - 09/23/25: Initial implementation

This module handles configuration loading and database connections.
Uses a simple connection approach without pooling for clarity.
"""

import json
import psycopg2
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file, defaults to ../config/loader_config.json

    Returns:
        Dictionary containing all configuration settings
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "loader_config.json"

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Load account mappings
    mappings_path = Path(__file__).parent.parent.parent / config["mappings"]["account_mappings_path"]
    with open(mappings_path, 'r') as f:
        config["account_mappings"] = json.load(f)

    return config

def get_connection(config: Dict[str, Any] = None) -> psycopg2.extensions.connection:
    """
    Create a database connection.

    Args:
        config: Configuration dictionary, loads default if None

    Returns:
        psycopg2 connection object

    Raises:
        psycopg2.Error: If connection fails
    """
    if config is None:
        config = load_config()

    db_config = config["database"]
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"]
    )

    # Set autocommit off for transaction control
    conn.autocommit = False

    return conn
```

### Module 2: `src/validator.py`
```python
"""
Validation Module for Database Loader

Created: 09/23/25
Purpose: Validate JSON structure and check for duplicate documents
Updates:
  - 09/23/25: Initial implementation

Validates input data and prevents duplicate document loads.
"""

from typing import Dict, Any

def validate_json_structure(data: Dict[str, Any], data_type: str) -> bool:
    """
    Validate that required fields exist in JSON data.

    Args:
        data: JSON data to validate
        data_type: 'positions' or 'activities'

    Returns:
        True if valid

    Raises:
        ValueError: If required fields are missing
    """
    # Check for metadata
    if "extraction_metadata" not in data:
        raise ValueError("Missing extraction_metadata")

    metadata = data["extraction_metadata"]
    required_metadata = ["file_hash", "file_path", "extraction_date"]
    for field in required_metadata:
        if field not in metadata:
            raise ValueError(f"Missing metadata field: {field}")

    # Check for data section
    if data_type == "positions":
        if "holdings" not in data:
            raise ValueError("Missing holdings data")
    elif data_type == "activities":
        if "activities" not in data:
            raise ValueError("Missing activities data")
    else:
        raise ValueError(f"Unknown data type: {data_type}")

    return True

def check_duplicate(md5_hash: str, conn) -> bool:
    """
    Check if document with this hash already exists.

    Args:
        md5_hash: MD5 hash of document
        conn: Database connection

    Returns:
        True if duplicate exists, False if new document
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM documents WHERE doc_md5_hash = %s",
        (md5_hash,)
    )
    result = cursor.fetchone()
    cursor.close()

    return result is not None
```

### Module 3: `src/entities.py`
```python
"""
Entity Management Module for Database Loader

Created: 09/23/25
Purpose: Handle lazy creation of entities, institutions, and accounts
Updates:
  - 09/23/25: Initial implementation with get_or_create pattern

Implements lazy creation - records created on-demand as encountered.
"""

import uuid
from typing import Optional, Dict, Any

# Cache to avoid repeated lookups
_entity_cache = {}
_institution_cache = {}
_account_cache = {}

def get_or_create_entity(name: str, conn, config: Dict[str, Any]) -> str:
    """
    Find existing entity or create new one with placeholder tax_id.

    Args:
        name: Entity name (from account holder)
        conn: Database connection
        config: Configuration dictionary

    Returns:
        entity_id as string
    """
    # Check cache
    if name in _entity_cache:
        return _entity_cache[name]

    cursor = conn.cursor()

    # Try to find existing
    cursor.execute(
        "SELECT id FROM entities WHERE entity_name = %s",
        (name,)
    )
    result = cursor.fetchone()

    if result:
        entity_id = str(result[0])
    else:
        # Create new entity with placeholder tax_id
        entity_id = str(uuid.uuid4())
        placeholder_tax_id = f"PENDING-{entity_id[:8]}"

        cursor.execute("""
            INSERT INTO entities (
                id, entity_name, entity_type, tax_id,
                tax_id_display, georgia_resident, entity_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            entity_id, name, 'individual', placeholder_tax_id,
            'PENDING', config["defaults"]["georgia_resident"], 'active'
        ))

        print(f"Created entity: {name} with ID {entity_id[:8]}")

    cursor.close()
    _entity_cache[name] = entity_id
    return entity_id

def get_or_create_institution(name: str, entity_id: str, conn) -> str:
    """
    Find existing institution or create new one.

    Args:
        name: Institution name
        entity_id: Associated entity
        conn: Database connection

    Returns:
        institution_id as string
    """
    # Normalize name
    institution_map = {
        "fidelity": "Fidelity Investments",
        "bofa": "Bank of America",
        "boa": "Bank of America",
        "suntrust": "SunTrust Bank"
    }
    normalized_name = institution_map.get(name.lower(), name)

    cache_key = f"{normalized_name}:{entity_id}"
    if cache_key in _institution_cache:
        return _institution_cache[cache_key]

    cursor = conn.cursor()

    # Try to find existing
    cursor.execute(
        "SELECT id FROM institutions WHERE institution_name = %s AND entity_id = %s",
        (normalized_name, entity_id)
    )
    result = cursor.fetchone()

    if result:
        institution_id = str(result[0])
    else:
        # Create new institution
        institution_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO institutions (
                id, entity_id, institution_name, institution_type, status
            ) VALUES (
                %s, %s, %s, %s, %s
            )
        """, (
            institution_id, entity_id, normalized_name, 'brokerage', 'active'
        ))

        print(f"Created institution: {normalized_name}")

    cursor.close()
    _institution_cache[cache_key] = institution_id
    return institution_id

def get_or_create_account(
    account_number: str,
    entity_id: str,
    institution_id: str,
    account_type: str,
    conn,
    config: Dict[str, Any]
) -> str:
    """
    Find existing account or create new one.

    Args:
        account_number: Full account number
        entity_id: Owner entity
        institution_id: Holding institution
        account_type: Type of account
        conn: Database connection
        config: Configuration dictionary

    Returns:
        account_id as string
    """
    if account_number in _account_cache:
        return _account_cache[account_number]

    cursor = conn.cursor()

    # Try to find existing
    cursor.execute(
        "SELECT id FROM accounts WHERE account_number = %s AND institution_id = %s",
        (account_number, institution_id)
    )
    result = cursor.fetchone()

    if result:
        account_id = str(result[0])
    else:
        # Create new account
        account_id = str(uuid.uuid4())
        display_number = "****" + account_number[-4:] if len(account_number) >= 4 else "****"

        # Check if this account is in mappings for tax flags
        mappings = config.get("account_mappings", {}).get("account_mappings", {})
        account_info = mappings.get(display_number, {})

        cursor.execute("""
            INSERT INTO accounts (
                id, entity_id, institution_id, account_number,
                account_number_display, account_type, account_status,
                is_tax_deferred, is_tax_free, requires_rmd
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            account_id, entity_id, institution_id, account_number,
            display_number, account_type, 'active',
            account_info.get("is_tax_deferred", False),
            account_info.get("is_tax_free", False),
            account_info.get("requires_rmd", False)
        ))

        print(f"Created account: {display_number} ({account_type})")

    cursor.close()
    _account_cache[account_number] = account_id
    return account_id
```

### Module 4: `src/documents.py`
```python
"""
Document Management Module for Database Loader

Created: 09/23/25
Purpose: Create and manage document records
Updates:
  - 09/23/25: Initial implementation

Handles document record creation and account linking.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime

def create_document(metadata: Dict[str, Any], institution_id: str, conn, config: Dict[str, Any]) -> str:
    """
    Create document record with metadata.

    Args:
        metadata: Document metadata from JSON
        institution_id: Institution that issued document
        conn: Database connection
        config: Configuration dictionary

    Returns:
        document_id as string
    """
    cursor = conn.cursor()
    document_id = str(uuid.uuid4())

    # Extract dates
    extraction_date = datetime.strptime(metadata["extraction_date"], "%Y-%m-%d")
    period_start = metadata.get("period_start")
    period_end = metadata.get("period_end")

    # Convert date strings if present
    if period_start:
        period_start = datetime.strptime(period_start, "%Y-%m-%d").date()
    if period_end:
        period_end = datetime.strptime(period_end, "%Y-%m-%d").date()

    cursor.execute("""
        INSERT INTO documents (
            id, institution_id, tax_year, document_type,
            period_start, period_end, file_path, file_name,
            doc_md5_hash, processed_at, processed_by
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        document_id,
        institution_id,
        config["defaults"]["tax_year"],
        'statement',
        period_start,
        period_end,
        metadata["file_path"],
        metadata.get("file_name", "unknown"),
        metadata["file_hash"],
        datetime.now(),
        'loader'
    ))

    cursor.close()
    print(f"Created document: {document_id[:8]}")
    return document_id

def link_document_accounts(doc_id: str, account_ids: List[str], conn) -> int:
    """
    Create document-account associations.

    Args:
        doc_id: Document ID
        account_ids: List of account IDs
        conn: Database connection

    Returns:
        Number of links created
    """
    cursor = conn.cursor()
    count = 0

    for account_id in set(account_ids):  # Use set to avoid duplicates
        cursor.execute("""
            INSERT INTO document_accounts (document_id, account_id)
            VALUES (%s, %s)
            ON CONFLICT (document_id, account_id) DO NOTHING
        """, (doc_id, account_id))
        count += cursor.rowcount

    cursor.close()
    return count
```

### Module 5: `src/transform.py`
```python
"""
Data Transformation Module for Database Loader

Created: 09/23/25
Purpose: Transform extracted data into database-ready formats
Updates:
  - 09/23/25: Initial implementation

Handles date parsing, amount conversion, and type inference.
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

    return 'other'

def infer_account_type(account_name: str) -> str:
    """
    Infer account type from name or description.

    Args:
        account_name: Account name or description

    Returns:
        Account type string
    """
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

    return 'brokerage'  # Default
```

### Module 6: `src/loader.py`
```python
"""
Core Loading Module for Database Loader

Created: 09/23/25
Purpose: Load positions and activities data into database
Updates:
  - 09/23/25: Initial implementation

Core logic for loading financial data into database tables.
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
    institution_name = data.get("extraction_metadata", {}).get("institution", "Fidelity")

    # Process each account's holdings
    for account_data in data.get("holdings", []):
        account_number = account_data.get("account_number")
        account_holder = account_data.get("account_holder", "Unknown")

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity
        entity_id = entities.get_or_create_entity(account_holder, conn, config)

        # Get or create institution
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Get or create account
        account_type = transform.infer_account_type(
            account_data.get("account_type", "brokerage")
        )
        account_id = entities.get_or_create_account(
            account_number, entity_id, institution_id, account_type, conn, config
        )

        account_ids_used.append(account_id)

        # Load each position
        for position in account_data.get("positions", []):
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
                position.get("description", "Unknown"),
                position.get("security_type", "other"),
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
    institution_name = data.get("extraction_metadata", {}).get("institution", "Fidelity")

    # Process each account's activities
    for account_data in data.get("activities", []):
        account_number = account_data.get("account_number")
        account_holder = account_data.get("account_holder", "Unknown")

        if not account_number:
            print(f"Warning: Skipping account with no number")
            continue

        # Get or create entity
        entity_id = entities.get_or_create_entity(account_holder, conn, config)

        # Get or create institution
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Get or create account
        account_type = transform.infer_account_type(
            account_data.get("account_type", "brokerage")
        )
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
                transform.infer_transaction_type(activity.get("description", "")),
                activity.get("description", ""),
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
```

### Module 7: `src/main.py`
```python
"""
Main Orchestrator for Database Loader

Created: 09/23/25
Purpose: Coordinate all modules to load financial data
Updates:
  - 09/23/25: Initial implementation

Entry point that orchestrates the complete loading process.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from . import config
from . import validator
from . import entities
from . import documents
from . import loader

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

        # Determine data type
        if "holdings" in data:
            data_type = "positions"
        elif "activities" in data:
            data_type = "activities"
        else:
            raise ValueError("Unknown data type in JSON")

        # Validate structure
        validator.validate_json_structure(data, data_type)

        # Check for duplicate
        md5_hash = data.get("extraction_metadata", {}).get("file_hash")
        if not md5_hash:
            raise ValueError("Missing file_hash in metadata")

        if validator.check_duplicate(md5_hash, conn):
            result["status"] = "duplicate"
            result["message"] = "Document already loaded"
            return result

        # Get institution (will be created if needed)
        institution_name = data.get("extraction_metadata", {}).get("institution", "Fidelity")

        # Use first account holder to determine entity for institution
        first_holder = None
        if data_type == "positions":
            holdings = data.get("holdings", [])
            if holdings:
                first_holder = holdings[0].get("account_holder", "Unknown")
        else:
            activities = data.get("activities", [])
            if activities:
                first_holder = activities[0].get("account_holder", "Unknown")

        if not first_holder:
            raise ValueError("No account holder found in data")

        # Get entity for institution
        entity_id = entities.get_or_create_entity(first_holder, conn, cfg)
        institution_id = entities.get_or_create_institution(institution_name, entity_id, conn)

        # Create document record
        doc_id = documents.create_document(
            data.get("extraction_metadata", {}),
            institution_id,
            conn,
            cfg
        )

        # Load the data
        if data_type == "positions":
            count, account_ids = loader.load_positions(data, doc_id, conn, cfg)
        else:
            count, account_ids = loader.load_activities(data, doc_id, conn, cfg)

        # Link document to accounts
        documents.link_document_accounts(doc_id, account_ids, conn)

        result["records_loaded"] = count

        if dry_run:
            conn.rollback()
            result["status"] = "dry_run"
            result["message"] = f"Would load {count} records"
        else:
            conn.commit()
            result["status"] = "success"
            result["message"] = f"Loaded {count} records"

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

    # Exit with error code if any failures
    sys.exit(0 if all(
        process_file(Path(f), args.dry_run)['status'] in ['success', 'dry_run', 'duplicate']
        for f in args.files
    ) else 1)

if __name__ == '__main__':
    main()
```

## Testing Guide

### Create Test Data

Create `/loaders/test_data/sample_positions.json`:
```json
{
  "extraction_metadata": {
    "file_path": "/test/sample_statement.pdf",
    "file_hash": "abc123def456789",
    "file_name": "sample_statement.pdf",
    "extraction_date": "2024-09-23",
    "institution": "Fidelity",
    "statement_date": "2024-08-31",
    "period_start": "2024-08-01",
    "period_end": "2024-08-31"
  },
  "holdings": [
    {
      "account_number": "X12345678",
      "account_holder": "John Doe",
      "account_type": "Individual Brokerage",
      "positions": [
        {
          "symbol": "AAPL",
          "cusip": "037833100",
          "description": "APPLE INC",
          "security_type": "stock",
          "quantity": "100",
          "price": "175.50",
          "market_value": "17550.00",
          "cost_basis": "15000.00",
          "unrealized_gain_loss": "2550.00"
        }
      ]
    }
  ]
}
```

### Manual Testing Steps

1. **Setup Database**
```bash
# Apply schema migration
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres < ../database-migration-plan.sql
```

2. **Install Dependencies**
```bash
cd loaders
pip install -r requirements.txt
```

3. **Test Dry Run**
```bash
python -m src.main --dry-run test_data/sample_positions.json
# Should show: "Would load X records"
```

4. **Test Actual Load**
```bash
python -m src.main test_data/sample_positions.json
# Should show: "Loaded X records"
```

5. **Test Duplicate Prevention**
```bash
python -m src.main test_data/sample_positions.json
# Should show: "Document already loaded"
```

6. **Verify in Database**
```sql
-- Check entities created
SELECT * FROM entities;

-- Check accounts created
SELECT * FROM accounts;

-- Check positions loaded
SELECT * FROM positions;

-- Check document created
SELECT * FROM documents;
```

### Unit Test Template

Create `/loaders/tests/test_transform.py`:
```python
"""
Unit Tests for Transform Module

Created: 09/23/25
Purpose: Test data transformation functions
"""

import unittest
from datetime import date
from decimal import Decimal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import transform

class TestTransform(unittest.TestCase):

    def test_parse_date_iso(self):
        """Test parsing ISO format dates."""
        result = transform.parse_date("2024-09-23")
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_date_mmddyyyy(self):
        """Test parsing MM/DD/YYYY dates."""
        result = transform.parse_date("09/23/2024")
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_date_mmdd_with_year(self):
        """Test parsing MM/DD with provided year."""
        result = transform.parse_date("09/23", tax_year=2024)
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_amount_simple(self):
        """Test parsing simple amounts."""
        result = transform.parse_amount("1234.56")
        self.assertEqual(result, Decimal("1234.56"))

    def test_parse_amount_with_symbols(self):
        """Test parsing amounts with $ and commas."""
        result = transform.parse_amount("$1,234.56")
        self.assertEqual(result, Decimal("1234.56"))

    def test_parse_amount_negative(self):
        """Test parsing negative amounts with parentheses."""
        result = transform.parse_amount("(1234.56)")
        self.assertEqual(result, Decimal("-1234.56"))

    def test_infer_transaction_type_dividend(self):
        """Test inferring dividend transaction type."""
        result = transform.infer_transaction_type("ORDINARY DIVIDEND")
        self.assertEqual(result, "dividend")

    def test_infer_transaction_type_buy(self):
        """Test inferring buy transaction type."""
        result = transform.infer_transaction_type("YOU BOUGHT 100 SHARES")
        self.assertEqual(result, "buy")

if __name__ == '__main__':
    unittest.main()
```

## Validation Checklist

- [ ] Database connection successful
- [ ] JSON validation catches missing fields
- [ ] MD5 duplicate detection works
- [ ] Entities created with placeholder tax IDs
- [ ] Institutions created and normalized
- [ ] Accounts created with proper types
- [ ] Positions loaded with all fields
- [ ] Activities loaded with all fields
- [ ] Document-account links created
- [ ] Transaction commits on success
- [ ] Transaction rollbacks on error
- [ ] Dry run doesn't modify database
- [ ] Command-line interface works
- [ ] Error messages are helpful

## Success Criteria

1. **Can load a positions JSON file** without errors
2. **Can load an activities JSON file** without errors
3. **Prevents duplicate document loading** via MD5 hash
4. **Creates entities automatically** from account holder names
5. **Creates accounts automatically** as encountered
6. **All data is committed atomically** (all or nothing)
7. **Dry run mode works** for testing
8. **Clear error messages** when things go wrong

## Next Steps After Implementation

1. Run loader on sample data
2. Verify all tables populated correctly
3. Test with real extraction outputs
4. Add more comprehensive error handling if needed
5. Create batch processing script for multiple files
6. Document any institution-specific quirks discovered

---

This implementation plan provides everything needed to build the database loader from scratch. The code is simple, modular, and focused solely on moving data from JSON files into the database efficiently.