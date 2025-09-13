# Financial Data Management System

**Created:** 09/09/25 4:47PM ET  
**Updated:** 09/10/25 12:40AM ET - Multi-entity schema complete, frontend design/implementation plan ready  
**Purpose:** Claude-assisted processing and analysis of financial documents with comprehensive tax treatment for multiple business entities

## Project Overview

This system manages financial data across multiple business entities (S-Corps, LLCs) and personal accounts, processing documents from various institutions to provide comprehensive financial insights with proper tax categorization. Built specifically to handle complex scenarios like multi-state municipal bonds, corporate tax exemptions, Georgia state tax exemptions, and inter-entity transfers.

## Key Features

- **Multi-Entity Management** - Track finances across 4-5 S-Corps/LLCs plus personal accounts
- **AI-Powered Document Processing** - Claude extracts data from PDFs with intelligent categorization
- **Multi-Institution Support** - Handle accounts at Fidelity, banks, and other institutions
- **Advanced Tax Intelligence** - Georgia state exemptions (FSIXX ~97%, SPAXX ~55%), municipal bonds
- **Tax Payment Tracking** - Monitor quarterly estimated payments vs actual liability
- **Asset Performance Analysis** - Track investments across entities with notes and strategies
- **Inter-Entity Transfers** - Manage money movements and loans between entities
- **QuickBooks Integration** - Generate QBO files for seamless bookkeeping integration

## ⚠️ CRITICAL: LOCAL DATABASE ONLY

**WARNING:** MCP Supabase tools are configured globally for a DIFFERENT cloud project.
- **DO NOT** use any `mcp__supabase__` commands
- **ONLY** use LOCAL Supabase at localhost:54322
- **Use** `psql` or `supabase` CLI commands instead

## Architecture

- **Database:** PostgreSQL via LOCAL Supabase (localhost:54322)
- **Host Platform:** Mac Mini M4 (silent, low-power, always-on)
- **Document Processing:** Claude AI for PDF extraction
- **Access:** Local network + Tailscale VPN for remote connectivity

## Quick Start

### 1. Setup Environment
```bash
# Clone/navigate to project directory
cd /Users/richkernan/Projects/Finances

# Supabase is ready with database schema applied
# 3 tables: accounts, documents, transactions

# Access LOCAL Studio to view data
open http://localhost:54323
```

### 2. Process Documents
- Drop PDFs into `/documents/inbox/`
- Use Claude commands to process and categorize
- Review extracted data in Supabase Studio
- Reconcile across sources

### 3. Generate Reports
- Monthly reconciliation summaries
- Tax preparation exports
- QBO files for QuickBooks integration

## Documentation Structure

### 📁 [docs/](/Users/richkernan/Projects/Finances/docs/)
Complete project documentation organized by category:

#### 📁 [archive/](/Users/richkernan/Projects/Finances/docs/archive/)
- **[context.md](/Users/richkernan/Projects/Finances/docs/archive/context.md)** - Original development context and discoveries
- **[prd.md](/Users/richkernan/Projects/Finances/docs/archive/prd.md)** - Complete product requirements document
- **[schema.md](/Users/richkernan/Projects/Finances/docs/archive/schema.md)** - Full database schema specification

#### 📁 [decisions/](/Users/richkernan/Projects/Finances/docs/decisions/)
- **[001-supabase-over-sqlite.md](/Users/richkernan/Projects/Finances/docs/decisions/001-supabase-over-sqlite.md)** - Technology choice rationale

#### 📁 [prd/](/Users/richkernan/Projects/Finances/docs/prd/)
- **[frontend-prd.md](/Users/richkernan/Projects/Finances/docs/prd/frontend-prd.md)** - Frontend product requirements with 11 workflows

#### 📁 [reports/](/Users/richkernan/Projects/Finances/docs/reports/)
- **[statement-processing-test-20250909-215500.md](/Users/richkernan/Projects/Finances/docs/reports/statement-processing-test-20250909-215500.md)** - Successful test processing report

#### 📁 [requirements/](/Users/richkernan/Projects/Finances/docs/requirements/)
- **[current-requirements.md](/Users/richkernan/Projects/Finances/docs/requirements/current-requirements.md)** - Active requirements and user stories

