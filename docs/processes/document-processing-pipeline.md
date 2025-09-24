# Document Processing Pipeline

**Created:** 09/24/25 5:15PM ET
**Purpose:** Complete reference for the financial document processing system

## Overview

This system transforms PDF financial statements into a queryable database through a multi-stage pipeline with Claude-assisted extraction and automatic transaction classification.

## Document Flow

```
/documents/1inbox/        → Initial drop location (generic filenames)
    ↓ (Staging)
/documents/2staged/       → Renamed with standard convention
    ↓ (Extraction)
/documents/4extractions/  → JSON extraction files
    ↓ (Completion)
/documents/3processed/    → Final archive of processed PDFs
```

## Processing Stages

### Stage 1: Document Assessment
- Extract text from first 2 pages using PyPDF2
- Generate MD5 hash for duplicate prevention
- Check account mappings in `/config/account-mappings.json`
- Verify accounts exist in database

### Stage 2: Staging & Naming
**Standard naming convention:**
```
Institution_DocType_YYYY-MM_AccountName.pdf
Examples:
- Fid_Stmnt_2024-08_Brok+CMA.pdf
- BofA_Stmnt_2024-09_Checking.pdf
```

### Stage 3: Extraction
**Sub-Agent Model:**
- Stateless extraction agents (fidelity-statement-extractor)
- Two modes: Holdings (positions) or Activities (transactions)
- Parallel processing supported
- JSON output with MD5 hash embedded

**Agent Invocation:**
```python
Task(
    description="Extract holdings",
    subagent_type="fidelity-statement-extractor",
    prompt="""
    EXTRACTION MODE: Holdings
    DOC_MD5_HASH: [hash]

    Extract HOLDINGS from: /path/to/staged.pdf
    """
)
```

### Stage 4: Transaction Classification
**Automatic Mapping System:**
- Three-table system: map_rules → map_conditions → map_actions
- CSV-based rule management at `/config/mapping-rules.csv`
- Classifies transaction types, tax categories, security types
- Options lifecycle tracking (opening/closing/assignment)

**Classification Priority:**
1. Security patterns (options lifecycle)
2. Description-based mapping
3. Section-based mapping
4. Fallback to raw section

### Stage 5: Post-Processing
- Move successfully processed PDFs to `/documents/3processed/`
- Keep problematic files in staging for review
- Update mapping rules based on new patterns encountered

## Duplicate Prevention

**Multi-Level Protection:**
1. **PDF Level:** MD5 hash stored in documents.doc_md5_hash (UNIQUE constraint)
2. **JSON Level:** Hash tracking for activities/positions separately
3. **Incremental Loading:** Same PDF can load holdings then activities later

## Account Management

**Account Resolution Flow:**
1. Extract account numbers from PDF
2. Check `/config/account-mappings.json`
3. If found → Use mapped metadata
4. If unknown → Ask user for entity/type/name
5. Update mappings for future use

## Key Commands

### Process New Documents
```bash
/process-inbox
```

### Check for Duplicates
```bash
# Generate hash
md5 document.pdf

# Check in database
grep -r "[hash]" /documents/4extractions/*.json
```

### Update Mapping Rules
```bash
# Edit rules
open /config/mapping-rules.csv

# Apply to database
python3 scripts/update_mapping_rules.py
```

## Directory Structure
```
/documents/
├── 1inbox/           # New documents arrive here
├── 2staged/          # Renamed, ready for extraction
├── 3processed/       # Successfully processed archive
└── 4extractions/     # JSON extraction files

/config/
├── account-mappings.json    # Account metadata
├── mapping-rules.csv        # Transaction classification rules
└── institution-guides/      # Extraction patterns per institution

/.claude/
├── commands/process-inbox.md    # Processing orchestration
└── agents/fidelity-statement-extractor.md  # Extraction agent
```

## Success Indicators
- ✅ All documents assessed for duplicates
- ✅ Accounts mapped to entities
- ✅ JSON extractions created with proper naming
- ✅ Transactions automatically classified
- ✅ Processed PDFs archived appropriately
- ✅ New patterns documented for rule updates