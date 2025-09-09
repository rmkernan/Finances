# Generate QBO Command Template

**Created:** 09/09/25 5:36PM ET  
**Updated:** 09/09/25 5:36PM ET  
**Purpose:** Claude Code command for generating QuickBooks QBO import files

## Command Overview

Generate OFX-format QBO files for importing brokerage account cash flows into QuickBooks. Focus on cash flow events (dividends, interest, withdrawals) while excluding internal security transactions.

## QBO Generation Strategy

### Cash Flow Focus Approach
Treat brokerage account like **bank account reconciliation** rather than investment tracking:

#### INCLUDE in QBO Export
- **Interest/Dividend payments** (actual cash received)
- **Deposits** (cash contributions to brokerage account)
- **Withdrawals** (cash distributions from brokerage account)  
- **Account fees** (management fees, advisory fees)
- **Bond redemptions** (principal payments received)
- **Wire transfers** (cash in/out)

#### EXCLUDE from QBO Export
- ~~Security purchases/sales~~ (only care about cash impact)
- ~~Reinvestment transactions~~ (wash transactions)
- ~~Position changes~~ (share quantity changes)
- ~~Internal transfers between fund positions~~
- ~~Market value adjustments~~

## QBO File Structure

### OFX Format Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <DTSERVER>[TIMESTAMP]</DTSERVER>
            <LANGUAGE>ENG</LANGUAGE>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <TRNUID>[UNIQUE_ID]</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
                <CURDEF>USD</CURDEF>
                <BANKACCTFROM>
                    <BANKID>[ROUTING_NUMBER]</BANKID>
                    <ACCTID>[ACCOUNT_NUMBER]</ACCTID>
                    <ACCTTYPE>CHECKING</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>[PERIOD_START]</DTSTART>
                    <DTEND>[PERIOD_END]</DTEND>
                    
                    <!-- Individual Transactions -->
                    <STMTTRN>
                        <TRNTYPE>[DEPOSIT|DEBIT|FEE]</TRNTYPE>
                        <DTPOSTED>[SETTLEMENT_DATE]</DTPOSTED>
                        <TRNAMT>[AMOUNT]</TRNAMT>
                        <FITID>[UNIQUE_TRANSACTION_ID]</FITID>
                        <NAME>[PAYEE_NAME]</NAME>
                        <MEMO>[TRANSACTION_MEMO]</MEMO>
                    </STMTTRN>
                    
                </BANKTRANLIST>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
```

## Transaction Mapping Rules

### Transaction Type Conversion

#### Income Transactions → DEPOSIT
```sql
-- Convert dividend/interest transactions to deposits
SELECT 
    transaction_date as settlement_date,
    amount,
    'DEPOSIT' as qbo_transaction_type,
    CASE 
        WHEN transaction_type = 'dividend' THEN 'Investment Income - Dividends'
        WHEN transaction_type = 'interest' AND federal_taxable = false 
            THEN 'Investment Income - Tax Exempt Interest'
        WHEN transaction_type = 'interest' AND federal_taxable = true 
            THEN 'Investment Income - Taxable Interest'
        WHEN transaction_type = 'redemption' 
            THEN 'Investment Income - Bond Principal'
    END as qbo_account_category,
    CONCAT(security_symbol, ' - ', LEFT(security_name, 50)) as memo
FROM transactions
WHERE transaction_type IN ('dividend', 'interest', 'redemption')
AND amount > 0;
```

#### Withdrawal Transactions → DEBIT  
```sql
-- Convert withdrawals and transfers out to debits
SELECT 
    transaction_date as settlement_date,
    ABS(amount) as amount,  -- Ensure positive for QBO
    'DEBIT' as qbo_transaction_type,
    'Transfer to Operating Account' as qbo_account_category,
    description as memo
FROM transactions
WHERE transaction_type = 'withdrawal'
AND amount < 0;
```

#### Fee Transactions → FEE
```sql
-- Convert account fees to fee transactions
SELECT 
    transaction_date as settlement_date,
    ABS(amount) as amount,
    'FEE' as qbo_transaction_type,
    'Investment Fees' as qbo_account_category,
    description as memo
