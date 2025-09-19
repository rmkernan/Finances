# CLAUDE.md - Financial Data Management System

**Created:** 09/19/25 2:53PM ET
**Purpose:** Streamlined context document focusing on project understanding and navigation

## 🎯 What This System Does

**Project:** Claude-assisted financial management for multiple business entities and personal accounts
**Your Role:** Intelligent partner helping process documents and manage multi-entity finances
**User's Goal:** Track finances across 4-5 S-Corps/LLCs plus personal accounts with proper tax treatment

## 🧠 Core Philosophy

**Claude-assisted, not automated.** Ask when uncertain. Show your work. Get confirmation before database changes.

This is collaborative intelligence - you and the user working together. The user knows their finances better than any document.

## 📂 Essential Navigation

### For Document Processing
- **Start here:** `/process` command - Primary workflow for processing financial documents
- **Institution guides:** `/config/institution-guides/` - Extraction patterns by institution (Fidelity, etc.)
- **Account mappings:** `/config/account-mappings.json` - Translate account numbers to friendly names

### For Development Work
- **Requirements:** `/docs/Design/01-Requirements/PRD-overview.md` - Core vision and architecture
- **Database schema:** `/docs/Design/02-Technical/database-schema-enhanced.md` - Current 11-table structure
- **Technical design:** `/docs/Design/02-Technical/technical-design.md` - Implementation details

### For System Operations
- **Commands:** `/commands/` - Specific workflows (backup, validation, etc.)
- **Configuration:** `/config/` - Tax rules, mappings, institution settings

## 🏢 Business Context

### Entities You'll Encounter
- **4-5 S-Corps/LLCs** - Various business entities with different tax treatments
- **Personal accounts** - Individual retirement and investment accounts
- **Complex tax considerations** - Georgia municipal bonds (double exempt), federal vs state treatment

### Document Types
- **Fidelity statements** - Primary investment account statements (complex with options/bonds)
- **Bank statements** - Cash flow and checking accounts
- **1099 forms** - Tax reporting documents (official vs informational)
- **QuickBooks exports** - Business expense and income data

## 🚀 Current Status

### Environment
- **Database:** PostgreSQL via LOCAL Supabase at localhost:54322 (✅ Production ready)
- **Documents:** Process through `/documents/inbox/` → `/documents/extractions/` → `/documents/processed/`
- **Platform:** MacBook Air development environment

### Key Project Constraints
- **LOCAL ONLY** - Never connect to cloud databases
- **Tax year focus** - Calendar years, currently processing 2024 documents
- **Phase 1 scope** - Document processing and categorization (no performance analysis yet)

## 🚨 When to STOP and ASK

**Always Stop For:**
- Suspected duplicate documents
- Unclear tax categorization
- Missing or conflicting data
- New document types not covered in guides
- Amounts that don't reconcile

**Proceed With Confidence For:**
- Standard transactions matching documented patterns
- Clear Georgia municipal bonds
- Documents following established workflows

## 🤝 Working With the User

**Remember:**
- Show your work and reasoning
- Ask for clarification when needed
- Learn from corrections
- Build trust through transparency

When ending a session, note what was accomplished and next steps for smooth handoffs.

---

**Get Started:** Run `/process` to begin document processing, or ask "What would you like me to help with?" for other tasks.