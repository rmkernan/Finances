# Database Migration Verification Checklist

**Created:** 09/09/25 4:34PM ET  
**Purpose:** User checklist to verify successful financial database schema deployment  

## Pre-Verification Steps

- [ ] Supabase local instance running (check `supabase status`)
- [ ] Access to Supabase Studio at http://localhost:54323

## Schema Verification

### Tables Present
- [ ] `accounts` table visible in Supabase Studio
- [ ] `documents` table visible in Supabase Studio  
- [ ] `transactions` table visible in Supabase Studio

### Data Types Correct
- [ ] `transactions.amount` shows as `numeric(15,2)` in table structure
- [ ] JSONB fields present: `security_info`, `tax_details`, `summary_data`, `raw_extraction`
- [ ] All foreign key relationships visible in Studio

### Indexes Created
- [ ] Performance indexes visible in Studio (account_date, document_hash, etc.)
- [ ] GIN indexes visible for JSONB fields

## Test Data Verification

### Sample Data Present
- [ ] 1 test account: "Fidelity Test Account" 
- [ ] 1 test document: 1099-DIV document
- [ ] 1 test transaction: $100.00 dividend

### Relationships Working
- [ ] Can view joined data across all three tables
- [ ] JSONB data accessible (security symbol: FSIXX)
- [ ] Foreign keys enforced (cannot delete referenced records)

## Functional Testing

### Basic Operations
- [ ] Can insert new account
- [ ] Can insert new document linked to account
- [ ] Can insert new transaction linked to document and account
- [ ] JSONB fields accept complex JSON data

### Query Testing
- [ ] Can query transactions by account and date range
- [ ] Can search JSONB fields (e.g., find by security symbol)
- [ ] Can join all three tables successfully

## Performance Verification

### Index Usage
- [ ] Queries on account_id + transaction_date use index
- [ ] JSONB queries use GIN indexes
- [ ] File hash lookups are fast

## Security & Constraints

### Data Integrity
- [ ] Cannot insert transaction without valid account_id
- [ ] Cannot insert transaction without valid document_id
- [ ] NUMERIC precision preserved for money amounts

## Migration Files

### File Verification
- [ ] Original migration file exists: `/supabase/migrations/001_20250109_create_financial_tables.sql`
- [ ] Applied migration shows in migration history
- [ ] All SQL executed without errors

## Documentation

### Reference Materials
- [ ] Migration report available: `/docs/reports/20250109-migration-report.md`
- [ ] Schema documentation: `/docs/technical/database-schema.md`
- [ ] Database guide for sub-agents: `/docs/SubagentResources/database.md`

## Common Issues & Solutions

**If tables are missing:**
1. Check `supabase status` - ensure all services running
2. Try `supabase db reset` to reapply migrations
3. Verify correct project directory

**If JSONB queries fail:**
1. Ensure GIN indexes created: `CREATE INDEX ... USING GIN (...)`
2. Use proper JSONB operators: `->`, `->>`, `@>`, `?`

**If foreign keys not working:**
1. Check referential integrity in Studio
2. Verify constraint names in migration file

## Sign-Off

**Verified by:** ________________  
**Date:** ________________  
**Status:** ✅ PASS / ❌ FAIL  
**Notes:** ________________________________

---

*Complete this checklist to ensure the financial database schema is properly deployed and functional.*