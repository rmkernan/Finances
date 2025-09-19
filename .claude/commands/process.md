# Process Documents Command

**Created:** 09/19/25 12:45PM ET
**Updated:** 09/19/25 12:47PM ET - Added project context for new Claude instances
**Updated:** 09/19/25 12:50PM ET - Restructured with progressive disclosure approach
**Updated:** 09/19/25 12:54PM ET - Clarified vision: transforming paper/PDFs into LLM-queryable database
**Updated:** 09/19/25 1:09PM ET - Updated to reference single comprehensive fidelity.md guide
**Updated:** 09/19/25 1:16PM ET - Fixed path to institution-guides, improved question examples
**Updated:** 09/19/25 1:20PM ET - Implemented token-efficient survey-first workflow
**Updated:** 09/19/25 1:33PM ET - Removed process-inbox reference, consolidated into institution guides
**Updated:** 09/19/25 2:04PM ET - Optimized survey approach from 50 to 25 lines based on token efficiency analysis
**Updated:** 09/19/25 2:07PM ET - Added account mappings reference for friendly account names in survey results
**Updated:** 09/19/25 2:18PM ET - Added filename-based duplicate checking workflow using database query
**Updated:** 09/19/25 2:34PM ET - Added explicit stop point with visual indicators to prevent premature extraction
**Updated:** 09/19/25 2:57PM ET - Added scale assessment integration and example workflow updates
**Purpose:** Orient Claude to financial document processing task with just-in-time learning
**Philosophy:** Human-AI teamwork, not automation

## Command: `/process`

### The Big Picture

This project transforms paper and PDF financial statements into an LLM-queryable database, allowing the user to have intelligent conversations with their financial data through Claude. Instead of digging through stacks of statements, the user will be able to ask questions like "What were my dividend earnings from municipal bonds last quarter?" or "Show me all options trades in August" and get immediate, accurate answers.

Your current role is to collaborate with the user to:
1. **Digest** source financial documents (PDFs from Fidelity, banks, etc.)
2. **Extract** structured data (transactions, positions, income) according to a specified format depending on the source file

This is collaborative work - you'll be working with the user making decisions together, asking questions when uncertain, and learning from the user's corrections. The user knows their finances better than any document; you're the intelligent assistant transforming tedious paper into intelligent, queryable data.

### The Document Processing Workflow

Here's how documents flow through the system:

1. **Arrival** - PDFs land in `/documents/inbox/` with generic names like "Statement8312025.pdf"
2. **Identification** - You read enough to determine institution, document type, and period
3. **Extraction** - Following patterns specific to that institution, extract all financial data
4. **Structured Output** - Create JSON files with consistent structure for database loading
5. **Smart Renaming** - Both source PDF and extraction get intuitive names like `Fid_Stmnt_2025-08_Brok&CMA`
6. **Loading** - Your structured output will be loaded to the DB using python scripts

### Your Toolkit

These resources are available - use them as needed based on what you discover:

**Start Here:**
- **`/Users/richkernan/Projects/Finances/CLAUDE.md`** - READ THIS FIRST. Contains project context, entities involved, tax complexity, and core philosophy

**Institution-Specific Resources (use after identifying document type):**
- **`/config/institution-guides/fidelity.md`** - Complete Fidelity extraction guide (field mappings, patterns, examples)
- Additional institution guides will be created as needed (e.g., `boa.md`, `suntrust.md`)

**For Account Identification:**
- **`/config/account-mappings.json`** - Translates account numbers to friendly labels (7872→Brok, 5656→CMA)
  - Load this during survey to show user-friendly account names
  - Use for generating intuitive filenames

### Discovery Phase

**Your First Steps:**

1. **Read CLAUDE.md** to understand the project context and philosophy
2. **Survey the inbox** with minimal token usage:
   ```bash
   ls -la /Users/richkernan/Projects/Finances/documents/inbox/
   ```
3. **Quick identification** - For each PDF, read ONLY the first 25 lines:
   ```python
   Read(file_path="/documents/inbox/Statement8312025.pdf", limit=25)
   ```
   This gives you enough to identify:
   - Institution (Fidelity, Bank of America, etc.)
   - Document type (monthly statement, 1099, etc.)
   - Period covered (month/year)
   - Page count
   - Account numbers (for mapping to friendly names)

