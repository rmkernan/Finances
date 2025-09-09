# Tax Categorization Rules

**Created:** 09/09/25 5:48PM ET  
**Updated:** 09/09/25 5:48PM ET  
**Purpose:** Tax treatment classification logic for financial transactions  
**Taxpayer Context:** Georgia resident, corporate entity (Milton Preschool Inc)

## Tax Classification Framework

### Multi-Layered Tax Treatment
Financial transactions require classification across multiple tax dimensions:
- **Federal Taxable/Exempt Status**
- **State Taxable/Exempt Status** (Georgia-specific)
- **Tax Category** (ordinary income, qualified dividends, municipal interest, etc.)
- **Special Treatments** (AMT preference, Section 199A eligibility)

### Corporate vs Individual Rules
Milton Preschool Inc operates as a corporate entity with special tax exemption status affecting 1099 reporting but not actual tax treatment obligations.

## Municipal Bond Tax Rules

### Core Municipal Bond Taxation Principles

#### Federal Tax Treatment
```markdown
ALL Municipal Bonds: Federal tax exempt (with rare exceptions)
- Municipal bond interest generally exempt from federal income tax
- Original Issue Discount (OID) may have different treatment
- Market discount may create taxable income upon sale
```

#### State Tax Treatment (Georgia Resident)
```markdown
In-State Bonds (Georgia): State tax exempt
- Georgia municipal bonds exempt from Georgia state income tax
- Applies to bonds issued by Georgia state, counties, cities, authorities

Out-of-State Bonds: State taxable  
- Municipal bonds from other states subject to Georgia state income tax
- California, Michigan, Ohio, Maine bonds are state-taxable for Georgia residents
- Must track issuer state for proper classification
```

### Municipal Bond Classification Matrix

| Issuer State | Security Examples | Federal Tax | Georgia State Tax | Tax Category |
|-------------|-------------------|-------------|------------------|-------------|
| Georgia (GA) | Atlanta Airport, Cobb County | Exempt | Exempt | municipal_interest_ga |
| California (CA) | CA State Bonds, CA Municipal | Exempt | **Taxable** | municipal_interest_other |
| Michigan (MI) | MI Municipal | Exempt | **Taxable** | municipal_interest_other |
| Ohio (OH) | OH Municipal | Exempt | **Taxable** | municipal_interest_other |
| Maine (ME) | Auburn ME | Exempt | **Taxable** | municipal_interest_other |

### Implementation Logic
```sql
-- Municipal bond tax classification
UPDATE transactions SET
    federal_taxable = false,
    state_taxable = CASE 
        WHEN issuer_state_code = 'GA' THEN false  -- Georgia bonds exempt for GA residents
        ELSE true  -- Out-of-state bonds taxable for GA residents
    END,
    tax_category = CASE 
        WHEN issuer_state_code = 'GA' THEN 'municipal_interest_ga'
        ELSE 'municipal_interest_other'
    END
WHERE transaction_type = 'interest' 
AND security_type = 'municipal_bond';
```

## Corporate Dividend and Interest Rules

### Money Market Fund Dividends

#### FSIXX (Fidelity Government Income Fund)
```yaml
security_symbol: "FSIXX"
security_type: "government_money_market"
tax_treatment:
  federal_taxable: true
  state_taxable: true  
  tax_category: "ordinary_dividend"
  qualified_dividend_eligible: false  # Money market dividends are ordinary
```

#### SPAXX (Fidelity Government Money Market)
```yaml
security_symbol: "SPAXX"  
security_type: "money_market"
tax_treatment:
  federal_taxable: true
  state_taxable: true
  tax_category: "ordinary_dividend"
  qualified_dividend_eligible: false
```

### Corporate Stock Dividends (Future)
```yaml
corporate_dividends:
  default_treatment:
    federal_taxable: true
    state_taxable: true
    tax_category: "ordinary_dividend"  # Default until qualified determination
  
  qualified_dividend_requirements:
    - Hold period > 60 days during 121-day period around ex-dividend date
    - Dividend from qualifying domestic corporation or qualified foreign corporation
    - Not specifically excluded (REITs, co-ops, etc.)
```

