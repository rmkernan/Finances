# QuickBooks Account Mapping Configuration

**Created:** 09/09/25 5:44PM ET  
**Updated:** 09/09/25 5:44PM ET  
**Purpose:** Maps financial transactions to QuickBooks chart of accounts  
**Usage:** Referenced during QBO file generation

## Account Mapping Philosophy

### Cash Flow Integration Approach
Map brokerage account transactions to QuickBooks as **cash flow events** rather than investment position tracking. Focus on income recognition and cash movement for proper bookkeeping integration.

### Account Structure Requirements
QuickBooks chart of accounts should reflect tax treatment distinctions for proper income categorization and tax preparation support.

## Recommended QuickBooks Chart of Accounts

### Assets
```
Current Assets
├── Cash and Cash Equivalents
│   ├── Operating Cash Account
│   └── Fidelity Brokerage Cash (Z40-394067)
└── Investments
    └── Investment Account Summary (for reference only)
```

### Income Accounts
```
Investment Income
├── Dividend Income  
│   ├── 4010 - Qualified Dividends
│   └── 4020 - Ordinary Dividends
├── Interest Income
│   ├── 4030 - Taxable Interest Income
│   └── 4040 - Tax-Exempt Municipal Interest
│       ├── 4041 - GA Municipal Interest (State Exempt)
│       └── 4042 - Out-of-State Municipal Interest (State Taxable)
└── Other Investment Income
    ├── 4050 - Bond Principal Repayments
    └── 4060 - Capital Gains (Short/Long Term)
```

### Expense Accounts
```
Investment Expenses
├── 6010 - Investment Management Fees
├── 6020 - Advisory Fees
└── 6030 - Transaction Fees

Transfer Accounts
├── 7010 - Transfer to Investment Account
└── 7020 - Transfer from Investment Account
```

## Transaction Type Mappings

### Income Transaction Mappings

#### Dividend Classifications
```yaml
dividend_mappings:
  qualified_dividend:
    qb_account: "4010 - Qualified Dividends"
    qb_type: "DEPOSIT"
    tax_treatment: "Federal/State Taxable - Preferential Rates"
    
  ordinary_dividend:
    qb_account: "4020 - Ordinary Dividends"  
    qb_type: "DEPOSIT"
    tax_treatment: "Federal/State Taxable - Ordinary Rates"
```

#### Interest Income Classifications
```yaml
interest_mappings:
  taxable_interest:
    condition: "federal_taxable = true AND state_taxable = true"
    qb_account: "4030 - Taxable Interest Income"
    qb_type: "DEPOSIT"
    tax_treatment: "Fully Taxable"
    
  municipal_interest_ga:
    condition: "federal_taxable = false AND state_taxable = false AND issuer_state_code = 'GA'"
    qb_account: "4041 - GA Municipal Interest (State Exempt)"
    qb_type: "DEPOSIT" 
    tax_treatment: "Federal and State Exempt"
    
  municipal_interest_other:
    condition: "federal_taxable = false AND state_taxable = true AND issuer_state_code != 'GA'"
    qb_account: "4042 - Out-of-State Municipal Interest (State Taxable)"
    qb_type: "DEPOSIT"
    tax_treatment: "Federal Exempt, State Taxable"
```

#### Other Income Classifications
```yaml
other_income_mappings:
  bond_redemption:
    condition: "transaction_type = 'redemption'"
    qb_account: "4050 - Bond Principal Repayments"
    qb_type: "DEPOSIT"
    tax_treatment: "Return of Principal (Non-Taxable)"
    
  capital_gains:
    condition: "transaction_type = 'sale' AND (amount - cost_basis) != 0"
    qb_account: "4060 - Capital Gains"
    qb_type: "DEPOSIT" # or "DEBIT" for losses
    tax_treatment: "Capital Gains Treatment"
```

### Cash Flow Transaction Mappings

#### Transfer Classifications
```yaml
transfer_mappings:
  deposit_to_account:
    condition: "transaction_type = 'deposit' AND amount > 0"
    qb_account: "7010 - Transfer to Investment Account"  
    qb_type: "DEPOSIT"
    contra_account: "Operating Cash Account"
    
  withdrawal_from_account:
    condition: "transaction_type = 'withdrawal' AND amount < 0"
    qb_account: "7020 - Transfer from Investment Account"
    qb_type: "DEBIT" 
    contra_account: "Operating Cash Account"
```

