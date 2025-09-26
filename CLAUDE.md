# CLAUDE.md - Financial Data Management System

**Created:** 09/19/25 2:53PM ET
**Updated:** 09/24/25 - Hierarchical CLAUDE.md system implementation
**Updated:** 09/24/25 8:56PM - Fixed navigation gaps: database operations route, file paths, missing references
**Updated:** 09/25/25 1:49PM - Fixed critical tactical navigation gaps: added implementer quick start, schema commands, quality gates prominence, implementation workflow checklist
**Updated:** 09/25/25 1:00AM - Frontend Week 1 complete, critical architectural discoveries documented
**Updated:** 09/25/25 12:30PM - Week 3 frontend complete, navigation architecture operational
**Updated:** 09/25/25 10:35PM - Rules engine simplified to 2-level structure, all 26 JSON extractions loaded successfully
**Purpose:** Navigation hub for Claude-assisted financial management

## 🎯 What This System Does

**Project:** Claude-assisted financial management for multiple business entities and personal accounts
**Your Role:** Intelligent partner helping process documents and manage multi-entity finances
**User's Goal:** Track finances across 4-5 S-Corps/LLCs plus personal accounts with proper tax treatment
**Current Status:** Frontend operational with 3 active accounts, full navigation, and admin monitoring

## 🚀 First Time Here? Start Here
👉 **READ FIRST:** `/docs/start/CLAUDE.md` - Essential orientation and quickstart

## 🧭 Navigation by Task

### 📄 Document Processing
**Route:** → `/docs/processes/CLAUDE.md`
- Process PDFs from inbox to database
- Extract financial data with specialized agents
- Handle Fidelity statements, bank statements, 1099s

### 🖥️ Frontend Development
**Route:** → `/docs/workflows/CLAUDE.md`
**Quick Start:** → `/frontend/implementer/README.md` (quality gates, gotchas, patterns)
**Implementer:** Read `/docs/start/CLAUDE.md` and `/frontend/implementer/README.md` immediately before coding
- Build dashboard components
- Implement transaction views
- Create document processing interfaces

### 🗄️ Database Operations
**Route:** → `/docs/Design/Database/CLAUDE.md`
**Quick Schema Check:** `PGPASSWORD=postgres psql -h localhost -p 54322 -d postgres -c "\d+ [table_name]"`
- Schema reference and connection details
- Query patterns and data relationships
- Multi-entity financial analysis

### ⚙️ Configuration Changes
**Route:** → `/config/CLAUDE.md`
- Update account mappings
- Modify transaction classification rules
- Configure institution extraction patterns

### 🤖 Command Execution
**Route:** → `/.claude/CLAUDE.md`
- Run document processing workflows
- Execute database loading commands
- Use specialized extraction agents

### 📚 Reference Lookup
**Route:** → `/docs/reference/CLAUDE.md`
- Database schema and query patterns
- API endpoints and data models
- Configuration structures

## 📊 System Capabilities (As of 09/25/25 Evening)

### Available Features:
- **Dashboard:** Global overview with real-time metrics and recent activity
- **Entity Management:** View all entities with filtering and detailed pages
- **Account Navigation:** Browse all accounts, detailed views with transactions/positions
- **Institution Overview:** See all institutions with account aggregations
- **Document Tracking:** Monitor document processing status
- **Admin Monitoring:** Data completeness dashboard at `/admin/data-status`

### Navigation Architecture:
- Landing pages for all major sections with filtering
- Detail pages for entities and accounts
- Tabbed interface for account details (Overview, Transactions, Positions, Documents)
- Breadcrumb navigation throughout

## 🚨 Emergency Protocols

### Always STOP and ASK for:
- Suspected duplicate documents
- Unclear tax categorization
- Missing or conflicting data
- New document types not covered in guides
- Amounts that don't reconcile

### Core Safety Rules:
- **LOCAL ONLY** - Never connect to cloud databases
- **Backup before changes** - This is live financial data
- **Verify accounts** - Check mappings before processing
- **Test connections** - Confirm database access before bulk operations

## ✅ Quality Gates (Frontend Development)

**MANDATORY before any code changes:**
```bash
npm run quality && npm run build && npm run dev
```

**File Header Standards:**
- New files: `Created: [date] - Purpose: [description]`
- Updated files: `Updated: [date] - [change description]`

## 🏢 Business Context (Quick Reference)
- **4-5 S-Corps/LLCs** with different tax treatments
- **Multiple account types** (investment, checking, retirement)
- **Tax year focus** - Calendar years (currently 2024-2025)
- **Local PostgreSQL** at localhost:54322 via Supabase
- **Active Accounts:** 3 operational (2 brokerage, 1 cash management)
- **Data Volume:** 152 positions, 267 transactions currently tracked

## 🔧 Current Platform Status
- ✅ **Database:** 12-table schema with 1200+ type definitions loaded
- ✅ **Processing:** Document extraction pipeline operational
- ✅ **Configuration:** SIMPLIFIED 2-level mapping rules system (Level 1: Transaction Classification, Level 2: Security Classification)
- ✅ **Data Loading:** ALL 26 JSON extractions loaded successfully - 0 NULL transaction_types
- ✅ **Frontend Core:** Week 1 complete - dashboard with real calculated data
- ✅ **Frontend Charts:** Week 2 complete - full data visualizations
- ✅ **Frontend Navigation:** Week 3 complete - all pages accessible with admin tools
- 🔄 **Frontend Advanced:** Week 4 planning - export, search, optimization

## 📞 Working With the User

### Communication Guidelines
**CRITICAL:** The user is technical but CANNOT read code. Communicate effectively by:
- ❌ **DON'T** show code blocks or SQL queries to explain problems
- ✅ **DO** explain issues in clear technical English
- ✅ **DO** use concrete examples: "The balance calculation is adding positions from August but transactions from September"
- ✅ **DO** describe solutions: "I'll update the query to filter by the same date range"
- ✅ **DO** summarize what code does: "This function calculates total value by summing all account balances"

**Example of Good Communication:**
- Bad: "Here's the SQL: `SELECT SUM(amount) FROM...`"
- Good: "I'm summing all transaction amounts for accounts belonging to Milton Preschool"

**Remember:** This is collaborative intelligence. Show your work, ask when uncertain, get confirmation before database changes. The user knows their finances better than any document.

---

**Quick Start Commands:**
- **Process documents:** Read `/docs/processes/CLAUDE.md` → use `/process-inbox`
- **Load extractions:** ✅ COMPLETE - All 26 JSON files loaded (use `/load-extractions` for future)
- **Build frontend:** Read `/docs/workflows/CLAUDE.md` → check BUILD guides
- **Query data:** Read `/docs/processes/CLAUDE.md` → see database-operations.md
- **View all accounts:** Navigate to `/accounts` in frontend
- **Check data status:** Navigate to `/admin/data-status` in frontend
- **Account details:** Click any account name for detailed view with tabs

## 🛠️ Implementation Workflow (Before You Code)

**1. Schema Verification First:**
```bash
grep "interface [TableName]" src/types/supabase.ts -A 10
PGPASSWORD=postgres psql -h localhost -p 54322 -d postgres -c "\d+ accounts"
```

**2. Find Existing Patterns:**
```bash
grep -r "similar_feature" src/
ls src/components/ui/  # Check available components
```

**3. Quality Gates (MANDATORY):**
```bash
npm run quality && npm run build && npm run dev
```

*Navigation system optimized for Claude's cognitive patterns and collaborative workflow.*
