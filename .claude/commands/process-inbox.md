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
**Updated:** 09/25/25 1:12PM - Added unique constraints for entity_name and institution_name, updated conflict handling to use proper composite keys
**Updated:** 09/26/25 2:00PM - Restructured extraction workflow with updated agent invocation formats
**Updated:** 09/26/25 2:12PM - Added PDF validation for holdings extraction workflow
**Updated:** 09/26/25 2:29PM - Fixed database connection command (added -U postgres flag) and added mandatory validation checkpoint with failure handling
**Updated:** 09/26/25 3:52PM - Fixed Quick Assessment section with clear step-by-step instructions
**Updated:** 09/26/25 4:07PM - Added critical instruction to read entire command before starting, preventing premature execution
**Updated:** 09/26/25 5:51PM - Complete removal of all CSV hybrid workflow sections, updated for pure LLM extraction
**Updated:** 09/26/25 5:54PM - Final cleanup of remaining CSV/hybrid workflow references in example sections
**Updated:** 09/29/25 6:12PM - Major restructure: Replaced Quick Assessment with single-pass Document Structure Analysis, added PDF trimming and page mapping for targeted sub-agent extraction
**Updated:** 09/29/25 6:40PM - Added mental verification step in Step 2 to recalculate page offsets after trimming, preventing page mapping errors without redundant PDF reads
**Updated:** 09/29/25 6:45PM - Changed extraction workflow to "one JSON per statement per type" (all accounts consolidated) instead of separate JSONs per account
**Updated:** 09/29/25 6:55PM - Critical fix: Clarified that account-level summary pages (with Account # header) must be KEPT during trimming, not removed with statement-level cover pages
**Purpose:** Guide Claude through orchestrating document processing from inbox using specialized extraction agents
**Usage:** User invokes this when ready to process financial documents

## Command: `/process-inbox`

### ⚠️ CRITICAL: READ THIS ENTIRE COMMAND FIRST ⚠️
**DO NOT start processing until you have read ALL sections of this document.**
This command contains specific instructions for document processing and extraction workflows.

### The Big Picture

This project transforms paper and PDF financial statements into an LLM-queryable database, allowing the user to have intelligent conversations with their financial data through Claude. Instead of digging through stacks of statements, the user will be able to ask questions like "What were my dividend earnings from municipal bonds last quarter?" or "Show me all options trades in August" and get immediate, accurate answers.

### Your Mission

You're the **Orchestra Conductor** for financial document processing. Your job is to:
1. **Assess** what documents need processing and detect potential duplicates
2. **Prepare** the right context and instructions for sub-agents
3. **Delegate** extraction work to specialized agents
4. **Interpret** agent reports and handle any issues
5. **Organize** successful extractions and maintain clean file structure

### Step 1: Document Structure Analysis & Preparation

**⚠️ This is a single-pass analysis that replaces the old two-step "Quick Assessment + Staging" workflow**

For each PDF in inbox, perform complete document analysis:

```bash
# List inbox files
ls -la /Users/richkernan/Projects/Finances/documents/1inbox/
```

**Then analyze the full document structure using PyPDF2:**

1. **Extract text from all pages** - Use `PdfReader` and extract_text() for complete document
2. **Identify key information:**
   - Institution type (look for "Fidelity", "Chase", "Vanguard", etc.)
   - Statement period (date ranges like "April 1, 2025 - April 30, 2025")
   - All account numbers (patterns like "Account # Z24-527872" or "Account Number:")
3. **Map page ranges** by scanning each page's text for section markers:
   - Account summary pages (account number + "Account Summary")
   - Holdings sections (account number + "Holdings" or "Positions" or "POSITIONS AS OF")
   - Activities sections (account number + "Activity" or "Trade History" or "TRADE HISTORY")
   - Extraneous sections to exclude:
     - "Estimated Cash Flow" pages
     - "Important Disclosure" or "Additional Information" in last 5 pages
     - Legal disclaimers and fine print
4. **Determine page ranges** for sub-agent extraction:
   - Group consecutive pages by account and section type
   - Example: "Account 1 holdings spans pages 4-15"
5. **Identify pages to trim** - List all pages that should be excluded

**Present findings in this format:**
```
✅ FIDELITY Statement: April 2025
   Accounts: Z24-527872 (KernBrok), Z27-375656 (KernCMA)
   Total: 30 pages → Recommend trimming to 26 pages

   HOLDINGS EXTRACTION:
   - Account Z24-527872: pages 4-15 (12 pages)
   - Account Z27-375656: pages 22-24 (3 pages)

   ACTIVITIES EXTRACTION:
   - Account Z24-527872: pages 16-20 (5 pages)
   - Account Z27-375656: pages 25-26 (2 pages)

   RECOMMEND EXCLUDING: pages 27-30 (cash flow + disclaimers)
```

**Important:** Ignore source filenames - extract all information from PDF content only.

### Step 2: Trim PDF & Parallel Validation

Once you have the page map, trim extraneous pages and run all validations in parallel.

**First, trim the PDF to remove extraneous pages:**

Use PyPDF2 to create a new PDF with only the relevant pages.

**CRITICAL - Keep these pages:**
- **Account-level summary pages** (pages with "Account # XXXXX" header + Net Account Value, Change in Account Value, Additions/Subtractions)
- **Holdings/positions data** (all subsections: Mutual Funds, Bonds, Stocks, Options, etc.)
- **Activities/transactions data** (Trade History, Income, Realized Gains, etc.)

**Exclude these pages:**
- Estimated Cash Flow projections (typically page 21 or near end)
- Legal disclaimers (typically last 3-5 pages with "Important Disclosure" or "Additional Information")
- Statement-level cover pages (first 1-3 pages) **ONLY if they don't contain account-specific data**

**Rule of thumb:** If a page shows "Account # Z24-XXXXXX" at the top, it's account-specific data - KEEP IT.

**After trimming, VERIFY YOUR PAGE MAPPING:**

Don't re-read the PDF. Instead, mentally recalculate the page numbers:

1. **List what you removed:** "I removed pages 1-3 and pages 27-30"
2. **Calculate page count:** Original X pages - Y removed = Z pages remaining
3. **Determine offset for each range:**
   - Pages before first removal: no offset
   - Pages after removing 1-3: subtract 3
   - Pages after removing 21: subtract 4 total (3 from earlier + 1 more)
   - Pages after removing 27-30: subtract 7 total (3 + 1 + 4)
4. **Apply offset to your original page map:**
   - "Original page 4 → Trimmed page 1" (4 - 3 = 1)
   - "Original page 22 → Trimmed page 18" (22 - 4 = 18)
5. **Verify your math:** Trimmed page ranges should make sense given the page count

**Then run validation checks in parallel:**

```bash
# Run ALL commands in parallel using multiple Bash tool calls in single message:

# 1. Generate MD5 hash for duplicate detection
md5 /Users/richkernan/Projects/Finances/documents/1inbox/[filename]_trimmed.pdf

# 2. Check for duplicate hash in extractions
grep -r "[hash_value]" /Users/richkernan/Projects/Finances/documents/4extractions/*.json 2>/dev/null || echo "No hash duplicates"

# 3. Check for similar processed files
ls -la /Users/richkernan/Projects/Finances/documents/3processed/[similar_pattern]*.pdf 2>/dev/null || echo "No processed duplicates"

# 4. Verify database accounts exist
PGPASSWORD=postgres psql -U postgres -h localhost -p 54322 -d postgres -c "SELECT a.account_number, a.account_type, i.institution_name FROM accounts a JOIN institutions i ON a.institution_id = i.id WHERE a.account_number IN ('[account1]', '[account2]');"
```

**VALIDATION CHECKPOINT:**
Before proceeding, verify ALL validation checks succeeded:
- ✅ PDF trimmed successfully with correct page count
- ✅ Page mapping recalculated and verified
- ✅ MD5 hash generated
- ✅ No duplicate hash in existing extractions
- ✅ No similar files in processed folder
- ✅ Database connection successful and accounts exist

**If any validation fails, STOP and ask user how to proceed.**

### Step 3: Account Resolution & Staging

Now stage the trimmed PDF with proper naming:

1. **Look up accounts** in [account-mappings.json](../config/account-mappings.json)
   - **Extract lookup key:** Use last 4 digits of account number
     - Example: `Z24-527872` → lookup key `"7872"`
     - Find in mappings: `accounts.fidelity["7872"]`
2. **Use mapped names** (`filename_label` field) for filename generation

**Account Matching Rules:**
- **Exact match:** Account in mappings → Use existing metadata, proceed with staging
- **Minor discrepancies:** Account matches but holder names differ → Do NOT overwrite mappings, use existing data
- **Unknown account:** Account not in mappings → STOP and ask user for complete metadata

**If unknown accounts found:**
1. Ask: "Found [Institution] account XXXX for [Holder]. Not in mappings. Should I add it?"
2. If yes, ask for complete metadata (entity, account type, etc.)
3. Update the mapping file
4. Proceed with staging

**Stage the trimmed PDF:**
```bash
# Use mapped account names for clarity
mv /Users/richkernan/Projects/Finances/documents/1inbox/[filename]_trimmed.pdf \
   /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf
```

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

### Step 4: Present Findings & Get User Direction

**All validation and staging completed.** Now present findings with the page map and ask what to do next:

For amended documents:
```python
# If filename suggests it's the same document but content differs:
# Check if original shows "AMENDED" or "CORRECTED"
Read /Users/richkernan/Projects/Finances/documents/2staged/Fid_1099_2024_Brok+CMA.pdf (page 1)
# Look for "AMENDED" or "CORRECTED" text
```


Present your findings with the complete page map and ask what to do next:
```
Staging complete. Here's what I found:

STAGED FILE:
Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf (26 pages, trimmed from 30)

✅ FIDELITY Statement: April 2025
   MD5: [use value from Step 2 validation]
   Accounts: Z24-527872 (KernBrok), Z27-375656 (KernCMA)
   ✅ No duplicates found
   ✅ Database accounts verified

📄 PAGE MAP FOR EXTRACTION (trimmed PDF page numbers):

   HOLDINGS (all accounts):
   - Account Z24-527872 (KernBrok): pages 1-12 (12 pages)
   - Account Z27-375656 (KernCMA): pages 19-21 (3 pages)

   ACTIVITIES (all accounts):
   - Account Z24-527872 (KernBrok): pages 13-17 (5 pages)
   - Account Z27-375656 (KernCMA): pages 22-23 (2 pages)

   EXCLUDED FROM ORIGINAL: pages 1-3, 27-30 (removed during trimming)

What do you want to do next?

Options:
- Extract holdings (all accounts - one JSON file)
- Extract activities (all accounts - one JSON file)
- Extract both holdings and activities
- Something else

What would you like me to do?
```

### Step 5: Extraction Process

**Both holdings and activities use pure LLM extraction:**
- Single-stage process for both extraction types
- LLM extracts all data directly from PDF
- Creates complete JSON from scratch
- Holdings and activities can be extracted in parallel if desired

**Prerequisites before invoking any sub-agent:**
1. **Verify the PDF is readable and supported** (Fidelity statements currently)
2. **Specify extraction type explicitly** (holdings OR activities)
3. **Provide complete file path** to the staged (trimmed) PDF
4. **Provide specific page ranges** for the account being extracted (from your page map)

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
5. **BE EXPLICIT about which pages to read and which to skip** (critical for accuracy)

**CRITICAL - Explicit Page Instructions:**

Based on your document analysis from Step 1, you know EXACTLY which pages contain the data you need and which pages don't. Use this knowledge to give the sub-agent EXPLICIT READ/DON'T READ instructions:

✅ **DO THIS** (Explicit):
```
READ ONLY THESE PAGES:
- Pages 1-12: Account Z24-527872 Holdings
- Pages 19-21: Account Z27-375656 Holdings

DO NOT READ:
- Pages 13-18: Activities sections (not needed for holdings)
- Page 22: Activities section (not needed for holdings)

STOP READING after page 21. You have all required holdings data.
```

❌ **NOT THIS** (Implicit):
```
PAGE MAP:
- Account Z24-527872: pages 1-12
- Account Z27-375656: pages 19-21
```

**Why this matters:** Experiment results show explicit instructions improve data quality by reducing ambiguity and preventing the sub-agent from mixing contexts between different sections.

**Pattern for constructing explicit instructions:**
1. List pages TO READ (with account labels)
2. List pages NOT TO READ (with explanation of what they contain)
3. State when to STOP READING (after last relevant page)

**Holdings Invocation Format (Pure LLM with Explicit Page Instructions):**

Use the Task tool with:
```python
Task(
    description="Extract holdings",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Holdings
DOC_MD5_HASH: [insert_md5_hash_here]
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf

READ ONLY THESE PAGES:
- Pages 1-12: Account Z24-527872 (KernBrok) Holdings
- Pages 19-21: Account Z27-375656 (KernCMA) Holdings

DO NOT READ:
- Pages 13-18: Activities sections (not needed for holdings)
- Page 22: Activities section (not needed for holdings)

STOP READING after page 21. You have all required holdings data.

Please extract HOLDINGS data for ALL ACCOUNTS in this statement.

CRITICAL: Extract all accounts found in the statement into a single JSON file. Focus ONLY on the pages specified above.

- EXTRACT holdings/positions for ALL accounts using the page map
- CREATE complete JSON from scratch using Map_Stmnt_Fid_Positions.md
- FOLLOW the mapping document to locate and extract ALL fields
- INCLUDE doc_md5_hash in output
- SAVE as new JSON file in /documents/4extractions/ (one file for entire statement)

Expected output:
- New JSON extraction file in /documents/4extractions/ containing all accounts
- Report on extraction success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**Activities Invocation Format (Pure LLM with Page Ranges):**

```python
Task(
    description="Extract activities",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Activities
DOC_MD5_HASH: [insert_md5_hash_here]
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf

READ ONLY THESE PAGES:
- Pages 13-17: Account Z24-527872 (KernBrok) Activities
- Pages 22-23: Account Z27-375656 (KernCMA) Activities

DO NOT READ:
- Pages 1-12: Holdings sections (not needed for activities)
- Pages 18-21: Holdings section (not needed for activities)

STOP READING after page 23. You have all required activities data.

Please extract ACTIVITIES data for ALL ACCOUNTS in this statement.

CRITICAL: Extract all accounts found in the statement into a single JSON file. Focus ONLY on the pages specified above.

- EXTRACT all transaction data for ALL accounts using the page map
- CREATE complete JSON from scratch using Map_Stmnt_Fid_Activities.md
- INCLUDE doc_md5_hash in output
- SAVE as new JSON file in /documents/4extractions/ (one file for entire statement)

Expected output:
- New JSON extraction file in /documents/4extractions/ containing all accounts
- Report on extraction success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**What to expect from the agent:**

**For both Holdings and Activities:**
- Reads PDF and creates complete JSON from scratch
- Uses full LLM extraction process
- Creates new timestamped JSON file

**Both modes produce completion reports with:**
- ✅ Success: Details of what was extracted, files created
- ⚠️ Partial: What worked, what failed, why
- ❌ Failed: Specific blocker that prevented extraction

**Important:** The agent is stateless and cannot ask follow-up questions. If it encounters an issue it can't resolve, it will document it in the report and exit.

### Step 6: Handle Agent Reports

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

### Step 7: Create Database Records (Reference Data + Documents)

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

### Step 8: Clean Up (When Appropriate)

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

### Parallel Processing (When User Wants Both)

**Holdings and activities can now be processed in parallel since both use pure LLM extraction.**

**Recommended Process:**
When the user wants both holdings and activities, you can invoke both Task tools in a single message for parallel execution.

**Example Parallel Processing:**
```python
# Send both Task invocations in a single message:
Task(description="Extract holdings", subagent_type="fidelity-statement-extractor", ...)
Task(description="Extract activities", subagent_type="fidelity-statement-extractor", ...)

# Both agents will run simultaneously and produce:
- Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.30ET.json
- Fid_Stmnt_2024-08_Brok+CMA_activities_2024.09.22_15.32ET.json
```

**Benefits of Parallel Processing:**
- Faster overall extraction time
- Both extractions complete independently
- No dependency between holdings and activities

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