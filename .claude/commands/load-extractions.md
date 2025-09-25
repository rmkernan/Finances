# Load Extractions Command

**Created:** 09/25/25 11:41AM ET
**Updated:** 09/25/25 1:03PM - Fixed timestamp validation to avoid false positives from 'ET' timezone suffix
**Updated:** 09/25/25 1:44PM - Enhanced presentation with entity-grouped statement pairs and deeper issue insights
**Updated:** 09/25/25 2:04PM - Fixed pairing logic to group by entity/period rather than exact timestamp matches
**Updated:** 09/25/25 4:09PM - Simplified pairing logic and integrated validation status reporting directly in presentation
**Purpose:** Guide Claude through loading validated JSON extraction files into the PostgreSQL database
**Usage:** User invokes this when ready to load extracted financial data into database

## Command: `/load-extractions`

### The Big Picture

This command loads structured JSON files produced by document extraction agents into the PostgreSQL database, making the financial data queryable for analysis. It uses a fail-fast approach that prioritizes data safety and workflow integrity.

### Your Mission

You're the **Database Loading Executor**. Your job is to:
1. **Discover** available JSON extraction files in `/documents/4extractions/`
2. **Validate** files for loading (proper timestamps, calculated hashes)
3. **Execute** loading using `simple_loader.py`
4. **Handle** loader errors with user guidance
5. **Verify** successful loading results

### Critical Workflow Requirements

**FAIL-FAST PHILOSOPHY:**
- Never autonomously resolve data conflicts
- Stop immediately when encountering issues
- Provide clear error explanations and resolution steps
- Only proceed when path is unambiguous

**Prerequisites:**
- Document records must exist (created by `/process-inbox`)
- Institution and account records must exist
- JSON files must have valid timestamps and MD5 hashes

## Step 1: Discover & Group Statement Pairs

```bash
# Find all JSON extraction files
ls -la /Users/richkernan/Projects/Finances/documents/4extractions/*.json
```

**CRITICAL:** Group files by statement (activities + holdings pairs) for user-friendly presentation.

Use Python to analyze and group files:

```bash
python3 -c "
import os
import json

# Get files and validate them
extraction_dir = '/Users/richkernan/Projects/Finances/documents/4extractions'
files = [f for f in os.listdir(extraction_dir) if f.endswith('.json')]

# Validate all files first
print('🔍 VALIDATION STATUS:')
all_valid = True
validation_issues = []

for filename in sorted(files):
    filepath = os.path.join(extraction_dir, filename)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            metadata = data.get('extraction_metadata', {})

        timestamp = metadata.get('extraction_timestamp', '')
        hash_val = metadata.get('json_output_md5_hash', '')

        # Check timestamp format
        if timestamp.count('T') > 1 or 'Z' in timestamp or ('T' in timestamp and not timestamp.endswith('ET')):
            validation_issues.append(f'{filename}: Invalid timestamp format')
            all_valid = False

        # Check MD5 hash
        if 'calculated_from_json_content' in hash_val or len(hash_val) != 32:
            validation_issues.append(f'{filename}: Invalid MD5 hash')
            all_valid = False

    except Exception as e:
        validation_issues.append(f'{filename}: Parse error - {e}')
        all_valid = False

if all_valid:
    print('✅ **NO ERRORS DETECTED - READY TO GO!**')
else:
    print('❌ **ERRORS DETECTED:**')
    for issue in validation_issues:
        print(f'   - {issue}')
    print()
    print('⚠️ Files with errors cannot be loaded. Fix issues before proceeding.')

print()
print('## Statement Pairs Available for Loading')
print()

# Extract pairs: period_entity as key
pairs = {}
for f in files:
    # Fid_Stmnt_2025-07_RichIRA+RichRoth_activities_2025.09.25_15.54ET.json
    parts = f.split('_')
    period = parts[2]  # 2025-07
    entity = parts[3]  # RichIRA+RichRoth
    key = f'{entity} ({period})'

    if key not in pairs:
        pairs[key] = {'activities': None, 'holdings': None}

    if 'activities' in f:
        pairs[key]['activities'] = f
    elif 'holdings' in f:
        pairs[key]['holdings'] = f

# Present the pairs
complete = 0
for i, (name, files) in enumerate(sorted(pairs.items()), 1):
    print(f'**{i}. {name}**')

    if files['activities'] and files['holdings']:
        print('   - ✅ **COMPLETE PAIR:** Activities + Holdings available')
        print(f'   - Activities: \`{files[\"activities\"]}\`')
        print(f'   - Holdings: \`{files[\"holdings\"]}\`')
        complete += 1
    else:
        print('   - ⚠️ **INCOMPLETE:** Missing', end='')
        if not files['activities']: print(' activities', end='')
        if not files['holdings']: print(' holdings', end='')
        print()
    print()

print(f'### Summary: ✅ **{complete} Complete Pairs** ready for loading')
print()

if all_valid:
    print('**What would you like to load?**')
else:
    print('**Fix validation errors before loading.**')
"
```

