# Data - Export Files and Data Management

**Created:** 09/09/25 6:00PM ET  
**Updated:** 09/09/25 6:00PM ET  
**Purpose:** Guide for managing exported data files and database-related operations

## Directory Structure

### Data Organization

```
/data/
├── /exports/         # Generated export files (QBO, CSV, reports)
│   ├── /qbo/        # QuickBooks import files
│   ├── /csv/        # Raw data exports
│   ├── /reports/    # Summary and analysis reports
│   └── /backups/    # Database backup exports
└── README.md        # This file - data management guide
```

## Export File Management

### QuickBooks Integration Files (`/exports/qbo/`)

#### QBO File Structure
```
/exports/qbo/
├── 2024-01_Fidelity_Z40394067.qbo      # Monthly QBO files
├── 2024-02_Fidelity_Z40394067.qbo
├── 2024-Q1_Fidelity_Z40394067.qbo      # Quarterly summaries
├── 2024-Annual_Fidelity_Z40394067.qbo  # Annual exports
└── import-logs/                         # Import tracking and validation
```

#### QBO File Naming Convention
```
Pattern: YYYY-MM_Institution_AccountNumber.qbo
Examples:
- 2024-01_Fidelity_Z40394067.qbo (Monthly)
- 2024-Q4_Fidelity_Z40394067.qbo (Quarterly)
- 2024-Annual_Fidelity_Z40394067.qbo (Full year)

Benefits:
- Chronological sorting
- Clear source identification  
- Prevents import conflicts
- Supports automated processing
```

#### QBO Content Focus
```markdown
Cash Flow Events Included:
✓ Dividend payments (FSIXX, SPAXX, etc.)
✓ Interest payments (taxable and tax-exempt)
✓ Bond principal repayments (redemptions)
✓ Account withdrawals and deposits
✓ Investment fees and charges

Internal Transactions Excluded:
✗ Security purchases and sales
✗ Position rebalancing between funds
✗ Reinvestment transactions
✗ Market value adjustments
```

### CSV Data Exports (`/exports/csv/`)

#### Raw Data Exports
```
/exports/csv/
├── transactions_2024.csv               # Complete transaction data
├── tax_summary_2024.csv               # Tax preparation summaries  
├── reconciliation_2024-01.csv         # Monthly reconciliation reports
├── securities_master.csv              # Security reference data
└── data_quality_flags.csv             # Data issues and resolutions
```

#### Export Formats and Usage

##### Complete Transaction Export
```sql
-- Generate comprehensive transaction CSV
SELECT 
    t.transaction_date,
    t.settlement_date,
    t.transaction_type,
    t.security_symbol,
    t.security_name,
    t.amount,
    t.federal_taxable,
    t.state_taxable,
    t.tax_category,
    t.description,
    a.account_name,
    d.file_path as source_document
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN documents d ON t.document_id = d.id
WHERE EXTRACT(year FROM t.transaction_date) = 2024
ORDER BY t.transaction_date, t.settlement_date;
```

##### Tax Preparation Summary
```sql  
-- Generate tax-focused summary export
SELECT 
    EXTRACT(year FROM settlement_date) as tax_year,
    tax_category,
    federal_taxable,
    state_taxable,
    issuer_state_code,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_type IN ('dividend', 'interest')
AND EXTRACT(year FROM settlement_date) = 2024
GROUP BY 
    EXTRACT(year FROM settlement_date),
    tax_category,
    federal_taxable,
    state_taxable,
    issuer_state_code
ORDER BY tax_category, issuer_state_code;
```

### Report Generation (`/exports/reports/`)

#### Standard Report Types

##### Monthly Reconciliation Reports
```
/exports/reports/
├── 2024-01_reconciliation_summary.pdf
├── 2024-01_variance_analysis.pdf
├── 2024-02_reconciliation_summary.pdf
└── annual_2024_tax_analysis.pdf
```

##### Tax Preparation Packages
```
/exports/reports/tax-2024/
├── dividend_income_summary.pdf
├── municipal_bond_analysis.pdf  
├── cross_source_reconciliation.pdf
├── corporate_exemption_documentation.pdf
└── supporting_documents/
    ├── 1099_official_vs_informational.pdf
    └── discrepancy_resolution_notes.pdf
```

## Database Backup and Recovery

### Backup Strategy (`/exports/backups/`)

#### Automated Backup Schedule
```
Daily: Point-in-time Supabase backup (automatic)
Weekly: Full database export to CSV files
Monthly: Complete schema + data backup
Annually: Archive backup with document verification
```

#### Backup File Structure
```
/exports/backups/
├── /daily/          # Daily incremental backups
├── /weekly/         # Weekly full exports
├── /monthly/        # Monthly complete backups
└── /annual/         # Year-end archive backups
    └── /2024/
        ├── schema_2024.sql
        ├── data_2024.sql
        ├── documents_catalog.csv
        └── verification_checksums.txt
```

#### Manual Backup Commands
```bash
# Weekly full database export
pg_dump -h localhost -U postgres finances > /data/exports/backups/weekly/finances_$(date +%Y%m%d).sql

# Export specific tables to CSV  
psql -h localhost -U postgres finances -c "\copy transactions to '/data/exports/backups/transactions_$(date +%Y%m%d).csv' CSV HEADER"

# Verify backup integrity
gzip -t /data/exports/backups/weekly/finances_$(date +%Y%m%d).sql.gz
```

## Data Quality and Validation

