# Database Context for Claude - Financial Data Management System

**Created:** 09/22/25 9:20PM ET
**Updated:** 09/23/25 2:58PM - Added comprehensive schema design defense and clarified doc_level_data as transcribed data
**Purpose:** Database-specific context and orientation for Claude when working with the financial database

## 🚀 Quick Start - Connection Details

### Local Supabase Connection
```bash
# Check if Supabase is running
supabase status

# Connection string
postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Connection parameters
Host: 127.0.0.1 (or localhost)
Port: 54322
Database: postgres
Username: postgres
Password: postgres

# Web interfaces
Supabase Studio: http://127.0.0.1:54323
API Endpoint: http://127.0.0.1:54321
```

### Connect via Command Line
```bash
# Using psql
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Using connection parameters
psql -h localhost -p 54322 -U postgres -d postgres
```

## 📊 Database Schema Overview

### Phase 1 Tables (Currently Implemented)
1. **entities** - Business entities and individual taxpayers
2. **institutions** - Financial institutions (Fidelity, banks, etc.)
3. **accounts** - Individual accounts within institutions
4. **documents** - Financial documents with MD5 hash duplicate prevention
5. **document_accounts** - Links documents to multiple accounts (ESSENTIAL for consolidated statements)
6. **transactions** - Individual financial transactions
7. **positions** - Point-in-time holdings snapshots
8. **doc_level_data** - Document-level summary data transcribed directly from PDFs

## 🛡️ Schema Design Defense

### Why `document_accounts` Junction Table is Essential

**Real-world requirement:** Fidelity consolidated statements cover multiple accounts in one PDF
- Example: `Fidelity_2025-08_Brok+CMA.pdf` contains both brokerage (Z40-394067) and IRA (Z27-375656) accounts
- One document → Multiple accounts → Multiple entities (through account ownership)

**Alternative approaches that fail:**
- **Add account_id to documents:** Can't handle consolidated statements covering multiple accounts
- **Use PostgreSQL arrays:** Breaks foreign key constraints and complicates queries
- **Infer from transactions:** Circular dependency during data loading + can't represent empty sections

**Required query patterns:**
```sql
-- Find all accounts in a document
SELECT a.* FROM accounts a
JOIN document_accounts da ON a.id = da.account_id
WHERE da.document_id = 'doc-uuid'

-- Find all documents for an account
SELECT d.* FROM documents d
JOIN document_accounts da ON d.id = da.document_id
WHERE da.account_id = 'account-uuid'
```

### Core Entity Hierarchy Justification

**documents table design:**
- **NO account_id column** - Documents can span multiple accounts
- **institution_id only** - Documents are issued by exactly one institution
- **doc_md5_hash UNIQUE** - Prevents duplicate document processing

**Relationship flow:**
```
Document (PDF) → Institution → Multiple Accounts → Multiple Entities
     ↓              ↓              ↓                 ↓
  documents    institutions    accounts         entities
     ↓
document_accounts (junction table)
     ↓
transactions + positions (actual financial data)
```

### Phase 2 Tables (Future Implementation)
- **tax_payments** - Quarterly estimated tax tracking
- **transfers** - Inter-entity money movements
- **asset_notes** - Investment strategy notes
- **real_assets** - Properties and physical assets
- **liabilities** - Mortgages and loans

## 🔑 Key Design Principles

### 1. Duplicate Prevention Strategy
- **Stage 1:** MD5 hash generated during document staging (`md5sum` command)
- **Stage 2:** Database UNIQUE constraint on `doc_md5_hash` column
- **Important:** Using MD5, NOT SHA-256 for hashing

### 2. Multi-Entity Architecture
- One document can reference multiple accounts (consolidated statements)
- Each account belongs to exactly one entity
- Entities can have accounts at multiple institutions

### 3. Soft Delete Pattern
- `is_archived` columns on documents and transactions
- Records are never deleted, only archived
- Use `WHERE is_archived = FALSE` in normal queries


## 📝 PostgreSQL Comments

The database is self-documenting with embedded comments:

```sql
-- View table comments
SELECT obj_description('tablename'::regclass);

-- View column comments
SELECT col_description('tablename'::regclass, ordinal_position)
FROM information_schema.columns
WHERE table_name = 'tablename';

-- In psql, use \d+ to see comments
\d+ documents
```

### Critical Comments to Know
- `doc_md5_hash`: "MD5 hash (NOT SHA-256) for duplicate detection"
- `doc_level_data` table: "Transcribed summary data from PDF documents - NOT derived/calculated"
- `document_accounts` table: "Essential junction table for consolidated statements covering multiple accounts"
- `account_number`: "Should be encrypted/masked in production"
- `is_archived`: "Soft delete flag - true means hidden from normal queries"

## 🔍 Common Database Queries

### Check for Duplicate Documents
```sql
-- Before inserting, check if document exists
SELECT id, file_name, period_start, period_end
FROM documents
WHERE doc_md5_hash = 'your_md5_hash_here';
```

