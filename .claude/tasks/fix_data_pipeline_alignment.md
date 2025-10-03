# Data Pipeline Alignment Fix Plan

**Created:** 09/29/25 9:15PM ET
**Purpose:** Sequenced action plan to fix critical blockers preventing database loading
**Source:** data_pipeline_alignment_report_2025.09.29_21.08EDT.md

## 🎯 Executive Summary

**12 critical blockers** must be fixed before database loading can succeed. These fixes must be executed in a specific order due to dependencies.

**Total Time Estimate:** 3-4 hours
- Phase 1 (Database): 45 minutes
- Phase 2 (Documentation): 15 minutes
- Phase 3 (Loader Implementation): 2-3 hours

---

## 📋 PHASE 1: DATABASE SCHEMA FIXES (MUST DO FIRST)

**Duration:** 45 minutes
**Why First:** Database constraints will reject data if not fixed. All other work is blocked until this is done.

### Fix 1.1: Increase Numeric Precision (CRITICAL)

**Problem:** Current NUMERIC(8,2) columns can only hold values up to $999,999.99. Actual data has values over $2.7 million.

**Impact:** Database will throw numeric overflow errors on insert.

**Files to Modify:**
1. `/docs/Design/Database/schema.md` - Update documentation
2. Create and execute migration SQL script

**Specific Changes:**

```sql
-- Migration: Increase numeric precision for financial data
-- File: /migrations/002_increase_numeric_precision.sql

BEGIN;

-- Transactions table
ALTER TABLE transactions
  ALTER COLUMN quantity TYPE NUMERIC(15,6),
  ALTER COLUMN amount TYPE NUMERIC(15,2),
  ALTER COLUMN cost_basis TYPE NUMERIC(15,2),
  ALTER COLUMN fees TYPE NUMERIC(8,2);

-- Positions table
ALTER TABLE positions
  ALTER COLUMN end_market_value TYPE NUMERIC(15,2),
  ALTER COLUMN beg_market_value TYPE NUMERIC(15,2),
  ALTER COLUMN cost_basis TYPE NUMERIC(15,2),
  ALTER COLUMN unrealized_gain_loss TYPE NUMERIC(15,2),
  ALTER COLUMN estimated_ann_inc TYPE NUMERIC(15,2);

COMMIT;
```

**Documentation Changes in schema.md:**
- Line 513: `quantity NUMERIC(8,6)` → `quantity NUMERIC(15,6)`
- Line 509: `amount NUMERIC(8,2)` → `amount NUMERIC(15,2)`
- Line 515: `cost_basis NUMERIC(8,2)` → `cost_basis NUMERIC(15,2)`
- Line 516: `fees NUMERIC(4,2)` → `fees NUMERIC(8,2)`
- Line 684: `end_market_value NUMERIC(8,2)` → `end_market_value NUMERIC(15,2)`
- Line 682: `beg_market_value NUMERIC(8,2)` → `beg_market_value NUMERIC(15,2)`
- Line 687: `cost_basis NUMERIC(8,2)` → `cost_basis NUMERIC(15,2)`
- Line 688: `unrealized_gain_loss NUMERIC(8,2)` → `unrealized_gain_loss NUMERIC(15,2)`
- Line 690: `estimated_ann_inc NUMERIC(8,2)` → `estimated_ann_inc NUMERIC(15,2)`

**Validation:**
```bash
# After running migration, verify schema:
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "\d+ transactions" | grep -E "quantity|amount|cost_basis|fees"

PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "\d+ positions" | grep -E "market_value|cost_basis|gain_loss|estimated_ann_inc"
```

---

## 📋 PHASE 2: DOCUMENTATION FIXES (DO SECOND)

**Duration:** 15 minutes
**Why Second:** Ensures loader developers have correct field names before implementation.

### Fix 2.1: Correct JSON Spec Field Name (HIGH PRIORITY)

