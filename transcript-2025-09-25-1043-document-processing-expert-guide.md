# Document Processing & Extraction Loading Expert Guide - Distilled Conversation

**Created:** 09/25/25 10:43AM ET
**Purpose:** Expert-level guidance on financial document processing workflows, agent coordination, and database loading for the Claude-assisted financial management system

## Context for Claude

This is a cleaned transcript focused on document processing expertise. You are inheriting deep knowledge of the `/process-inbox` and `/load-extractions` commands, file workflow management, agent coordination patterns, and database loading logic. This system processes financial PDFs through specialized extraction agents and loads structured data into PostgreSQL.

## Referenced Documentation

**Key files that inform this workflow:**
- `/.claude/commands/process-inbox.md` - Complete orchestration workflow for document processing
- `/.claude/commands/load-extractions.md` - Database loading procedures with validation
- `/.claude/agents/fidelity-statement-extractor.md` - Specialized PDF extraction agent specs
- `/config/account-mappings.json` - Account resolution and entity mapping
- `/loaders/simple_loader.py` - Database loading script with incremental loading

**Critical workflow understanding:**
- Documents flow: `/1inbox/` → `/2staged/` → `/4extractions/` → `/5loaded/` with PDFs going to `/3processed/`
- Agent-based extraction with stateless sub-agents requiring complete prompts
- Incremental loading supporting both holdings and activities for same document
- Timestamp format requirements: `YYYY.MM.DD_HH.MMET` (not ISO format)

---

## Process-Inbox Command Execution

I need to run the process-inbox command. Let me first read the command documentation:

The process-inbox command guides orchestration of document processing from inbox using specialized extraction agents. The workflow is:

**Document Flow:**
```
/documents/1inbox/ (generic names) → Staging → /documents/2staged/ (renamed PDFs)
                                              → Extraction → /documents/4extractions/ (JSON)
                                              → Completion → /documents/3processed/ (final archive)
```

I found one document in the inbox: `Statement7312025.pdf`. Let me extract text from the first 2 pages to identify what type of document this is.

This is a Fidelity Investment Report for July 2025 with accounts Z24-527872 (Joint Brokerage) and Z27-375656 (Cash Management Account). Both accounts are already mapped in the account-mappings.json:
- Account Z24-527872 → "KernBrok"
- Account Z27-375656 → "KernCMA"

Now let me generate the MD5 hash and check for duplicates in parallel, then stage the document:

Both accounts exist in the database and no duplicates were found. The document has been staged as `Fid_Stmnt_2025-07_KernBrok+KernCMA.pdf`.

Staging complete. Here's what I found:

**STAGED FILES:**
1. **Fid_Stmnt_2025-07_KernBrok+KernCMA.pdf**
   - Fidelity Investment Statement for July 2025
   - Accounts: Joint Brokerage (Z24-527872) + Cash Management (Z27-375656)
   - 32 pages
   - Portfolio value: $6,902,214.08
   - ✅ No duplicate found (hash: e884e535f5b8a8135e2ea130e076b6e1)
   - ✅ Accounts exist in database
   - ✓ Ready for extraction with fidelity-statement-extractor

What would you like me to do next?

Let's extract both activities and holdings from that July statement using parallel processing.

I'm ready to invoke the fidelity-statement-extractor agent twice in parallel. Here are the prompts I'll send:

**Holdings Extraction:**
```
EXTRACTION MODE: Holdings
DOC_MD5_HASH: e884e535f5b8a8135e2ea130e076b6e1

Please extract HOLDINGS data from the following Fidelity statement:
/Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-07_KernBrok+KernCMA.pdf
```

**Activities Extraction:**
```
EXTRACTION MODE: Activities
DOC_MD5_HASH: e884e535f5b8a8135e2ea130e076b6e1

Please extract ACTIVITIES data from the same Fidelity statement.
```

Both extractions completed successfully:

**Holdings Extraction Results:**
- 69 positions across 2 accounts (66 from Z24-527872 brokerage + 3 from Z27-375656 CMA)
- File created: `Fid_Stmnt_2025-07_KernBrok+KernCMA_holdings_2025.09.25_1454ET.json`

**Activities Extraction Results:**
- 91 transactions (71 from brokerage + 20 from CMA)
- File created: `Fid_Stmnt_2025-07_KernBrok+KernCMA_activities_2025.09.25_08.45ET.json`
- Notable: $270K in withdrawals to Coinbase, options trading activity, bond redemptions

Both agents reported successful extraction with no unknown patterns or issues.

## Critical Process Issue: PDF Movement

The PDF should have been moved from `/2staged/` to `/3processed/` after successful extractions, but it wasn't. This is because I bypassed the full process-inbox orchestration by directly invoking agents rather than following the complete workflow sequence.

**Process Flow Distinction:**
- **Direct agent invocation**: Gets extraction work done but skips workflow management
- **Full process-inbox command**: Includes complete orchestration with file management

The individual extraction agents correctly don't move PDFs (per instructions: "Do NOT move the PDF - orchestrator will handle that"), but I didn't complete the orchestration layer.

Moving the PDF to correct location and proceeding with load command.

## Load-Extractions Command Execution

Now following the load-extractions command to load the JSON files into the database.

**Found extraction files ready for loading:**
- Holdings: 69 positions, portfolio value calculation ready
- Activities: 91 transactions with automatic classification rules applied

## Critical Issue: Timestamp Format Problems

I discovered a timestamp format inconsistency between extraction agents:
- **Holdings file**: Wrong ISO format `2025-09-25T14:54:00Z` ❌
- **Activities file**: Correct format `2025.09.25_08.45ET` ✅

