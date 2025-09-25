# Project Architecture & Business Context

## Business Context

### Entities Managed
- **4-5 S-Corps/LLCs** - Various business entities with different tax treatments
- **Personal accounts** - Individual retirement and investment accounts

### Document Types Processed
- **Fidelity statements** - Primary investment accounts (complex: options, bonds, multi-account)
- **Bank statements** - Cash flow and checking accounts
- **1099 forms** - Tax reporting (official vs informational)
- **QuickBooks exports** - Business expense and income data

## Technical Architecture

### Database (PostgreSQL - localhost:54322)
12-table schema with configuration-driven mapping system:
- **Core tables:** transactions, accounts, entities, documents
- **Mapping tables:** map_rules, map_conditions, map_actions (CSV-editable)
- **Reference tables:** tax_categories, institutions

### Configuration-Driven Processing
- **Account mappings:** `/config/account-mappings.json` - Entity/institution relationships
- **Transaction rules:** `/config/mapping-rules.csv` - Classification rules (Excel-editable)
- **Institution guides:** `/config/institution-guides/` - Extraction patterns per bank

### Processing Pipeline
```
Documents → Extraction → Staging → Validation → Database Loading
```

## Development Status

### Completed
✅ Database schema implemented and loaded with data
✅ Document processing pipeline with specialized agents
✅ Configuration-driven transaction mapping
✅ Multi-entity account management

### Current Phase
🔄 **Frontend Development** - Building read-only dashboard and reporting interface

### Platform
MacBook Air development environment with local PostgreSQL via Supabase