**Problem:** JSON spec says `sec_cusip` but actual JSON output uses `cusip`.

**Impact:** Loader developers will code to wrong field name.

**File:** `/config/institution-guides/JSON_Stmnt_Fid_Positions.md`

**Change:**
- Line 676: `"sec_cusip": "string"` → `"cusip": "string"`

### Fix 2.2: Document Source Field Derivation (MEDIUM PRIORITY)

**Problem:** JSON spec doesn't document how `source` field should be derived.

**Impact:** Loader developers won't know how to populate required database column.

**File:** `/config/institution-guides/JSON_Stmnt_Fid_Activities.md`

**Add Section (after line ~50):**
```markdown
### Source Field Derivation

The database requires a `source` field (NOT NULL) to identify which statement section the transaction came from. This field is NOT present in the JSON but must be derived by the loader based on which array the transaction appears in:

**Mapping Table:**
| JSON Array Name | Database source Value |
|-----------------|----------------------|
| securities_bought_sold | 'sec_bot_sold' |
| dividends_interest_income | 'div_int_income' |
| short_activity | 'short_activity' |
| other_activity_in | 'other_activity_in' |
| other_activity_out | 'other_activity_out' |
| deposits | 'deposits' |
| withdrawals | 'withdrawals' |
| exchanges_in | 'exchanges_in' |
| exchanges_out | 'exchanges_out' |
| fees_charges | 'fees_charges' |
| core_fund_activity | 'core_fund' |
| trades_pending_settlement | 'trades_pending' |

**Loader Implementation:** When iterating through `accounts[i].securities_bought_sold[j]`, set `source = 'sec_bot_sold'` for all transactions in that array.
```

### Fix 2.3: Document Section Total Fields (MEDIUM PRIORITY)

**Problem:** Section totals appear in actual JSON but aren't in spec.

**Impact:** Minor - totals are for validation only, not loaded to database.

**File:** `/config/institution-guides/JSON_Stmnt_Fid_Activities.md`

**Add to field definitions (around line ~120):**
```markdown
#### Section Total Fields (Account Level)

Each activity section may include a section total field for reconciliation:

- `total_sec_bot`: Total securities bought (negative amount)
- `total_sec_sold`: Total securities sold (positive amount)
- `net_sec_act`: Net securities activity (bought + sold)
- `total_div_int_inc`: Total dividends and interest
- `total_short_act`: Total short activity (usually nets to $0.00)
- `total_other_in`: Total other activity in
- `total_dep`: Total deposits
- `total_withdrwls`: Total withdrawals
- `total_exchanges_in`: Total exchanges in
- `total_exchanges_out`: Total exchanges out
- `total_core`: Total core fund activity

**Type:** string (numeric value as string)
**Purpose:** Statement reconciliation and validation
**Database Storage:** Not typically stored in transactions table (optional: could use section_total column with source to identify)
```

---

## 📋 PHASE 3: LOADER IMPLEMENTATION (DO THIRD)

**Duration:** 2-3 hours
**Why Third:** Requires database schema and documentation to be finalized first.

### Fix 3.1: Implement Field Name Mapping (CRITICAL)

**Problem:** JSON field names don't match database column names.

**Implementation:** Create field mapping dictionary in loader code.

```python
# Field name mappings: JSON → Database
ACTIVITIES_FIELD_MAP = {
    'settlement_date': 'sett_date',
    'sec_description': 'security_name',
    'transaction_cost': 'fees',
    'reference': 'reference_number',
    'ytd_payments': 'ytd_amount',
    'post_date': 'sett_date',
    'date': 'sett_date',
}

POSITIONS_FIELD_MAP = {
    'sec_description': 'sec_name',
    'price_per_unit': 'price',
}

def map_field_name(json_field, data_type):
    """Map JSON field name to database column name."""
    field_map = ACTIVITIES_FIELD_MAP if data_type == 'activities' else POSITIONS_FIELD_MAP
    return field_map.get(json_field, json_field)  # Return original if no mapping
```

