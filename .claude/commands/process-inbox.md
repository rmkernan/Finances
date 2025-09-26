# Process Inbox Command

**Created:** 09/18/25 11:15AM ET
**Updated:** 09/22/25 3:00PM ET - Refactored for sub-agent orchestration with stateless execution model
**Updated:** 09/22/25 3:20PM ET - Simplified with staging workflow: inbox → staged → processed
**Updated:** 09/22/25 3:28PM ET - Added prescriptive sub-agent invocation requirements aligned with agent definition
**Updated:** 09/22/25 4:19PM ET - Added entity recognition guidance, sub-agent prompt review requirement
**Updated:** 09/22/25 5:42PM ET - Fixed paths, Task tool syntax, parallel processing, and simplified mapping updates
**Updated:** 09/22/25 6:29PM ET - Added token-efficient PDF page extraction guidance using scripts/extract_pdf_pages.py
**Updated:** 09/22/25 6:46PM ET - Simplified PDF text extraction to direct Python code (no temporary files)
**Updated:** 09/22/25 6:51PM ET - Added note to ignore institution-generated filenames
**Updated:** 09/22/25 6:59PM ET - Simplified filename handling, merged staging steps, clarified mapping usage
**Updated:** 09/22/25 7:03PM ET - Changed user prompting to open-ended "What do you want to do next?" with flexible response handling
**Updated:** 09/22/25 8:55PM ET - Added MD5 hash generation for duplicate prevention and document tracking
**Updated:** 09/23/25 3:08PM - Added critical Step 2: Account Resolution & Database Setup to ensure complete account metadata before extraction
**Updated:** 09/23/25 3:33PM - Updated account resolution to use account-mappings.json as definitive source of truth with anti-overwrite protections
**Updated:** 09/23/25 7:29PM - Added automatic transaction classification section and updated workflow documentation for configuration-driven mapping system
**Updated:** 09/24/25 10:25AM - Updated transaction classification section to reflect new three-table mapping system and enhanced options tracking
**Updated:** 09/24/25 10:35AM - Added comprehensive mapping system integration with post-extraction analysis workflow and intelligent rule recommendation process
**Updated:** 09/24/25 11:16AM - Restructured workflow with parallel processing optimizations, reducing execution time from ~45 to ~15 seconds
**Updated:** 09/25/25 12:54PM - Added critical Step 6: Create Database Document Records to complete workflow before PDF archival
**Updated:** 09/25/25 12:56PM - Simplified Step 6 to use direct SQL commands instead of separate Python script
**Updated:** 09/25/25 1:08PM - Expanded Step 6 to include missing reference data loading (entities and accounts) before document creation
**Updated:** 09/25/25 1:12PM - Added unique constraints for entity_name and institution_name, updated conflict handling to use proper composite keys
**Updated:** 09/26/25 2:00PM - Restructured extraction workflow with updated agent invocation formats
**Updated:** 09/26/25 2:12PM - Added PDF validation for holdings extraction workflow
**Updated:** 09/26/25 2:29PM - Fixed database connection command (added -U postgres flag) and added mandatory validation checkpoint with failure handling
**Updated:** 09/26/25 3:52PM - Fixed Quick Assessment section with clear step-by-step instructions
**Updated:** 09/26/25 4:07PM - Added critical instruction to read entire command before starting, preventing premature execution
**Purpose:** Guide Claude through orchestrating document processing from inbox using specialized extraction agents
**Usage:** User invokes this when ready to process financial documents

## Command: `/process-inbox`

### ⚠️ CRITICAL: READ THIS ENTIRE COMMAND FIRST ⚠️
**DO NOT start processing until you have read ALL sections of this document.**
This command contains specific instructions for CSV+PDF hybrid processing that differ significantly between holdings and activities extraction. Skipping ahead will cause errors.

### The Big Picture

