# Process Inbox Command

**Created:** 09/18/25 11:15AM ET
**Updated:** 09/22/25 3:00PM ET - Refactored for sub-agent orchestration with stateless execution model
**Updated:** 09/22/25 3:07PM ET - Enhanced overview with context and improved duplicate detection strategies
**Purpose:** Guide Claude through orchestrating document processing from inbox using specialized extraction agents
**Usage:** User invokes this when ready to process financial documents

## Command: `/process-inbox`

### Your Mission

You're the **Orchestra Conductor** for financial document processing. Your job is to:
1. **Assess** what documents need processing and detect potential duplicates
2. **Prepare** the right context and instructions for sub-agents
3. **Delegate** extraction work to specialized agents
4. **Interpret** agent reports and handle any issues
5. **Organize** successful extractions and maintain clean file structure

### Understanding the Workflow

**Document Flow:**
```
/documents/inbox/ (generic names) → Extraction → /documents/extractions/ (JSON)
                                                → /documents/processed/ (renamed PDFs)
```

**Your Role vs Sub-Agent Role:**
- **You:** Identify, coordinate, verify, handle exceptions
- **Sub-Agent:** Read PDF, extract specific data type, produce JSON, report outcome
- **Key:** Sub-agents can't ask questions mid-task - they either complete or report what blocked them

### Setting Sub-Agents Up for Success

Sub-agents need clear, complete instructions because they're stateless. Before invoking:
1. **Verify the PDF is readable** 
2. **Confirm it's a supported document type** (Fidelity statement currently)
3. **Specify extraction type explicitly** (holdings OR activities)
4. **Provide the full file path** (not relative paths)
5. **Be ready to interpret their report** (success, partial, or failure)

### Step 1: Discovery & Duplicate Check

First, see what needs processing:
```bash
# Check the inbox for new documents
ls -la /Users/richkernan/Projects/Finances/documents/inbox/
```

For each file found, you need to determine if it's already been processed. Since inbox files have generic names but processed files are renamed, you have three strategies:

**Strategy 1: Peek Inside and Predict Renamed File**
```python
# Read first few pages to get institution, document type, and period
Read /documents/inbox/Statement8312025.pdf (pages 1-3)

# Based on what you find, predict the renamed filename:
# - Institution: Fidelity → "Fid"
# - Type: Statement → "Stmnt"
# - Period: August 2024 → "2024-08"
# - Accounts: Map account numbers to labels using account-mappings.json
# Expected name: Fid_Stmnt_2024-08_Brok+CMA.pdf

# Check if this file already exists
ls /documents/processed/Fid_Stmnt_2024-08*.pdf
```

**Strategy 2: Hash Comparison** (Most Reliable)
```bash
# Calculate hash of inbox file
md5sum /documents/inbox/Statement8312025.pdf

# Compare against hashes of processed files
for file in /documents/processed/Fid*.pdf; do
  echo "$(md5sum "$file") - $file"
done

# If hashes match, it's a duplicate
```

**Strategy 3: Database Query** (When DB is built)
```sql
-- Query documents table for matching hash
SELECT file_name, file_hash, processed_at
FROM documents
WHERE file_hash = '[calculated_hash]';
```

### Step 2: Document Assessment

For each document in the inbox, you need to actually look inside:

```python
# Read the first few pages of each PDF to identify:
# - Institution (look for logos, letterhead)
# - Document type (statement, 1099, etc.)
# - Statement period/date
# - Account numbers mentioned

# For example, for a file called Statement8312025.pdf:
Read /Users/richkernan/Projects/Finances/documents/inbox/Statement8312025.pdf (first 3 pages)
```

After reading, check for these patterns:
- **Fidelity Statement**: Look for "Fidelity Investments" header, "Account Summary" section
- **Fidelity 1099**: Look for "1099-DIV", "1099-B", tax year reference
- **Bank Statement**: Look for bank name, "Statement Period", transaction listings
- **Duplicate Check**: Compare the statement date and account numbers against processed files

Load the account mappings to understand what you're looking at:
```python
Read /Users/richkernan/Projects/Finances/config/account-mappings.json
```

### Step 3: Present Findings to User

Only after doing the above work, present your assessment with specific details:
```
Found 3 documents in inbox:

1. Statement8312025.pdf
   - Fidelity Investment Statement for August 2024
   - Accounts: Z24-527872 (maps to "Brok"), Z27-375656 (maps to "CMA")
   - 36 pages total
   - ✓ Can process with fidelity-statement-extractor agent
   - Note: No August 2024 Fidelity statement found in processed folder

2. BofA_Statement.pdf
   - Bank of America checking statement for September 2024
   - Account: ****4521 (not in our mappings)
   - 12 pages
   - ✗ No extraction agent available
   - Would need manual processing or skip

3. 1099DIV_2024.pdf
   - Fidelity 1099-DIV for tax year 2024
   - ⚠️ Possible duplicate: Found "Fid_1099_2024_Brok+CMA.pdf" in processed folder
   - Hash comparison shows different file (might be amended version?)
   - ✗ No 1099 extraction agent yet

How would you like to proceed?
1. Process the Fidelity statement (holdings/activities/both)?
2. Check if the 1099 is an amended version?
3. Skip to manual processing for Bank of America?
```

