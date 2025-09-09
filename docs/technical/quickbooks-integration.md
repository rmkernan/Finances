# QuickBooks Integration Specifications

**Created:** 09/09/25 6:08PM ET  
**Updated:** 09/09/25 6:08PM ET  
**Purpose:** Technical specifications for QuickBooks QBO export and integration  
**Related:** [QBO Generation Command](/Users/richkernan/Projects/Finances/commands/generate-qbo.md)

## Integration Overview

### Cash Flow Integration Philosophy
The QuickBooks integration treats the brokerage account as a **cash management account** rather than an investment tracking system. Focus on cash flows (income, expenses, transfers) while excluding internal security position changes.

### Benefits of QBO Integration
- **Eliminates Manual Entry:** Automatic import of all brokerage cash flows
- **Preserves Tax Categories:** Income properly classified for tax preparation
- **Maintains Audit Trail:** Complete linkage between source documents and bookkeeping
- **Supports Reconciliation:** Monthly account reconciliation in QuickBooks
- **Enables Reporting:** Standard QuickBooks reports include investment activity

## Technical Architecture

### OFX (Open Financial Exchange) Format
QBO files use OFX XML format, the industry standard for financial data exchange between institutions and accounting software.

#### Core OFX Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<OFX>
    <SIGNONMSGSRSV1>
        <!-- Authentication and session info -->
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <!-- Bank account and transaction data -->
        <STMTTRNRS>
            <STMTRS>
                <BANKACCTFROM>
                    <!-- Account identification -->
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <!-- Individual transactions -->
                </BANKTRANLIST>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
```

#### Account Identification Strategy
```xml
<BANKACCTFROM>
    <BANKID>FIDELITY001</BANKID>           <!-- Synthetic routing number -->
    <ACCTID>Z40394067</ACCTID>             <!-- Actual Fidelity account number -->
    <ACCTTYPE>CHECKING</ACCTTYPE>          <!-- Treat as checking account -->
</BANKACCTFROM>
```

**Rationale:** Using CHECKING account type enables standard bank reconciliation workflows in QuickBooks, which is appropriate for cash flow tracking.

## Transaction Mapping Specifications

### Cash Flow Transaction Types

#### Income Transactions (DEPOSIT)
```yaml
dividend_income:
  source_transaction_type: "dividend"
  qbo_transaction_type: "DEPOSIT"
  amount_handling: "Positive value as-is"
  memo_format: "{security_symbol} - Dividend Payment"
  category_mapping: "Based on tax treatment and security type"

interest_income:
  source_transaction_type: "interest"  
  qbo_transaction_type: "DEPOSIT"
  amount_handling: "Positive value as-is"
  memo_format: "{security_symbol} - Interest Payment ({tax_status})"
  category_mapping: "Federal/state tax treatment drives account assignment"

bond_redemption:
  source_transaction_type: "redemption"
  qbo_transaction_type: "DEPOSIT"
  amount_handling: "Principal amount received"
  memo_format: "{security_name} - Bond Redemption"
  category_mapping: "Bond Principal Repayment (non-taxable)"
```

#### Cash Movement Transactions
```yaml
account_deposit:
  source_transaction_type: "deposit"
  qbo_transaction_type: "DEPOSIT"
  amount_handling: "Positive value as-is"
  memo_format: "Transfer from {source_account}"
  category_mapping: "Transfer account or capital contribution"

account_withdrawal:
  source_transaction_type: "withdrawal"
  qbo_transaction_type: "DEBIT"
  amount_handling: "Convert negative to positive for QBO"
  memo_format: "Transfer to {destination_account}"
  category_mapping: "Transfer account or distribution"
```

#### Expense Transactions (FEE)
```yaml
investment_fees:
  source_transaction_type: "fee"
  qbo_transaction_type: "FEE"
  amount_handling: "Convert negative to positive for QBO"
  memo_format: "{fee_type} - {description}"
  category_mapping: "Investment expense accounts"