This project transforms paper and PDF financial statements into an LLM-queryable database, allowing the user to have intelligent conversations with their financial data through Claude. Instead of digging through stacks of statements, the user will be able to ask questions like "What were my dividend earnings from municipal bonds last quarter?" or "Show me all options trades in August" and get immediate, accurate answers.

### Your Mission

You're the **Orchestra Conductor** for financial document processing. Your job is to:
1. **Assess** what documents need processing and detect potential duplicates
2. **Prepare** the right context and instructions for sub-agents
3. **Delegate** extraction work to specialized agents
4. **Interpret** agent reports and handle any issues
5. **Organize** successful extractions and maintain clean file structure

### Quick Assessment (Do This First)

```bash
ls -la /Users/richkernan/Projects/Finances/documents/1inbox/
```

**⚠️ CRITICAL: Fidelity Statements Require CSV+PDF Pairs for Holdings ⚠️**

**STEP 1: Identify ALL Files and Check for Pairing**
1. List all files in inbox (PDFs and CSVs)
2. Look for date patterns in filenames:
   - PDFs: `Fid_Stmnt_YYYY-MM_*.pdf` or similar
   - CSVs: `*Statement*MMDDYYYY.csv` or `*MMDDYYYY.csv`
   - Match by period (e.g., `2025-04` PDF with `4302025` CSV)

**STEP 2: Validate CSV Files First**
For each CSV file found, check if it's Fidelity positions data:
```bash
head -3 /Users/richkernan/Projects/Finances/documents/1inbox/[csv_filename].csv
# Look for: "Account Type,Account,Beginning mkt Value" header
# This confirms it's a Fidelity positions export
```

**STEP 3: Extract PDF Period and Accounts**
For each PDF, extract text to identify period and accounts:
```bash
python3 -c "
import PyPDF2
with open('documents/1inbox/[filename].pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    print('=== PAGE 1 ===')
    print(reader.pages[0].extract_text())
    print('\n=== PAGE 2 ===')
    print(reader.pages[1].extract_text() if len(reader.pages) > 1 else 'No page 2')
"
# Look for: Statement period dates and account numbers
```

**STEP 4: Report Pairing Status CLEARLY**
Present findings WITH explicit pairing status:
- "✅ **PAIRED:** Fidelity April 2025 - PDF + CSV found (ready for BOTH holdings AND activities)"
- "⚠️ **UNPAIRED:** Fidelity March 2025 - PDF only, NO CSV (activities OK, holdings BLOCKED)"
- "📄 **NON-FIDELITY:** Chase statement - Different processor needed"

**CRITICAL RULES:**
- **Holdings extraction REQUIRES both CSV and PDF files**
- **Activities extraction can use PDF alone**
- **Never proceed with holdings if CSV is missing**

**Note:** Ignore source filenames for content - extract all details from file contents.

### Understanding the Workflow

**Document Flow:**
```
/documents/1inbox/ (generic names) → Staging → /documents/2staged/ (renamed PDFs)
                                          → Extraction → /documents/4extractions/ (JSON)
                                          → Completion → /documents/3processed/ (final archive)
```

**Your Role vs Sub-Agent Role:**
- **You:** Identify, coordinate, verify, handle exceptions
- **Sub-Agent:** Read PDF, extract specific data type, produce JSON, report outcome
- **Key:** Sub-agents can't ask questions mid-task - they either complete or report what blocked them

## 🗺️ Automatic Transaction Classification

The enhanced loader automatically classifies transactions using a configuration-driven mapping system:

### What Happens Automatically
- **Transaction Types:** Dividends vs interest vs trades properly categorized
- **Security Classification:** Options identified as calls/puts with lifecycle tracking
- **Tax Categories:** Municipal bonds separated from regular dividends for tax reporting
- **Options Lifecycle:** Opening, closing, and assignment transactions properly tagged with enhanced put/call identification