FROM transactions
WHERE transaction_type = 'fee'
AND amount < 0;
```

### Sample QBO Transactions

#### From January 2024 Statement
```xml
<!-- FSIXX Dividend - $4,327.65 -->
<STMTTRN>
    <TRNTYPE>DEPOSIT</TRNTYPE>
    <DTPOSTED>20240131</DTPOSTED>
    <TRNAMT>4327.65</TRNAMT>
    <FITID>Z40394067_20240131_DIV_FSIXX</FITID>
    <NAME>Fidelity Government Income Fund</NAME>
    <MEMO>FSIXX - Dividend Payment</MEMO>
</STMTTRN>

<!-- SPAXX Dividend - $2.03 -->
<STMTTRN>
    <TRNTYPE>DEPOSIT</TRNTYPE>
    <DTPOSTED>20240131</DTPOSTED>
    <TRNAMT>2.03</TRNAMT>
    <FITID>Z40394067_20240131_DIV_SPAXX</FITID>
    <NAME>Fidelity Government Money Market</NAME>
    <MEMO>SPAXX - Dividend Payment</MEMO>
</STMTTRN>

<!-- Wire Transfer Out - $200,000 -->
<STMTTRN>
    <TRNTYPE>DEBIT</TRNTYPE>
    <DTPOSTED>20240130</DTPOSTED>
    <TRNAMT>200000.00</TRNAMT>
    <FITID>Z40394067_20240130_WIRE_OUT</FITID>
    <NAME>Reliant Income Fund</NAME>
    <MEMO>Wire Transfer to Reliant Income Fund</MEMO>
</STMTTRN>
```

## QBO Generation Workflow

### 1. Period Selection & Data Query

#### Select Export Period
```sql
-- Generate QBO for specific month or date range
WITH export_period AS (
    SELECT 
        '2024-01-01'::date as period_start,
        '2024-01-31'::date as period_end,
        'Z40-394067' as account_number
)
SELECT 
    t.*,
    a.account_name,
    a.institution
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN export_period p ON t.transaction_date BETWEEN p.period_start AND p.period_end
    AND a.account_number = p.account_number
WHERE t.transaction_type IN ('dividend', 'interest', 'withdrawal', 'deposit', 'fee', 'redemption')
ORDER BY t.settlement_date, t.transaction_date;
```

### 2. Transaction Filtering & Validation

#### Apply Cash Flow Filters
```sql
-- Exclude internal transactions that don't affect cash position
SELECT * FROM transactions 
WHERE transaction_type IN ('dividend', 'interest', 'withdrawal', 'deposit', 'fee', 'redemption')
-- Exclude reinvestments and internal position changes
AND NOT (description ILIKE '%reinvest%' OR description ILIKE '%exchange%')
-- Only include transactions with real cash impact
AND amount != 0;
```

#### Validate Data Completeness
```markdown
Pre-export validation checklist:
- [ ] All cash flow transactions have settlement dates
- [ ] No duplicate FITID values (unique transaction identifiers)
- [ ] Amount precision preserved (2 decimal places)
- [ ] Transaction types properly classified
- [ ] Account mapping configured for target QuickBooks chart of accounts
```

### 3. Generate Unique Transaction IDs

#### FITID Format Strategy
```sql
-- Create unique, stable transaction identifiers
SELECT 
    CONCAT(
        REPLACE(account_number, '-', ''),  -- Z40394067
        '_',
        TO_CHAR(settlement_date, 'YYYYMMDD'),  -- 20240131
        '_',
        UPPER(LEFT(transaction_type, 3)),  -- DIV, INT, WTH
        '_',
        COALESCE(security_symbol, 'CASH'),  -- FSIXX, SPAXX, CASH
        '_',
        LPAD(ROW_NUMBER() OVER (PARTITION BY settlement_date ORDER BY transaction_date), 3, '0')  -- 001
    ) as fitid
FROM transactions;
```

#### Duplicate Prevention
```sql
-- Verify FITID uniqueness before export
SELECT fitid, COUNT(*) 
FROM qbo_export_staging
GROUP BY fitid 
HAVING COUNT(*) > 1;
```

### 4. Account Mapping Configuration

#### QuickBooks Account Structure
```sql
-- Map transaction types to QuickBooks accounts
CREATE TABLE qb_account_mapping (
    transaction_type TEXT,
    federal_taxable BOOLEAN,
    state_taxable BOOLEAN,
    qb_account_name TEXT,
    qb_account_type TEXT
);