### Fix 3.2: Implement Currency String Parser (CRITICAL)

**Problem:** JSON has `"$738,691.27"` but database expects numeric `738691.27`.

**Implementation:**

```python
import re
from decimal import Decimal

def parse_currency(value):
    """
    Parse currency string to Decimal, handling $, commas, and special values.

    Examples:
        "$738,691.27" → Decimal("738691.27")
        "758.61" → Decimal("758.61")
        "-$2,091.38" → Decimal("-2091.38")
        "unavailable" → None
        null → None
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    value_str = str(value).strip()

    # Handle special values
    if value_str.lower() in ('unavailable', 'not applicable', '-', 'n/a', ''):
        return None

    # Strip $ sign, commas, and parentheses
    cleaned = value_str.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')

    try:
        return Decimal(cleaned)
    except:
        raise ValueError(f"Cannot parse currency value: {value}")
```

### Fix 3.3: Implement Date Parser (CRITICAL)

**Problem:** JSON has mix of `"2025-04-30"` (ISO) and `"04/15/34"` (MM/DD/YY) formats.

**Implementation:**

```python
from datetime import datetime

def parse_date(value):
    """
    Parse date string handling multiple formats.

    Formats accepted:
        - ISO 8601: "2025-04-30"
        - MM/DD/YY: "04/15/34" (assumes 50-year window)
        - MM/DD/YYYY: "04/15/2034"

    Returns: datetime.date object or None
    """
    if value is None or value == '':
        return None

    value_str = str(value).strip()

    # Try ISO 8601 first (most common)
    try:
        return datetime.strptime(value_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    # Try MM/DD/YYYY
    try:
        return datetime.strptime(value_str, '%m/%d/%Y').date()
    except ValueError:
        pass

    # Try MM/DD/YY with century logic
    try:
        dt = datetime.strptime(value_str, '%m/%d/%y')
        # 50-year window: 00-49 → 2000-2049, 50-99 → 1950-1999
        if dt.year > 2050:
            dt = dt.replace(year=dt.year - 100)
        return dt.date()
    except ValueError:
        pass

    raise ValueError(f"Cannot parse date value: {value}")
```

### Fix 3.4: Implement Symbol/CUSIP Merger (CRITICAL)

**Problem:** JSON has separate `sec_symbol` and `cusip` fields, database has single `symbol_cusip` column.

**Implementation:**

```python
def merge_symbol_cusip(sec_symbol, cusip):
    """
    Merge symbol and CUSIP into single identifier.

    Strategy: Use whichever is non-null. Securities have one OR the other, never both.

    Returns: string or None
    """
    # Prefer symbol for stocks/ETFs
    if sec_symbol and sec_symbol.strip():
        return sec_symbol.strip()

    # Fall back to CUSIP for bonds/options
    if cusip and cusip.strip():
        return cusip.strip()

    return None
```

### Fix 3.5: Implement Source Field Derivation (CRITICAL)

**Problem:** Database requires `source` column but JSON doesn't have it.

**Implementation:**

```python
# Source value mapping (from Fix 2.2)
SOURCE_MAP = {
    'securities_bought_sold': 'sec_bot_sold',
    'dividends_interest_income': 'div_int_income',
    'short_activity': 'short_activity',
    'other_activity_in': 'other_activity_in',
    'other_activity_out': 'other_activity_out',
    'deposits': 'deposits',
    'withdrawals': 'withdrawals',
    'exchanges_in': 'exchanges_in',
    'exchanges_out': 'exchanges_out',
    'fees_charges': 'fees_charges',
    'core_fund_activity': 'core_fund',
    'trades_pending_settlement': 'trades_pending',
}

def derive_source(section_name):
    """Derive database source value from JSON section name."""
    source = SOURCE_MAP.get(section_name)
    if source is None:
        raise ValueError(f"Unknown activity section: {section_name}")
    return source
```