### Key Benefits for Document Processing
- **No Manual Intervention:** Known patterns are classified automatically via database mapping rules
- **Consistent Results:** Same transaction types always get same classification
- **Tax Accuracy:** Municipal interest properly separated from dividend income
- **Options Tracking:** Foundation for matching opening/closing pairs with enhanced put/call identification

### When Manual Review Needed
- **New Transaction Types:** Descriptions not covered by existing classification rules
- **Unusual Securities:** Complex instruments not covered by existing patterns
- **Data Quality Issues:** Malformed or incomplete transaction data

### Mapping System Integration

**Your Role in System Improvement:**
After extraction agents complete their work, you play a crucial role in maintaining and improving the classification system by analyzing their reports and recommending mapping rule enhancements.

**Mapping System Files:**
- **Current rules:** `/config/mapping-rules.csv` - Human-readable rule definitions
- **Update script:** `python3 scripts/update_mapping_rules.py` - Applies CSV changes to database
- **View current rules:** Read the CSV to understand existing classification patterns

### Post-Extraction Analysis Process

After each extraction, you must:

1. **Read Sub-Agent Reports** - Look for "Unknown transaction patterns" and "New security patterns" sections
2. **Review Current Mapping Rules** - Read `/config/mapping-rules.csv` to avoid duplicates
3. **Analyze Gaps** - Compare reported patterns against existing rules
4. **Propose Specific Rules** - Suggest exact CSV additions with business justification
5. **Present Recommendations** - Show user before/after comparison

**Example Analysis Flow:**
```
Sub-agent reported: "Found transaction description 'CRYPTO DIVIDEND' not seen before"

My analysis:
- Checked current rules: No crypto-related dividend patterns exist
- Gap identified: Cryptocurrency dividend transactions not classified
- Recommendation: Add rule "Crypto Dividend Detection"
  - Trigger: activities.description contains "CRYPTO DIVIDEND"
  - Actions: SET activities.type = "dividend"; SET activities.subtype = "crypto"
  - Problem solved: Cryptocurrency dividends properly classified for tax reporting

Would you like me to add this rule to the mapping system?
```

### Handling New Patterns
When sub-agents encounter unknown patterns:
1. **Document precisely** - Note exact descriptions and security names
2. **Cross-reference** against current mapping rules
3. **Identify gaps** - Determine what classification rules are missing
4. **Recommend solutions** - Propose specific mapping rule additions
5. **Implement improvements** - Update mapping system with user approval
6. **Verify results** - Confirm new rules work as expected

### Step 1: Parallel Assessment & Staging

**⚠️ CRITICAL: ALL VALIDATION STEPS ARE REQUIRED**
**If ANY step fails, STOP immediately and consult with the user before proceeding.**

**Estimated Time:** ~10-15 seconds (parallel) vs ~45 seconds (sequential)

For each document, run all validation checks in parallel:

```bash
# Run all checks simultaneously using multiple Bash tool calls in single message:
# 1. Generate MD5 hash
md5 /Users/richkernan/Projects/Finances/documents/1inbox/[filename].pdf

# 2. Check for duplicate hash in extractions (parallel)
grep -r "[hash_value]" /Users/richkernan/Projects/Finances/documents/4extractions/*.json 2>/dev/null || echo "No hash duplicates"

# 3. Check for similar processed files (parallel)
ls -la /Users/richkernan/Projects/Finances/documents/3processed/[similar_pattern]*.pdf 2>/dev/null || echo "No processed duplicates"

# 4. Verify database accounts exist (parallel)
PGPASSWORD=postgres psql -U postgres -h localhost -p 54322 -d postgres -c "SELECT a.account_number, a.account_type, i.institution_name FROM accounts a JOIN institutions i ON a.institution_id = i.id WHERE a.account_number IN ('[account1]', '[account2]');"
```

**VALIDATION CHECKPOINT:**
Before proceeding, verify ALL four validation checks succeeded:
- ✅ MD5 hash generated successfully
- ✅ No duplicate hash found in existing extractions
- ✅ No similar processed files found
- ✅ Database connection successful and accounts exist

