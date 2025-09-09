# Reconcile Income Command Template

**Created:** 09/09/25 5:32PM ET  
**Updated:** 09/09/25 5:32PM ET  
**Purpose:** Claude Code command for cross-source income reconciliation

## Command Overview

Use this template to reconcile income data across multiple sources (Fidelity statements, 1099 forms, QuickBooks exports) and identify discrepancies requiring investigation.

## Reconciliation Strategy

### Known Discrepancy Patterns
Based on historical analysis, expect these common discrepancies:
- **Official vs Informational 1099s:** Corporate exemption creates $0 official vs actual amounts informational
- **Fidelity vs QuickBooks:** PPR Interest payments may appear in QB but not Fidelity statements  
- **Statement vs 1099 Timing:** Monthly transactions may aggregate differently due to settlement vs transaction dates

## Reconciliation Queries

### 1. Monthly Statement vs 1099 Summary Reconciliation

#### Dividend Reconciliation
```sql
-- Compare monthly statement dividend totals vs 1099-DIV Box 1a
WITH monthly_dividends AS (
    SELECT 
        account_id,
        EXTRACT(year FROM transaction_date) as tax_year,
        SUM(amount) as statement_dividend_total
    FROM transactions 
    WHERE transaction_type = 'dividend'
    AND EXTRACT(year FROM transaction_date) = 2024
    GROUP BY account_id, EXTRACT(year FROM transaction_date)
),
form_1099_div AS (
    SELECT 
        account_id,
        tax_year,
        ordinary_dividends,
        is_official
    FROM tax_reports 
    WHERE form_type = '1099-DIV' 
    AND tax_year = 2024
)
SELECT 
    m.account_id,
    m.tax_year,
    m.statement_dividend_total,
    f_official.ordinary_dividends as official_1099_amount,
    f_info.ordinary_dividends as informational_1099_amount,
    (m.statement_dividend_total - COALESCE(f_official.ordinary_dividends, 0)) as official_variance,
    (m.statement_dividend_total - COALESCE(f_info.ordinary_dividends, 0)) as informational_variance
FROM monthly_dividends m
LEFT JOIN form_1099_div f_official ON m.account_id = f_official.account_id 
    AND m.tax_year = f_official.tax_year AND f_official.is_official = true
LEFT JOIN form_1099_div f_info ON m.account_id = f_info.account_id 
    AND m.tax_year = f_info.tax_year AND f_info.is_official = false;
```

#### Expected Results Analysis
```markdown
For Milton Preschool Inc corporate exemption:
- Official 1099: $0 (corporate exemption)
- Informational 1099: ~$29,515 (actual dividends)  
- Monthly statements: Should aggregate to ~$29,515
- Variance with official: Expected ~$29,515 (flag as "corporate_exemption")
- Variance with informational: Should be < $10 (flag if larger)
```

### 2. Tax-Exempt Interest Reconciliation

#### Municipal Bond Interest Analysis
```sql
-- Compare statement municipal interest vs 1099-INT Box 8
WITH municipal_interest AS (
    SELECT 
        account_id,
        EXTRACT(year FROM transaction_date) as tax_year,
        issuer_state_code,
        SUM(amount) as statement_exempt_interest
    FROM transactions 
    WHERE transaction_type = 'interest' 
    AND federal_taxable = false
    AND EXTRACT(year FROM transaction_date) = 2024
    GROUP BY account_id, EXTRACT(year FROM transaction_date), issuer_state_code
),
form_1099_int AS (
    SELECT 
        account_id,
        tax_year,
        tax_exempt_interest,
        is_official
    FROM tax_reports 
    WHERE form_type = '1099-INT' 
    AND tax_year = 2024
)
SELECT 
    m.account_id,
    m.tax_year,
    m.issuer_state_code,
    m.statement_exempt_interest,
    f.tax_exempt_interest as form_1099_amount,
    (m.statement_exempt_interest - COALESCE(f.tax_exempt_interest, 0)) as variance
FROM municipal_interest m
LEFT JOIN form_1099_int f ON m.account_id = f.account_id 
    AND m.tax_year = f.tax_year
ORDER BY ABS(m.statement_exempt_interest - COALESCE(f.tax_exempt_interest, 0)) DESC;
```

### 3. QuickBooks vs Fidelity Cross-Validation

#### Missing Transaction Detection
```sql
-- Identify transactions in QuickBooks but not in Fidelity statements
-- Focus on "PPR Interest" and similar patterns

WITH qb_income AS (
    SELECT 
        account_id,
        transaction_date,
        amount,
        description,
        'quickbooks' as source
    FROM transactions t
    JOIN documents d ON t.document_id = d.id
    WHERE d.document_type = 'quickbooks'
    AND transaction_type IN ('interest', 'dividend')
    AND EXTRACT(year FROM transaction_date) = 2024
),
fidelity_income AS (
    SELECT 
        account_id,
        transaction_date,
        amount,
        description,
        'fidelity' as source
    FROM transactions t
    JOIN documents d ON t.document_id = d.id
    WHERE d.document_type IN ('statement', '1099_official', '1099_info')
    AND transaction_type IN ('interest', 'dividend')
    AND EXTRACT(year FROM transaction_date) = 2024
)
-- Find QuickBooks transactions without matching Fidelity transactions
SELECT DISTINCT
    qb.account_id,
    qb.transaction_date,
    qb.amount,
    qb.description,
    'QB_ONLY' as variance_type
FROM qb_income qb
LEFT JOIN fidelity_income f ON qb.account_id = f.account_id
    AND qb.transaction_date = f.transaction_date  
    AND ABS(qb.amount - f.amount) < 0.01
WHERE f.account_id IS NULL
ORDER BY qb.transaction_date, qb.amount DESC;
```

