"""
Validation Module for Database Loader

Created: 09/23/25 11:05AM
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

    # Check for file hash (either doc_md5_hash or file_hash)
    if "doc_md5_hash" not in metadata and "file_hash" not in metadata:
        raise ValueError("Missing metadata field: doc_md5_hash or file_hash")

    # Check for file path
    if "file_path" not in metadata:
        raise ValueError("Missing metadata field: file_path")

    # Check for extraction date/timestamp
    if "extraction_date" not in metadata and "extraction_timestamp" not in metadata:
        raise ValueError("Missing metadata field: extraction_date or extraction_timestamp")

    # Check for accounts section
    if data_type == "accounts":
        if "accounts" not in data:
            raise ValueError("Missing accounts data")
    elif data_type == "positions":
        if "holdings" not in data and "accounts" not in data:
            raise ValueError("Missing holdings or accounts data")
    elif data_type == "activities":
        if "activities" not in data and "accounts" not in data:
            raise ValueError("Missing activities or accounts data")
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