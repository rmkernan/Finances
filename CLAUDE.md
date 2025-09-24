# CLAUDE.md - Financial Data Management System

**Created:** 09/19/25 2:53PM ET
**Updated:** 09/23/25 - Added configuration-driven mapping system documentation and enhanced duplicate detection with JSON hash tracking
**Updated:** 09/24/25 5:08PM - Updated database schema path, added Database/CLAUDE.md reference, noted BUILD docs as frontend guides
**Updated:** 09/24/25 5:15PM - Added document-processing-pipeline.md reference, streamlined process documentation
**Purpose:** Streamlined context document focusing on project understanding and navigation

## 🎯 What This System Does

**Project:** Claude-assisted financial management for multiple business entities and personal accounts
**Your Role:** Intelligent partner helping process documents and manage multi-entity finances
**User's Goal:** Track finances across 4-5 S-Corps/LLCs plus personal accounts with proper tax treatment

## 🧠 Core Philosophy

**Claude-assisted, not automated.** Ask when uncertain. Show your work. Get confirmation before database changes.

This is collaborative intelligence - you and the user working together. The user knows their finances better than any document.

## 🗺️ Configuration-Driven Mapping System

**Overview:** Transaction classification uses database-driven mapping rules (`map_rules`, `map_conditions`, `map_actions` tables) for flexible categorization without code changes.

### Key Components
- **Three-table system:** Rules → Conditions (IF) → Actions (SET)
- **CSV management:** Edit rules in Excel via `/config/mapping-rules.csv`
- **Account mappings:** `/config/account-mappings.json` - Entity/institution/account relationships

### For Details
See `/docs/Design/Database/CLAUDE.md` for complete mapping system documentation

## 📂 Essential Navigation

### For Document Processing
- **Pipeline overview:** `/docs/processes/document-processing-pipeline.md` - Complete processing system reference
- **Run command:** `/.claude/commands/process-inbox.md` - Execute document processing workflow
- **Institution guides:** `/config/institution-guides/` - Extraction patterns per institution
- **Account mappings:** `/config/account-mappings.json` - Entity/account metadata

### For Development Work
- **Requirements:** `/docs/Design/01-Requirements/PRD-overview.md` - Core vision and architecture
- **Database schema:** `/docs/Design/Database/schema.md` - Complete 12-table structure (implemented and loaded with data)
- **Database context:** `/docs/Design/Database/CLAUDE.md` - Database operations and query guide
- **Frontend workflows:** `/docs/Design/01-Requirements/BUILD-*.md` - Individual workflow implementation guides

### For System Operations
- **Commands:** `/.claude/commands/` - Specific workflows (process-inbox, etc.)
- **Configuration:** `/config/` - Tax rules, mappings, institution settings
- **Agents:** `/.claude/agents/` - Specialized extraction agents (fidelity-statement-extractor)

## 🏢 Business Context

### Entities You'll Encounter
- **4-5 S-Corps/LLCs** - Various business entities with different tax treatments
- **Personal accounts** - Individual retirement and investment accounts

### Document Types
- **Fidelity statements** - Primary investment account statements (complex with options/bonds)
- **Bank statements** - Cash flow and checking accounts
- **1099 forms** - Tax reporting documents (official vs informational)
- **QuickBooks exports** - Business expense and income data

## 🚀 Current Status

### Environment
- **Database:** PostgreSQL via LOCAL Supabase at localhost:54322 (loaded with financial data)
- **Documents:** Process through `/documents/1inbox/` → `/documents/2staged/` → `/documents/4extractions/` → `/documents/3processed/`
- **Platform:** MacBook Air development environment

### Key Project Constraints
- **LOCAL ONLY** - Never connect to cloud databases
- **Tax year focus** - Calendar years, currently processing 2024-2025 documents
- **Frontend phase** - Building read-only dashboard and reporting interface

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

## 🎯 Code Quality Standards

### Simplicity First - Anti-Over-Engineering Rules

**ALWAYS Ask These Questions First:**
1. **"What's the simplest solution that works?"** - Start with the most basic approach
2. **"Am I solving a problem that actually exists?"** - Don't build for imaginary future needs
3. **"Can this be done in 50% fewer lines?"** - Prefer concise, readable code
4. **"Am I adding abstraction without clear benefit?"** - Avoid unnecessary layers

### 🛑 Stop Signals - When to PAUSE and Simplify

**STOP when you find yourself:**
- Creating more than 3 functions for a simple task
- Adding caching for data that's accessed rarely
- Supporting multiple formats when only one is used
- Writing "flexible" code for requirements that don't exist
- Creating classes/modules for single-use logic
- Adding configuration for values that never change

### ✅ Simplicity Principles

**Follow the "Single Task, Single Function" Rule:**
- One function should do one clear thing
- If you can't explain the function in one sentence, split it
- Prefer direct database queries over caching for rare operations

**Prefer Explicit Over Generic:**
- Hard-code known values instead of making them configurable
- Use specific logic instead of generic frameworks for simple cases
- Choose readable code over "clever" abstractions

**Data Loading Specifically:**
- If data structure is consistent, write for that structure only
- Don't support legacy formats unless actively used
- Transcribe data directly - avoid interpretation layers

### 📏 Complexity Limits

**File Size Limits:**
- Single-purpose modules: < 100 lines
- Main logic files: < 200 lines
- If approaching limits, explain necessity or refactor

**Function Limits:**
- Simple functions: < 20 lines
- Complex functions: < 50 lines
- If longer, break into smaller pieces with clear names

### 🔄 Review Questions Before Committing Code

1. **"Could a junior developer understand this in 5 minutes?"**
2. **"Am I building for actual requirements or imagined ones?"**
3. **"What would happen if I deleted 50% of this code?"**
4. **"Is this the simplest solution that meets the known requirements?"**

### 🎯 When Complexity IS Justified

**Add complexity ONLY when:**
- Requirements explicitly demand flexibility
- Performance is measured and insufficient
- Multiple real use cases exist (not hypothetical)
- Error handling for critical operations
- User explicitly requests configurability

### 🚨 Red Flag Phrases to Avoid

- "This makes it more flexible for the future"
- "We might need this later"
- "This is more enterprise-ready"
- "This follows best practices" (without specific benefit)
- "This is more scalable" (without scale requirements)

### User Coaching

When you catch yourself over-engineering, tell the user: *"I notice I'm adding complexity. Let me step back and implement the simplest solution that meets your actual needs."*

**Remember:** Simple, working code beats complex, "enterprise" code every time.

---

**Get Started:**
- **Document processing:** Run `/process-inbox` to process new documents
- **Frontend development:** Start with `/docs/Design/01-Requirements/BUILD-dashboards.md`
- **Database queries:** See `/docs/Design/Database/CLAUDE.md` for query examples

## 🔄 Recent Improvements (09/22/25)

### Document Processing System
- **Enhanced extraction agents** with improved confidence and reduced false error reporting
- **Parallel processing support** - multiple extractions can run simultaneously
- **Streamlined workflow** - simplified from 6 to 5 steps with better user prompting
- **Comprehensive testing** - successfully processed 3 statements with 8 extractions

### Current State
- **Database** - 12-table schema implemented and loaded with financial data
- **Document processing** - Working extraction pipeline with multiple statements processed
- **Ready for frontend** - Beginning dashboard implementation with BUILD-*.md guides