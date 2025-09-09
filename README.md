# Financial Data Management System

**Created:** 09/09/25 4:47PM ET  
**Updated:** 09/09/25 4:47PM ET  
**Purpose:** Automated processing and analysis of financial documents with comprehensive tax treatment

## Project Overview

This system automates the processing of financial documents from multiple sources (Fidelity statements, 1099 forms, QuickBooks exports) to provide comprehensive financial insights with proper tax categorization. Built specifically to handle complex scenarios like multi-state municipal bonds, corporate tax exemptions, and cross-source data reconciliation.

## Key Features

- **AI-Powered Document Processing** - Extract structured data from PDF statements and tax forms
- **Multi-Source Reconciliation** - Identify discrepancies between statements, 1099s, and QuickBooks
- **Advanced Tax Intelligence** - Handle complex federal/state tax treatments for municipal bonds
- **QuickBooks Integration** - Generate QBO files for seamless bookkeeping integration
- **Corporate Tax Support** - Handle tax-exempt entities and informational-only reporting

## Architecture

- **Database:** PostgreSQL via Supabase Docker
- **Host Platform:** Mac Mini M4 (silent, low-power, always-on)
- **Document Processing:** Claude AI for PDF extraction
- **Access:** Local network + Tailscale VPN for remote connectivity

## Quick Start

### 1. Setup Environment
```bash
# Clone/navigate to project directory
cd /Users/richkernan/Projects/Finances

# Start Supabase (when implemented)
docker-compose up -d

# Access dashboard
open http://mac-mini.local:3000
```

### 2. Import Documents
- Drop PDFs into `/documents/inbox/`
- System automatically processes and categorizes
- Review results in web dashboard

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

#### 📁 [requirements/](/Users/richkernan/Projects/Finances/docs/requirements/)
- **[current-requirements.md](/Users/richkernan/Projects/Finances/docs/requirements/current-requirements.md)** - Active requirements and user stories

#### 📁 [technical/](/Users/richkernan/Projects/Finances/docs/technical/)
- **[database-schema.md](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Essential database tables
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

**Current Phase:** Initial setup and architecture documentation  
**Next Steps:** Supabase setup and basic document processing pipeline

See [current-requirements.md](/Users/richkernan/Projects/Finances/docs/requirements/current-requirements.md) for detailed development roadmap.

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