"""
Document Management Module for Database Loader

Created: 09/23/25 11:05AM
Purpose: Create and manage document records
Updates:
  - 09/23/25 11:05AM: Initial implementation
  - 09/23/25 11:20AM: Added comment clarifying file_hash maps to doc_md5_hash column

Handles document record creation and account linking.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

def create_document(metadata: Dict[str, Any], institution_id: str, conn, config: Dict[str, Any], final_file_path: str = None) -> str:
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

    # Extract dates - handle both extraction_date and extraction_timestamp
    if "extraction_date" in metadata:
        extraction_date = datetime.strptime(metadata["extraction_date"], "%Y-%m-%d")
    elif "extraction_timestamp" in metadata:
        # Parse ISO timestamp and extract date part
        extraction_date = datetime.fromisoformat(metadata["extraction_timestamp"].replace('Z', '+00:00'))
    else:
        raise ValueError("Missing extraction_date or extraction_timestamp in metadata")
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
        final_file_path or metadata["file_path"],
        Path(metadata["file_path"]).name,
        metadata["file_hash"],  # Maps to doc_md5_hash column
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