```

### Excluded Transaction Types
```markdown
Internal Transactions NOT Exported to QBO:
- Security purchases/sales (only net cash impact matters)
- Reinvestment transactions (automatic, no net cash change)  
- Position transfers between funds (internal rebalancing)
- Market value adjustments (unrealized gains/losses)
- Share splits and stock dividends (position changes only)
```

## Unique Transaction Identification (FITID)

### FITID Generation Strategy
```python
def generate_fitid(account_number, settlement_date, transaction_type, security_symbol, sequence):
    """
    Generate unique, stable transaction identifier for QBO import
    
    Format: {AccountNumber}_{YYYYMMDD}_{TransactionType}_{SecuritySymbol}_{Sequence}
    Example: Z40394067_20240131_DIV_FSIXX_001
    """
    clean_account = account_number.replace('-', '')
    date_str = settlement_date.strftime('%Y%m%d')
    trans_type = transaction_type[:3].upper()
    symbol = security_symbol or 'CASH'
    seq = f"{sequence:03d}"
    
    return f"{clean_account}_{date_str}_{trans_type}_{symbol}_{seq}"
```

### FITID Uniqueness Requirements
```sql
-- Ensure FITID uniqueness before QBO export
WITH fitid_check AS (
    SELECT 
        CONCAT(
            REPLACE(a.account_number, '-', ''),
            '_',
            TO_CHAR(t.settlement_date, 'YYYYMMDD'),
            '_',
            UPPER(LEFT(t.transaction_type, 3)),
            '_',
            COALESCE(t.security_symbol, 'CASH'),
            '_',
            LPAD(ROW_NUMBER() OVER (
                PARTITION BY t.settlement_date, a.account_number 
                ORDER BY t.transaction_date, t.id
            )::text, 3, '0')
        ) as fitid,
        t.id as transaction_id
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE t.settlement_date BETWEEN :start_date AND :end_date
)
SELECT fitid, COUNT(*) as duplicate_count
FROM fitid_check
GROUP BY fitid
HAVING COUNT(*) > 1;  -- Should return no rows
```

## QuickBooks Account Structure

### Recommended Chart of Accounts

#### Asset Accounts
```
1000 - Assets
├── 1100 - Current Assets  
│   ├── 1110 - Operating Cash
│   └── 1120 - Fidelity Brokerage Cash (Z40-394067)
└── 1200 - Investments (Summary Only)
    └── 1210 - Investment Account Summary
```

#### Income Accounts
```
4000 - Investment Income
├── 4010 - Dividend Income
│   ├── 4011 - Qualified Dividends
│   └── 4012 - Ordinary Dividends
├── 4020 - Interest Income
│   ├── 4021 - Taxable Interest
│   └── 4022 - Tax-Exempt Interest
│       ├── 4022.1 - GA Municipal (State Exempt)
│       └── 4022.2 - Out-of-State Municipal (State Taxable)
└── 4030 - Other Investment Income
    ├── 4031 - Bond Principal Repayments
    └── 4032 - Capital Gains
```

#### Expense Accounts
```
6000 - Investment Expenses
├── 6010 - Investment Management Fees
├── 6020 - Investment Advisory Fees
└── 6030 - Transaction and Other Fees

