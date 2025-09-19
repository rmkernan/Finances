# Validate Extraction Command

**Created:** 09/19/25 1:42PM ET
**Updated:** 09/19/25 1:42PM ET - Focused on completeness validation rather than business logic
**Purpose:** Quality check extraction files for completeness before database loading
**Usage:** Run after extraction to ensure compatibility with database schema

## Command: `/validate [extraction_file]`

### What This Validates

Quality checks to ensure the extraction meets specifications and database requirements.

### 1. JSON Structure Validation

```python
import json
import sys
from datetime import datetime

# Load and validate JSON structure
with open(extraction_file) as f:
    data = json.load(f)
```

Check required top-level keys:
- `extraction_session` - Metadata about extraction
- `document_info` - Document identification
- `accounts` - Array of account data

### 2. Required Field Validation

#### Extraction Session Requirements
- [ ] `timestamp` - ISO-8601 format
- [ ] `source_file` - Original filename
- [ ] `file_hash` - MD5 hash (32 chars)
- [ ] `document_pages` - Integer > 0
- [ ] `extractor` - Should be "claude"

#### Document Info Requirements
- [ ] `institution` - Matches known institutions
- [ ] `document_type` - Valid type (statement/1099/etc)
- [ ] `period.start` - Valid date YYYY-MM-DD
- [ ] `period.end` - Valid date YYYY-MM-DD
- [ ] `portfolio_total_value` - Numeric value

#### Per Account Requirements
- [ ] `account_number` - Non-empty string
- [ ] `account_holder_name` - Non-empty string
- [ ] `transactions` - Array (can be empty)
- [ ] `positions` - Array (can be empty)

### 3. Data Type Validation

#### Transaction Fields
```python
for account in data['accounts']:
    for transaction in account.get('transactions', []):
        # Required fields
        assert 'settlement_date' in transaction  # YYYY-MM-DD
        assert 'amount' in transaction  # Numeric
        assert 'transaction_type' in transaction  # Known type

        # Type checks
        assert isinstance(transaction.get('quantity'), (int, float, type(None)))
        assert isinstance(transaction.get('price_per_unit'), (float, type(None)))
```

Valid transaction types:
- `BUY`, `SELL`, `DIVIDEND`, `INTEREST`
- `REDEMPTION`, `REINVEST`
- `OPTION_BUY`, `OPTION_SELL`, `OPTION_EXPIRE`

#### Position Fields
```python
for position in account.get('positions', []):
    assert 'security_name' in position
    assert 'quantity' in position
    assert 'market_value' in position
    assert isinstance(position['quantity'], (int, float))
```

### 4. Completeness Validation

#### Required Transaction Fields
For each transaction, check that ALL required fields are present:
```python
REQUIRED_TRANSACTION_FIELDS = [
    'settlement_date',
    'transaction_type',
    'amount'
]

EXPECTED_TRANSACTION_FIELDS = [
    'security_name',
    'security_identifier',
    'transaction_description',
    'quantity',
    'price_per_unit',
    'fees'
]

for transaction in transactions:
    # Check required fields - MUST have these
    missing_required = [f for f in REQUIRED_TRANSACTION_FIELDS if f not in transaction]
    if missing_required:
        print(f"✗ Transaction missing required fields: {missing_required}")

    # Check expected fields - SHOULD have these (warn if missing)
    missing_expected = [f for f in EXPECTED_TRANSACTION_FIELDS if f not in transaction]
    if missing_expected:
        print(f"⚠ Transaction missing expected fields: {missing_expected}")
```

#### Required Position Fields
For each position, check completeness:
```python
REQUIRED_POSITION_FIELDS = [
    'security_name',
    'quantity',
    'market_value'
]

for position in positions:
    missing = [f for f in REQUIRED_POSITION_FIELDS if f not in position]
    if missing:
        print(f"✗ Position missing required fields: {missing}")
```

#### Date Consistency
- All dates should be in YYYY-MM-DD format
- Dates should be complete (not missing year)

#### Account Mapping
- Account endings match `/config/account-mappings.json`
- Or flag for new account labels needed

### 5. Database Compatibility Checks

#### Field Length Limits
```python
# Database column constraints
MAX_LENGTHS = {
    'account_number': 50,
    'security_name': 255,
    'description': 500,
    'security_identifier': 50
}

for field, max_len in MAX_LENGTHS.items():
    if len(value) > max_len:
        print(f"WARNING: {field} exceeds {max_len} chars")
```

#### Special Fields
- Option details: Valid JSON if present
- Bond details: Valid JSON if present
- Numeric fields: No text like "unavailable" (use null)

### 6. Output Report

```
=== EXTRACTION VALIDATION REPORT ===
File: Fid_Stmnt_2025-08_Brok+CMA_2025.09.19_13.15ET.json
Institution: Fidelity
Period: 2025-08-01 to 2025-08-31

✓ JSON Structure: Valid
✓ Required Fields: All present
✓ Data Types: Correct
✓ Transaction Types: All recognized
✓ Date Range: Consistent
✓ Amount Signs: Correct
✓ Database Compatibility: Ready

Accounts Found: 2
- Z24-527872 → Brok ✓
- Z27-375656 → CMA ✓

Transactions: 15 total
- BUY: 5
- SELL: 3
- DIVIDEND: 7

⚠ Warnings:
- None

✗ Errors:
- None

Status: READY FOR DATABASE LOADING
```

### 7. Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Missing transaction_type | Check institution guide for mapping |
| Invalid date format | Ensure YYYY-MM-DD format |
| Wrong amount signs | BUY = negative, SELL = positive |
| Text in numeric fields | Use null instead of "unavailable" |
| Account not mapped | Update account-mappings.json |

### 8. Integration Points

After successful validation:
1. Proceed to `/load-extraction` command
2. Or fix issues and re-validate
3. Update institution guide if patterns missing

### Usage Examples

**Basic validation:**
```bash
/validate Fid_Stmnt_2025-08_Brok+CMA_2025.09.19_13.15ET.json
```

**With verbose output:**
```bash
/validate --verbose [filename]  # Show all checks
```

**Fix common issues:**
```bash
/validate --auto-fix [filename]  # Attempt automatic corrections
```

## Success Criteria

Extraction is valid when:
- [ ] All required fields present
- [ ] Data types correct
- [ ] Business logic consistent
- [ ] Database constraints met
- [ ] No critical errors

Only proceed with database loading after validation passes!