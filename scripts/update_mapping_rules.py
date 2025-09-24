#!/usr/bin/env python3
"""
Update Mapping Rules Script - Configuration-Driven Transaction Classification System

Created: 09/24/25 9:55AM
Purpose: Parse CSV rule definitions and update the three-table mapping system in the database

OVERVIEW:
This script bridges the user-friendly CSV rule management interface with the database-driven
classification system. It reads human-readable rules from /config/mapping-rules.csv and
populates the three-table system (map_rules, map_conditions, map_actions).

USER WORKFLOW:
1. User edits /config/mapping-rules.csv in Excel with visual formatting
2. User saves changes (Excel keeps CSV format)
3. User runs: python3 scripts/update_mapping_rules.py
4. Script parses CSV and updates database tables
5. New rules immediately apply to future transaction processing

CSV FORMAT EXPECTED:
- Rule Name: Human-readable identifier
- Triggers: Compound conditions with AND/OR logic
- Actions: Multiple SET statements separated by semicolons
- Problem Solved: Business justification

INTEGRATION WITH LOADING PROCESS:
This script will be called by the main data loading pipeline whenever:
- New documents are processed (to ensure latest rules are active)
- User explicitly updates rules via CSV file
- System detects CSV file changes (future enhancement)

The script performs a complete refresh of mapping rules, allowing users to:
- Add new rules for emerging transaction patterns
- Modify existing rule conditions or actions
- Remove obsolete rules
- Reorder rule application sequence

TECHNICAL APPROACH:
1. Parse CSV file with proper quote handling for complex conditions
2. Clear existing mapping tables (preserves rule application order)
3. Parse compound triggers (AND/OR logic) into individual conditions
4. Parse multiple actions (semicolon-separated) into individual actions
5. Insert rules with proper foreign key relationships
6. Validate rule syntax and provide helpful error messages

SAFETY FEATURES:
- Database transaction ensures atomic updates (all-or-nothing)
- Validation of CSV format and required fields
- Clear error messages for troubleshooting
- Preserves existing data_mappings table as fallback

EXAMPLES:
Single condition: activities.description contains "OPENING TRANSACTION"
Compound condition: activities.description contains "Muni Exempt Int" AND activities.section equals "dividends_interest_income"
Multiple actions: SET activities.type = "interest"; SET activities.subtype = "muni_exempt"

"""

import csv
import psycopg2
import re
import sys
from pathlib import Path

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 54322,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

# Path to CSV file with rule definitions
CSV_FILE = Path(__file__).parent.parent / 'config' / 'mapping-rules.csv'


def parse_triggers(trigger_string):
    """
    Parse compound trigger conditions into individual condition records.

    Handles formats like:
    - Single: activities.description contains "OPENING TRANSACTION"
    - Compound: activities.description contains "Muni Exempt Int" AND activities.section equals "dividends_interest_income"
    - OR logic: activities.description contains "CALL (" OR activities.security contains "CALL ("

    Returns list of tuples: (check_field, match_operator, match_value, logic_connector)
    """
    conditions = []

    # Split on AND/OR while preserving the connector
    # This regex splits on AND/OR but keeps them in the result
    parts = re.split(r'\s+(AND|OR)\s+', trigger_string.strip())

    i = 0
    while i < len(parts):
        part = parts[i].strip()

        if part in ('AND', 'OR'):
            i += 1
            continue

        # Parse individual condition: field operator "value"
        # Match pattern like: activities.description contains "OPENING TRANSACTION"
        match = re.match(r'(\w+\.\w+)\s+(contains|equals|starts_with)\s+"([^"]+)"', part)

        if not match:
            raise ValueError(f"Cannot parse condition: {part}")

        check_field, match_operator, match_value = match.groups()

        # Determine the connector for this condition
        # First condition gets 'AND', others get the connector that preceded them
        if len(conditions) == 0:
            logic_connector = 'AND'
        else:
            # Look back to find the connector
            if i > 1 and parts[i-1] in ('AND', 'OR'):
                logic_connector = parts[i-1]
            else:
                logic_connector = 'AND'

        conditions.append((check_field, match_operator, match_value, logic_connector))
        i += 1

    return conditions


def parse_actions(action_string):
    """
    Parse multiple SET actions separated by semicolons.

    Handles formats like:
    - Single: SET activities.type = "interest"
    - Multiple: SET activities.type = "interest"; SET activities.subtype = "muni_exempt"

    Returns list of tuples: (set_field, set_value)
    """
    actions = []

    # Split on semicolons and process each SET statement
    action_parts = [part.strip() for part in action_string.split(';')]

    for part in action_parts:
        # Parse: SET field = "value"
        match = re.match(r'SET\s+(\w+\.\w+)\s*=\s*"([^"]+)"', part.strip())

        if not match:
            raise ValueError(f"Cannot parse action: {part}")

        set_field, set_value = match.groups()
        actions.append((set_field, set_value))

    return actions


