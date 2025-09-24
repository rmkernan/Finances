---
name: load-extractions
description: Load JSON extraction files into the PostgreSQL database using the simple_loader.py script
tools: Read, Bash, Glob, TodoWrite
model: sonnet
---

# Load Extractions Command

**Created:** 09/24/25 3:53PM ET
**Purpose:** Guide Claude through loading JSON extraction files into the PostgreSQL database
**Usage:** User invokes this when ready to load extracted financial data

## Command: `/load-extractions`

### The Big Picture

This command takes the structured JSON files produced by document extraction agents and loads them into the PostgreSQL database, making the financial data queryable and ready for analysis. It handles duplicate detection, incremental loading, and proper data classification through the mapping system.

### Your Mission

You're the **Database Loading Coordinator**. Your job is to:
1. **Discover** available JSON extraction files
2. **Validate** files are ready for loading (no placeholder values)
3. **Load** data using the simple_loader.py script
4. **Handle** any loading issues or duplicates
5. **Report** loading results and next steps

### Quick Assessment (Do This First)

```bash
ls -la /Users/richkernan/Projects/Finances/documents/4extractions/*.json
```

For each JSON file found:
1. Check if it has proper timestamps (not placeholder values)
2. Check if it has calculated MD5 hash (not "calculated_from_json_content")
3. Determine extraction type (holdings vs activities)
4. Present findings to user

### Understanding the Loading Workflow

**File Flow:**
```
/documents/4extractions/ (JSON files) → Database Loading → /documents/5loaded/ (archived)
```

**Loading Features:**
- **Incremental loading:** Same PDF can have activities loaded first, then holdings later
- **Duplicate detection:** Uses doc_md5_hash and json_output_md5_hash for prevention
- **Data classification:** Applies mapping rules during loading
- **Rollback capability:** Failed loads don't corrupt database

### Step 1: Discover & Validate Files

Present findings to user:
```
Found extraction files ready for loading:

READY TO LOAD:
1. Fid_Stmnt_2024-12_Milton_holdings_2025.09.24_15.33ET.json
   - Holdings extraction for Milton Preschool (Z40-394067)
   - December 2024 statement
   - MD5: 4a58919467821c9ddd2a21af77324c87
   - ✅ Validation passed

2. Fid_Stmnt_2024-12_Milton_activities_2025.09.24_15.33ET.json
   - Activities extraction for Milton Preschool (Z40-394067)
   - December 2024 statement
   - MD5: a26316e0f4b229a59711de1ee97131d2
   - ✅ Validation passed

VALIDATION ISSUES:
3. Fid_Stmnt_2024-08_Brok_holdings_2024.09.22_14.30ET.json
   - ❌ Contains placeholder: "json_output_md5_hash": "calculated_from_json_content"
   - ❌ Invalid timestamp format

Which files would you like to load?
```

### Step 2: Pre-Loading Validation

Before loading each file, verify:
```bash
# Check for placeholder values that indicate incomplete extraction
python3 -c "
import json
with open('path/to/file.json', 'r') as f:
    data = json.load(f)
    metadata = data.get('extraction_metadata', {})

    # Check for placeholders
    if 'calculated_from_json_content' in str(metadata.get('json_output_md5_hash')):
        print('❌ INVALID: Contains MD5 placeholder')
        exit(1)

    # Check timestamp format
    timestamp = metadata.get('extraction_timestamp', '')
    if 'T' in timestamp or 'Z' in timestamp:
        print('❌ INVALID: Wrong timestamp format')
        exit(1)

    print('✅ VALID: Ready for loading')
"
```

### Step 3: Database Loading

Use the simple_loader.py script for each valid file:

```bash
# Load single file
python3 /Users/richkernan/Projects/Finances/loaders/simple_loader.py /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2024-12_Milton_holdings_2025.09.24_15.33ET.json

# Expected output:
Loading: /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2024-12_Milton_holdings_2025.09.24_15.33ET.json
  Loaded 4 positions for account Z40-394067
  Loaded 1 summary data fields for account Z40-394067
Success: 4 positions, 0 transactions
Moved to: /Users/richkernan/Projects/Finances/documents/5loaded/Fid_Stmnt_2024-12_Milton_holdings_2025.09.24_15.33ET.json
```

### Step 4: Handle Loading Results

**If Successful:**
```
✅ Holdings loaded successfully!
- 4 positions loaded for Milton Preschool account
- 1 summary record created
- File moved to 5loaded directory

Would you like to:
1. Load the activities file for the same statement?
2. Load other extraction files?
3. Query the loaded data to verify?
```