7000 - Transfer Accounts
├── 7010 - Transfers to Investment Account
└── 7020 - Transfers from Investment Account
```

### Account Mapping Implementation
```sql
-- Function to map transactions to QuickBooks accounts
CREATE OR REPLACE FUNCTION map_to_qb_account(
    p_transaction_type TEXT,
    p_federal_taxable BOOLEAN,
    p_state_taxable BOOLEAN,
    p_tax_category TEXT,
    p_issuer_state_code TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        -- Dividend income mapping
        WHEN p_transaction_type = 'dividend' AND p_tax_category = 'qualified_dividend' 
            THEN '4011 - Qualified Dividends'
        WHEN p_transaction_type = 'dividend' 
            THEN '4012 - Ordinary Dividends'
            
        -- Interest income mapping based on tax treatment
        WHEN p_transaction_type = 'interest' AND p_federal_taxable = true
            THEN '4021 - Taxable Interest'
        WHEN p_transaction_type = 'interest' AND p_federal_taxable = false 
             AND p_state_taxable = false AND p_issuer_state_code = 'GA'
            THEN '4022.1 - GA Municipal (State Exempt)'
        WHEN p_transaction_type = 'interest' AND p_federal_taxable = false
            THEN '4022.2 - Out-of-State Municipal (State Taxable)'
            
        -- Other income types
        WHEN p_transaction_type = 'redemption'
            THEN '4031 - Bond Principal Repayments'
            
        -- Cash movements
        WHEN p_transaction_type = 'withdrawal'
            THEN '7020 - Transfers from Investment Account'
        WHEN p_transaction_type = 'deposit'
            THEN '7010 - Transfers to Investment Account'
            
        -- Fees and expenses
        WHEN p_transaction_type = 'fee'
            THEN '6010 - Investment Management Fees'
            
        ELSE 'UNMAPPED - ' || p_transaction_type
    END;
END;
$$ LANGUAGE plpgsql;
```

## QBO Export Process

### Export Query Implementation
```sql
-- Generate QBO export data for specific period
WITH qbo_transactions AS (
    SELECT 
        t.settlement_date,
        CASE 
            WHEN t.transaction_type IN ('dividend', 'interest', 'redemption', 'deposit') 
                THEN 'DEPOSIT'
            WHEN t.transaction_type = 'withdrawal' 
                THEN 'DEBIT'
            WHEN t.transaction_type = 'fee' 
                THEN 'FEE'
            ELSE 'OTHER'
        END as qbo_transaction_type,
        
        ABS(t.amount) as qbo_amount,  -- Ensure positive amounts for QBO
        
        -- Generate unique FITID
        CONCAT(
            REPLACE(a.account_number, '-', ''),
            '_',
            TO_CHAR(t.settlement_date, 'YYYYMMDD'),
            '_',
            UPPER(LEFT(t.transaction_type, 3)),
            '_',
            COALESCE(t.security_symbol, 'CASH'),
            '_',
            LPAD(ROW_NUMBER() OVER (
                PARTITION BY t.settlement_date, a.account_number 
                ORDER BY t.transaction_date, t.id
            )::text, 3, '0')
        ) as fitid,
        
        -- Payee name for QBO
        CASE 
            WHEN t.security_name IS NOT NULL 
                THEN LEFT(t.security_name, 32)  -- QBO length limit
            ELSE 'Fidelity Brokerage'
        END as payee_name,
        
        -- Transaction memo
        CASE 
            WHEN t.security_symbol IS NOT NULL
                THEN t.security_symbol || ' - ' || INITCAP(t.transaction_type)
            ELSE INITCAP(t.transaction_type)
        END as memo,
        
        -- QuickBooks account mapping
        map_to_qb_account(
            t.transaction_type,
            t.federal_taxable,
            t.state_taxable,
            t.tax_category,
            t.issuer_state_code
        ) as qb_account,
        
        a.account_number,
        a.account_name
        
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE t.settlement_date BETWEEN :export_start_date AND :export_end_date
    AND t.transaction_type IN ('dividend', 'interest', 'withdrawal', 'deposit', 'fee', 'redemption')
    AND t.amount != 0  -- Exclude zero-amount transactions
)
SELECT * FROM qbo_transactions
ORDER BY settlement_date, fitid;
```

## Data Validation and Quality Assurance

### Pre-Export Validation
```sql
-- Comprehensive pre-export validation checks
WITH validation_results AS (
    -- Check for missing settlement dates
    SELECT 'Missing Settlement Dates' as check_type, COUNT(*) as issue_count
    FROM transactions 
    WHERE settlement_date IS NULL 
    AND transaction_date BETWEEN :export_start_date AND :export_end_date
    
    UNION ALL
    
    -- Check for zero amounts
    SELECT 'Zero Amount Transactions', COUNT(*)
    FROM transactions
    WHERE amount = 0
    AND transaction_date BETWEEN :export_start_date AND :export_end_date
    
    UNION ALL
    
    -- Check for unmapped accounts  
    SELECT 'Unmapped Account Types', COUNT(*)
    FROM transactions t
    WHERE map_to_qb_account(t.transaction_type, t.federal_taxable, 
                           t.state_taxable, t.tax_category, t.issuer_state_code) 
          LIKE 'UNMAPPED%'
    AND t.transaction_date BETWEEN :export_start_date AND :export_end_date
)
SELECT * FROM validation_results WHERE issue_count > 0;
```

### Post-Export Verification
```xml
<!-- QBO file structure validation -->
<verification_checklist>
    <structure_checks>
        <valid_xml>true</valid_xml>
        <ofx_headers_present>true</ofx_headers_present>
        <bank_account_info_complete>true</bank_account_info_complete>
        <transaction_count_matches_export>true</transaction_count_matches_export>
    </structure_checks>
    
    <data_integrity_checks>
        <unique_fitids>true</unique_fitids>
        <positive_amounts>true</positive_amounts>
        <valid_date_formats>true</valid_date_formats>
        <total_amounts_balance>true</total_amounts_balance>
    </data_integrity_checks>
</verification_checklist>
```

## QuickBooks Import Process

### Import Preparation
```markdown
Before importing QBO files into QuickBooks:
1. **Backup QuickBooks Company File** - Create full backup before import
2. **Verify Chart of Accounts** - Ensure required accounts exist
3. **Review Account Mappings** - Confirm mapping configuration is current
4. **Validate QBO File** - Run pre-import validation checks
5. **Test Import Process** - Import small test file first if possible
```

### Import Workflow
```markdown
Standard QuickBooks QBO Import Process:
1. **File → Utilities → Import → Web Connect Files**
2. **Select QBO File** - Choose generated .qbo file  
3. **Review Account Mapping** - Confirm QB account assignments
4. **Assign Categories** - Verify income/expense categorization
5. **Accept Transactions** - Import validated transactions
6. **Run Reconciliation** - Verify account balance matches expectations
```

### Post-Import Reconciliation
```sql
-- Generate reconciliation report comparing QBO export to QB import
SELECT 
    'QBO Export Total' as source,
    SUM(CASE WHEN qbo_transaction_type = 'DEPOSIT' THEN qbo_amount ELSE -qbo_amount END) as net_change
FROM qbo_export_transactions
WHERE export_period = :current_period

-- Compare with QuickBooks account balance change
-- (Manual verification in QB required)
```

## Error Handling and Troubleshooting

### Common QBO Import Issues

#### Invalid OFX Format
```markdown
Symptoms: QuickBooks rejects QBO file with format error
Causes: Invalid XML structure, missing required elements, incorrect date formats
Resolution: Validate OFX structure, check XML syntax, verify date formatting (YYYYMMDD)
```

#### Duplicate Transaction Detection
```markdown
Symptoms: Some transactions skipped during import
Causes: Duplicate FITID values, previous import of same transactions
Resolution: Verify FITID uniqueness, check import history, modify FITID generation if needed
```

#### Account Mapping Failures
```markdown
Symptoms: Transactions imported to wrong accounts or "Uncategorized" 
Causes: Missing QB accounts, incorrect mapping configuration
Resolution: Update QB chart of accounts, verify mapping function, test with sample transactions
```

### Debugging and Diagnostics
```sql
-- Generate diagnostic report for troubleshooting
SELECT 
    t.transaction_type,
    t.federal_taxable,
    t.state_taxable,
    t.tax_category,
    COUNT(*) as transaction_count,
    map_to_qb_account(t.transaction_type, t.federal_taxable, 
                     t.state_taxable, t.tax_category, t.issuer_state_code) as mapped_account
FROM transactions t
WHERE t.settlement_date BETWEEN :export_start_date AND :export_end_date
GROUP BY t.transaction_type, t.federal_taxable, t.state_taxable, t.tax_category,
         map_to_qb_account(t.transaction_type, t.federal_taxable, 
                          t.state_taxable, t.tax_category, t.issuer_state_code)
ORDER BY transaction_count DESC;
```

## Related Documentation

### Implementation Guides
- **[QBO Generation Command](/Users/richkernan/Projects/Finances/commands/generate-qbo.md)** - Step-by-step generation process
- **[Account Mapping Configuration](/Users/richkernan/Projects/Finances/config/accounts-map.md)** - QB account structure

### Business Rules
- **[Processing Doctrine](/Users/richkernan/Projects/Finances/config/doctrine.md)** - Cash flow focus rationale
- **[Tax Rules Configuration](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax treatment preservation

### System Architecture  
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Source data structure
- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Data extraction guidelines

---

*QuickBooks integration enables seamless bookkeeping while maintaining complete audit trails between source documents and accounting records.*