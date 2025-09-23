"""
Configuration Module for Database Loader

Created: 09/23/25 11:05AM
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
    mappings_path = Path(__file__).parent.parent.parent / "config" / "database-account-mappings.json"
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