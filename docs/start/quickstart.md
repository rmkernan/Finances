# 5-Minute Project Understanding

## What This System Does
Claude-assisted financial management for multiple business entities (4-5 S-Corps/LLCs) plus personal accounts with proper tax treatment.

## Key Numbers
- **12-table database** with financial data loaded
- **PostgreSQL** at localhost:54322 (local Supabase)
- **4-5 business entities** with different tax treatments
- **Multiple account types** (investment, checking, retirement)

## Document Flow
```
/documents/1inbox/ → 2staged/ → 4extractions/ → 3processed/
```

## Primary Tasks
1. **Process documents:** `/process-inbox` command
2. **Load data:** `/load-extractions` command
3. **Query analysis:** Direct PostgreSQL queries
4. **Build frontend:** Dashboard and reporting UI

## Critical Constraints
- **LOCAL ONLY** - Never connect to cloud databases
- **Tax year focus** - Calendar years (currently 2024-2025)
- **Backup before changes** - This is live financial data

## When to STOP and ASK
- Suspected duplicate documents
- Unclear tax categorization
- Missing or conflicting data
- New document types

## Next Steps
- **Document processing:** Read `/docs/processes/CLAUDE.md`
- **Frontend development:** Read `/docs/workflows/CLAUDE.md`
- **Database work:** Read `/docs/processes/CLAUDE.md`