### Fix 3.6: Implement Foreign Key Resolution (CRITICAL)

**Problem:** Database requires `account_id`, `entity_id`, `document_id` (UUIDs) but JSON only has `account_number` (string).

**Implementation:**

```python
def resolve_account_id(conn, account_number):
    """
    Lookup account_id UUID from account_number.

    Raises: ValueError if account not found
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM accounts WHERE account_number = %s",
        (account_number,)
    )
    row = cursor.fetchone()

    if row is None:
        raise ValueError(f"Account not found: {account_number}")

    return row[0]  # UUID

def resolve_entity_id(conn, account_id):
    """
    Lookup entity_id from account_id.

    Raises: ValueError if entity not found
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT entity_id FROM accounts WHERE id = %s",
        (account_id,)
    )
    row = cursor.fetchone()

    if row is None or row[0] is None:
        raise ValueError(f"Entity not found for account: {account_id}")

    return row[0]  # UUID
```

### Fix 3.7: Implement Transaction Type Classification (HIGH PRIORITY)

**Problem:** Database requires `transaction_type` (NOT NULL) but JSON doesn't have it.

**Implementation:**

```python
def classify_transaction(transaction_data):
    """
    Apply mapping rules to classify transaction.

    This is a simplified version - actual implementation should use
    the full mapping rules system from map_rules/map_conditions/map_actions tables.

    Returns: transaction_type string (e.g., 'dividend', 'option_trade', 'stock_trade')
    """
    # Temporary simple classification
    desc = transaction_data.get('desc', '').lower()
    security_name = transaction_data.get('security_name', '').lower()
    source = transaction_data.get('source', '')

    # This should be replaced with actual mapping rules query
    if 'put' in security_name or 'call' in security_name:
        return 'option_trade'
    elif 'dividend' in desc:
        return 'dividend'
    elif 'interest' in desc:
        return 'interest'
    elif 'deposit' in source:
        return 'deposit'
    elif 'withdrawal' in source:
        return 'withdrawal'
    elif 'bought' in desc or 'sold' in desc:
        return 'stock_trade'
    else:
        return 'unknown'  # Flag for manual review
```

### Fix 3.8: Implement Pre-Load Validation (HIGH PRIORITY)

**Problem:** Better to validate entire JSON before attempting database insert.

**Implementation:**

```python
def validate_json_before_load(json_data, data_type):
    """
    Validate JSON structure and values before attempting database load.

    Returns: (is_valid, error_list)
    """
    errors = []

    # Check required top-level structure
    if 'accounts' not in json_data:
        errors.append("Missing 'accounts' array")
        return False, errors

    for i, account in enumerate(json_data['accounts']):
        account_num = account.get('account_number', f'account[{i}]')

        # Validate required fields
        if 'account_number' not in account:
            errors.append(f"Account {i}: Missing account_number")

        # Validate numeric ranges
        if data_type == 'activities':
            for section_name in ['securities_bought_sold', 'dividends_interest_income']:
                if section_name not in account:
                    continue

                for j, txn in enumerate(account[section_name]):
                    # Check amount fits in NUMERIC(15,2)
                    if 'amount' in txn:
                        try:
                            amount = parse_currency(txn['amount'])
                            if amount and abs(amount) >= Decimal('10000000000000'):  # 15 digits
                                errors.append(f"{account_num}.{section_name}[{j}]: Amount too large: {amount}")
                        except Exception as e:
                            errors.append(f"{account_num}.{section_name}[{j}]: Invalid amount: {e}")

        # Validate dates
        if data_type == 'positions':
            for k, pos in enumerate(account.get('holdings', [])):
                if 'maturity_date' in pos and pos['maturity_date']:
                    try:
                        parse_date(pos['maturity_date'])
                    except Exception as e:
                        errors.append(f"{account_num}.holdings[{k}]: Invalid maturity_date: {e}")

    return len(errors) == 0, errors
```

---

