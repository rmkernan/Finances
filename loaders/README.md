# Database Loader for Financial Data

**Created:** 09/23/25 11:07AM
**Purpose:** Load extracted JSON financial data into PostgreSQL database

## Overview

This system loads JSON files extracted from financial statements into a PostgreSQL database. It follows a "lazy creation" pattern where entities, institutions, and accounts are created automatically as they're encountered in the data.

## Quick Start

### 1. Prerequisites

Ensure you have:
- PostgreSQL database running at `localhost:54322`
- Database schema migrated (see `/database-migration-plan.md`)
- Account mappings file at `/config/database-account-mappings.json`

### 2. Install Dependencies

```bash
cd loaders
pip install -r requirements.txt
```

### 3. Test the System

Run a dry-run test:
```bash
python -m src.main --dry-run test_data/sample_positions.json
```

Load actual data:
```bash
python -m src.main test_data/sample_positions.json
```

## Usage

### Load Single File
```bash
python -m src.main path/to/extraction.json
```

### Load Multiple Files
```bash
python -m src.main file1.json file2.json file3.json
```

### Dry Run (Validate Only)
```bash
python -m src.main --dry-run file.json
```

## File Structure

```
loaders/
├── src/                    # Core modules
│   ├── config.py          # Database connection and configuration
│   ├── validator.py       # JSON validation and duplicate checking
│   ├── entities.py        # Entity/Institution/Account creation
│   ├── documents.py       # Document record management
│   ├── transform.py       # Data transformation utilities
│   ├── loader.py          # Core loading logic
│   └── main.py            # Main orchestrator
├── tests/                  # Unit tests
├── config/                 # Configuration files
├── test_data/             # Sample JSON files for testing
└── README.md              # This file
```

## Supported Data Types

### Positions JSON
- Holdings data with account positions
- Security details (symbol, CUSIP, quantities, values)
- Account information and holders

### Activities JSON
- Transaction data with account activities
- Buy/sell transactions, dividends, fees
- Transaction dates and settlement information

## Features

- **Automatic Entity Creation**: Creates entities from account holder names
- **Institution Normalization**: Maps institution names to standard forms
- **Account Type Inference**: Determines account types from descriptions
- **Duplicate Prevention**: Uses MD5 hashes to prevent reloading same documents
- **Transaction Safety**: All-or-nothing loading with rollback on errors
- **Dry Run Mode**: Validate data without making changes

## Running Tests

Run all tests:
```bash
python -m unittest discover tests/
```

Run specific test:
```bash
python -m unittest tests.test_transform
```

## Configuration

Edit `/config/loader_config.json` to modify:
- Database connection settings
- Default tax year and institution
- Processing options (batch size, duplicate handling)

## Error Handling

The loader provides clear error messages for:
- Missing required JSON fields
- Database connection issues
- Data validation failures
- Duplicate document detection

All operations are atomic - if any error occurs, the entire transaction is rolled back.

## Next Steps

After successful implementation:
1. Test with real extraction files
2. Verify database population
3. Add any institution-specific handling
4. Create batch processing scripts for large datasets