4. **Load account mappings** to translate account numbers:
   ```python
   Read(file_path="/config/account-mappings.json")
   ```

5. **Check for duplicates** using generated filenames:  !!Ignore this step. It has not yet been built out!!
   ```sql
   -- Generate expected filename: Fid_Stmnt_2025-08_Brok+CMA.pdf
   -- Query database for existing documents
   SELECT d.id, d.processed_at, d.extraction_json_path, i.institution_name
   FROM documents d
   JOIN institutions i ON d.institution_id = i.id
   WHERE d.source_filename = '[generated_filename]';
   ```

6. **Present findings** to the user with friendly account names and duplicate status, let them choose what to process

---

# 🛑 STOP HERE AND WAIT FOR USER RESPONSE

**DO NOT proceed until the user explicitly selects which documents to process.**

Present findings exactly like this and wait:
"I've surveyed the inbox and found X documents:
[list with status]
Which would you like to process? (all / specific numbers / skip)"

---

## Extraction Phase (ONLY AFTER user selection)

**ONLY AFTER the user selects documents**, then:
- Read the FULL selected document(s)
- Load the appropriate institution-specific guide(s)
- Load account mappings to translate account numbers to friendly names
- **Assess document scale** using the scale assessment in the institution guide
- **Choose extraction strategy** based on scale (file editing / memory+checkpoints / memory+Task tool)
- Proceed with extraction following the recommended approach

### Starting the Conversation

After the quick survey, present your findings:

"I've surveyed the inbox and found 3 documents:

1. **Fidelity statement** - August 2025 (36 pages)
   - Accounts: Z24-527872 (Brok) + Z27-375656 (CMA)
2. **Fidelity statement** - July 2025 (34 pages)
   - Accounts: Z24-527872 (Brok) + Z27-375656 (CMA)
3. **Bank of America statement** - August 2025 (8 pages)
   - Account: 1234 (checking)

Which would you like to process? (all / specific numbers / skip)"

**After user selection**, then dive deep:

"Great! Let me read the full August Fidelity statement and load the Fidelity extraction guide..."
[Read full document and institution guide]
"This is a 36-page statement with 50+ holdings and 80+ transactions - qualifies as 'Large' per the Fidelity guide. I'll use the memory-first approach with Task tool for bulk sections."
[Proceed with scale-appropriate extraction strategy]

### Engagement Principles

**Show Your Thinking:**
- "I'm looking at page 8 where the transaction details begin..."
- "I notice this has both regular securities and options transactions..."

**Ask When Uncertain:**
- "I see a transaction type 'SECURITIES LENDING INCOME' that's not in the guide - how should I categorize this?"
- "There's a wire transfer to 'ABC Corp' - which entity does this relate to?"

**Confirm Important Details:**
- "I found a new account ending in 9943. What label should I use?"
- "This appears to be an amended statement. Should I link it to the original?"

### Progressive Processing

1. **Start broad** - Understand the document as a whole
2. **Get specific** - Dive into transaction details using the institution map
3. **Extract systematically** - Follow the patterns in process-inbox.md
4. **Create meaningful output** - Use naming conventions from account-mappings.json
5. **Validate together** - Review what was extracted before moving forward

### Example Interaction Flow

**You:** "I see Statement8312025.pdf in the inbox. Let me identify what this is..."
[Read PDF]
"This is a Fidelity statement for August 2025. It contains two accounts - Brokerage and CMA. Should I proceed with extraction?"

**User:** "Yes, go ahead"

**You:** "I'll extract the data following the Fidelity document map. I'll show you my progress as I work through each section..."
[Extract data]
"I've found 23 transactions, 12 positions, and income summaries. The data will be saved as Fid_Stmnt_2025-08_Brok&CMA_2025.09.19_13.00ET.json. Should I also rename the source PDF?"

**User:** "Yes, and then load it to the database"

**You:** "I'll rename the PDF to match and then use the load-extraction process to populate the database tables..."

### Remember

This is collaborative intelligence, not automation. You're helping make tedious work easier while ensuring accuracy through partnership. The user's knowledge of their finances combined with your ability to process documents systematically creates the best outcome.