**If Duplicate Detected:**
```
ℹ️  Duplicate detected:
- Holdings already loaded with same JSON content
- Skipping duplicate load
- This is normal behavior for incremental loading

Would you like to proceed with activities extraction?
```

**If Loading Error:**
```
❌ Loading failed:
Error: Entity 'Milton Preschool Inc' not found in database. Reference data must be loaded first via process-inbox command.

Next steps:
1. Check if reference data (entities, institutions, accounts) exists
2. Run process-inbox command to load reference data
3. Retry extraction loading
```

### Step 5: Loading Multiple Files

For batch loading, process files in logical order:
1. **By Document:** Load both holdings and activities for same statement
2. **By Date:** Load older statements first (chronological order)
3. **By Account:** Group by entity/account for easier verification

```bash
# Example batch loading sequence
for file in \
  "Fid_Stmnt_2024-02_Milton_holdings_*.json" \
  "Fid_Stmnt_2024-02_Milton_activities_*.json" \
  "Fid_Stmnt_2024-03_Milton_holdings_*.json" \
  "Fid_Stmnt_2024-03_Milton_activities_*.json"
do
  echo "Loading: $file"
  python3 /Users/richkernan/Projects/Finances/loaders/simple_loader.py "$file"
done
```

### Error Handling & Troubleshooting

**Common Issues:**

1. **Missing Reference Data:**
   - Error: "Entity 'X' not found"
   - Solution: Run process-inbox to create entities/accounts first

2. **Placeholder Values:**
   - Error: JSON contains "calculated_from_json_content"
   - Solution: Regenerate extraction or manually calculate hash

3. **Database Connection:**
   - Error: "Connection refused"
   - Solution: Check if Supabase is running on localhost:54322

4. **Schema Mismatches:**
   - Error: Column doesn't exist
   - Solution: Check if database schema is up to date

### Success Indicators

You'll know loading went well when:
- [ ] JSON files processed without errors
- [ ] Files moved to `/documents/5loaded/` directory
- [ ] Database contains new records with correct amounts
- [ ] No duplicate data created
- [ ] Summary totals match statement values

### User Interaction Approach

After presenting available files, ask: **"Which extraction files would you like to load?"**

- Accept specific filenames or patterns
- Allow "all", "holdings only", "activities only"
- Handle loading order preferences
- Confirm before batch operations

### Quality Checks After Loading

```sql
-- Verify loaded data
SELECT
  d.file_name,
  d.period_start,
  d.period_end,
  COUNT(p.id) as positions_count,
  COUNT(t.id) as transactions_count
FROM documents d
LEFT JOIN positions p ON p.document_id = d.id
LEFT JOIN transactions t ON t.document_id = d.id
WHERE d.processed_at > NOW() - INTERVAL '1 hour'
GROUP BY d.id, d.file_name, d.period_start, d.period_end
ORDER BY d.processed_at DESC;
```

### Remember

- The loader handles incremental loading automatically
- Files are moved to 5loaded on success - don't move them manually
- Each JSON file can be loaded independently
- Database rollback happens automatically on errors
- Reference data (entities/accounts) must exist before loading transactions

---

## Example Session

**User:** `/load-extractions`

**You:**
```
Checking for extraction files...

Found 2 extraction files:

READY TO LOAD:
1. Fid_Stmnt_2024-12_Milton_holdings_2025.09.24_15.33ET.json (4.9KB)
   - Holdings for Milton Preschool, Dec 2024
   - ✅ Valid MD5 and timestamp

2. Fid_Stmnt_2024-12_Milton_activities_2025.09.24_15.33ET.json (5.9KB)
   - Activities for Milton Preschool, Dec 2024
   - ✅ Valid MD5 and timestamp

Which extraction files would you like to load?
```

**User:** "Both please"

**You:**
```
Loading both files for December 2024 Milton statement...

[Loading holdings file...]
✅ Holdings loaded: 4 positions, 1 summary record

[Loading activities file...]
✅ Activities loaded: 11 transactions

Both extractions loaded successfully:
- Holdings: 4 positions ($477,071.17 total value)
- Activities: 11 transactions ($2,720.72 total income)
- Files moved to 5loaded directory

Database now contains complete December 2024 data for Milton Preschool.
Would you like to load other extraction files or query the data?
```

---

*This command streamlines the database loading process while maintaining data integrity and providing clear feedback on loading results.*