### Step 4: Delegate to Sub-Agents

When you have a Fidelity statement to process:

```markdown
# For holdings extraction
I'll extract the holdings data from [filename].

Launching the fidelity-statement-extractor agent for holdings extraction...
@fidelity-statement-extractor Please extract holdings from /Users/richkernan/Projects/Finances/documents/inbox/[filename]
```

**What to expect from the agent:**
- It will read the PDF and reference documents
- It will create a JSON file in `/documents/extractions/`
- It will produce a report with one of these outcomes:
  - ✅ Success: "Extraction complete - Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.30ET.json"
  - ⚠️ Partial: "Extracted 2 of 3 accounts - account X12-9999 had unrecognized structure"
  - ❌ Failed: "Could not parse document - appears to be encrypted"

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

### Step 6: Clean Up (When Appropriate)

Only after successful processing:
```bash
# Move processed document with standardized name
mv /documents/inbox/Statement8312025.pdf /documents/processed/Fid_Stmnt_2024-08_Brok+CMA.pdf
```

But if there were issues, keep it in inbox and note why:
```
Keeping Statement8312025.pdf in inbox - manual review needed for option positions
```

### Parallel Processing (When User Wants Both)

If the user wants both holdings and activities:
```
I'll run both extractions. Since sub-agents are independent, I'll launch them sequentially:

1. Starting holdings extraction...
   @fidelity-statement-extractor Please extract holdings from [file]
   [Wait for report]

2. Starting activities extraction...
   @fidelity-statement-extractor Please extract activities from [file]
   [Wait for report]

Both extractions complete:
- Holdings: Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.30ET.json
- Activities: Fid_Stmnt_2024-08_Brok+CMA_activities_2024.09.22_15.32ET.json
```

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

**When no agent exists:**
```
This appears to be a Bank of America statement.
We don't have an extraction agent for BofA yet.

Options:
1. I can help you process it manually
2. We can create a BofA extraction guide for future use
3. Skip for now and focus on Fidelity documents
```

### Decision Points to Ask User

Always ask when:
- **Extraction type unclear**: "This Fidelity statement has both holdings and transactions. Which would you like extracted?"
- **Multiple documents**: "Found 5 documents. Process all, or select specific ones?"
- **Errors encountered**: "Extraction had errors. Review now or continue with other documents?"
- **Unknown formats**: "This document type is unfamiliar. Want to try anyway or skip?"

### Success Indicators

You'll know processing went well when:
- [ ] Each document has been addressed (processed or intentionally skipped)
- [ ] JSON extraction files are created with proper naming
- [ ] Agent reports show successful completion
- [ ] Processed PDFs are moved to `/documents/processed/`
- [ ] Any issues are clearly documented for follow-up

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
1. FidelityStatement_Aug2024.pdf (35 pages)
2. Fidelity_1099_2024.pdf (3 pages)

The first appears to be a Fidelity statement I can process with our extraction agent.
The second is a 1099 - we don't have an agent for that yet.

For the Fidelity statement, would you like me to extract:
- Holdings only
- Activities only
- Both
```

**User:** "Both please"

**You:**
```
I'll extract both holdings and activities from the Fidelity statement.

Starting with holdings extraction...
@fidelity-statement-extractor Please extract holdings from /Users/richkernan/Projects/Finances/documents/inbox/FidelityStatement_Aug2024.pdf

[Agent produces report: "Successfully extracted holdings for 2 accounts - Fid_Stmnt_2024-08_Brok+CMA_holdings_2024.09.22_15.45ET.json"]

✓ Holdings extraction successful - 2 accounts, 52 positions extracted

Now extracting activities...
@fidelity-statement-extractor Please extract activities from /Users/richkernan/Projects/Finances/documents/inbox/FidelityStatement_Aug2024.pdf

[Agent produces report: "Successfully extracted activities for 2 accounts - Fid_Stmnt_2024-08_Brok+CMA_activities_2024.09.22_15.47ET.json"]

✓ Activities extraction successful - 2 accounts, 38 transactions extracted

Both extractions complete! Moving the processed document...
mv /documents/inbox/FidelityStatement_Aug2024.pdf /documents/processed/Fid_Stmnt_2024-08_Brok+CMA.pdf

Done with the statement. For the 1099 form, we'll need to process that manually. Would you like to do that now?
```

---

*This command helps you orchestrate document processing efficiently while maintaining visibility into what the sub-agents are doing and keeping the user informed throughout the process.*