**If any validation step failed, STOP and ask user how to proceed.**

Then:
1. **Extract account information** from PDF content (already done in Quick Assessment)
2. **Look up accounts in mappings** at /Users/richkernan/Projects/Finances/config/account-mappings.json
3. **Use mapped names** for filename generation and staging

**Account Matching Rules:**
- **Exact match:** Account number found in mappings → Use existing metadata, proceed with staging
- **Minor discrepancies:** Account matches but holder names slightly different → Do NOT overwrite mappings, proceed with existing data
- **Unknown account:** Account not in mappings → Stop and ask user for complete metadata

If unknown accounts found:
1. Ask: "Found [Institution] statement with unknown account XXXX for [Holder Name]. This account is not in the mappings file. Should I add it?"
2. If yes, ask for complete metadata (entity, account type, etc.)
3. Update the mapping file with full metadata
4. Stage with mapped names

```bash
# Use mapped account names for clarity
mv /Users/richkernan/Projects/Finances/documents/1inbox/Statement12312024.pdf /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-12_Milton.pdf
```

### Step 2: Present Findings & Get User Direction

**All validation completed in Step 1.** Now present findings and ask what to do next:

For amended documents:
```python
# If filename suggests it's the same document but content differs:
# Check if original shows "AMENDED" or "CORRECTED"
Read /Users/richkernan/Projects/Finances/documents/2staged/Fid_1099_2024_Brok+CMA.pdf (page 1)
# Look for "AMENDED" or "CORRECTED" text
```


After checking for duplicates and CSV pairing, present your findings and ask what to do next:
```
Staging complete. Here's what I found:

STAGED FILES:
1. Fid_Stmnt_2024-08_Brok+CMA.pdf + Statement8312024.csv
   - ✅ PAIRED: Fidelity Investment Statement for August 2024
   - Accounts: Brokerage + CMA
   - 36 pages PDF + CSV export
   - ✅ No duplicate found in processed folder
   - ✓ Ready for HYBRID holdings extraction (CSV+LLM)
   - ✓ Ready for activities extraction (LLM only)

2. Fid_Stmnt_2024-07_Brok+CMA.pdf
   - ❌ UNPAIRED: Fidelity statement without CSV export
   - ✗ Holdings extraction BLOCKED (no CSV)
   - ✓ Activities extraction still possible

3. BofA_Stmnt_2024-09_Checking.pdf
   - Bank of America checking statement
   - ✗ No extraction agent available
   - Options: Manual processing or skip

POTENTIAL ISSUES:
4. Fid_1099_2024_Brok+CMA.pdf
   - ⚠️ Similar file exists: Fid_1099_2024_Brok+CMA.pdf in processed folder
   - Content shows "AMENDED" marking
   - ✗ No 1099 extraction agent available anyway

I found these files. What do you want to do next?

Some options:
- Extract holdings from paired Fidelity statement (#1)
- Extract activities from any Fidelity statement (#1 or #2)
- Extract both from paired statement (sequential)
- Skip unpaired statement until CSV available
- Handle Bank of America manually
- Review the amended 1099 situation
- Something else entirely

What would you like me to do?
```

### Step 3: Extraction Process

The extraction process differs based on data type:

#### Step 3A: Holdings Extraction (Hybrid CSV+LLM)

**For holdings, we use a two-stage hybrid process:**

1. **Stage 1: Python CSV Extraction**
   - Export CSV from Fidelity statement (manual step)
   - Run `scripts/csv_to_holdings_json.py` to create base JSON structure (~75% complete)
   - Python fills all CSV-available fields marked with (C) in mapping document

2. **Stage 2: LLM PDF Augmentation**
   - LLM reads the pre-populated JSON from Stage 1
   - LLM extracts PDF-only fields (yields, bond details, doc_level_data)
   - LLM ignores all CSV fields, preserves existing data

