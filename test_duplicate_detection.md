# Test Plan: JSON Hash Duplicate Detection

**Created:** 09/23/25 8:20PM ET
**Purpose:** Test the enhanced duplicate detection system with JSON hash tracking at data level

## Test Setup

### Pre-Test Verification
```bash
# Check current database state
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres

-- Verify new columns exist
\d+ transactions  -- Should show source_json_hash column
\d+ positions     -- Should show source_json_hash column
\d+ documents     -- Should NOT have extraction_md5_hash or extraction_filename

-- Check existing data
SELECT COUNT(*) FROM documents WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5';
SELECT COUNT(*) FROM transactions WHERE source_file LIKE '%2025-08%';
SELECT COUNT(*) FROM positions WHERE source_file LIKE '%2025-08%';
```

## Test Cases

### Test 1: Load Activities JSON (First Time)
**File:** `/Users/richkernan/Projects/Finances/documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_activities_2025.09.22_14.30ET.json`

**Expected Result:**
- Document record created or retrieved (if holdings already loaded)
- Transactions loaded successfully
- JSON hash saved in transactions.source_json_hash

**Test Command:**
```bash
python3 simple_loader.py documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_activities_2025.09.22_14.30ET.json
```

### Test 2: Reload Same Activities JSON (Duplicate Test)
**File:** Same as Test 1

**Expected Result:**
- Script should detect duplicate via source_json_hash
- Output: "Activities JSON already loaded: [filename]"
- No new transactions created

**Test Command:**
```bash
# Run same command again
python3 simple_loader.py documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_activities_2025.09.22_14.30ET.json
```

### Test 3: Load Holdings JSON (First Time)
**File:** `/Users/richkernan/Projects/Finances/documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_holdings_2025.09.22_14.30ET.json`

**Expected Result:**
- Document record retrieved (already created by activities)
- Positions loaded successfully
- JSON hash saved in positions.source_json_hash

**Test Command:**
```bash
python3 simple_loader.py documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_holdings_2025.09.22_14.30ET.json
```

### Test 4: Reload Same Holdings JSON (Duplicate Test)
**File:** Same as Test 3

**Expected Result:**
- Script should detect duplicate via source_json_hash
- Output: "Holdings JSON already loaded: [filename]"
- No new positions created

**Test Command:**
```bash
# Run same command again
python3 simple_loader.py documents/5loaded/Fid_Stmnt_2025-08_Brok+CMA_holdings_2025.09.22_14.30ET.json
```

## Verification Queries

### After Test 1 (Activities Loaded)
```sql
-- Check document created
SELECT id, file_name, doc_md5_hash FROM documents
WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5';

-- Check transactions have JSON hash
SELECT COUNT(*), COUNT(DISTINCT source_json_hash)
FROM transactions
WHERE source_file LIKE '%2025-08_Brok+CMA_activities%';

-- Verify hash is consistent
SELECT DISTINCT source_json_hash
FROM transactions
WHERE source_file LIKE '%2025-08_Brok+CMA_activities%';
```

### After Test 3 (Holdings Loaded)
```sql
-- Document should still be just one record
SELECT COUNT(*) FROM documents
WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5';

-- Check positions have JSON hash
SELECT COUNT(*), COUNT(DISTINCT source_json_hash)
FROM positions
WHERE source_file LIKE '%2025-08_Brok+CMA_holdings%';

-- Verify hash is consistent
SELECT DISTINCT source_json_hash
FROM positions
WHERE source_file LIKE '%2025-08_Brok+CMA_holdings%';
```

## Cleanup (If Needed)

```sql
-- To reset for testing (CAUTION: Deletes data!)
DELETE FROM transactions WHERE source_file LIKE '%2025-08%';
DELETE FROM positions WHERE source_file LIKE '%2025-08%';
DELETE FROM doc_level_data WHERE document_id IN (
    SELECT id FROM documents WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5'
);
DELETE FROM document_accounts WHERE document_id IN (
    SELECT id FROM documents WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5'
);
DELETE FROM documents WHERE doc_md5_hash = '32967b1d3e40b2c544cc42e0c6f378e5';
```

## Success Criteria

✅ **Test 1:** Activities load successfully, JSON hash stored
✅ **Test 2:** Duplicate activities rejected with clear message
✅ **Test 3:** Holdings load successfully using same document record
✅ **Test 4:** Duplicate holdings rejected with clear message
✅ **Final State:** One document record, separate JSON hashes for activities and holdings