# Database Loader Specification

**Created:** 09/23/25 10:35AM ET
**Updated:** 09/23/25 10:48AM ET - Added actual account mapping structure and entity/institution creation logic
**Updated:** 09/23/25 10:58AM ET - Switched to lazy creation pattern for entities/institutions discovered in source data
**Purpose:** Complete specification and research for implementing database loader scripts for positions and activities

## Architecture Decision: Single Modular Script

### Recommendation: One Script with Modular Functions

After analysis, I recommend a **single loader script** with modular functions for these reasons:

1. **Shared Infrastructure** - Both loaders need identical:
   - Database connection handling
   - MD5 hash validation
   - Account/entity resolution
   - Document record creation
   - Error handling and rollback
   - Logging framework

2. **Atomic Operations** - A single statement produces both positions AND activities, requiring coordinated loading

3. **Maintenance** - One codebase for common functions reduces duplication and bugs

4. **Usage Pattern**:
```python
# Load everything from a statement
python loader.py --file activities.json --file positions.json

# Load just positions
python loader.py --file positions.json

# Load just activities
python loader.py --file activities.json
```

---

## Core Components Required

### 1. Configuration Management

**File:** `/config/loader-config.json`
```json
{
  "database": {
    "connection_string": "postgresql://postgres:postgres@127.0.0.1:54322/postgres",
    "schema": "public",
    "timeout": 30000,
    "retry_attempts": 3
  },
  "defaults": {
    "institution_name": "Fidelity Investments",
    "tax_year": 2024,
    "processed_by": "claude"
  },
  "validation": {
    "require_hash": true,
    "require_account_exists": false,
    "auto_create_accounts": true,
    "strict_mode": false
  },
  "processing": {
    "batch_size": 500,
    "use_transactions": true,
    "rollback_on_error": true,
    "continue_on_warning": true
  },
  "logging": {
    "level": "INFO",
    "file": "/logs/loader.log",
    "console": true,
    "log_sql": false
  }
}
```

### 2. Account Resolution System

**Existing Files:**
- `/config/account-mappings.json` - Simple filename labels (for document naming)
- `/config/database-account-mappings.json` - Full database mapping structure (NEW)

**Actual Mapping Structure (database-account-mappings.json):**
```json
{
  "entities": [
    {
      "entity_name": "Individual Name",
      "entity_type": "individual|s_corp|llc",
      "tax_id": "XXX-XX-XXXX",
      "georgia_resident": true
    }
  ],
  "institutions": [
    {
      "institution_name": "Fidelity Investments",
      "institution_type": "brokerage",
      "default_entity": "entity_name_reference"
    }
  ],
  "account_mappings": {
    "fidelity": {
      "X????7872": {  // Full account number pattern
        "label": "Brok",
        "entity_name": "Entity Name Reference",
        "institution_name": "Fidelity Investments",
        "account_holder_name": "Name on Account",
        "account_type": "brokerage",
        "account_number_display": "****7872",
        "is_tax_deferred": false
      }
    }
  }
}
```

**Account Resolution Logic:**
```python
def resolve_account(account_number, institution_hint=None):
    """
    1. Try exact match on full account number
    2. Try last-4 digit match if enabled
    3. If no match and auto_create is true:
       - Create entity if needed
       - Create institution if needed
       - Create account
    4. Return account_id or raise error
    """
```

### 3. Data Transformation Rules

#### Date Handling
```python
def parse_date(date_str, year=None):
    """
    Convert various date formats to DATE object
    Input: "09/15", "09/15/2024", "09/15/24", "2024-09-15"
    Output: datetime.date(2024, 9, 15)
    """
    # If MM/DD format without year, use document's tax year
    # Handle end-of-month dates carefully (02/30 -> 02/28)
```

#### Amount Handling
```python
def parse_amount(amount_str):
    """
    Convert amount strings to Decimal
    Input: "$1,234.56", "1234.56", "(1,234.56)", "- 1,234.56"
    Output: Decimal('1234.56') or Decimal('-1234.56')
    """
    # Remove $, commas
    # Handle parentheses as negative
    # Handle minus signs
```

#### Security Type Inference
```python
SECURITY_TYPE_RULES = {
    "patterns": {
        "CASH": ["MONEY MARKET", "CASH SWEEP", "FDIC INSURED"],
        "BOND": ["BOND", "NOTE", "TREASURY", "MUNI"],
        "MUTUAL_FUND": ["FUND", "TRUST"],
        "ETF": ["ETF", "EXCHANGE TRADED"],
        "OPTION": ["CALL", "PUT", "OPTION"]
    },
    "by_cusip_length": {
        9: "standard_security",
        12: "option"
    }
}
```