#### Fee Classifications
```yaml
fee_mappings:
  management_fee:
    condition: "transaction_type = 'fee' AND description ILIKE '%management%'"
    qb_account: "6010 - Investment Management Fees"
    qb_type: "FEE"
    tax_treatment: "Deductible Investment Expense"
    
  advisory_fee:  
    condition: "transaction_type = 'fee' AND description ILIKE '%advisory%'"
    qb_account: "6020 - Advisory Fees"
    qb_type: "FEE"
    tax_treatment: "Deductible Investment Expense"
    
  transaction_fee:
    condition: "transaction_type = 'fee' AND description ILIKE '%transaction%'"
    qb_account: "6030 - Transaction Fees"
    qb_type: "FEE"
    tax_treatment: "Deductible Investment Expense"
```

## Mapping Implementation

### SQL Mapping Function
```sql
-- Function to determine QuickBooks account based on transaction attributes
CREATE OR REPLACE FUNCTION get_qb_account_mapping(
    p_transaction_type TEXT,
    p_federal_taxable BOOLEAN,
    p_state_taxable BOOLEAN,
    p_issuer_state_code TEXT,
    p_description TEXT
) RETURNS TABLE (
    qb_account_name TEXT,
    qb_transaction_type TEXT,
    tax_treatment TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            -- Dividend income
            WHEN p_transaction_type = 'dividend' AND p_description ILIKE '%qualified%' 
                THEN '4010 - Qualified Dividends'
            WHEN p_transaction_type = 'dividend' 
                THEN '4020 - Ordinary Dividends'
                
            -- Interest income  
            WHEN p_transaction_type = 'interest' AND p_federal_taxable = false AND p_state_taxable = false
                THEN '4041 - GA Municipal Interest (State Exempt)'
            WHEN p_transaction_type = 'interest' AND p_federal_taxable = false AND p_state_taxable = true
                THEN '4042 - Out-of-State Municipal Interest (State Taxable)'
            WHEN p_transaction_type = 'interest' AND p_federal_taxable = true
                THEN '4030 - Taxable Interest Income'
                
            -- Bond redemptions
            WHEN p_transaction_type = 'redemption'
                THEN '4050 - Bond Principal Repayments'
                
            -- Transfers
            WHEN p_transaction_type = 'withdrawal'
                THEN '7020 - Transfer from Investment Account'
            WHEN p_transaction_type = 'deposit'
                THEN '7010 - Transfer to Investment Account'
                
            -- Fees
            WHEN p_transaction_type = 'fee' AND p_description ILIKE '%management%'
                THEN '6010 - Investment Management Fees'
            WHEN p_transaction_type = 'fee' AND p_description ILIKE '%advisory%'
                THEN '6020 - Advisory Fees'
            WHEN p_transaction_type = 'fee'
                THEN '6030 - Transaction Fees'
                
            ELSE 'UNMAPPED - ' || p_transaction_type
        END as account_name,
        
        CASE 
            WHEN p_transaction_type IN ('dividend', 'interest', 'redemption', 'deposit') THEN 'DEPOSIT'
            WHEN p_transaction_type IN ('withdrawal') THEN 'DEBIT'
            WHEN p_transaction_type = 'fee' THEN 'FEE'
            ELSE 'OTHER'
        END as transaction_type,
        
        CASE 
            WHEN p_federal_taxable = false AND p_state_taxable = false THEN 'Tax Exempt (Fed & State)'
            WHEN p_federal_taxable = false AND p_state_taxable = true THEN 'Fed Exempt, State Taxable'
            WHEN p_federal_taxable = true AND p_state_taxable = true THEN 'Fully Taxable'
            ELSE 'Tax Treatment TBD'
        END as tax_treatment;
END;
$$ LANGUAGE plpgsql;
```

## Security-Specific Mappings

### Known Securities Account Assignments

#### Money Market Funds
```yaml
FSIXX: # Fidelity Government Income Fund
  default_account: "4020 - Ordinary Dividends"
  tax_treatment: "Fully Taxable"
  description_pattern: "FSIXX - Treasury Fund Dividend"
  
SPAXX: # Fidelity Government Money Market  
  default_account: "4020 - Ordinary Dividends"
  tax_treatment: "Fully Taxable"
  description_pattern: "SPAXX - Money Market Dividend"
```