**CSV Extraction Command:**
```bash
python3 scripts/csv_to_holdings_json.py /path/to/exported.csv /documents/4extractions/
```

#### Step 3B: Activities Extraction (Pure LLM)

**For activities, we use traditional LLM extraction:**
- Single-stage process
- LLM extracts all transaction data from PDF
- Creates complete JSON from scratch

**Prerequisites before invoking any sub-agent:**
1. **Verify the PDF is readable and supported** (Fidelity statements currently)
2. **For holdings: Verify CSV+PDF pairing** - Holdings extraction requires both files
3. **For holdings: Complete CSV extraction first** using `scripts/csv_to_holdings_json.py`
4. **Specify extraction type explicitly** (holdings OR activities)
5. **Provide complete file paths** (PDF + CSV_JSON for holdings, PDF only for activities)

**CRITICAL: Holdings extraction will FAIL without CSV companion file**

**IMPORTANT: Before invoking any sub-agent, present the prompt you're about to send for user review:**

```
I'm ready to invoke the fidelity-statement-extractor agent.
Here's the prompt I'll send:

[Show the exact prompt here]

Does this look correct?
```

Wait for user approval before proceeding.

**Required Elements for Sub-Agent Invocation:**
1. **Specify extraction mode explicitly** (holdings OR activities - pick ONE)
2. **Provide complete file path** to the staged PDF
3. **Use directive language** (not conversational)
4. **Set clear expectations** for the output

**Holdings Invocation Format (Hybrid CSV+LLM):**

