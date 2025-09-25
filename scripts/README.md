# Scripts Directory Documentation

**Created:** 09/23/25 7:16PM
**Updated:** 09/23/25 7:30PM
**Updated:** 09/25/25 10:35PM - Note: Most mapping scripts are DEPRECATED. New system uses 3-table rules (map_rules/map_conditions/map_actions)
**Purpose:** Comprehensive guide to utility scripts for data management and mapping system maintenance

## ⚠️ IMPORTANT: Mapping System Migration

**As of 09/25/25:** The mapping system has migrated from the `data_mappings` table to a new 3-table system:
- `map_rules` - Rule definitions with 2-level application order
- `map_conditions` - IF logic (check_field, match_operator, match_value)
- `map_actions` - THEN logic (set_field, set_value)

**Current Status:**
- ✅ **Active:** `extract_pdf_pages.py` - Still useful for PDF processing
- ❌ **Deprecated:** `load_data_mappings.py`, `fix_transaction_types.py`, `populate_sec_class.py`
- 🔄 **New System:** Rules managed via `/config/mapping-rules.csv` and `update_mapping_rules.py`

**For Current Rule Management:** See `/docs/Design/Database/CLAUDE.md` for the simplified 2-level rule structure.

## Overview

This directory contains utility scripts for managing the financial data system, particularly focusing on the configuration-driven mapping system and data maintenance operations. These scripts work together to maintain data consistency and proper classification of financial transactions.

## Mapping System Scripts

### `load_data_mappings.py`
**Purpose:** Loads all mapping configurations from JSON files into the database `data_mappings` table for dynamic transaction classification.

**Usage:**
```bash
cd /Users/richkernan/Projects/Finances/scripts
python3 load_data_mappings.py
```

**What it does:**
- Reads `/config/data-mappings.json` configuration file
- Clears existing mappings from `data_mappings` table
- Loads all mapping types (transaction_descriptions, activity_sections, security_patterns, security_classification)
- Validates successful load with count summaries
- Tests key mappings to verify functionality

**Example Output:**
```
Loading data mappings into database...
Clearing existing mappings...

Loading transaction_descriptions mappings...
  Muni Exempt Int → income/tax-exempt
  Dividend Received → income/dividend
  ...

✅ Successfully loaded 47 mappings into database

Mapping counts by type:
  activity_sections: 8
  security_classification: 4
  security_patterns: 4
  transaction_descriptions: 31
```

**Prerequisites:**
- Local Supabase database running on localhost:54322
- Valid `/config/data-mappings.json` file
- `data_mappings` table exists in database

**Safety Notes:**
- ⚠️ **DESTRUCTIVE**: Clears all existing mappings before reload
- Always backup database before running
- Verify configuration file syntax before execution

### `fix_transaction_types.py`
**Purpose:** Bulk correction of transaction_type and transaction_subtype fields for existing transactions using the dynamic mapping system.

**Usage:**
```bash
cd /Users/richkernan/Projects/Finances/scripts
python3 fix_transaction_types.py
```

**What it does:**
- Tests mapping system with known examples first
- Processes all existing transactions in database
- Applies cascading mapping logic:
  1. Description-based mapping (highest priority)
  2. Activity section mapping (fallback)
  3. Security pattern overrides (for subtypes)
- Updates transaction_type and transaction_subtype fields
- Provides detailed correction summary

**Mapping Logic:**
```
Priority Order:
1. transaction_descriptions: "Muni Exempt Int" → income/tax-exempt
2. activity_sections: "dividends_interest_income" → income/null
3. security_patterns: "CLOSING TRANSACTION" → option/closing
```

**Example Output:**
```
Testing mapping system:
  dividends_interest_income + 'Muni Exempt Int' → income/tax-exempt
  securities_bought_sold + 'You Bought' (with CLOSING TRANSACTION) → trade/closing

Updated 47 transactions

Corrections made:
dividends_interest_income/null → income/tax-exempt:
  • Muni Exempt Int (from dividends_interest_income)
  • Interest Earned (from dividends_interest_income)
```

**Prerequisites:**
- `load_data_mappings.py` must be run first to populate mappings
- Existing transactions in `transactions` table
- Database connection to localhost:54322

**Safety Notes:**
- Non-destructive: Only updates type/subtype fields
- Provides preview with test cases before making changes
- All changes committed in single transaction (atomic)

### `populate_sec_class.py`
**Purpose:** Adds security classification (call, put, etc.) to transactions based on security_name pattern matching.