### Find All Accounts for an Entity
```sql
SELECT a.*, i.institution_name
FROM accounts a
JOIN institutions i ON a.institution_id = i.id
WHERE a.entity_id = 'entity_uuid_here'
AND a.account_status = 'active';
```

### Get Non-Archived Transactions
```sql
SELECT * FROM transactions
WHERE account_id = 'account_uuid_here'
AND is_archived = FALSE
ORDER BY transaction_date DESC;
```

### View Georgia Tax-Exempt Bonds
```sql
SELECT * FROM transactions
WHERE security_type = 'bond'
AND bond_state = 'GA'
AND federal_taxable = FALSE;
```

## ⚠️ Important Constraints

### UNIQUE Constraints (Prevent Duplicates)
- `documents.doc_md5_hash` - No duplicate document uploads
- `accounts.(institution_id, account_number)` - No duplicate accounts
- `positions.(document_id, account_id, position_date, sec_ticker, cusip)` - No duplicate positions
- `doc_level_data.(document_id, account_id, doc_section)` - No duplicate summaries

### Foreign Key Rules
- **CASCADE:** Deleting a document deletes its transactions and positions
- **RESTRICT:** Can't delete entities, institutions, or accounts with dependent records
- **SET NULL:** Amendment links cleared if original document deleted

## 🛠️ Database Maintenance

### View Table Sizes
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Index Usage
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Find Missing Indexes
```sql
-- Tables with sequential scans but no index scans
SELECT
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    seq_scan - idx_scan AS difference
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY difference DESC;
```

## 🔄 Migration Management

### Current Migration Files
- **Schema Definition:** `/docs/Design/02-Technical/schema.md`
- **Migration Plan:** `/database-migration-plan.md`

### Apply Migration
```bash
# Connect to database
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Run migration script
\i /path/to/database-migration-plan.sql

# Or use Supabase migrations
supabase db reset  # WARNING: Drops all data
supabase migration new initial_schema
# Copy SQL to the new migration file
supabase db push
```

## 🏗️ Schema Evolution Guidelines

When modifying the schema:

1. **Add, Don't Remove:** Add new columns as nullable, don't remove existing ones
2. **Update Both Docs:** Update both `schema.md` and `database-migration-plan.md`
3. **Add Comments:** Always add PostgreSQL comments for new columns
4. **Test Constraints:** Verify UNIQUE and CHECK constraints don't break existing data
5. **Consider Archives:** Check if changes affect archived (soft-deleted) records

## 🔐 Security Considerations

### Sensitive Data Columns
- `entities.tax_id` - Should be encrypted/hashed
- `accounts.account_number` - Should be encrypted/masked
- `transactions.payee_account` - Should be masked

### Display-Only Fields
- `entities.tax_id_display` - Last 4 digits only
- `accounts.account_number_display` - Last 4 digits only

## 📊 Database Statistics

### Quick Health Check
```sql
-- Document processing status
SELECT
    CASE
        WHEN processed_at IS NOT NULL THEN 'Processed'
        ELSE 'Pending'
    END as status,
    COUNT(*) as count
FROM documents
GROUP BY status;

-- Transactions by type
SELECT transaction_type, COUNT(*) as count
FROM transactions
WHERE is_archived = FALSE
GROUP BY transaction_type
ORDER BY count DESC;

-- Active accounts by institution
SELECT i.institution_name, COUNT(a.*) as account_count
FROM institutions i
LEFT JOIN accounts a ON i.id = a.institution_id
WHERE a.account_status = 'active'
GROUP BY i.institution_name;
```

## 🎯 Common Tasks

### Reset Database (Development Only)
```bash
# Complete reset - drops and recreates
supabase db reset

# Or manually
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
# Then run migration script
```

### Backup Database
```bash
# Backup structure and data
pg_dump postgresql://postgres:postgres@127.0.0.1:54322/postgres > backup_$(date +%Y%m%d).sql

# Backup structure only
pg_dump --schema-only postgresql://postgres:postgres@127.0.0.1:54322/postgres > schema_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres < backup_20250922.sql
```

## 💡 Tips for Claude

1. **Always check for duplicates** before inserting documents (use MD5 hash)
2. **Include `is_archived = FALSE`** in queries unless specifically looking for archived records
3. **Use transactions** for multi-table inserts to maintain consistency
4. **Check constraints** before inserting - the database will reject invalid data
5. **Read the comments** - use `\d+ tablename` to understand column purposes
6. **Test with SELECT first** - verify your WHERE clause before UPDATE/DELETE
7. **Remember the hierarchy:** Entity → Institution → Account → Transaction

## 🚨 Critical Reminders

- **LOCAL ONLY** - Never connect to cloud databases
- **MD5 for hashing** - Not SHA-256
- **doc_level_data is cached** - Can be regenerated from transactions
- **Georgia tax rules** - Municipal bonds from GA are state tax-exempt
- **Soft deletes only** - Never hard DELETE, use is_archived flag

---

When in doubt, check the schema documentation at `/docs/Design/02-Technical/schema.md` for detailed table definitions and relationships.