#### Expected PPR Interest Gap
```markdown
Based on historical analysis:
- QuickBooks shows ~$23,000 in "PPR Interest" payments
- Fidelity statements may not show these transactions
- This represents a significant reconciliation item requiring investigation
- Flag as "missing_from_fidelity" for follow-up
```

## Reconciliation Workflow

### 1. Data Completeness Check

#### Verify All Sources Processed
```sql
-- Ensure we have all expected document types for the reconciliation period
SELECT 
    account_id,
    document_type,
    COUNT(*) as document_count,
    MIN(period_start) as earliest_period,
    MAX(period_end) as latest_period
FROM documents 
WHERE EXTRACT(year FROM period_start) = 2024
GROUP BY account_id, document_type
ORDER BY account_id, document_type;
```

#### Expected Document Coverage
```markdown
For complete 2024 reconciliation, expect:
- 12 monthly statements (January-December)
- 1+ 1099-DIV forms (official and/or informational)
- 1+ 1099-INT forms (tax-exempt interest)
- 1+ 1099-B forms (bond redemptions)  
- 1 QuickBooks export (annual summary)
```

### 2. Execute Reconciliation Queries

#### Run All Cross-Source Comparisons
```bash
# Execute the reconciliation queries above
# Document variances and flag items requiring investigation
# Create data quality flags for significant discrepancies
```

#### Variance Threshold Guidelines
```markdown
Acceptable Variances:
- < $1: Rounding differences (normal)
- $1-$10: Minor timing/settlement differences (review)  
- > $10: Significant discrepancy (requires investigation)

Special Cases:
- Corporate exemption: Official $0 vs actual amounts (expected)
- PPR Interest: QB-only transactions (known gap)
- Municipal bond timing: Settlement vs transaction date differences
```

### 3. Generate Reconciliation Report

#### Summary Report Template
```markdown
# Income Reconciliation Report - [Year]

## Account: [Account Name] ([Account Number])
**Report Date:** [Current Date]
**Period:** [Tax Year]

## Summary Totals
| Source | Dividends | Interest | Tax-Exempt Interest | Total Income |
|--------|-----------|----------|-------------------|--------------|
| Monthly Statements | $[amount] | $[amount] | $[amount] | $[amount] |
| 1099 Official | $[amount] | $[amount] | $[amount] | $[amount] |
| 1099 Informational | $[amount] | $[amount] | $[amount] | $[amount] |
| QuickBooks | $[amount] | $[amount] | $[amount] | $[amount] |

## Significant Variances (> $10)

### [Variance Type] - $[Amount]
**Description:** [Details of discrepancy]
**Sources:** [Which sources show variance]
**Recommended Action:** [Investigation needed / known issue / etc.]

## Data Quality Flags
- [Count] flags created for manual review
- [Count] corporate exemption notices (expected)
- [Count] missing transaction investigations required

## Reconciliation Status
- ✓ [Completed items]
- ❌ [Items requiring follow-up]
- ⚠️ [Items flagged for manual review]
```

## Investigation Procedures

### For Significant Variances

#### Step 1: Document Analysis
```markdown
1. Review original source documents for missing transactions
2. Check PDF extraction quality and completeness  
3. Verify tax classification and categorization accuracy
4. Look for settlement date vs transaction date timing differences
```

#### Step 2: Cross-Reference Validation
```markdown
1. Compare similar months/periods for pattern consistency
2. Check for known corporate exemption or special tax status
3. Validate municipal bond issuer state classifications
4. Review QuickBooks export for additional transaction sources
```

#### Step 3: Flag for Resolution
```sql
-- Create data quality flags for unresolved variances
INSERT INTO data_quality_flags (
    document_id, transaction_id, flag_type, severity, description
) VALUES (
    [doc_id], [trans_id], 'reconciliation_variance', 'warning',
    'Cross-source variance of $[amount] between [source1] and [source2]'
);
```

### For Missing Transactions

#### Investigation Process
```markdown
1. Verify transaction exists in source document
2. Check if extraction process missed or misclassified
3. Determine if timing difference or genuine gap
4. Research transaction type (PPR Interest, bond payments, etc.)
5. Update extraction rules if systematic issue identified
```

## Automated Reconciliation Monitoring

### Daily Reconciliation Checks
```sql
-- Set up automated variance detection
CREATE OR REPLACE FUNCTION daily_reconciliation_check()
RETURNS TABLE(variance_summary TEXT) AS $$
BEGIN
    -- Run key reconciliation queries
    -- Flag variances > $10 for investigation
    -- Generate summary for daily review
END;
$$ LANGUAGE plpgsql;
```

### Alert Thresholds
```markdown
Immediate Alerts (> $100 variance):
- Likely extraction error or missing document
- Requires same-day investigation

Weekly Review (> $10 variance):
- May indicate systematic issue
- Schedule for next reconciliation cycle

Monthly Summary (all variances):
- Complete reconciliation report
- Document resolution of all flagged items
```

## Related Resources

- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Data extraction guidelines
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Table relationships for queries
- **[Known Discrepancies](/Users/richkernan/Projects/Finances/docs/archive/context.md)** - Historical patterns and explanations
- **[Tax Rules Config](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax classification validation

---

*Reconciliation is critical for financial data integrity. Flag uncertainties for investigation rather than making assumptions about variances.*