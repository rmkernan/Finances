#!/usr/bin/env python3
"""
Populate sec_class column for existing transactions using security classification mappings.

Created: 09/23/25 7:13PM
Purpose: Add security classification (call, put) to existing transactions based on security_name patterns
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

def get_security_classification(security_name, conn):
    """
    Get security classification (call, put, etc.) from security name patterns.

    Args:
        security_name: The security description from transactions
        conn: Database connection

    Returns:
        String classification (call, put) or None if no match
    """
    if not security_name:
        return None

    # Get all security classification patterns, ordered by length for specificity
    # Longer patterns like "ASSIGNED PUTS" should match before shorter ones like "PUT ("
    cur = conn.cursor()
    cur.execute("""
        SELECT source_value, target_subtype
        FROM data_mappings
        WHERE mapping_type = 'security_classification'
        ORDER BY LENGTH(source_value) DESC
    """)
    patterns = cur.fetchall()

    # Check each pattern against the security name
    for pattern_row in patterns:
        pattern = pattern_row['source_value']
        if pattern in security_name:
            return pattern_row['target_subtype']

    return None

def populate_sec_class():
    """
    Update all existing transactions with sec_class values based on security_name patterns.

    This handles options classification:
    - CALL ( → sec_class = 'call'
    - PUT ( → sec_class = 'put'
    - ASSIGNED CALLS → sec_class = 'call'
    - ASSIGNED PUTS → sec_class = 'put'
    """

    conn = connect_db()
    cur = conn.cursor()

    try:
        # Get all transactions that have security names (candidates for classification)
        print("Finding transactions with security names...")
        cur.execute("""
            SELECT id, security_name, sec_class
            FROM transactions
            WHERE security_name IS NOT NULL
            ORDER BY id
        """)

        transactions = cur.fetchall()
        print(f"Found {len(transactions)} transactions with security names")

        updates_made = 0
        classifications = {}

        # Process each transaction
        for tx in transactions:
            # Get security classification using our mapping system
            new_sec_class = get_security_classification(tx['security_name'], conn)

            # Only update if we found a classification and it's different from current value
            if new_sec_class and tx['sec_class'] != new_sec_class:
                # Track the classification for reporting
                if new_sec_class not in classifications:
                    classifications[new_sec_class] = []
                classifications[new_sec_class].append(tx['security_name'][:50] + '...' if len(tx['security_name']) > 50 else tx['security_name'])

                # Update the transaction
                cur.execute("""
                    UPDATE transactions
                    SET sec_class = %s
                    WHERE id = %s
                """, (new_sec_class, tx['id']))

                updates_made += 1

        # Commit all changes
        conn.commit()
        print(f"\n✅ Updated {updates_made} transactions with sec_class values")

        # Show summary of classifications
        if classifications:
            print("\nClassifications applied:")
            for sec_class, examples in classifications.items():
                print(f"\n{sec_class.upper()}:")
                for example in examples[:5]:  # Show first 5 examples
                    print(f"  • {example}")
                if len(examples) > 5:
                    print(f"  ... and {len(examples) - 5} more")

        # Verify the results
        print("\n" + "="*50)
        print("Final sec_class distribution:")
        cur.execute("""
            SELECT sec_class, COUNT(*) as count
            FROM transactions
            WHERE sec_class IS NOT NULL
            GROUP BY sec_class
            ORDER BY count DESC
        """)

        results = cur.fetchall()
        for result in results:
            print(f"  {result['sec_class']}: {result['count']} transactions")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error populating sec_class: {e}")
        raise
    finally:
        conn.close()

def test_classification():
    """Test the classification system with known examples"""

    conn = connect_db()

    test_cases = [
        "CALL (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS)",
        "PUT (CRWV) COREWEAVE INC COM CL AUG 29 25 $100 (100 SHS)",
        "TESLA INC COM ASSIGNED PUTS",
        "ADVANCED MICRO DEVICES INC ASSIGNED PUTS",
        "AT&T INC COM USD1",  # Should return None (not an option)
    ]

    print("Testing security classification:")
    for security_name in test_cases:
        result = get_security_classification(security_name, conn)
        print(f"  '{security_name[:40]}...' → {result or 'None'}")

    conn.close()

if __name__ == "__main__":
    print("Testing classification system first...")
    test_classification()

    print("\n" + "="*50)
    print("Proceeding with populating sec_class for existing transactions...")

    populate_sec_class()