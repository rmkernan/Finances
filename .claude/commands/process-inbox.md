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
**Purpose:** Guide Claude through orchestrating document processing from inbox using specialized extraction agents
**Usage:** User invokes this when ready to process financial documents

## Command: `/process-inbox`

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

**Note:** Ignore source filenames completely - extract all document details from PDF content.

For each document found:
1. **DO NOT Read the PDF file directly** - instead extract text from first 2 pages using Python provided below
2. Check account mappings from extracted text
3. Present findings simply:
   - "Found Fidelity statement for Milton Preschool (unmapped account 4067)"
   - "Found Chase statement for Smith Corp (already mapped as 'Smith')"

**Token-Efficient PDF Text Extraction:**
```bash
# Extract text from first 2 pages directly - DO NOT Read the PDF file
python3 -c "
import PyPDF2
with open('documents/1inbox/[filename].pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    print('=== PAGE 1 ===')
    print(reader.pages[0].extract_text())
    print('\n=== PAGE 2 ===')
    print(reader.pages[1].extract_text())
"
# Read the printed text output above, not the original PDF file
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

### Step 1: Stage & Rename Documents

For each document:
1. **Extract account information** from PDF content
2. **Look up accounts in mappings** at /Users/richkernan/Projects/Finances/config/account-mappings.json
3. **Use mapped names** for filename generation

If accounts are already mapped, proceed with staging. If unmapped accounts found:
1. Ask: "Found [Institution] statement with unmapped account XXXX. What short name should I use?"
2. Update the mapping file
3. Stage with mapped names:

```bash
# Use mapped account names for clarity
mv /Users/richkernan/Projects/Finances/documents/1inbox/Statement12312024.pdf /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-12_Milton.pdf
```

### Step 2: Duplicate Check & Present Findings

Now with properly named files, check for duplicates:
```bash
# Check if similar file exists in processed folder
ls -la /Users/richkernan/Projects/Finances/documents/3processed/Fid_Stmnt_2024-08*.pdf

# If exact match found: It's likely a duplicate
# If close match (different accounts): May be a different statement
# If no match: Safe to process
```

For amended documents:
```python
# If filename suggests it's the same document but content differs:
# Check if original shows "AMENDED" or "CORRECTED"
Read /Users/richkernan/Projects/Finances/documents/2staged/Fid_1099_2024_Brok+CMA.pdf (page 1)
# Look for "AMENDED" or "CORRECTED" text
```


After checking for duplicates, present your findings and ask what to do next:
```
Staging complete. Here's what I found:

STAGED FILES:
1. Fid_Stmnt_2024-08_Brok+CMA.pdf
   - Fidelity Investment Statement for August 2024
   - Accounts: Brokerage + CMA
   - 36 pages
   - ✅ No duplicate found in processed folder
   - ✓ Ready for extraction with fidelity-statement-extractor

2. BofA_Stmnt_2024-09_Checking.pdf
   - Bank of America checking statement
   - ✗ No extraction agent available
   - Options: Manual processing or skip

POTENTIAL ISSUES:
3. Fid_1099_2024_Brok+CMA.pdf
   - ⚠️ Similar file exists: Fid_1099_2024_Brok+CMA.pdf in processed folder
   - Content shows "AMENDED" marking
   - ✗ No 1099 extraction agent available anyway

I found these files. What do you want to do next?

Some options:
- Extract holdings from Fidelity statement
- Extract activities from Fidelity statement
- Extract both (parallel or serial)
- Skip Fidelity and handle Bank of America manually
- Review the amended 1099 situation
- Something else entirely

What would you like me to do?
```

### Step 3: Delegate to Sub-Agents

**Prerequisites before invoking any sub-agent:**
1. **Verify the PDF is readable and supported** (Fidelity statements currently)
2. **Specify extraction type explicitly** (holdings OR activities)
3. **Provide complete file path** to staged PDF
4. **Be ready to interpret the report** (success, partial, or failure)

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

**Proper Invocation Format:**

Use the Task tool with:
```python
Task(
    description="Extract holdings",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Holdings

Please extract HOLDINGS data from the following Fidelity statement:
/Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-12_Milton.pdf

Note: This file has been staged for processing (not in inbox).

Expected output:
- JSON extraction file in /documents/4extractions/
- Report on extraction success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**Alternative for Activities:**
```python
Task(
    description="Extract activities",
    subagent_type="fidelity-statement-extractor",
    prompt="""
EXTRACTION MODE: Activities

Please extract ACTIVITIES data from the following Fidelity statement:
/Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2024-08_Brok+CMA.pdf

Note: This file has been staged for processing (not in inbox).

Expected output:
- JSON extraction file in /documents/4extractions/
- Report on extraction success/issues
- Do NOT move the PDF - orchestrator will handle that
"""
)
```

**What to expect from the agent:**
- It will load its reference documents based on extraction mode
- It will create a timestamped JSON file in `/documents/4extractions/`
- It will produce a completion report with:
  - ✅ Success: Details of what was extracted, file created
  - ⚠️ Partial: What worked, what failed, why
  - ❌ Failed: Specific blocker that prevented extraction

**Important:** The agent is stateless and cannot ask follow-up questions. If it encounters an issue it can't resolve, it will document it in the report and exit.

### Step 4: Handle Agent Reports

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

### Step 5: Clean Up (When Appropriate)

Only after successful processing:
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

If the user wants both holdings and activities, run them in parallel:
```python
# Launch both extractions in parallel with a single message containing two Task tool calls:
Task(
    description="Extract holdings",
    subagent_type="fidelity-statement-extractor",
    prompt="EXTRACTION MODE: Holdings\n\nExtract HOLDINGS data from: /Users/richkernan/Projects/Finances/documents/2staged/[filename].pdf"
)
Task(
    description="Extract activities",
    subagent_type="fidelity-statement-extractor",
    prompt="EXTRACTION MODE: Activities\n\nExtract ACTIVITIES data from: /Users/richkernan/Projects/Finances/documents/2staged/[filename].pdf"
)

# Both agents will run simultaneously and return their reports
# Results:
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
- [ ] Agent reports show successful completion
- [ ] Processed PDFs are moved to `/documents/3processed/`
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