## Corporate Tax Exemption Handling

### Milton Preschool Inc Special Status

#### 1099 Reporting Implications
```markdown
Corporate Exemption Status: "Exempt recipient for 1099 reporting purposes"

Impact on 1099 Forms:
- Official 1099s: Show $0 for all income categories (not reported to IRS)
- Informational 1099s: Show actual income amounts (for corporate records)
- Both forms may exist for same tax year - process and store separately

Tax Obligations: Corporate exemption affects REPORTING, not actual TAX TREATMENT
- Corporation still subject to income tax on taxable income
- Must maintain complete records of actual income for corporate tax return
- Informational 1099s provide complete income picture for tax preparation
```

#### Processing Rules for Corporate Exemption
```sql
-- Store both official and informational 1099 data
INSERT INTO tax_reports (account_id, tax_year, form_type, is_official, ordinary_dividends)
VALUES 
    (account_id, 2024, '1099-DIV', true, 0.00),          -- Official (IRS-reported)
    (account_id, 2024, '1099-DIV', false, 29515.27);     -- Informational (actual)

-- Flag the corporate exemption pattern  
INSERT INTO data_quality_flags (document_id, flag_type, severity, description)
VALUES (doc_id, 'corporate_exemption', 'info', 
        'Corporate exemption: Official=$0, Informational=$29,515');
```

## Special Tax Categories

### Alternative Minimum Tax (AMT) Items

#### Private Activity Bonds
```markdown
Definition: Municipal bonds that benefit private parties rather than general public
Examples: Hospital bonds, housing bonds, industrial development bonds

Tax Treatment:
- Federal income tax exempt for regular tax
- PREFERENCE ITEM for Alternative Minimum Tax (AMT)
- State treatment varies by state and bond type

Identification: 
- Look for "private activity" in bond description
- CUSIP database lookup for definitive classification
- Conservative approach: flag uncertain cases for manual review
```

#### AMT Processing Rules
```sql
-- Private activity bond classification
UPDATE transactions SET
    federal_taxable = false,           -- Exempt for regular tax
    state_taxable = false,            -- Typically exempt (verify by state)
    is_amt_preference = true,         -- AMT preference item
    tax_category = 'private_activity_bond'
WHERE security_type = 'municipal_bond'
AND (security_name ILIKE '%private activity%' 
     OR security_name ILIKE '%hospital%'
     OR security_name ILIKE '%housing%');
```

### Section 199A Qualified Business Income (QBI)

#### REIT Dividends (Future Consideration)
```yaml
reit_dividends:
  tax_treatment:
    federal_taxable: true
    state_taxable: true
    tax_category: "ordinary_dividend"  # Not qualified dividend rates
    section_199a_eligible: true       # May qualify for 20% QBI deduction
  
  identification:
    - Security type = "REIT" 
    - 1099-DIV Box 5 "Section 199A Dividends"
    - Corporate vs individual treatment may differ
```

## Tax Year and Timing Rules

### Income Recognition Timing

#### Settlement Date vs Transaction Date
```markdown
Tax Recognition: Use SETTLEMENT DATE for tax year assignment
- Income taxable when settled/received, not when declared
- Important for December/January transactions crossing tax years
- Monthly statements show transaction dates, but settlement determines tax year

Cross-Year Transactions:
- December transaction, January settlement = next tax year income
- Use settlement_date for tax_year assignment in database
```

#### 1099 Aggregation Rules
```sql
-- Aggregate monthly transactions to match 1099 annual totals
SELECT 
    account_id,
    EXTRACT(year FROM settlement_date) as tax_year,  -- Use settlement date
    SUM(CASE WHEN tax_category = 'ordinary_dividend' THEN amount ELSE 0 END) as ordinary_dividends,
    SUM(CASE WHEN tax_category = 'municipal_interest_ga' OR tax_category = 'municipal_interest_other' 
             THEN amount ELSE 0 END) as tax_exempt_interest
FROM transactions
WHERE transaction_type IN ('dividend', 'interest')
GROUP BY account_id, EXTRACT(year FROM settlement_date);
```