**Root Cause**: The fidelity-statement-extractor agent has inconsistent timestamp generation between extraction types.

**Solution Applied**: Updated the agent instructions with explicit Python code:
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M") + "ET"
```

Fixed the holdings file timestamp and recalculated its hash, then successfully loaded both files into the database.

## Multi-Document Processing: Milton Preschool Statements

Found unprocessed extraction files for Milton Preschool December 2024 statement. The source PDF was located in `/2staged/` and needed to be moved to `/3processed/` after the extractions were already complete - another example of incomplete workflow orchestration.

Successfully loaded Milton December 2024 data:
- Holdings: 4 positions ($477,071.17 total value)
- Activities: 13 transactions

## Parallel Agent Coordination

Extracted activities and holdings for both February and March 2024 Milton statements using 4 agents in parallel:

**Parallel Processing Technique:**
- Launch all 4 agents simultaneously using multiple Task tool calls in a single message
- Each agent gets complete context with DOC_MD5_HASH and extraction mode
- Agents work independently and report back simultaneously

**Results:**
- **February 2024**: 2 positions, 6 transactions
- **March 2024**: 6 positions (including 4 municipal bonds), 10 transactions

**Agent Reports Analysis:**
All 4 extractions completed with no issues:
- No errors or data quality problems
- All transaction patterns covered by existing mapping guidance
- No new security types requiring mapping rule updates
- 100% confidence levels across all extractions

## Database Loading Issues & Solutions

### Duplicate Document Hash Violations

**Problem Encountered:**
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "documents_doc_md5_hash_key"
```

**Root Cause Analysis:**
This occurs when running parallel extractions because of a race condition:
1. Two agents check simultaneously: "Does document exist?" → "No"
2. Both try to INSERT the same document
3. Second one fails with constraint violation

**The Real Issue:** The loader uses "ask forgiveness rather than permission" approach - tries to create document first, then handles incremental loading on failure.

**Solution Implemented:**
Added PostgreSQL "upsert" capability using `ON CONFLICT`:

```sql
INSERT INTO documents (...) VALUES (...)
ON CONFLICT (doc_md5_hash) DO UPDATE SET
    id = documents.id
RETURNING id
```

This eliminates scary error messages while maintaining data integrity and incremental loading functionality.

### Understanding Incremental Loading Logic

**Two-Level Duplicate Detection (Correct):**

**Level 1 - Document-Level (PDF):**
- Check if `doc_md5_hash` exists in database
- If exists: ✅ Expected and good - proceed to Level 2
- If not exists: Create new document record

**Level 2 - Extraction-Level (JSON):**
- **For Activities**: Check `activities_json_md5_hash` against current JSON
- **For Holdings**: Check `positions_json_md5_hash` against current JSON
- Load only if NULL or different hash value

**Critical Insight:** Having the document exist is not only OK, it's expected. The PDF should already be in database from the first extraction. The second extraction should add the missing data type to the existing document record.

## Document Summary View Creation

Created a human-friendly database view for loaded documents:

```sql
CREATE VIEW document_summary AS
SELECT
    file_name as document_name,
    institution_name,
    TO_CHAR(period_start, 'Mon YYYY') as period,
    tax_year,
    STRING_AGG(DISTINCT entity_name, ', ') as entities,
    STRING_AGG(DISTINCT account_number || ' (' || account_name || ')', ', ') as accounts,
    COUNT(DISTINCT positions.id) as positions_count,
    COUNT(DISTINCT transactions.id) as transactions_count,
    ROUND(SUM(DISTINCT positions.end_market_value), 2) as total_portfolio_value,
    CASE
        WHEN positions_loaded IS NOT NULL AND activities_loaded IS NOT NULL THEN 'Complete'
        WHEN positions_loaded IS NOT NULL THEN 'Holdings Only'
        WHEN activities_loaded IS NOT NULL THEN 'Activities Only'
        ELSE 'Not Loaded'
    END as data_status
FROM documents d
[joins and grouping logic]
```

**View shows:**
- Document name, institution, period in human-readable format
- Entities and accounts involved
- Data completeness status
- Portfolio values and transaction counts

## Final System State

**Database contains 5 complete documents:**
- **Milton Preschool**: Feb 2024, Mar 2024, Dec 2024 statements (~$477K-$793K portfolio)
- **Kernan Family**: Jul 2025, Aug 2025 statements (~$5.7M-$5.8M portfolio)
- **Total**: 150 positions, 260 transactions across 2 entities

**File Organization:**
- `/3processed/`: All source PDFs properly archived
- `/5loaded/`: All JSON extractions properly archived
- `/4extractions/`: Only report files (.txt) remain
- `/2staged/`: Empty (proper workflow state)

---

## Handoff Note

You now have complete expertise in the financial document processing system. Key knowledge areas:

**Process Management:**
- Full orchestration workflow vs direct agent invocation
- Critical importance of file state management across directories
- PDF movement triggers and timing in the workflow

**Agent Coordination:**
- Parallel processing patterns for 4+ simultaneous agents
- Proper prompt structure with DOC_MD5_HASH and extraction modes
- Agent report interpretation and issue identification

**Database Loading:**
- Incremental loading logic for same document, different data types
- Race condition handling with upsert patterns
- Timestamp format validation and correction procedures

**Troubleshooting:**
- Document hash constraint violations are usually race conditions, not data problems
- Missing PDF movements indicate incomplete orchestration
- ISO vs custom timestamp format issues in agent outputs

The user values technical accuracy, direct communication without code display, and systematic workflow completion. Always verify file locations match expected workflow state and complete all orchestration steps when processing documents.