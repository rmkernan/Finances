# Database Resource Guide for Financial System Sub-Agents

**Created:** 09/09/25 4:34PM ET  
**Last Updated:** 09/09/25 4:34PM ET - Initial creation with Phase 1 schema deployment  
**Purpose:** Essential database context and resources for future database sub-agents working on financial data management system  

## Your Role

You are a database expert working on a financial data management system designed for Claude-assisted processing. This system serves as **Claude's persistent memory** for intelligent financial decision-making, not automated processing. Your expertise helps maintain data integrity, optimize performance, and extend capabilities as needed.

## Database Architecture

### Core Design Philosophy
- **3-table Phase 1 design** optimized for Claude's cognitive efficiency
- **PostgreSQL via Supabase** for reliability and JSON capabilities  
- **JSONB fields for flexibility** - handle complex financial scenarios without rigid schema constraints
- **NUMERIC precision for money** - prevents floating-point errors in financial calculations
- **Full audit trail** - every transaction linked to source documents

### Schema Overview

**accounts (9 columns)**
- Purpose: Store financial account information across institutions
- Key fields: account_number, institution, account_type, tax_id, notes
- Design: Simple structure with notes field for Claude context

**documents (16 columns)**  
- Purpose: Track financial documents (statements, 1099s, QuickBooks exports)
- Key fields: file_hash (deduplication), extraction_confidence, raw_extraction (JSONB), summary_data (JSONB)
- Design: Flexible JSONB storage for Claude-extracted data and observations

**transactions (22 columns)**
- Purpose: Individual financial transactions from documents  
- Key fields: amount (NUMERIC 15,2), security_info (JSONB), tax_details (JSONB)
- Design: Precise money handling with flexible security and tax data

## Connection Information

- **Local URL:** postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Supabase Studio:** http://localhost:54323
- **Environment variables:** Check `.env` file in project root
- **Project ID:** "Finances" (from supabase/config.toml)

## Migration Patterns

### Naming Convention
- Format: `XXX_YYYYMMDD_description.sql`
- Applied migration: `create_financial_schema_phase1` (direct application)
- Location: `/supabase/migrations/`

### Application Methods
- **File-based:** `supabase db reset` (applies all migrations)
- **Direct application:** `mcp__supabase__apply_migration` (when file-based fails)
- **Important:** This project shares Supabase instance with childcare inspection system

### Schema Coexistence
- **Financial tables:** accounts, documents, transactions (our system)
- **Existing tables:** ~20 childcare inspection tables (different system)
- **No conflicts:** Systems coexist successfully

## Common Query Patterns

```sql
-- 1. Find all transactions for an account in date range
SELECT t.*, d.document_type, a.institution 
FROM transactions t
JOIN documents d ON t.document_id = d.id
JOIN accounts a ON t.account_id = a.id
WHERE t.account_id = $1 
  AND t.transaction_date BETWEEN $2 AND $3
ORDER BY t.transaction_date DESC;

-- 2. Check for duplicate documents by hash
SELECT file_name, file_hash, COUNT(*) 
FROM documents 
WHERE file_hash = $1 
GROUP BY file_name, file_hash 
HAVING COUNT(*) > 1;

-- 3. Find transactions by security symbol
SELECT t.*, t.security_info->>'symbol' as symbol
FROM transactions t 
WHERE t.security_info->>'symbol' = $1;

-- 4. Get 1099 summary data
SELECT d.summary_data->>'form_type' as form_type,
       d.summary_data->>'ordinary_dividends' as ordinary_dividends
FROM documents d 
WHERE d.document_type = '1099' 
  AND d.summary_data->>'tax_year' = $1;

-- 5. List all accounts with transaction counts
SELECT a.institution, a.account_name, COUNT(t.id) as transaction_count
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id
GROUP BY a.id, a.institution, a.account_name;

-- 6. Find transactions needing review
SELECT t.*, d.file_name, t.review_notes
FROM transactions t
JOIN documents d ON t.document_id = d.id
WHERE t.needs_review = true;

-- 7. Complex tax scenario queries
SELECT t.*, t.tax_details->>'issuer_state' as issuer_state,
       t.tax_details->>'special_notes' as notes
FROM transactions t 
WHERE t.tax_category = 'municipal_interest' 
  AND t.federal_taxable = false;

-- 8. Document extraction confidence audit
SELECT extraction_confidence, COUNT(*) as count
FROM documents 
GROUP BY extraction_confidence 
ORDER BY count DESC;

-- 9. Amendment tracking
SELECT original.file_name as original,
       amended.file_name as amendment  
FROM documents original
JOIN documents amended ON original.id = amended.amends_document_id
WHERE amended.is_amended = true;

-- 10. Financial precision verification
SELECT amount, 
       pg_typeof(amount) as data_type,
       amount::text as exact_value
FROM transactions 
WHERE amount IS NOT NULL 
LIMIT 5;
```

## Critical Data Types

### Money Fields - ALWAYS use NUMERIC
```sql
-- ✅ CORRECT
amount NUMERIC(15,2)  -- Exact precision, no floating-point errors

-- ❌ NEVER USE
amount FLOAT         -- Causes rounding errors in financial calculations
amount DOUBLE        -- Same problem as FLOAT
```

### JSONB Field Structures

**security_info examples:**
```json
{
  "cusip": "04780MWW5",
  "symbol": "FSIXX", 
  "name": "Fidelity Government Money Market Fund",
  "quantity": 1234.567,
  "price": 1.0000,
  "security_type": "money_market"
}
```

