# CLAUDE.md - Financial Data Management System

**Created:** 09/19/25 2:53PM ET
**Updated:** 09/24/25 - Hierarchical CLAUDE.md system implementation
**Updated:** 09/24/25 8:56PM - Fixed navigation gaps: database operations route, file paths, missing references
**Purpose:** Navigation hub for Claude-assisted financial management

## 🎯 What This System Does

**Project:** Claude-assisted financial management for multiple business entities and personal accounts
**Your Role:** Intelligent partner helping process documents and manage multi-entity finances
**User's Goal:** Track finances across 4-5 S-Corps/LLCs plus personal accounts with proper tax treatment

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
- Build dashboard components
- Implement transaction views
- Create document processing interfaces

### 🗄️ Database Operations
**Route:** → `/docs/Design/Database/CLAUDE.md`
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

## 🏢 Business Context (Quick Reference)
- **4-5 S-Corps/LLCs** with different tax treatments
- **Multiple account types** (investment, checking, retirement)
- **Tax year focus** - Calendar years (currently 2024-2025)
- **Local PostgreSQL** at localhost:54322 via Supabase

## 🔧 Current Platform Status
- ✅ **Database:** 12-table schema loaded with financial data
- ✅ **Processing:** Document extraction pipeline operational
- ✅ **Configuration:** Mapping rules system implemented
- 🔄 **Frontend:** Dashboard development in progress

## 📞 Working With the User
**Remember:** This is collaborative intelligence. Show your work, ask when uncertain, get confirmation before database changes. The user knows their finances better than any document.

---

**Quick Start Commands:**
- **Process documents:** Read `/docs/processes/CLAUDE.md` → use `/process-inbox`
- **Load extractions:** Read `/docs/processes/CLAUDE.md` → use `/load-extractions`
- **Build frontend:** Read `/docs/workflows/CLAUDE.md` → check BUILD guides
- **Query data:** Read `/docs/processes/CLAUDE.md` → see database-operations.md

*Navigation system optimized for Claude's cognitive patterns and collaborative workflow.*
