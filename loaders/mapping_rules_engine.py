#!/usr/bin/env python3
"""
Mapping Rules Engine - Transaction Classification System

Created: 09/24/25 3:21PM
Updated: 09/25/25 5:05PM - Added Custom Rules category to rule query filter, added activities.transaction field support
Purpose: Reusable rule evaluation engine for transaction/position classification

This module provides rule-based classification for financial transactions and positions
using the three-table mapping system (map_rules, map_conditions, map_actions).

Key Features:
- Evaluates complex conditions with AND/OR logic
- Supports multiple operators: contains, equals, starts_with
- Handles field name translation (activities.* to database columns)
- Rule priority system via application_order
- Reusable by loader, UI application, and batch processors

Usage:
    from mapping_rules_engine import apply_mapping_rules, reapply_rules_to_transactions

    # During loading
    field_updates = apply_mapping_rules(transaction_data, conn)

    # After rule changes (UI "Apply Rules" button)
    updated_count = reapply_rules_to_transactions(conn)
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def get_field_value(field_name, transaction_data):
    """Extract field value from transaction data using activities.* notation"""
    field_mapping = {
        'activities.description': transaction_data.get('description', ''),
        'activities.transaction': transaction_data.get('transaction', ''),
        'activities.section': transaction_data.get('section', ''),
        'activities.source': transaction_data.get('source', ''),
        'activities.security': transaction_data.get('sec_description', ''),
        'activities.amount': str(transaction_data.get('amount', '')),
        'activities.quantity': str(transaction_data.get('quantity', '')),
        # Add positions support for future use
        'positions.sec_name': transaction_data.get('sec_name', ''),
        'positions.sec_type': transaction_data.get('sec_type', ''),
        'positions.market_value': str(transaction_data.get('market_value', '')),
    }
    return field_mapping.get(field_name, '')


def evaluate_condition(condition, transaction_data):
    """Evaluate a single condition against transaction data

    Updated: 09/24/25 3:57PM - Added null-safe field value handling to prevent TypeError on None values
    """
    field_value = get_field_value(condition['check_field'], transaction_data)
    match_value = condition['match_value']
    operator = condition['match_operator']

    # Handle null/None field values safely
    if field_value is None:
        return False

    if operator == 'contains':
        return match_value in str(field_value)
    elif operator == 'equals' or operator == 'is':
        return str(field_value) == match_value
    elif operator == 'starts_with':
        return str(field_value).startswith(match_value)
    else:
        print(f"Warning: Unknown operator '{operator}' in rule condition")
        return False


def evaluate_rule_conditions(rule_id, transaction_data, conn):
    """Evaluate all conditions for a rule (handles AND/OR logic)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT check_field, match_operator, match_value, logic_connector
        FROM map_conditions
        WHERE rule_id = %s
        ORDER BY id
    """, (rule_id,))

    conditions = cur.fetchall()
    if not conditions:
        return True  # No conditions = always match

    # Start with first condition
    result = evaluate_condition(conditions[0], transaction_data)

    # Apply remaining conditions with their connectors
    for i, condition in enumerate(conditions[1:], 1):
        condition_result = evaluate_condition(condition, transaction_data)
        # Use the connector from the previous condition to connect to this one
        connector = conditions[i-1].get('logic_connector', 'AND')

        if connector == 'AND':
            result = result and condition_result
        elif connector == 'OR':
            result = result or condition_result

    return result


def apply_rule_actions(rule_id, conn):
    """Get actions to apply for a matched rule"""
    cur = conn.cursor()
    cur.execute("""
        SELECT set_field, set_value
        FROM map_actions
        WHERE rule_id = %s
        ORDER BY id
    """, (rule_id,))

    return cur.fetchall()


def translate_field_to_database_column(field_name):
    """Translate activities.* field names to database column names"""
    translation_map = {
        # Transaction fields
        'activities.transactiontype': 'transaction_type',
        'activities.transactionsubtype': 'transaction_subtype',
        'activities.sec_class': 'sec_class',
        'activities.type': 'transaction_type',  # Legacy support
        'activities.subtype': 'transaction_subtype',  # Legacy support

        # Position fields (for future use)
        'positions.security_type': 'security_type',
        'positions.sec_class': 'sec_class',
    }
    return translation_map.get(field_name, field_name)


def apply_mapping_rules(transaction_data, conn):
    """
    Apply all mapping rules to transaction data and return field updates

    Args:
        transaction_data (dict): Transaction/position data from JSON
        conn: Database connection

    Returns:
        dict: Field updates to apply {column_name: value}
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT id, rule_name
        FROM map_rules
        ORDER BY application_order
    """)

    rules = cur.fetchall()
    field_updates = {}

    for rule in rules:
        if evaluate_rule_conditions(rule['id'], transaction_data, conn):
            actions = apply_rule_actions(rule['id'], conn)

            for action in actions:
                db_field = translate_field_to_database_column(action['set_field'])
                field_updates[db_field] = action['set_value']

            # Log rule application for debugging
            print(f"Applied rule: {rule['rule_name']}")

    return field_updates


def reapply_rules_to_transactions(conn, document_id=None):
    """
    Reapply all mapping rules to existing transactions

    Args:
        conn: Database connection
        document_id (optional): Limit to specific document

    Returns:
        int: Number of transactions updated
    """
    cur = conn.cursor()

    # Build query conditions
    where_clause = "WHERE t.is_archived = FALSE"
    params = []

    if document_id:
        where_clause += " AND t.document_id = %s"
        params.append(document_id)

    # Get all non-archived transactions with their source data
    cur.execute(f"""
        SELECT
            t.id,
            t.description,
            t.source,
            t.security_name as sec_description,
            t.amount,
            t.quantity
        FROM transactions t
        {where_clause}
    """, params)

    transactions = cur.fetchall()
    updated_count = 0

    for transaction in transactions:
        # Reconstruct transaction data for rule evaluation
        transaction_data = {
            'description': transaction['description'] or '',
            'source': transaction['source'] or '',
            'sec_description': transaction['sec_description'] or '',
            'amount': transaction['amount'] or 0,
            'quantity': transaction['quantity'] or 0,
            'section': transaction['source'],  # Source contains section name
        }

        # Apply rules and get field updates
        field_updates = apply_mapping_rules(transaction_data, conn)

        if field_updates:
            # Build UPDATE query dynamically
            set_clauses = []
            update_params = []

            for field, value in field_updates.items():
                set_clauses.append(f"{field} = %s")
                update_params.append(value)

            if set_clauses:
                update_params.append(transaction['id'])
                update_query = f"""
                    UPDATE transactions
                    SET {', '.join(set_clauses)}, updated_at = NOW()
                    WHERE id = %s
                """
                cur.execute(update_query, update_params)
                updated_count += 1

    conn.commit()
    return updated_count


def reapply_rules_to_positions(conn, document_id=None):
    """
    Reapply all mapping rules to existing positions

    Args:
        conn: Database connection
        document_id (optional): Limit to specific document

    Returns:
        int: Number of positions updated
    """
    # Similar to reapply_rules_to_transactions but for positions table
    # Implementation placeholder for when position rules are added
    return 0


if __name__ == "__main__":
    """Test rule engine functionality"""
    import os
    from urllib.parse import urlparse

    # Database connection for testing
    DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:54322/postgres')

    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

        # Test sample transaction data
        sample_transaction = {
            'description': 'MUNI EXEMPT INT as of Sep-01-2024 SOUTH DAKOTA ST HEALTH',
            'section': 'dividends_interest_income',
            'source': 'dividends_interest_income',
            'sec_description': '',
            'amount': '1000.00',
            'quantity': '0'
        }

        print("Testing rule engine with sample transaction...")
        field_updates = apply_mapping_rules(sample_transaction, conn)

        print(f"Field updates: {field_updates}")

        # Test reapplication
        print("\nTesting rule reapplication...")
        updated_count = reapply_rules_to_transactions(conn)
        print(f"Updated {updated_count} transactions")

        conn.close()

    except Exception as e:
        print(f"Error testing rule engine: {e}")