**tax_details examples:**
```json
{
  "issuer_state": "GA",
  "taxpayer_state": "GA", 
  "is_amt_preference": false,
  "section_199a_eligible": false,
  "special_notes": "Georgia municipal bond - double exempt"
}
```

**summary_data (1099-DIV) examples:**
```json
{
  "form_type": "1099-DIV",
  "tax_year": 2024,
  "ordinary_dividends": 1234.56,
  "qualified_dividends": 1000.00,
  "capital_gain_distributions": 234.56,
  "exempt_interest_dividends": 0.00
}
```

## Error Handling

### Common Errors and Solutions

**"relation does not exist"**
- Check table names: accounts, documents, transactions
- Verify you're connected to correct database
- Run `\dt` to list tables

**JSONB query errors**
- Use `->` for JSON object, `->>` for text
- Use GIN indexes for performance: `WHERE security_info @> '{"symbol": "AAPL"}'`
- Test JSON structure: `SELECT security_info FROM transactions LIMIT 1;`

**Foreign key violations**
- Always insert accounts first, then documents, then transactions
- Check referential integrity: account_id and document_id must exist
- Use transactions for multi-table operations

**Numeric precision issues**
- Always use NUMERIC(15,2) for money
- Avoid FLOAT/DOUBLE for financial data
- Verify precision: `SELECT pg_typeof(amount) FROM transactions;`

## Tools & Commands

### Supabase CLI
```bash
supabase status                 # Check all services
supabase db reset              # Apply all migrations (destructive)
supabase studio                # Open Studio in browser
supabase logs                  # View logs
```

### Database Access
```bash
# Connect via psql
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Check migration status
SELECT * FROM supabase_migrations.schema_migrations;

# View table info
\d+ accounts
\d+ documents  
\d+ transactions
```

### MCP Supabase Tools
- `mcp__supabase__execute_sql` - Run queries
- `mcp__supabase__apply_migration` - Apply migrations
- `mcp__supabase__list_tables` - View schema
- `mcp__supabase__get_logs` - Debug issues

## Performance Considerations

### Existing Indexes
```sql
-- Core performance indexes
idx_transactions_account_date   -- (account_id, transaction_date)
idx_transactions_document       -- (document_id)
idx_documents_hash             -- (file_hash) for deduplication  
idx_documents_account          -- (account_id)

-- JSONB GIN indexes
idx_transactions_security_info -- USING GIN (security_info)
idx_documents_summary_data     -- USING GIN (summary_data)
```

### Query Optimization Tips
- Use account_id + date range for transaction queries
- file_hash lookups are indexed for fast duplicate detection
- JSONB queries with `@>` operator use GIN indexes
- Join order: accounts → documents → transactions

## File Locations

- **Migrations:** `/supabase/migrations/`
- **Schema documentation:** `/docs/technical/database-schema.md`  
- **Migration reports:** `/docs/reports/`
- **This guide:** `/docs/SubagentResources/database.md`
- **Config:** `/supabase/config.toml`

## Phase 1 Limitations

### What's NOT in Phase 1
- **No securities master table** - Security data in JSONB instead
- **No tax_reports table** - 1099 data in documents.summary_data  
- **No QuickBooks integration** - Focus on PDF processing first
- **No complex validation** - Relies on Claude intelligence

### Future Expansion Opportunities
- **Phase 2:** Securities master table if JSONB becomes insufficient
- **Phase 3:** Dedicated tax_reports table for complex reconciliation  
- **Phase 4:** QuickBooks integration and automated categorization
- **Phase 5:** Multi-entity support and consolidated reporting

## Lessons Learned

### Migration Process
- **Direct application sometimes needed** - File-based migrations can fail in complex environments
- **Shared database instances work** - Multiple systems can coexist safely
- **Always verify NUMERIC precision** - Critical for financial accuracy

### Schema Design
- **JSONB is powerful** - Handles complex scenarios without schema changes
- **Comments are crucial** - Document everything for future developers
- **Index planning matters** - Performance indexes must match query patterns

### Data Quality
- **file_hash prevents duplicates** - Essential for document management
- **Foreign keys enforce integrity** - Prevents orphaned transactions
- **extraction_confidence helps** - Claude can flag uncertain data

## IMPORTANT: Self-Update Requirement

**Before completing ANY database task, you MUST:**

1. **Review this document** - Understand current state and patterns
2. **Update this document** - Add new discoveries, patterns, errors  
3. **Update the "Last Updated" timestamp** - Track when changes were made
4. **Add to "Lessons Learned"** - Document what you discovered

### Update Template
```markdown
**Last Updated:** MM/DD/YY H:MMAM/PM ET - [Brief description of your changes]

## Lessons Learned
- [Your new discovery/pattern/solution]
- [Any gotchas or important findings]
```

## Emergency Procedures

### If Database is Corrupted
1. Check `supabase status` - restart services if needed
2. Try `supabase db reset` - reapplies all migrations
3. Restore from backup if available
4. Recreate test data for validation

### If Migrations Fail
1. Try direct application: `mcp__supabase__apply_migration`
2. Check for syntax errors in SQL
3. Verify foreign key dependencies
4. Apply migrations in correct order

### If Performance Degrades
1. Check index usage: `EXPLAIN ANALYZE` on slow queries
2. Monitor JSONB query patterns - may need additional GIN indexes
3. Consider table statistics updates
4. Review query plans for full table scans

---

**Remember:** This system is Claude's memory for financial intelligence. Maintain data quality, document everything, and always update this guide with your discoveries.

*This guide should evolve with every database task. Keep it current and comprehensive.*