#### Municipal Bonds by Issuer State
```yaml
georgia_municipals:
  issuers: ["Atlanta GA Airport", "Cobb County GA", "Georgia State"]
  default_account: "4041 - GA Municipal Interest (State Exempt)"
  tax_treatment: "Federal and State Exempt"
  
california_municipals:
  issuers: ["California Municipal", "CA State"]
  default_account: "4042 - Out-of-State Municipal Interest (State Taxable)"
  tax_treatment: "Federal Exempt, State Taxable"
  
other_state_municipals:
  default_account: "4042 - Out-of-State Municipal Interest (State Taxable)"  
  tax_treatment: "Federal Exempt, State Taxable"
  note: "Applies to MI, OH, ME and other non-GA municipal bonds"
```

## QBO Export Configuration

### Standard QBO Account Setup

#### Bank Account Information
```yaml
qbo_bank_account:
  bank_id: "FIDELITY001"  # Routing number equivalent 
  account_id: "Z40394067"  # Fidelity account number
  account_type: "CHECKING"  # Treat as checking account for QBO purposes
  account_name: "Fidelity Brokerage Cash"
```

#### Transaction Memo Formatting
```yaml
memo_templates:
  dividend: "{security_symbol} - Dividend Payment"
  interest: "{security_symbol} - Interest Payment ({tax_status})"
  redemption: "{security_name} - Bond Redemption"
  withdrawal: "Transfer to {destination_account}"
  deposit: "Transfer from {source_account}"
  fee: "{fee_type} - {description}"
```

### Custom Field Mapping (Optional)

#### QuickBooks Custom Fields for Investment Tracking
```yaml
custom_fields:
  security_cusip:
    qb_field: "Custom1"
    purpose: "Link to investment tracking"
    
  tax_treatment:
    qb_field: "Custom2" 
    purpose: "Tax preparation reference"
    
  source_document:
    qb_field: "Custom3"
    purpose: "Audit trail reference"
```

## Validation and Testing

### Account Mapping Validation
```sql
-- Test account mapping function with sample data
SELECT 
    transaction_type,
    federal_taxable,
    state_taxable,
    issuer_state_code,
    get_qb_account_mapping(transaction_type, federal_taxable, state_taxable, issuer_state_code, description) as mapping
FROM transactions 
WHERE transaction_date >= '2024-01-01'
LIMIT 10;
```

### Mapping Coverage Analysis  
```sql
-- Identify unmapped transaction types
SELECT 
    transaction_type,
    federal_taxable,
    state_taxable,
    COUNT(*) as transaction_count
FROM transactions t
WHERE NOT EXISTS (
    SELECT 1 FROM get_qb_account_mapping(
        t.transaction_type, t.federal_taxable, t.state_taxable, t.issuer_state_code, t.description
    ) WHERE qb_account_name NOT LIKE 'UNMAPPED%'
)
GROUP BY transaction_type, federal_taxable, state_taxable;
```

## Maintenance and Updates

### Quarterly Review Process
```markdown
1. **New Transaction Types:** Check for unmapped transaction categories
2. **Account Structure Changes:** Verify QuickBooks chart of accounts alignment  
3. **Tax Rule Updates:** Incorporate any federal/state tax law changes
4. **Security Mappings:** Add new securities as they appear in portfolio
5. **Performance Review:** Analyze QBO import success rates and error patterns
```

### Adding New Mappings
```markdown
When adding new transaction types or securities:
1. Update the mapping function with new conditions
2. Add corresponding QuickBooks account if needed
3. Test mapping with sample transactions
4. Document tax treatment and business rationale
5. Update this configuration document
```

## Related Documentation

- **[QBO Generation Command](/Users/richkernan/Projects/Finances/commands/generate-qbo.md)** - Implementation details
- **[Processing Doctrine](/Users/richkernan/Projects/Finances/config/doctrine.md)** - Core processing decisions
- **[Tax Rules Configuration](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax classification logic
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Source data structure

---

*Account mappings bridge financial data processing with bookkeeping systems. Maintain accuracy and consistency for reliable QuickBooks integration.*