#### 📁 [technical/](/Users/richkernan/Projects/Finances/docs/technical/)
- **[database-schema.md](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Essential database tables (Phase 1: 3 tables)
- **[database-schema-enhanced.md](/Users/richkernan/Projects/Finances/docs/technical/database-schema-enhanced.md)** - Complete multi-entity schema (8 tables)
- **[frontend-technical-design.md](/Users/richkernan/Projects/Finances/docs/technical/frontend-technical-design.md)** - Comprehensive frontend architecture
- **[frontend-implementation-plan.md](/Users/richkernan/Projects/Finances/docs/technical/frontend-implementation-plan.md)** - 9-week phased development roadmap
- **[processing-rules.md](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Document processing guidelines
- **[quickbooks-integration.md](/Users/richkernan/Projects/Finances/docs/technical/quickbooks-integration.md)** - QBO export specifications

### 📁 [commands/](/Users/richkernan/Projects/Finances/commands/)
Claude Code command templates for common operations:
- **[process-document.md](/Users/richkernan/Projects/Finances/commands/process-document.md)** - Process new financial documents
- **[reconcile-income.md](/Users/richkernan/Projects/Finances/commands/reconcile-income.md)** - Cross-source income reconciliation
- **[generate-qbo.md](/Users/richkernan/Projects/Finances/commands/generate-qbo.md)** - QuickBooks export generation
- **[README.md](/Users/richkernan/Projects/Finances/commands/README.md)** - Command usage instructions

### 📁 [config/](/Users/richkernan/Projects/Finances/config/)
Processing rules and configuration:
- **[doctrine.md](/Users/richkernan/Projects/Finances/config/doctrine.md)** - Core processing decisions and patterns
- **[accounts-map.md](/Users/richkernan/Projects/Finances/config/accounts-map.md)** - QuickBooks account mappings
- **[tax-rules.md](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax categorization rules

## Project Structure

```
/Finances/
├── README.md                 # This file - project overview
├── /docs/                   # All documentation
│   ├── /archive/           # Original project documents
│   ├── /decisions/         # Architecture decisions (ADRs)
│   ├── /requirements/      # Current requirements
│   └── /technical/         # Technical specifications
├── /commands/              # Claude Code command templates
├── /config/               # Processing rules and mappings
├── /documents/            # Financial document storage
│   ├── /inbox/           # New documents to process
│   ├── /processed/       # Successfully processed
│   └── /archived/        # Year-end archives
├── /data/                # Data storage and exports
│   └── /exports/         # QBO and report files
├── /supabase/            # Database configuration
│   └── /migrations/      # SQL schema migrations
├── /scripts/             # Utility scripts
└── /.claude/             # Claude Code configuration (preserved)
```

## Key Capabilities

### Complex Tax Scenarios Handled
- **Multi-State Municipal Bonds** - Georgia bonds (tax-exempt) vs California bonds (state-taxable for Georgia residents)
- **Corporate Tax Exemptions** - Handle "informational only" 1099s for tax-exempt entities
- **AMT Preference Items** - Private activity bond identification and reporting
- **Section 199A Eligibility** - QBI deduction qualification analysis

### Data Reconciliation
- **Cross-Source Validation** - Compare Fidelity statements vs 1099s vs QuickBooks
- **Discrepancy Detection** - Flag missing or mismatched data (e.g., $58k actual vs $0 reported)
- **Audit Trail** - Complete lineage from source document to processed transaction

### Integration Features
- **QBO Export** - Generate QuickBooks-compatible files for seamless bookkeeping
- **PDF Processing** - AI-powered extraction from complex financial documents
- **Real-Time Updates** - Live dashboard updates as documents are processed

## Development Status

**Current Phase:** Ready for frontend implementation  
**Completed:**
- ✅ Local Supabase database with 3-table schema
- ✅ Successfully processed January 2024 statement ($4,329.68 extracted)
- ✅ Georgia tax exemption rules documented (FSIXX ~97%, SPAXX ~55%)
- ✅ Enhanced 8-table schema for multi-entity support
- ✅ Frontend technical design with eMoney-inspired UI
- ✅ 9-week implementation roadmap

**Next Steps:** 
1. Initialize Next.js 14 project with shadcn/ui
2. Implement core dashboard and entity management
3. Build document viewer with PDF + data overlay

See [frontend-implementation-plan.md](/Users/richkernan/Projects/Finances/docs/technical/frontend-implementation-plan.md) for detailed roadmap.

## Getting Help

### For New Claude Instances
1. Read [current-requirements.md](/Users/richkernan/Projects/Finances/docs/requirements/current-requirements.md) for active work
2. Review [database-schema.md](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md) for data structure
3. Check [processing-rules.md](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md) for document handling
4. Use [commands/](/Users/richkernan/Projects/Finances/commands/) templates for common tasks

### For Historical Context
- [context.md](/Users/richkernan/Projects/Finances/docs/archive/context.md) - Original discoveries and sample data analysis
- [prd.md](/Users/richkernan/Projects/Finances/docs/archive/prd.md) - Complete product vision and detailed requirements

### Configuration Files
- [.claude/CLAUDE.md](/Users/richkernan/Projects/Finances/.claude/CLAUDE.md) - Claude Code project configuration
- [config/](/Users/richkernan/Projects/Finances/config/) - Processing rules and account mappings

---

*This project handles real financial data with complex tax implications. Prioritize data accuracy, audit trails, and proper tax treatment in all implementations.*