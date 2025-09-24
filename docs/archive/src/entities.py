"""
Entity Management Module for Database Loader

Created: 09/23/25 11:05AM
Purpose: Handle lazy creation of entities, institutions, and accounts
Updates:
  - 09/23/25 11:05AM: Initial implementation with get_or_create pattern
  - 09/23/25 11:20AM: Fixed account cache key to include institution_id to prevent collisions

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
    if not name:
        raise ValueError(f"Institution name is required but was None/empty. Check extraction_metadata.institution or document_data.institution in source JSON.")

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
    # Use institution_id + account_number as cache key to avoid collisions
    cache_key = f"{institution_id}:{account_number}"
    if cache_key in _account_cache:
        return _account_cache[cache_key]

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
    _account_cache[cache_key] = account_id
    return account_id