### Data Integrity Monitoring

#### Daily Quality Checks
```sql
-- Daily data quality validation query
WITH daily_quality AS (
    SELECT 
        CURRENT_DATE as check_date,
        COUNT(*) as total_transactions,
        COUNT(CASE WHEN federal_taxable IS NULL THEN 1 END) as missing_tax_classification,
        COUNT(CASE WHEN ABS(amount) < 0.01 THEN 1 END) as zero_amount_transactions,
        COUNT(CASE WHEN settlement_date IS NULL THEN 1 END) as missing_settlement_dates
    FROM transactions
    WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT * FROM daily_quality;
```

#### Cross-Source Reconciliation Validation
```sql
-- Monthly reconciliation verification
SELECT 
    'Monthly Statement Total' as source,
    SUM(amount) as total_dividends
FROM transactions t
JOIN documents d ON t.document_id = d.id
WHERE t.transaction_type = 'dividend'
AND d.document_type = 'statement'
AND EXTRACT(year FROM t.settlement_date) = 2024

UNION ALL

SELECT 
    '1099 Informational Total' as source,
    ordinary_dividends as total_dividends
FROM tax_reports
WHERE form_type = '1099-DIV'
AND is_official = false
AND tax_year = 2024;
```

### Export Data Validation

#### Pre-Export Quality Checks
```markdown
Before generating any export files:
1. **Completeness Check:** All expected documents processed
2. **Accuracy Validation:** Cross-source totals match within tolerance
3. **Tax Classification:** All income transactions properly categorized
4. **Date Consistency:** Settlement dates align with tax year requirements
5. **Amount Precision:** All monetary values maintain proper decimal precision
```

#### Post-Export Verification
```bash
# Verify QBO file format and structure
xmllint --noout /data/exports/qbo/2024-01_Fidelity_Z40394067.qbo
echo "QBO file validation: $?"

# Check CSV export completeness
wc -l /data/exports/csv/transactions_2024.csv
grep -c "^[0-9]" /data/exports/csv/transactions_2024.csv  # Count data rows

# Validate backup file integrity
gzip -t /data/exports/backups/weekly/finances_20240901.sql.gz
```

## Performance and Storage Management

### Storage Utilization Monitoring

#### Disk Space Management
```bash
# Check data directory disk usage
du -sh /Users/richkernan/Projects/Finances/data/*

# Monitor export file growth
ls -lah /Users/richkernan/Projects/Finances/data/exports/qbo/ | tail -10

# Archive old export files (quarterly cleanup)
find /data/exports/ -name "*.csv" -mtime +90 -exec gzip {} \;
```

#### File Retention Policies
```markdown
Retention Guidelines:
- QBO files: 2 years active, then compress and archive
- CSV exports: 1 year active, then compress  
- Reports: 3 years active (tax audit protection)
- Daily backups: 30 days retention
- Weekly backups: 1 year retention
- Monthly backups: Permanent retention
```

### Database Performance Optimization

#### Index Maintenance
```sql
-- Monitor query performance for export operations
EXPLAIN ANALYZE 
SELECT t.*, a.account_name 
FROM transactions t 
JOIN accounts a ON t.account_id = a.id
WHERE t.transaction_date >= '2024-01-01'
ORDER BY t.transaction_date;

-- Maintain essential indexes for export queries
CREATE INDEX IF NOT EXISTS idx_transactions_export 
ON transactions(transaction_date, transaction_type, amount);
```

## Security and Access Control

### Data Protection Standards

#### File Permissions
```bash
# Secure export directories (read/write for owner only)
chmod 700 /Users/richkernan/Projects/Finances/data/exports
chmod 600 /Users/richkernan/Projects/Finances/data/exports/qbo/*.qbo

# Verify no world-readable financial data
find /Users/richkernan/Projects/Finances/data -type f -perm +004 -ls
```

#### Backup Encryption
```bash
# Encrypt sensitive backup files
gpg --cipher-algo AES256 --compress-algo 1 --symmetric \
    /data/exports/backups/weekly/finances_$(date +%Y%m%d).sql

# Verify encrypted backup integrity
gpg --decrypt /data/exports/backups/weekly/finances_$(date +%Y%m%d).sql.gpg > /dev/null
```

### Access Logging
```sql
-- Track data export activities
CREATE TABLE export_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    export_type TEXT NOT NULL,  -- 'qbo', 'csv', 'report', 'backup'
    file_path TEXT NOT NULL,
    export_date TIMESTAMPTZ DEFAULT NOW(),
    user_context TEXT,
    record_count INTEGER,
    file_size_bytes BIGINT
);
```

## Related Documentation

### Export Generation
- **[/commands/generate-qbo.md](../commands/generate-qbo.md)** - QBO file creation process
- **[/config/accounts-map.md](../config/accounts-map.md)** - QuickBooks integration configuration

### Data Processing  
- **[/commands/reconcile-income.md](../commands/reconcile-income.md)** - Cross-source validation
- **[/docs/technical/database-schema.md](../docs/technical/database-schema.md)** - Data structure reference

### System Administration
- **[/docs/decisions/001-supabase-over-sqlite.md](../docs/decisions/001-supabase-over-sqlite.md)** - Database platform rationale
- **[.claude/CLAUDE.md](../.claude/CLAUDE.md)** - Project configuration and setup

---

*Data exports bridge internal processing with external systems. Maintain integrity, security, and auditability throughout the export lifecycle.*