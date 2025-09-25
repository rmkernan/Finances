# Document Processing Pipeline

## Overview
Complete system for processing financial documents from PDF to database loading.

## Processing Flow
```
1inbox/ → extraction → 2staged/ → validation → 4extractions/ → loading → 3processed/
```

## Key Components

### 1. Document Staging
- Place PDFs in `/documents/1inbox/`
- System moves to `/documents/2staged/` for processing
- Prevents accidental reprocessing

### 2. Extraction Agents
- **Fidelity statements:** Complex multi-account processing
- **Bank statements:** Standard transaction extraction
- **1099 forms:** Tax document processing
- **QuickBooks exports:** Business data integration

### 3. Validation & Loading
- JSON extraction files created in `/documents/4extractions/`
- Database loading via `/load-extractions` command
- Duplicate detection with JSON hash tracking
- Processed files moved to `/documents/3processed/`

## Safety Protocols

### Before Processing
- ✅ Verify document is complete (not partial scan)
- ✅ Check for existing processed versions
- ✅ Confirm account mappings exist
- ✅ Database connection verified

### During Processing
- ⚠️ Monitor for extraction errors
- ⚠️ Verify account/entity matches
- ⚠️ Flag unusual transaction patterns
- ⚠️ Check date ranges for consistency

### After Processing
- ✅ Verify extraction completeness
- ✅ Confirm database loading success
- ✅ Archive processed documents properly
- ✅ Update tracking records

## Common Issues & Solutions

### Missing Account Mappings
**Problem:** Extraction fails due to unknown account
**Solution:** Update `/config/account-mappings.json` with new account details

### Duplicate Detection
**Problem:** System flags potential duplicate
**Solution:** Compare JSON hashes, verify with user before proceeding

### Extraction Errors
**Problem:** Agent reports parsing issues
**Solution:** Check document quality, verify institution guide patterns

## Execution Commands
- **Process documents:** `/.claude/commands/process-inbox.md`
- **Load extractions:** `/.claude/commands/load-extractions.md`
- **Verify results:** Database queries via processes/database-operations.md