## 📋 PHASE 4: TESTING & VERIFICATION (DO LAST)

**Duration:** 30 minutes

### Test 4.1: Dry Run Validation

```bash
# Test the loader validation without actually inserting
python3 scripts/load_extractions.py \
  --file documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_activities_2025.09.29_15.45ET.json \
  --validate-only \
  --verbose
```

**Expected Output:**
- ✅ All field names mapped successfully
- ✅ All currency values parsed successfully
- ✅ All dates parsed successfully
- ✅ All foreign keys resolvable
- ✅ No numeric overflow warnings

### Test 4.2: Single Transaction Load

```bash
# Test loading just one transaction
python3 scripts/load_extractions.py \
  --file documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_activities_2025.09.29_15.45ET.json \
  --limit 1 \
  --verbose
```

**Validation Queries:**
```sql
-- Check if transaction loaded
SELECT
  sett_date,
  security_name,
  amount,
  source,
  transaction_type
FROM transactions
ORDER BY created_at DESC
LIMIT 1;

-- Verify foreign keys resolved
SELECT
  t.sett_date,
  a.account_number,
  e.entity_name,
  d.period_end
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN entities e ON t.entity_id = e.id
JOIN documents d ON t.document_id = d.id
ORDER BY t.created_at DESC
LIMIT 1;
```

### Test 4.3: Full Load

```bash
# Load all transactions from both files
python3 scripts/load_extractions.py \
  --file documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_activities_2025.09.29_15.45ET.json \
  --verbose

python3 scripts/load_extractions.py \
  --file documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_holdings_2025.09.29_15.42ET.json \
  --verbose
```

**Validation Queries:**
```sql
-- Count loaded records
SELECT
  'activities' as type,
  COUNT(*) as count,
  MIN(sett_date) as earliest,
  MAX(sett_date) as latest
FROM transactions
UNION ALL
SELECT
  'positions' as type,
  COUNT(*) as count,
  MIN(position_date) as earliest,
  MAX(position_date) as latest
FROM positions;

-- Check for classification issues
SELECT transaction_type, COUNT(*)
FROM transactions
WHERE transaction_type = 'unknown'
GROUP BY transaction_type;

-- Verify no NULL required fields
SELECT
  COUNT(*) FILTER (WHERE account_id IS NULL) as null_account_id,
  COUNT(*) FILTER (WHERE entity_id IS NULL) as null_entity_id,
  COUNT(*) FILTER (WHERE source IS NULL) as null_source,
  COUNT(*) FILTER (WHERE transaction_type IS NULL) as null_txn_type
FROM transactions;
```

---

## ✅ SUCCESS CRITERIA

Loading is successful when:
1. ✅ All 66 activities transactions loaded without errors
2. ✅ All 102 positions loaded without errors
3. ✅ No NULL values in required fields
4. ✅ All foreign keys resolved correctly
5. ✅ All numeric values within column precision limits
6. ✅ All dates parsed correctly
7. ✅ Transaction types classified (even if 'unknown')
8. ✅ Source values derived correctly for all records

---

## 🚨 ROLLBACK PLAN

If loading fails partway through:

```sql
-- Rollback transactions from this load
BEGIN;
DELETE FROM transactions WHERE document_id = '[document_uuid]';
DELETE FROM positions WHERE document_id = '[document_uuid]';
COMMIT;
```

Or restore from backup if database was backed up before loading.

---

## 📞 NEXT STEPS AFTER SUCCESSFUL LOAD

1. Run transaction classification rules to populate transaction_type = 'unknown'
2. Review classification results
3. Add new mapping rules for unclassified patterns
4. Generate financial reports to verify data integrity
5. Archive source PDFs to /documents/3processed/

---

**Total Estimated Time:** 3-4 hours
**Dependencies:** Must execute in order (Phase 1 → 2 → 3 → 4)
**Confidence Level:** HIGH - All issues identified and solutions specified