#### Transaction Type Determination
```python
TRANSACTION_TYPE_MAP = {
    "DIVIDEND": ["DIV", "DIVIDEND", "ORDINARY DIVIDEND"],
    "INTEREST": ["INT", "INTEREST"],
    "BUY": ["BUY", "BOUGHT", "PURCHASE"],
    "SELL": ["SELL", "SOLD"],
    "FEE": ["FEE", "CHARGE", "EXPENSE"],
    "REINVEST": ["REINVEST", "DRIP"]
}
```

---

## Lazy Entity/Institution/Account Creation

The loader uses a "lazy creation" pattern - entities, institutions, and accounts are created on-demand as they're encountered in the data:

### Entity Creation Logic
```python
def get_or_create_entity(account_holder_name):
    """
    1. Check if entity exists by name
    2. If not exists:
       - Create with placeholder tax_id (e.g., 'PENDING-001')
       - Use defaults from config (georgia_resident=true, etc.)
       - Set entity_name = account_holder_name
       - Set entity_type = 'individual' (can be updated in UI)
    3. Return entity_id

    Note: Placeholder tax_ids will be updated through the application UI
    """
```

### Institution Creation Logic
```python
def get_or_create_institution(institution_hint, entity_id):
    """
    1. Normalize institution name using institution_defaults
       (e.g., "Fidelity" -> "Fidelity Investments")
    2. Check if institution exists for this entity
    3. If not exists:
       - Create institution with normalized name
       - Link to entity_id
       - Set type from defaults or infer
    4. Return institution_id
    """
```

### Account Creation Logic
```python
def get_or_create_account(account_number, account_data, entity_id, institution_id):
    """
    1. Check if account exists by number + institution
    2. If not exists:
       - Create account linked to entity and institution
       - Use account_type from mapping or infer
       - Set account_number_display as last 4 digits
       - Set tax flags from mapping or defaults
    3. Return account_id
    """
```

### Benefits of Lazy Creation
- **No pre-configuration needed** - Start loading data immediately
- **Self-organizing** - Database structure emerges from actual data
- **UI cleanup later** - Fix entity types, tax IDs, names in application
- **Flexible** - Handles new accounts/entities without config changes
- **Simpler config** - Just maps account numbers to owner names

## Loader Workflow Sequence

### Phase 1: Pre-flight Validation
```python
def preflight_check(json_data):
    """
    1. Validate JSON structure
    2. Check for required fields
    3. Extract MD5 hash from metadata
    4. Query database for existing hash
    5. If duplicate:
       - STOP and report
    6. Extract account numbers
    7. Resolve account numbers to database IDs
    8. If unknown accounts and auto_create is false:
       - STOP and report unmapped accounts
    """
```

### Phase 2: Document Creation
```python
def create_document_record(metadata, account_ids):
    """
    1. Extract document metadata:
       - institution_id (lookup or create)
       - tax_year
       - period_start, period_end
       - document_type ('statement')
       - file_path, file_name
       - doc_md5_hash
    2. Insert into documents table
    3. Get document_id
    4. Insert document-account links
    5. Return document_id for FK references
    """
```

### Phase 3A: Load Positions
```python
def load_positions(positions_json, document_id, account_map):
    """
    For each position:
    1. Map account_number to account_id
    2. Get entity_id from account
    3. Transform dates (expiration, maturity, call dates)
    4. Transform amounts (prices, values)
    5. Determine option_type if applicable
    6. Insert into positions table with:
       - document_id (FK)
       - account_id (FK)
       - entity_id (FK)
       - All position fields
    """
```

### Phase 3B: Load Activities
```python
def load_activities(activities_json, document_id, account_map):
    """
    For each activity:
    1. Map account_number to account_id
    2. Get entity_id from account
    3. Parse dates (transaction, settlement)
    4. Determine transaction_type from description
    5. Parse amounts, handle signs
    6. Extract security info if present
    7. Determine tax implications:
       - Is it municipal bond from GA?
       - Is dividend qualified?
    8. Insert into transactions table
    """
```

### Phase 4: Load Summary Data
```python
def load_doc_level_data(json_data, document_id, account_map):
    """
    1. Extract income summaries if present
    2. Extract realized gains/losses if present
    3. For each summary section:
       - Map account to account_id
       - Insert into doc_level_data with doc_section identifier
    """
```

### Phase 5: Post-Load Validation
```python
def validate_load(document_id):
    """
    1. Count records created
    2. Verify no orphaned records
    3. Check transaction totals if provided
    4. Log summary:
       - Document ID created
       - Number of positions loaded
       - Number of transactions loaded
       - Any warnings
    """
```

### Phase 6: Commit or Rollback
```python
def finalize_load(success, connection):
    """
    If success and no critical errors:
        - COMMIT transaction
        - Log success
        - Move source files to processed
    Else:
        - ROLLBACK transaction
        - Log failure details
        - Keep source files in staging
    """
```

---

## Error Handling Strategy

### Error Levels
1. **CRITICAL** - Stop immediately, rollback everything
   - Duplicate document (hash exists)
   - Database connection failure
   - Missing required fields