Use the Task tool with:
```python
Task(
    description="Augment CSV holdings",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Holdings
DOC_MD5_HASH: [insert_md5_hash_here]
CSV_JSON_FILE: /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_YYYY-MM_[Accounts]_holdings_YYYY.MM.DD_HH.MMET.json
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-12_Milton.pdf

Please AUGMENT the pre-populated JSON file with PDF-only data.

CRITICAL: The CSV_JSON_FILE contains ~75% of holdings data from CSV extraction.
- IGNORE all fields marked with (C) in Map_Stmnt_Fid_Positions.md
- EXTRACT ONLY non-(C) fields from PDF: yields, bond details, options details, doc_level_data
- UPDATE the existing JSON in-place, preserving all CSV data
- SAVE the completed JSON back to the CSV_JSON_FILE path

Expected output:
- Updated JSON file with complete holdings data
- Report on augmentation success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**Activities Invocation Format (Pure LLM - Unchanged):**

```python
Task(
    description="Extract activities",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Activities
DOC_MD5_HASH: [insert_md5_hash_here]
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-08_Brok+CMA.pdf

Please extract ACTIVITIES data from the Fidelity statement PDF.

This is full LLM extraction (not hybrid mode).
- EXTRACT all transaction data from PDF
- CREATE complete JSON from scratch using Map_Stmnt_Fid_Activities.md
- SAVE as new JSON file in /documents/4extractions/

Expected output:
- New JSON extraction file in /documents/4extractions/
- Report on extraction success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**What to expect from the agent:**

**For Holdings (Hybrid Mode):**
- Reads pre-populated JSON and PDF
- Updates existing JSON with PDF-only fields
- Preserves all CSV data exactly as-is
- Reports what fields were augmented from PDF

**For Activities (Traditional Mode):**
- Reads PDF and creates complete JSON from scratch
- Uses full LLM extraction process
- Creates new timestamped JSON file

**Both modes produce completion reports with:**
- ✅ Success: Details of what was extracted/augmented, files updated/created
- ⚠️ Partial: What worked, what failed, why
- ❌ Failed: Specific blocker that prevented extraction

**Important:** The agent is stateless and cannot ask follow-up questions. If it encounters an issue it can't resolve, it will document it in the report and exit.

### Step 5: Handle Agent Reports

After the agent completes, review its report and determine next steps:

**If Successful:**
```
✓ Holdings extraction complete!
Created: Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.30ET.json

The agent identified:
- 2 accounts (Brokerage, CMA)
- 47 positions extracted
- All data validated against schema

Would you like me to:
1. Run activities extraction on the same document?
2. Move the PDF to processed folder?
3. Process the next document?
```

**If Issues Reported:**
```
⚠️ Holdings extraction completed with warnings:

The agent reported:
- Successfully extracted 45 positions
- Could not parse 2 option positions (unusual format)
- Manual review needed for options on page 18

The partial extraction has been saved. Would you like to:
1. Review the problematic entries together?
2. Continue with activities extraction?
3. Keep in inbox for manual review later?
```

### Step 6: Create Database Records (Reference Data + Documents)

**CRITICAL STEP:** Ensure all reference data exists, then create document records before moving PDFs to processed folder.

#### 6A: Load Missing Entities from Config

```sql
-- Load missing entities from account-mappings.json
INSERT INTO entities (entity_name, entity_type, tax_id, primary_taxpayer, georgia_resident, created_at, updated_at)
VALUES
    ('Kernan Family', 'individual', '2222', 'Richard Michael Kernan', true, NOW(), NOW()),
    ('HMA Group, LLC', 'llc', 'PLACEHOLDER_EIN_HMA', 'HMA Group, LLC', true, NOW(), NOW()),
    ('T&M Nevada Real Estate Holdings, LLC', 'llc', 'PLACEHOLDER_EIN_TMNEVADA', 'T&M Nevada Real Estate Holdings, LLC', false, NOW(), NOW()),
    ('Milton Preschool Inc', 's_corp', 'PLACEHOLDER_EIN_MILTON', 'Milton Preschool Inc', true, NOW(), NOW())
ON CONFLICT (entity_name) DO NOTHING;
```

#### 6B: Load Missing Accounts from Config

```sql
-- Load missing accounts from account-mappings.json
INSERT INTO accounts (
    account_number, account_holder_name, account_name, account_type, account_subtype,
    institution_id, entity_id, is_tax_deferred, is_tax_free, requires_rmd,
    created_at, updated_at
)
SELECT
    vals.account_number, vals.account_holder_name, vals.account_name,
    vals.account_type, vals.account_subtype, i.id, e.id,
    vals.is_tax_deferred, vals.is_tax_free, vals.requires_rmd, NOW(), NOW()
FROM (VALUES
    ('Z24-527872', 'RICHARD M KERNAN AND PEGGY E KERNAN', 'Joint Brokerage', 'brokerage', 'joint_taxable', 'Fidelity', 'Kernan Family', false, false, false),
    ('Z27-375656', 'RICHARD M KERNAN AND PEGGY E KERNAN', 'Cash Management Account', 'cash_management', 'joint_cash', 'Fidelity', 'Kernan Family', false, false, false),
    ('Z40-394067', 'MILTON PRESCHOOL INC', 'Brokerage Account', 'brokerage', 'corporate', 'Fidelity', 'Milton Preschool Inc', false, false, false),
    ('Z28-257895', 'RICHARD M KERNAN CUSTODIAN FOR TIMOTHY W KERNAN A MINOR', 'UTMA Account', 'custodial', 'utma', 'Fidelity', 'Kernan Family', false, false, false),
    ('238-908592', 'RICHARD M KERNAN', 'Traditional IRA', 'retirement', 'traditional_ira', 'Fidelity', 'Kernan Family', true, false, true),
    ('239-694275', 'RICHARD M KERNAN', 'Roth IRA', 'retirement', 'roth_ira', 'Fidelity', 'Kernan Family', false, true, false),
    ('Z40-394071', 'HMA GROUP, LLC', 'Brokerage Account', 'brokerage', 'corporate', 'Fidelity', 'HMA Group, LLC', false, false, false),
    ('Z25-666083', 'T&M NEVADA REAL ESTATE HOLDINGS, LLC', 'Brokerage Account', 'brokerage', 'corporate', 'Fidelity', 'T&M Nevada Real Estate Holdings, LLC', false, false, false)
) AS vals(account_number, account_holder_name, account_name, account_type, account_subtype, institution_name, entity_name, is_tax_deferred, is_tax_free, requires_rmd)
JOIN institutions i ON i.institution_name = vals.institution_name
JOIN entities e ON e.entity_name = vals.entity_name
ON CONFLICT (institution_id, account_number) DO NOTHING;
```

#### 6C: Create Document Records

For each processed PDF, create a document record using metadata from extraction JSON files:

```sql
-- Extract metadata from JSON first, then run INSERT
-- Example for Fid_Stmnt_2025-07_HMA.pdf:
INSERT INTO documents (
    institution_id, tax_year, document_type,
    period_start, period_end, file_path, file_name,
    doc_md5_hash, processed_at, processed_by
) VALUES (
    '33333333-3333-3333-3333-333333333333',  -- Fidelity institution ID
    2025, 'statement',
    '2025-07-01', '2025-07-31',  -- From extraction JSON document_data
    '/Users/richkernan/Projects/Finances/documents/3processed/',
    'Fid_Stmnt_2025-07_HMA.pdf',  -- From extraction JSON metadata
    '96084b875762cacdfd1fbaf9771bb5fb',  -- From extraction JSON doc_md5_hash
    NOW(),
    'Claude - process-inbox'
) ON CONFLICT (doc_md5_hash) DO NOTHING;
```

**Required metadata sources:**
- `doc_md5_hash`: From `extraction_metadata.doc_md5_hash` in JSON
- `file_name`: From `extraction_metadata.source_pdf_filepath` in JSON
- `period_start/end`: From `document_data.period_start/end` in JSON
- `tax_year`: Extract year from period_start date

**Key Design Points:**
- **Reference data first** - Entities and accounts loaded before documents
- **Uses extraction metadata** - Period dates and PDF hash from JSON files
- **Database UUID generation** - Let PostgreSQL handle ID generation
- **Conflict handling** - ON CONFLICT DO NOTHING prevents duplicates
- **Fail-fast** - Stops on any error to prevent incomplete state
- **Institution ID** - Hardcoded Fidelity ID from schema (33333333-3333-3333-3333-333333333333)

### Step 7: Clean Up (When Appropriate)

Only after successful processing AND database record creation:
```bash
# Move from staged to processed (already has correct name)
mv /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-08_Brok+CMA.pdf \
   /Users/richkernan/Projects/Finances/documents/3processed/Fid_Stmnt_2024-08_Brok+CMA.pdf
```

But if there were issues, keep it in staged and note why:
```
Keeping Fid_Stmnt_2024-08_Brok+CMA.pdf in staged folder - manual review needed for option positions
```

### Sequential Processing (When User Wants Both)

**IMPORTANT:** Holdings and activities must be processed sequentially, not in parallel, because holdings requires CSV extraction first.

**Recommended Process:**
1. **Holdings First (Hybrid):**
   - Extract CSV from statement (manual step for now)
   - Run Python CSV extraction script → creates base JSON
   - Run LLM agent to augment JSON with PDF-only fields

2. **Activities Second (Traditional):**
   - Run LLM agent for full activities extraction from PDF

**Example Sequential Processing:**
```bash
# Step 1A: CSV Extraction (manual CSV export required first)
python3 scripts/csv_to_holdings_json.py /path/to/statement.csv /documents/4extractions/
# Creates: Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.30ET.json (base structure)

# Step 1B: LLM Augmentation
Task(description="Augment CSV holdings", subagent_type="fidelity-statement-extractor", ...)
# Updates: Same JSON file with PDF-only fields

# Step 2: Activities extraction (after holdings complete)
Task(description="Extract activities", subagent_type="fidelity-statement-extractor", ...)
# Creates: Fid_Stmnt_2024-08_Brok+CMA_activities_2024.09.22_15.32ET.json (new file)

# Final Results:
- Holdings: Complete JSON with CSV data + PDF augmentation
- Activities: Complete JSON from PDF extraction
```

**Why Sequential:**
- Holdings CSV extraction must complete before LLM augmentation
- Parallel processing would break the hybrid workflow
- Activities can run independently after holdings completes

### Handling Edge Cases

**When the agent asks questions it can't answer:**
The agent might stop and report:
```
"Found unfamiliar security type 'RESTRICTED WARRANTS' on page 22.
Need guidance on classification."
```

You'll need to:
1. Look at the specific issue
2. Consult with the user
3. Either retry with additional context or handle manually
4. Consider adding new patterns to `/config/data-mappings.json` for future automation

**When transaction classification fails:**
If the automatic mapping system encounters unknown patterns:
```
"Transaction description 'SPECIAL DIVIDEND - RARE CASE' not found in mappings.
Classified as 'unknown' - manual review recommended."
```

Check the mapping system logs and consider updating the configuration for better future classification.

**When no agent exists:**
```
This appears to be a Bank of America statement.
We don't have an extraction agent for BofA yet.

Options:
1. I can help you process it manually
2. We can create a BofA extraction guide for future use
3. Skip for now and focus on Fidelity documents
```

### User Interaction Approach

After presenting findings, always ask: **"I found [X] file(s). What do you want to do next?"**

- Provide some common options as suggestions
- Accept any freeform response from the user
- Clarify if their request is unclear
- Don't force them into predefined choices

### Success Indicators

You'll know processing went well when:
- [ ] Each document has been addressed (processed or intentionally skipped)
- [ ] JSON extraction files are created with proper naming
- [ ] Agent reports show successful completion with automatic transaction classification
- [ ] Processed PDFs are moved to `/documents/3processed/`
- [ ] Any issues are clearly documented for follow-up
- [ ] Transaction types are automatically classified using the mapping system

### Remember

- Sub-agents are fire-and-forget - they can't have a conversation
- Each agent run produces a report you need to interpret
- Keep the user informed of progress and decisions
- When in doubt, ask the user rather than guess
- Document what was done for each file

---

## Example Session

**User:** `/process-inbox`

**You:**
```
Checking inbox...

Found 2 documents:
1. Fidelity statement for Milton Preschool Inc (Dec 2024)
   - Account Z40-394067 not in mappings
   - Should I add mapping: 4067 → 'Milton'?

2. 1099 for Johnson Trust (2024)
   - We don't have a 1099 extraction agent yet

Would you like me to:
1. Update mappings and process the Fidelity statement?
2. Skip to document #2?
```

**User:** "Both please"

**You:**
```
I'll extract both holdings and activities from the Fidelity statement using parallel processing.

[Running both Task tools in parallel...]

[Agents produce reports simultaneously:
- Holdings: "Successfully extracted holdings for 2 accounts - Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.45ET.json"
- Activities: "Successfully extracted activities for 2 accounts - Fid_Stmnt_2024-08_Brok+CMA_activities_2024.09.22_15.47ET.json"]

✓ Both extractions successful:
- Holdings: 2 accounts, 52 positions extracted
- Activities: 2 accounts, 38 transactions extracted

Moving the processed document...
mv /Users/richkernan/Projects/Finances/documents/2staged/FidelityStatement_Aug2024.pdf /Users/richkernan/Projects/Finances/documents/3processed/Fid_Stmnt_2024-08_Brok+CMA.pdf

Done with the statement. For the 1099 form, we'll need to process that manually. Would you like to do that now?
```

---

*This command helps you orchestrate document processing efficiently while maintaining visibility into what the sub-agents are doing and keeping the user informed throughout the process.*