#!/usr/bin/env python3
"""
Fix existing transaction types using the new dynamic mapping system.

Created: 09/23/25 6:55PM
Purpose: Correct transaction_type and transaction_subtype for existing transactions using data_mappings table
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db():
    """Get database connection"""
    return psycopg2.connect(
        host='localhost',
        port=54322,
        user='postgres',
        password='postgres',
        database='postgres',
        cursor_factory=RealDictCursor
    )

def get_mapping(mapping_type, source_value, conn):
    """Get type and subtype mapping from database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT target_type, target_subtype
        FROM data_mappings
        WHERE mapping_type = %s AND source_value = %s
    """, (mapping_type, source_value))

    result = cur.fetchone()
    return result if result else None

def get_transaction_type_and_subtype(section_name, description, security_name, conn):
    """Get transaction type and subtype using cascading mapping logic"""

    # First try description-based mapping for precise categorization
    if description:
        desc_mapping = get_mapping('transaction_descriptions', description, conn)
        if desc_mapping:
            transaction_type = desc_mapping['target_type']
            transaction_subtype = desc_mapping['target_subtype']
        else:
            # Fall back to section-based mapping for type
            section_mapping = get_mapping('activity_sections', section_name, conn)
            if section_mapping:
                transaction_type = section_mapping['target_type']
                transaction_subtype = section_mapping['target_subtype']
            else:
                transaction_type = section_name
                transaction_subtype = None
    else:
        # Fall back to section-based mapping
        section_mapping = get_mapping('activity_sections', section_name, conn)
        if section_mapping:
            transaction_type = section_mapping['target_type']
            transaction_subtype = section_mapping['target_subtype']
        else:
            transaction_type = section_name
            transaction_subtype = None

    # Check for security pattern overrides (highest priority for subtypes)
    if security_name:
        # Check if security_name contains any mapped patterns
        cur = conn.cursor()
        cur.execute("""
            SELECT source_value, target_subtype
            FROM data_mappings
            WHERE mapping_type = 'security_patterns'
        """)
        patterns = cur.fetchall()

        for pattern_row in patterns:
            pattern = pattern_row['source_value']
            if pattern in security_name:
                transaction_subtype = pattern_row['target_subtype']
                break

    return transaction_type, transaction_subtype

def fix_transaction_types():
    """Update all existing transactions with correct types using mapping system"""

    conn = connect_db()
    cur = conn.cursor()

    try:
        # Get all transactions that need fixing
        cur.execute("""
            SELECT id, source, description, security_name, transaction_type, transaction_subtype
            FROM transactions
            ORDER BY id
        """)

        transactions = cur.fetchall()
        print(f"Found {len(transactions)} transactions to process")

        updates_made = 0
        corrections = {}

        for tx in transactions:
            # Get new type and subtype
            new_type, new_subtype = get_transaction_type_and_subtype(tx['source'], tx['description'], tx['security_name'], conn)

            # Check if we need to update
            needs_update = (
                tx['transaction_type'] != new_type or
                tx['transaction_subtype'] != new_subtype
            )

            if needs_update:
                # Track the correction
                old_key = f"{tx['transaction_type']}/{tx['transaction_subtype'] or 'null'}"
                new_key = f"{new_type}/{new_subtype or 'null'}"
                correction_key = f"{old_key} → {new_key}"

                if correction_key not in corrections:
                    corrections[correction_key] = []
                corrections[correction_key].append({
                    'description': tx['description'],
                    'source': tx['source']
                })

                # Update the transaction
                cur.execute("""
                    UPDATE transactions
                    SET transaction_type = %s, transaction_subtype = %s
                    WHERE id = %s
                """, (new_type, new_subtype, tx['id']))

                updates_made += 1

        # Commit all changes
        conn.commit()

        print(f"\n✅ Updated {updates_made} transactions")

        # Show summary of corrections
        if corrections:
            print("\nCorrections made:")
            for correction, examples in corrections.items():
                print(f"\n{correction}:")
                for example in examples[:3]:  # Show first 3 examples
                    print(f"  • {example['description']} (from {example['source']})")
                if len(examples) > 3:
                    print(f"  ... and {len(examples) - 3} more")

        # Verify the key fix
        print("\n" + "="*50)
        print("Verifying CUSIP 380037FU0 fix:")
        cur.execute("""
            SELECT description, transaction_type, transaction_subtype, sec_cusip
            FROM transactions
            WHERE sec_cusip = '380037FU0'
        """)

        cusip_results = cur.fetchall()
        for result in cusip_results:
            print(f"  {result['description']} → {result['transaction_type']}/{result['transaction_subtype'] or 'null'}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error fixing transaction types: {e}")
        raise
    finally:
        conn.close()

def test_mapping_system():
    """Test the mapping system with key examples"""

    conn = connect_db()

    test_cases = [
        ('dividends_interest_income', 'Muni Exempt Int', None),
        ('dividends_interest_income', 'Dividend Received', None),
        ('dividends_interest_income', 'Interest Earned', None),
        ('dividends_interest_income', 'Reinvestment', None),
        ('securities_bought_sold', 'You Bought', None),
        ('securities_bought_sold', 'You Bought', 'PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) CLOSING TRANSACTION'),
    ]

    print("Testing mapping system:")
    for source, description, security_name in test_cases:
        result_type, result_subtype = get_transaction_type_and_subtype(source, description, security_name, conn)
        security_note = f" (with CLOSING TRANSACTION)" if security_name and "CLOSING TRANSACTION" in security_name else ""
        print(f"  {source} + '{description}'{security_note} → {result_type}/{result_subtype or 'null'}")

    conn.close()

if __name__ == "__main__":
    print("Testing mapping system first...")
    test_mapping_system()

    print("\n" + "="*50)
    print("Proceeding with fixing existing transactions...")

    fix_transaction_types()