**Usage:**
```bash
cd /Users/richkernan/Projects/Finances/scripts
python3 populate_sec_class.py
```

**What it does:**
- Scans all transactions with non-null security_name fields
- Applies pattern matching from `security_classification` mappings
- Updates `sec_class` field with appropriate values
- Handles options classification:
  - "CALL (" → sec_class = 'call'
  - "PUT (" → sec_class = 'put'
  - "ASSIGNED CALLS" → sec_class = 'call'
  - "ASSIGNED PUTS" → sec_class = 'put'

**Pattern Matching Logic:**
```
Ordered by pattern length (longest first for specificity):
1. "ASSIGNED PUTS" (12 chars) → 'put'
2. "ASSIGNED CALLS" (13 chars) → 'call'
3. "PUT (" (4 chars) → 'put'
4. "CALL (" (5 chars) → 'call'
```

**Example Output:**
```
Testing security classification:
  'CALL (COIN) COINBASE GLOBAL INC AUG 15 25...' → call
  'PUT (CRWV) COREWEAVE INC COM CL AUG 29 25...' → put
  'TESLA INC COM ASSIGNED PUTS...' → put
  'AT&T INC COM USD1...' → None

✅ Updated 23 transactions with sec_class values

Classifications applied:
CALL:
  • CALL (COIN) COINBASE GLOBAL INC AUG 15 25 $300...
  • CALL (NVDA) NVIDIA CORP AUG 15 25 $140 (100 SHS)...

PUT:
  • PUT (CRWV) COREWEAVE INC COM CL AUG 29 25 $100...
  • TESLA INC COM ASSIGNED PUTS...
```

**Prerequisites:**
- `load_data_mappings.py` must be run first
- Transactions with security_name data
- `sec_class` column exists in transactions table

**Safety Notes:**
- Only updates transactions where classification is found AND different from current value
- Does not overwrite existing correct classifications
- Non-destructive to other transaction data

## Data Management Scripts

### `extract_pdf_pages.py`
**Purpose:** Utility for extracting specific pages from PDF files, supporting both full PDF extraction and text-only extraction for token efficiency.

**Usage:**
```bash
cd /Users/richkernan/Projects/Finances/scripts

# Extract full PDF pages
python3 extract_pdf_pages.py input.pdf output.pdf start_page [end_page]

# Extract text only (token efficient)
python3 extract_pdf_pages.py input.pdf output.txt start_page [end_page] --text
```

**Examples:**
```bash
# Extract first page as PDF
python3 extract_pdf_pages.py statement.pdf first_page.pdf 1

# Extract pages 1-3 as PDF
python3 extract_pdf_pages.py statement.pdf first_three.pdf 1 3

# Extract pages 1-2 as text file (for Claude reading)
python3 extract_pdf_pages.py statement.pdf first_two.txt 1 2 --text
```

**Output for text extraction:**
```
=== PAGE 1 ===
[Extracted text content from page 1]

=== PAGE 2 ===
[Extracted text content from page 2]
```

**Prerequisites:**
- PyPDF2 library installed (`pip install PyPDF2`)
- Valid PDF input file

**Use Cases:**
- Reducing Claude token usage when analyzing large PDFs
- Extracting summary pages from statements
- Isolating specific transaction sections

## Common Workflows

### Initial System Setup
Complete setup sequence for new database:

```bash
cd /Users/richkernan/Projects/Finances/scripts

# 1. Load mapping configurations into database
python3 load_data_mappings.py

# 2. Fix existing transaction classifications
python3 fix_transaction_types.py

# 3. Populate security classifications
python3 populate_sec_class.py
```

### Adding New Transaction Types
When new transaction patterns are discovered:

1. **Update configuration:**
   ```bash
   # Edit the mapping configuration
   code /Users/richkernan/Projects/Finances/config/data-mappings.json
   ```

2. **Reload mappings:**
   ```bash
   python3 load_data_mappings.py
   ```

3. **Apply to existing data:**
   ```bash
   python3 fix_transaction_types.py
   ```

### Bulk Data Corrections
After adding new mapping rules:

```bash
# Full correction sequence
python3 load_data_mappings.py     # Reload updated mappings
python3 fix_transaction_types.py  # Fix transaction types
python3 populate_sec_class.py     # Update security classifications
```

### Testing and Validation
Verify mapping system functionality:

```bash
# Each script includes test functionality
python3 load_data_mappings.py    # Tests key mappings after load
python3 fix_transaction_types.py # Tests mapping logic before applying
python3 populate_sec_class.py    # Tests classification patterns
```

**Database verification queries:**
```sql
-- Check mapping distribution
SELECT mapping_type, COUNT(*) FROM data_mappings GROUP BY mapping_type;

-- Verify transaction type corrections
SELECT transaction_type, transaction_subtype, COUNT(*)
FROM transactions
GROUP BY transaction_type, transaction_subtype
ORDER BY count DESC;

-- Check security classifications
SELECT sec_class, COUNT(*) FROM transactions
WHERE sec_class IS NOT NULL
GROUP BY sec_class;
```

## Script Usage Examples

### PDF Processing for Document Analysis
```bash
# Extract account summary page for Claude analysis
python3 extract_pdf_pages.py "/path/to/statement.pdf" "summary.txt" 1 --text

# Extract activity pages 3-8 for transaction processing
python3 extract_pdf_pages.py "/path/to/statement.pdf" "activities.txt" 3 8 --text
```

### Mapping System Maintenance
```bash
# Weekly mapping update routine
echo "Updating mapping system..."
python3 load_data_mappings.py

echo "Correcting transaction types..."
python3 fix_transaction_types.py

echo "Updating security classifications..."
python3 populate_sec_class.py

echo "Mapping system update complete!"
```

### Development Testing
```bash
# Test individual mapping lookups
python3 -c "
from load_data_mappings import test_mapping_lookup
test_mapping_lookup('transaction_descriptions', 'Muni Exempt Int')
test_mapping_lookup('security_classification', 'PUT (')
"
```

## Troubleshooting

### Common Issues and Solutions

**Database Connection Errors:**
```
Error: psycopg2.OperationalError: could not connect to server
```
**Solution:** Verify Supabase is running on localhost:54322
```bash
# Check if Supabase is running
docker ps | grep supabase

# Start Supabase if needed
cd /Users/richkernan/Projects/Finances
supabase start
```

**Missing Mappings Configuration:**
```
Error: FileNotFoundError: config/data-mappings.json
```
**Solution:** Ensure configuration file exists with valid JSON structure
```bash
# Verify file exists
ls -la /Users/richkernan/Projects/Finances/config/data-mappings.json

# Validate JSON syntax
python3 -m json.tool /Users/richkernan/Projects/Finances/config/data-mappings.json
```

**Empty Tables:**
```
Error: No mappings found / No transactions to process
```
**Solution:**
- For mappings: Run `load_data_mappings.py` first
- For transactions: Ensure data has been loaded into transactions table
- Check database schema migration status

**Permission Errors:**
```
Error: Permission denied when writing output files
```
**Solution:** Ensure write permissions to output directory
```bash
# Check/fix permissions
chmod 755 /Users/richkernan/Projects/Finances/scripts/
chmod +x /Users/richkernan/Projects/Finances/scripts/*.py
```

**PyPDF2 Import Errors:**
```
ModuleNotFoundError: No module named 'PyPDF2'
```
**Solution:** Install required dependency
```bash
pip3 install PyPDF2
```

### Database Schema Issues
If scripts fail due to missing tables/columns:

```sql
-- Verify required tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('data_mappings', 'transactions');

-- Check data_mappings structure
\d data_mappings

-- Check transactions structure
\d transactions
```

### Data Validation
After running scripts, verify results:

```sql
-- Check for unmapped transactions
SELECT DISTINCT transaction_type, transaction_subtype
FROM transactions
WHERE transaction_type NOT IN (
    SELECT DISTINCT target_type FROM data_mappings
)
LIMIT 10;

-- Find transactions without security classification
SELECT COUNT(*) FROM transactions
WHERE security_name IS NOT NULL
AND sec_class IS NULL;
```

### Script Dependencies
If scripts fail, ensure proper execution order:

1. **load_data_mappings.py** (must run first)
2. **fix_transaction_types.py** (requires mappings)
3. **populate_sec_class.py** (requires mappings)
4. **extract_pdf_pages.py** (independent)

### Performance Considerations
For large datasets:
- Scripts process transactions in batches
- Consider running during off-peak hours
- Monitor disk space during PDF extraction
- Database transactions are atomic but may be slow for large updates

---

*These scripts are designed for reliability and auditability of financial data operations. Always backup your database before running destructive operations like `load_data_mappings.py`.*