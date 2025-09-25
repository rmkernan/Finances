# Database Operations Guide

## Connection Details
- **Host:** localhost:54322 (local Supabase)
- **Database:** postgres
- **Environment:** LOCAL ONLY - never cloud connections

## Schema Overview
12-table structure optimized for multi-entity financial management:

### Core Data Tables
- `transactions` - All financial transactions
- `accounts` - Account definitions with entity relationships
- `entities` - Business entities and personal accounts
- `documents` - Processed document tracking

### Configuration Tables
- `map_rules` - Transaction classification rules
- `map_conditions` - Rule condition logic (IF statements)
- `map_actions` - Rule actions (SET operations)

### Reference Tables
- `tax_categories` - Tax classification system
- `institutions` - Financial institution definitions

## Common Query Patterns

### Entity Analysis
```sql
-- All transactions for specific entity
SELECT t.*, a.account_name, e.entity_name
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN entities e ON a.entity_id = e.entity_id
WHERE e.entity_name = 'EntityName'
ORDER BY t.transaction_date DESC;
```

### Monthly Summaries
```sql
-- Monthly transaction summary by category
SELECT
    DATE_TRUNC('month', transaction_date) as month,
    tax_category,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
WHERE a.entity_id = ?
GROUP BY month, tax_category
ORDER BY month DESC, total_amount DESC;
```

### Document Tracking
```sql
-- Processing status by document type
SELECT
    document_type,
    processing_status,
    COUNT(*) as document_count,
    MIN(created_at) as oldest_processed,
    MAX(created_at) as newest_processed
FROM documents
GROUP BY document_type, processing_status
ORDER BY document_type, processing_status;
```

## Safety Protocols

### Before Queries
- ✅ Verify connection to localhost (never cloud)
- ✅ Use transactions for data modifications
- ✅ Backup before bulk operations

### Query Guidelines
- 🎯 Use parameterized queries to prevent injection
- 📊 Limit large result sets with appropriate WHERE clauses
- 🔍 Test complex queries on small datasets first

### Data Modification Rules
- ⚠️ **NEVER** modify core transaction data without user approval
- ⚠️ **ALWAYS** backup before schema changes
- ⚠️ **VERIFY** foreign key relationships before deletions

## Maintenance Operations

### Regular Maintenance
- Monitor disk space usage
- Analyze query performance
- Review and archive old documents
- Validate data integrity constraints

### Troubleshooting
- Check connection settings if queries fail
- Verify table permissions for operations
- Review foreign key constraints for modification issues
- Analyze slow queries with EXPLAIN ANALYZE