2. **ERROR** - Skip record, continue if possible
   - Invalid date format
   - Invalid amount
   - Unknown account (if not auto-creating)

3. **WARNING** - Log but continue
   - Missing optional fields
   - Unusual but valid values
   - Tax categorization uncertainty

### Logging Format
```json
{
  "timestamp": "2024-09-23T10:30:00Z",
  "level": "ERROR",
  "component": "account_resolver",
  "message": "Unknown account number",
  "context": {
    "account_number": "X99999999",
    "document_hash": "abc123...",
    "line_number": 42
  },
  "action": "skipped"
}
```

---

## Required Database Queries

### Check for Duplicate Document
```sql
SELECT id, file_name, period_start, period_end
FROM documents
WHERE doc_md5_hash = %s;
```

### Resolve Account
```sql
SELECT a.id as account_id,
       a.entity_id,
       a.account_number_display,
       e.entity_name
FROM accounts a
JOIN entities e ON a.entity_id = e.id
WHERE a.account_number = %s
  AND a.institution_id = %s
  AND a.account_status = 'active';
```

### Create Institution if Needed
```sql
WITH ins AS (
  SELECT id FROM institutions
  WHERE institution_name = %s
    AND entity_id = %s
)
INSERT INTO institutions (entity_id, institution_name, institution_type)
SELECT %s, %s, %s
WHERE NOT EXISTS (SELECT 1 FROM ins)
RETURNING id;
```

### Insert Document with Hash
```sql
INSERT INTO documents (
    institution_id, tax_year, document_type,
    period_start, period_end,
    file_path, file_name, file_size,
    doc_md5_hash, processed_at, processed_by
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s
) RETURNING id;
```

---

## Special Handling Rules

### Georgia Municipal Bonds
```python
def is_georgia_tax_exempt(security_description, bond_state):
    """
    Georgia residents don't pay state tax on GA municipal bonds
    """
    if bond_state == 'GA':
        return {
            'federal_taxable': False,
            'state_taxable': False,
            'tax_category': 'municipal_interest'
        }
```

### Qualified Dividends
```python
def determine_dividend_qualification(description, holding_period):
    """
    Qualified dividends get preferential tax treatment
    Look for "QUALIFIED" in description or apply holding period rules
    """
```

### Option Handling
```python
def parse_option_details(description, cusip):
    """
    Extract from description: "AAPL 09/15/24 150 CALL"
    - Underlying: AAPL
    - Expiration: 2024-09-15
    - Strike: 150.00
    - Type: CALL
    """
```

---

## Testing Requirements

### Test Data Sets Needed
1. **Simple case** - Single account, basic transactions
2. **Multi-account** - Consolidated statement
3. **Complex securities** - Options, bonds, mutual funds
4. **Edge cases**:
   - Zero amounts
   - Missing optional fields
   - Corrected/amended documents
   - Year-end date handling

### Validation Tests
```python
def test_duplicate_prevention():
    """Load same document twice, verify rejection"""

def test_rollback_on_error():
    """Inject error mid-load, verify complete rollback"""

def test_account_creation():
    """Load with unknown account, verify auto-creation"""

def test_tax_categorization():
    """Load GA muni bond, verify tax exemption"""
```

---

## Implementation Checklist

- [ ] Set up Python environment with psycopg2, decimal, json
- [ ] Create loader-config.json with defaults
- [ ] Implement configuration loader
- [ ] Build database connection manager with retry logic
- [ ] Create account resolution module
- [ ] Implement date/amount parsers
- [ ] Build preflight validation
- [ ] Implement document creation
- [ ] Create positions loader
- [ ] Create activities loader
- [ ] Build summary data loader
- [ ] Implement transaction management
- [ ] Add comprehensive logging
- [ ] Create test data sets
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Document usage and examples

---

## Next Steps

1. **Examine** existing `/config/account-mappings.json` structure
2. **Create** loader-config.json with appropriate defaults
3. **Prototype** the account resolution logic
4. **Build** core transformation functions (dates, amounts)
5. **Implement** the loader in phases, testing each phase

## Usage Examples

### Basic Usage
```bash
# Load both positions and activities from a statement
python db_loader.py \
  --positions /extractions/2024-08-positions.json \
  --activities /extractions/2024-08-activities.json \
  --config /config/loader-config.json

# Load only positions
python db_loader.py \
  --positions /extractions/2024-08-positions.json

# Dry run - validate without loading
python db_loader.py \
  --positions /extractions/2024-08-positions.json \
  --dry-run

# Override configuration
python db_loader.py \
  --positions data.json \
  --tax-year 2025 \
  --institution "Charles Schwab"
```

### Error Recovery
```bash
# Retry failed load with verbose logging
python db_loader.py \
  --positions failed.json \
  --log-level DEBUG \
  --continue-on-error

# Force reload (ignore duplicate check)
python db_loader.py \
  --positions data.json \
  --force
```

---

This specification provides all the research and planning needed to implement a robust database loader system.