INSERT INTO qb_account_mapping VALUES
('dividend', true, true, 'Investment Income:Dividends:Taxable', 'Income'),
('interest', false, false, 'Investment Income:Interest:Tax Exempt', 'Income'),
('interest', true, true, 'Investment Income:Interest:Taxable', 'Income'),
('withdrawal', null, null, 'Transfer:From Investment Account', 'Expense'),
('redemption', null, null, 'Investment Income:Bond Principal', 'Income'),
('fee', null, null, 'Investment Fees', 'Expense');
```

### 5. Generate OFX File

#### File Generation Process
```python
# Python pseudocode for QBO file generation
def generate_qbo_file(transactions, account_info, period_start, period_end):
    ofx_content = build_ofx_header()
    ofx_content += build_account_info(account_info)
    ofx_content += build_transaction_list(transactions, period_start, period_end)
    ofx_content += build_ofx_footer()
    
    filename = f"Fidelity_{account_info.account_number}_{period_start}_{period_end}.qbo"
    save_file(filename, ofx_content)
    
    return filename
```

#### Output File Location
```bash
# Save QBO files to exports directory
/Users/richkernan/Projects/Finances/data/exports/qbo/
```

## Quality Assurance & Validation

### Pre-Import Testing

#### QBO File Validation
```markdown
Before importing to QuickBooks:
1. **File Format Check:** Validate OFX XML structure
2. **Amount Verification:** Confirm transaction amounts match source data
3. **Date Range Check:** Ensure all transactions fall within specified period  
4. **Duplicate Check:** Verify no duplicate FITID values
5. **Account Balance:** QBO net change should match statement cash flow
```

#### Test Import Process
```markdown
1. **Backup QuickBooks:** Create backup before test import
2. **Small Test Set:** Import single month first
3. **Transaction Review:** Verify transactions appear in correct accounts
4. **Reconciliation Test:** Confirm transactions can be matched/reconciled
5. **Duplicate Prevention:** Re-import same file should be rejected/ignored
```

### Post-Import Reconciliation

#### QuickBooks Reconciliation Workflow
```markdown
After successful QBO import:
1. **Account Reconciliation:** Match imported transactions to Fidelity statement
2. **Category Verification:** Confirm income/expense accounts assigned correctly  
3. **Tax Treatment Check:** Verify tax-exempt vs taxable categorization
4. **Cash Flow Validation:** Net change matches brokerage account cash flow
```

## Account Configuration Templates

### QuickBooks Chart of Accounts Setup

#### Recommended Account Structure
```
Assets
├── Current Assets
│   └── Fidelity Brokerage Account (Z40-394067)

Income  
├── Investment Income
│   ├── Dividends
│   │   ├── Taxable Dividends
│   │   └── Qualified Dividends
│   ├── Interest Income
│   │   ├── Taxable Interest  
│   │   └── Tax-Exempt Interest (Municipal)
│   └── Bond Principal Payments

Expenses
├── Investment Fees
└── Transfer Expenses
```

### Account Mapping Configuration File

#### Create mapping configuration
```markdown
Save account mappings in:
/Users/richkernan/Projects/Finances/config/accounts-map.md

This allows customization without code changes and supports
multiple account structures or QuickBooks company files.
```

## Error Handling & Troubleshooting

### Common QBO Issues

#### Invalid OFX Format
```markdown
Symptoms: QuickBooks rejects import file
Solutions:
- Validate XML structure with OFX schema
- Check date formats (YYYYMMDD required)
- Verify required OFX elements present
- Test with minimal transaction set first
```

#### Duplicate Transaction Detection
```markdown
Symptoms: Some transactions not importing
Solutions:  
- Check FITID uniqueness and stability
- Verify transaction hasn't been imported previously
- Review QuickBooks import history
- Consider FITID format changes if needed
```

#### Account Mapping Errors
```markdown
Symptoms: Transactions appear in wrong accounts
Solutions:
- Review account mapping configuration
- Verify QuickBooks chart of accounts matches expectations
- Update mapping rules for new transaction types
- Test mapping with small transaction set
```

## Related Resources

- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Transaction classification guidelines
- **[Account Mapping Config](/Users/richkernan/Projects/Finances/config/accounts-map.md)** - QuickBooks account structure
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Source data structure
- **[Sample Data Analysis](/Users/richkernan/Projects/Finances/docs/archive/context.md)** - Real transaction examples

---

*QBO generation enables seamless QuickBooks integration while maintaining complete audit trail between source documents and bookkeeping records.*