# CLAUDE.md - Financial Data Management System

**Created:** 09/09/25 3:58PM ET
**Updated:** 09/12/25 7:45PM ET - Removed outdated content, fixed paths, streamlined for clarity
**Updated:** 09/17/25 3:17PM ET - Added Supabase local setup, source attributes documentation, and extraction guides
**Updated:** 09/18/25 9:42AM ET - Database schema applied, backup system tested, standardized paths for multi-machine sync
**Updated:** 01/18/25 3:45PM ET - Reset database with enhanced schema, simplified extraction documentation, tested full pipeline
**Purpose:** Primary context document for Claude instances working on this project

## 🎯 Quick Start

**What This Is:** A Claude-assisted financial management system for multiple business entities and personal accounts  
**Your Role:** Intelligent partner helping process documents, make categorization decisions, and manage multi-entity finances  
**User's Goal:** Track finances across 4-5 S-Corps/LLCs plus personal accounts with proper tax treatment

### 📋 For PRD/Design Work
If asked to work on product requirements or design:
1. **Start with:** `/docs/Design/01-Requirements/PRD-overview.md` - Core vision and architecture
2. **Then choose based on task:**
   - Building dashboards → `/docs/Design/01-Requirements/BUILD-dashboards.md`
   - Document features → `/docs/Design/01-Requirements/BUILD-workflows-documents.md`
   - Financial analysis → `/docs/Design/01-Requirements/BUILD-workflows-financial.md`
   - Tax features → `/docs/Design/01-Requirements/BUILD-workflows-tax.md`
   - Admin features → `/docs/Design/01-Requirements/BUILD-workflows-admin.md`
3. **Current schema:** `/docs/Design/02-Technical/database-schema-enhanced.md`
4. **Technical design:** `/docs/Design/02-Technical/technical-design.md`

**Key Design Decisions Already Made:**
- Fixed dashboard layouts (no drag-and-drop widgets)
- Read-only frontend (Claude processes documents via terminal)
- No inter-entity loan tracking (out of scope)
- Tax years are calendar years (use date functions)
- Context-based navigation (Global → Entity → Institution → Account)  

## 🚀 Current Status (Updated: 01/18/25)

**Database:** ✅ Fresh reset with 11-table schema supporting complex instruments
**Schema:** `/docs/Design/02-Technical/database-schema-enhanced.md` - Now includes JSONB for options/bonds
**Extraction:** Simplified collaborative process - tested with 36-page Fidelity statement
**Documentation:** Streamlined to leverage Claude's intelligence while maintaining field mappings

### Environment
- **Database:** PostgreSQL via LOCAL Supabase ONLY (✅ Fresh reset 01/18/25)
- **Connection:** postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Studio:** http://localhost:54323 (LOCAL ONLY)
- **Documents:** Located in `/documents/inbox/` for processing
- **Extraction Output:** `/documents/extractions/` for JSON files
- **Platform:** MacBook Air development environment
- **Path:** `/Users/richkernan/Projects/Finances` (standardized for Mac Mini sync)

### Database Tables (Fresh as of 01/18/25)
✅ **entities** - Business entities and individuals
✅ **institutions** - Financial institutions (Fidelity, banks, etc.)
✅ **accounts** - Financial accounts with holder names
✅ **documents** - Source documents with extraction metadata
✅ **document_accounts** - Many-to-many junction for multi-account statements
✅ **transactions** - Enhanced with option_details and bond_details JSONB columns
✅ **positions** - Portfolio holdings with option support
✅ **income_summaries** - Period income tracking
✅ **tax_payments** - Quarterly estimated tax tracking
✅ **transfers** - Inter-entity money movements
✅ **asset_notes** - Investment strategies and price targets

### Key Updates (01/18/25)
- **Simplified Extraction:** `/config/institution-guides/fidelity.md` - Complete Fidelity extraction guide
- **Transaction Types:** Added `redemption`, `reinvest`, `option_buy`, `option_sell`
- **JSONB Support:** `option_details` and `bond_details` for complex instruments
- **Collaborative Process:** ASK when uncertain - this is human-AI teamwork
- **Fresh Migration:** `/supabase/migrations/20250118_complete_schema.sql`

### ⚠️ CRITICAL WARNING
**ONLY use LOCAL Supabase** at localhost:54322. Never connect to cloud instances.
All database operations must use local CLI or psql commands.

## 🧠 Core Philosophy

**Claude-assisted, not automated.** Ask when uncertain. Show your work. Get confirmation before database changes.

## 📁 Project Structure

### Key Directories
- `/docs/` - All documentation (requirements, technical specs, decisions)
- `/commands/` - Templates for your document processing workflows
- `/config/` - Doctrine, tax rules, account mappings
- `/documents/` - PDF/CSV storage (inbox → processed → archived)
- `/supabase/` - Database migrations and configuration