Present the grouped results to the user with clear validation status and pairing information.

## Step 2: Execute Loading

Use the enhanced `simple_loader.py` script for each file:

```bash
# Load single file
python3 /Users/richkernan/Projects/Finances/loaders/simple_loader.py /path/to/extraction.json
```

**Expected Successful Output:**
```
Loading: /path/to/extraction.json
  Loaded X positions for account Z40-394067
  Loaded Y transactions for account Z40-394067
  Loaded Z summary data fields for account Z40-394067
Success: X positions, Y transactions
Moved to: /Users/richkernan/Projects/Finances/documents/5loaded/filename.json
```

## Step 3: Handle Loader Errors (Fail-Fast Approach)

The loader will provide clear error messages for common issues:

### Missing Document Record
```
MISSING DOCUMENT RECORD:
  PDF file: Fid_Stmnt_2024-01_Milton.pdf
  PDF hash: 53bf7c2204d6c90ee55143789e67eaad

Resolution required: Run /process-inbox command to create document
structure before loading extractions.

Workflow: /process-inbox → /load-extractions
```

**Your Action:** Stop and inform user that process-inbox needs to be run first.

### Duplicate Data Conflict
```
DUPLICATE DATA CONFLICT:
  Document: Fid_Stmnt_2024-01_Milton.pdf
  Extraction type: activities
  Already loaded: 2025-09-25 10:58:00
  Existing hash: abc123...
  New hash: def456...

Resolution required: Determine if this is a duplicate extraction,
corrected data, or extraction bug before proceeding.
```

**Your Action:** Stop and ask user:
1. Is this a corrected extraction that should replace the existing data?
2. Is this a duplicate that should be skipped?
3. Is this an extraction bug that needs investigation?

### Missing Reference Data
```
Entity 'Milton Preschool Inc' not found in database.
Reference data must be loaded first via process-inbox command.
```

**Your Action:** Stop and inform user that account/entity setup is incomplete.

## Step 4: Verify Loading Results

After successful loading, verify data integrity:

```sql
-- Check recently loaded documents
SELECT
    d.file_name,
    d.period_start,
    d.period_end,
    d.activities_loaded IS NOT NULL as has_activities,
    d.positions_loaded IS NOT NULL as has_holdings,
    COUNT(DISTINCT t.id) as transaction_count,
    COUNT(DISTINCT p.id) as position_count
FROM documents d
LEFT JOIN transactions t ON d.id = t.document_id
LEFT JOIN positions p ON d.id = p.document_id
WHERE d.processed_at > NOW() - INTERVAL '2 hours'
GROUP BY d.id, d.file_name, d.period_start, d.period_end, d.activities_loaded, d.positions_loaded
ORDER BY d.processed_at DESC;
```

## User Interaction Guidelines

**After presenting grouped statement pairs, ask:** "What would you like to load?"

**Accept these user responses:**
- **Statement numbers:** "1, 3, 5" or "1-4" (load specific statements)
- **Complete pairs only:** "complete pairs only" (skip partial extractions)
- **Partial OK:** "partial ok" or "include partials" (load everything valid)
- **All:** "all" or "everything" (load all valid files)
- **None:** "none" or "skip" (exit without loading)
- **Entity-specific:** "Milton only" or "HMA statements"
- **Time-specific:** "2024 only" or "recent statements"

**For batch loading:** Process files individually and report results for each statement pair.

**Always confirm selection before proceeding** and summarize what will be loaded.

## Success Indicators

Loading completed successfully when:
- [ ] JSON files processed without errors
- [ ] Files moved to `/documents/5loaded/` directory
- [ ] Database contains expected record counts
- [ ] Verification query shows correct data
- [ ] No error messages or warnings

## Error Recovery Patterns

**Common resolution steps:**

1. **Missing document:** Run `/process-inbox` first
2. **Validation issues:** Re-extract with corrected timestamp logic
3. **Duplicate conflicts:** Work with user to determine correct action
4. **Database connection:** Verify Supabase running on localhost:54322

## Remember

- **Data Safety First:** Never autonomously overwrite financial data
- **Workflow Integrity:** Enforce proper `/process-inbox` → `/load-extractions` sequence
- **Clear Communication:** Provide specific error details and resolution steps
- **File Management:** Loader handles moving files to `/5loaded/` automatically
- **User Guidance:** When in doubt, ask the user for clarification

---

*This command ensures safe, systematic loading of financial extractions with comprehensive error handling and user guidance.*