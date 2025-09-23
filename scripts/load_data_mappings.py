#!/usr/bin/env python3
"""
Load data mappings from config/data-mappings.json into the database.
"""

import json
import psycopg2
from datetime import datetime
import os

def load_mappings_to_database():
    """Load all mappings from JSON config into database table."""

    # Read the configuration file
    config_path = '/Users/richkernan/Projects/Finances/config/data-mappings.json'
    with open(config_path, 'r') as f:
        mappings_config = json.load(f)

    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        port=54322,
        user='postgres',
        password='postgres',
        database='postgres'
    )
    cursor = conn.cursor()

    try:
        # Clear existing mappings (for clean reload)
        print("Clearing existing mappings...")
        cursor.execute("DELETE FROM data_mappings")

        # Load each mapping type
        total_inserted = 0

        for mapping_type, mappings in mappings_config.items():
            print(f"\nLoading {mapping_type} mappings...")

            for source_value, mapping_data in mappings.items():
                cursor.execute("""
                    INSERT INTO data_mappings (mapping_type, source_value, target_type, target_subtype, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    mapping_type,
                    source_value,
                    mapping_data['type'],
                    mapping_data.get('subtype'),
                    mapping_data.get('notes')
                ))
                total_inserted += 1
                print(f"  {source_value} → {mapping_data['type']}/{mapping_data.get('subtype', 'null')}")

        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully loaded {total_inserted} mappings into database")

        # Verify the load
        cursor.execute("SELECT mapping_type, COUNT(*) FROM data_mappings GROUP BY mapping_type ORDER BY mapping_type")
        results = cursor.fetchall()
        print("\nMapping counts by type:")
        for mapping_type, count in results:
            print(f"  {mapping_type}: {count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error loading mappings: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_mapping_lookup(mapping_type, source_value):
    """Test looking up a specific mapping."""
    conn = psycopg2.connect(
        host='localhost',
        port=54322,
        user='postgres',
        password='postgres',
        database='postgres'
    )
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT target_type, target_subtype, notes
            FROM data_mappings
            WHERE mapping_type = %s AND source_value = %s
        """, (mapping_type, source_value))

        result = cursor.fetchone()
        if result:
            print(f"✅ {mapping_type}.{source_value} → {result[0]}/{result[1] or 'null'}")
            if result[2]:
                print(f"   Notes: {result[2]}")
        else:
            print(f"❌ No mapping found for {mapping_type}.{source_value}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Loading data mappings into database...")
    load_mappings_to_database()

    print("\n" + "="*50)
    print("Testing mappings...")

    # Test the key mappings
    test_mapping_lookup('transaction_descriptions', 'Muni Exempt Int')
    test_mapping_lookup('transaction_descriptions', 'Dividend Received')
    test_mapping_lookup('security_types', 'PUT')