### Essential Documents
1. **For Requirements:** See `/docs/Design/01-Requirements/` folder
2. **For Technical:** See `/docs/Design/02-Technical/` folder
3. **Database Schema:** `/docs/Design/02-Technical/database-schema-enhanced.md`

## 💡 Critical Information

### Document Types You'll See
1. **Fidelity Monthly Statements** - PDFs with transaction details
2. **Official 1099s** - What's reported to IRS (may show $0)
3. **Informational 1099s** - Actual income data not reported to IRS
4. **QuickBooks Exports** - CSV files with cash flow data


## 🔧 Common Tasks

### Database Backup and Sync
See `/commands/backup-database.md` for complete procedures:
- **Data backup:** `supabase db dump --data-only --local`
- **Full backup:** `supabase db dump --local` (recommended for sync)
- **Container backup:** `docker exec supabase_db_Finances pg_dump` (most reliable)

### Processing a Document (Simplified Process)
```bash
# 1. Check /documents/inbox/ for new documents
# 2. Run /process-inbox command
# 3. Reference /config/institution-guides/fidelity.md for patterns
# 4. Extract to /documents/extractions/[timestamp]_[filename].json
# 5. ASK USER when uncertain about categorization
# 6. Move original to /documents/processing/ after extraction
```

### Checking for Duplicates
```sql
-- Check by file hash
SELECT * FROM documents WHERE file_hash = '[hash]';

-- Check by period
SELECT * FROM documents 
WHERE period_start = '2024-01-01' 
AND document_type = 'statement';
```

### Handling Amendments
1. Look for "AMENDED" or "CORRECTED" on document
2. Find original document in database
3. Link them with `amends_document_id`
4. Use amended version for reporting

## 🚨 When to STOP and ASK

**Always Stop For:**
- Suspected duplicate documents
- Unclear tax categorization
- Missing or conflicting data
- New document types not in doctrine
- Amounts that don't reconcile

**Proceed With Confidence For:**
- Standard FSIXX/SPAXX dividends
- Documents matching doctrine patterns
- Clear Georgia municipal bonds
- Amounts that match across sources

## 🗄️ Database Quick Reference

### Current Schema (11 tables - fully operational)
1. **entities** - S-Corps, LLCs, Individual (master hub)
2. **institutions** - Fidelity, banks, etc.
3. **accounts** - Links entities to institutions with holder names
4. **documents** - Source documents with extraction JSON path
5. **document_accounts** - Junction for multi-account statements
6. **transactions** - With JSONB for options/bonds
7. **positions** - Portfolio holdings snapshot
8. **income_summaries** - Period income tracking
9. **tax_payments** - Quarterly estimated tax tracking
10. **transfers** - Inter-entity money movements
11. **asset_notes** - Investment strategies and price targets

### Key Fields to Use
- `extraction_json_path` - Path to JSON extraction file
- `extraction_notes` - Questions or uncertainties
- `option_details` (JSONB) - Options-specific data
- `bond_details` (JSONB) - Bond-specific data
- `account_holder_name` - Exact name from statements

## 🎯 Phase 1 Goals

1. **Process all 2024 documents** from Fidelity
2. **Reconcile the $58k discrepancy** between sources
3. **Categorize for taxes** (federal vs state treatment)
4. **Build clean dataset** for tax preparation

**NOT in Phase 1:**
- QuickBooks export (Phase 2)
- Expense tracking
- Investment performance analysis
- Multi-year processing

## 🛠️ Development Commands

### Database Operations
```bash
# View Studio
open http://localhost:54323

# Create migration
supabase migration new [name]

# Apply migrations (reset database)
supabase db reset --local

# Check status
supabase status
```

### Document Processing
- Start with `/commands/process-inbox.md`
- Reference patterns in `/config/institution-guides/fidelity.md`
- Schema details in `/docs/Design/02-Technical/database-schema-enhanced.md`

## 📊 Success Metrics

You're doing well when:
- User understands what you're doing
- Duplicates are caught before storage
- Tax categories are correctly assigned
- Reconciliation identifies all discrepancies
- User confirms your extractions

## 🤝 Working With the User

**Remember:**
- They know their finances better than you
- Show your work and reasoning
- Ask for clarification when needed
- Learn from their corrections
- Build trust through transparency

## 🔄 Session Handoff

When ending a session, note:
1. What documents were processed
2. Any unresolved questions
3. Next steps planned
4. Any patterns learned

This helps the next Claude instance continue smoothly.

---

**Final Reminder:** You are an intelligent assistant, not an automation system. Work WITH the user to achieve accurate financial data processing. When in doubt, ask!