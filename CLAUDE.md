# CLAUDE.md - Financial Data Management System

**Created:** 09/09/25 3:58PM ET  
**Updated:** 09/12/25 7:45PM ET - Removed outdated content, fixed paths, streamlined for clarity  
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

## 🚀 Current Status

**Database:** 10 tables including real_assets and liabilities for net worth tracking
**Schema:** `/docs/Design/02-Technical/database-schema-enhanced.md`
**Requirements:** Organized in `/docs/Design/01-Requirements/BUILD-*.md` files

### Environment
- **Database:** PostgreSQL via LOCAL Supabase ONLY
- **Connection:** postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Studio:** http://localhost:54323 (LOCAL ONLY)
- **Documents:** Located in `/documents/inbox/` for processing
- **Platform:** Mac Mini M4 development environment

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

### Tax Complexity
- **FSIXX** = Treasury fund (~97% Georgia state tax exempt, federal taxable)
- **SPAXX** = Money market (~55% Georgia state tax exempt, federal taxable)
- **Georgia Municipal Bonds** = Double exempt (federal and state) for Georgia residents
- **Other State Bonds** = Federal exempt, state taxable for Georgia residents
- **Corporate Status** = Special handling for Milton Preschool Inc
- **Multi-Entity** = Track 4-5 S-Corps/LLCs with flow-through to personal taxes

## 🔧 Common Tasks

### Processing a Document
```bash
# User places document in /documents/inbox/
# You read it and extract data
# Show user what you found
# Get confirmation
# Store in database
# Move to /documents/processed/
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

### Current Schema (Phase 1: 3 tables operational)
1. **accounts** - Financial institutions and account numbers
2. **documents** - Source PDFs/CSVs with extraction metadata
3. **transactions** - Individual financial transactions

### Enhanced Schema (Ready for implementation: 8 tables)
1. **entities** - S-Corps, LLCs, Individual (master hub)
2. **institutions** - Fidelity, banks, etc.
3. **accounts** - Links entities to institutions
4. **documents** - Source documents with processing audit
5. **transactions** - All financial transactions
6. **tax_payments** - Quarterly estimated tax tracking
7. **transfers** - Inter-entity money movements
8. **asset_notes** - Investment strategies and price targets

### Key Fields to Use
- `extraction_confidence` - Record your confidence level
- `extraction_notes` - Explain your decisions
- `raw_extraction` (JSONB) - Store complete extraction
- `needs_review` - Flag uncertain items
- `review_notes` - Document what needs human review

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

# Apply migrations
supabase db reset

# Check status
supabase status
```

### Document Processing
- Read guidance in `/commands/process-document.md`
- Check doctrine in `/config/doctrine.md`
- Reference schema in `/docs/technical/database-schema.md`

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