## Validation and Error Checking

### Tax Classification Validation Rules

#### Required Field Validation
```sql
-- Ensure all income transactions have complete tax classification
SELECT transaction_id, transaction_type, amount, 'Missing tax classification' as error
FROM transactions 
WHERE transaction_type IN ('dividend', 'interest', 'sale')
AND amount != 0
AND (federal_taxable IS NULL OR state_taxable IS NULL OR tax_category IS NULL);
```

#### Logical Consistency Checks
```sql
-- Municipal bond consistency check
SELECT transaction_id, 'Municipal bond should be federal exempt' as error
FROM transactions 
WHERE security_type = 'municipal_bond' 
AND transaction_type = 'interest'
AND federal_taxable = true;  -- Should be false for municipal bonds

-- State tax consistency for Georgia resident
SELECT transaction_id, 'Out-of-state municipal should be state taxable' as error  
FROM transactions
WHERE security_type = 'municipal_bond'
AND transaction_type = 'interest' 
AND issuer_state_code != 'GA'
AND state_taxable = false;  -- Should be true for out-of-state bonds
```

### Cross-Source Validation
```markdown
1099 vs Transaction Reconciliation:
- Monthly statement transaction totals should equal 1099 informational amounts
- Significant variances (>$10) require investigation
- Corporate exemption creates expected variance between official/informational 1099s
- Use informational 1099s as baseline for corporate exemption entities
```

## Tax Rule Updates and Maintenance

### Annual Tax Law Review
```markdown
Update Schedule: January after tax law changes
Review Areas:
- Municipal bond tax exemption changes
- AMT exemption amount adjustments  
- Section 199A deduction rule modifications
- State tax law changes affecting municipal bond treatment
```

### New Security Type Handling
```markdown
Process for Unknown Securities:
1. Default to most conservative (fully taxable) treatment
2. Research security type and issuer information
3. Update classification rules based on research
4. Reprocess affected transactions with correct treatment
5. Document new rules in this configuration
```

### Documentation Requirements
```sql
-- Track tax rule changes for audit purposes
CREATE TABLE tax_rule_changes (
    id UUID PRIMARY KEY,
    change_date DATE,
    rule_type TEXT,  -- 'municipal_bond', 'amt_item', 'section_199a', etc.
    old_rule TEXT,
    new_rule TEXT,
    reason TEXT,
    affected_transactions INTEGER
);
```

## Implementation Examples

### Sample Tax Classifications

#### Georgia Municipal Bond Interest
```sql
INSERT INTO transactions (
    transaction_type, security_type, issuer_state_code, amount,
    federal_taxable, state_taxable, tax_category
) VALUES (
    'interest', 'municipal_bond', 'GA', 1500.00,
    false, false, 'municipal_interest_ga'
);
```

#### California Municipal Bond Interest  
```sql
INSERT INTO transactions (
    transaction_type, security_type, issuer_state_code, amount,
    federal_taxable, state_taxable, tax_category
) VALUES (
    'interest', 'municipal_bond', 'CA', 800.00,
    false, true, 'municipal_interest_other'  -- State taxable for GA resident
);
```

#### Money Market Dividend
```sql
INSERT INTO transactions (
    transaction_type, security_symbol, amount,
    federal_taxable, state_taxable, tax_category
) VALUES (
    'dividend', 'FSIXX', 4329.68,
    true, true, 'ordinary_dividend'
);
```

## Related Documentation

- **[Processing Doctrine](/Users/richkernan/Projects/Finances/config/doctrine.md)** - Core processing decisions
- **[Account Mapping](/Users/richkernan/Projects/Finances/config/accounts-map.md)** - QuickBooks integration rules
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Tax field definitions
- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Implementation guidelines

---

*Tax rules reflect Georgia resident status and corporate entity structure. Update annually and validate against current tax law.*