def determine_rule_category(rule_name):
    """
    Automatically determine rule category based on rule name patterns.
    This provides consistent categorization without requiring user input.
    """
    rule_lower = rule_name.lower()

    if any(keyword in rule_lower for keyword in ['opening', 'closing', 'assignment']):
        return 'Options Lifecycle'
    elif any(keyword in rule_lower for keyword in ['dividend', 'interest', 'muni']):
        return 'Transaction Types'
    elif any(keyword in rule_lower for keyword in ['identifier', 'call', 'put']):
        return 'Security Identification'
    elif 'section' in rule_lower:
        return 'Section Fallbacks'
    elif 'security type' in rule_lower:
        return 'General Securities'
    else:
        return 'Custom Rules'


def determine_application_order(rule_category):
    """
    Assign processing order based on rule category.
    Lower numbers = higher priority (processed first).
    """
    order_map = {
        'Options Lifecycle': 1,
        'Transaction Types': 2,
        'Security Identification': 3,
        'Section Fallbacks': 4,
        'General Securities': 5,
        'Custom Rules': 6
    }
    return order_map.get(rule_category, 6)


def load_csv_rules():
    """
    Load and parse rules from CSV file.
    Returns list of rule dictionaries with parsed conditions and actions.
    """
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    rules = []

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
            try:
                rule_name = row['Rule Name'].strip()
                triggers = row['Triggers'].strip()
                actions = row['Actions'].strip()
                problem_solved = row['Problem Solved'].strip()

                if not all([rule_name, triggers, actions]):
                    print(f"Warning: Skipping row {row_num} - missing required fields")
                    continue

                # Parse triggers and actions
                conditions = parse_triggers(triggers)
                action_list = parse_actions(actions)

                # Determine category and processing order
                rule_category = determine_rule_category(rule_name)
                application_order = determine_application_order(rule_category)

                rules.append({
                    'rule_name': rule_name,
                    'application_order': application_order,
                    'rule_category': rule_category,
                    'problem_solved': problem_solved,
                    'conditions': conditions,
                    'actions': action_list,
                    'csv_row': row_num
                })

            except Exception as e:
                print(f"Error parsing row {row_num} ({rule_name}): {e}")
                raise

    # Sort by application order to ensure consistent processing
    rules.sort(key=lambda x: (x['application_order'], x['rule_name']))

    return rules


def update_database_rules(rules):
    """
    Update the three mapping tables with parsed rules from CSV.
    Uses database transaction to ensure atomic updates.
    """
    conn = psycopg2.connect(**DB_PARAMS)

    try:
        with conn:
            with conn.cursor() as cur:
                print("Clearing existing mapping rules...")

                # Clear existing rules (cascades to conditions and actions)
                cur.execute("DELETE FROM map_rules")

                print(f"Inserting {len(rules)} rules...")

                for rule in rules:
                    # Insert rule record
                    cur.execute("""
                        INSERT INTO map_rules (rule_name, application_order, rule_category, problem_solved)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (
                        rule['rule_name'],
                        rule['application_order'],
                        rule['rule_category'],
                        rule['problem_solved']
                    ))

                    rule_id = cur.fetchone()[0]

                    # Insert conditions
                    for check_field, match_operator, match_value, logic_connector in rule['conditions']:
                        cur.execute("""
                            INSERT INTO map_conditions (rule_id, check_field, match_operator, match_value, logic_connector)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (rule_id, check_field, match_operator, match_value, logic_connector))

                    # Insert actions
                    for set_field, set_value in rule['actions']:
                        cur.execute("""
                            INSERT INTO map_actions (rule_id, set_field, set_value)
                            VALUES (%s, %s, %s)
                        """, (rule_id, set_field, set_value))

                    print(f"  ✓ {rule['rule_name']} (order {rule['application_order']}, {len(rule['conditions'])} conditions, {len(rule['actions'])} actions)")

                # Verify the results
                cur.execute("SELECT COUNT(*) FROM map_rules")
                rule_count = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM map_conditions")
                condition_count = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM map_actions")
                action_count = cur.fetchone()[0]

                print(f"\nDatabase updated successfully:")
                print(f"  Rules: {rule_count}")
                print(f"  Conditions: {condition_count}")
                print(f"  Actions: {action_count}")

    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """
    Main function to update mapping rules from CSV to database.
    """
    print("=" * 60)
    print("UPDATE MAPPING RULES - Configuration-Driven Classification")
    print("=" * 60)
    print(f"Reading rules from: {CSV_FILE}")
    print()

    try:
        # Load and parse CSV rules
        rules = load_csv_rules()
        print(f"Parsed {len(rules)} rules from CSV file")
        print()

        # Show summary by category
        from collections import Counter
        category_counts = Counter(rule['rule_category'] for rule in rules)

        print("Rules by category:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} rules")
        print()

        # Update database
        update_database_rules(rules)
        print()
        print("✓ Mapping rules updated successfully!")
        print("✓ New rules will apply to future transaction processing")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()