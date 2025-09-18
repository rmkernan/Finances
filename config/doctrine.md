# Processing Doctrine - Claude-Assisted Financial Data Management

**Created:** 09/09/25 5:40PM ET
**Updated:** 09/09/25 8:15PM ET - Updated for Claude-assisted collaborative approach
**Updated:** 09/18/25 11:45AM ET - Clarified extraction (raw data) vs analysis (tax logic) separation
**Purpose:** Guidelines for intelligent Claude-assisted financial document processing
**Status:** Active - Living document for Claude decision-making support

## Core Philosophy: Extract Facts, Don't Interpret

### CRITICAL: Separation of Concerns
- **EXTRACTION PHASE:** Pull raw data exactly as shown in documents - no interpretation
- **DATABASE STORAGE:** Store facts without tax categorization or business logic
- **FRONTEND/REPORTING:** Apply tax rules, categorization, and analysis at display time

## Core Philosophy: Claude as Intelligent Partner

### Collaborative Intelligence Approach
- **Claude as Co-Processor:** This system works WITH Claude, not automatically
- **Intelligent Decision Making:** Claude makes smart choices based on context, not rigid rules
- **Pause When Uncertain:** Always stop and ask user when patterns are unclear
- **Database as Memory:** Store context and patterns for Claude to reference across sessions
- **User-Claude Partnership:** Users and Claude work together to process complex financial documents

### Decision-Making Principles
- **Context Over Automation:** Use database history and patterns to inform intelligent choices
- **Ask Don't Guess:** When duplicate detection or classification is uncertain, engage user
- **Learn and Remember:** Document decisions in database for future Claude instances
- **Quality Over Speed:** Accuracy and user collaboration matter more than processing velocity

### Data Accuracy Standards
- **Precision First:** Use NUMERIC types, never floating-point for currency
- **Audit Trail:** Every data point must trace back to source document
- **Conservative Approach:** Flag uncertainties for user collaboration rather than guess
- **Validate Everything:** Cross-check data between multiple sources with user when discrepancies arise

## Duplicate Detection Guidelines

### Claude's Intelligent Duplicate Detection Process
Claude should check for duplicates using multiple strategies before processing any document:

#### Primary Detection Methods
1. **Exact File Match:** Check `file_hash` in database - if exact match exists, STOP and ask user
2. **Name + Period Match:** Check `file_name` + `statement_period` combination - if similar match, ASK user
3. **Transaction Pattern Match:** Look for identical transaction sets within same time period - if found, PAUSE and verify with user

#### When Claude Suspects Duplicates
**ALWAYS STOP and ask the user:**
- "I found a similar document already processed: [filename] from [date]. Should I:"
- "1. Skip this document (it's a duplicate)"  
- "2. Process anyway (it's different/updated)"
- "3. Let me show you the differences first"

#### Detection Query Pattern for Claude
```sql
-- Check for potential duplicates before processing
SELECT file_name, statement_period, file_hash, processed_date
FROM documents 
WHERE file_name ILIKE '%[similar_name]%' 
   OR file_hash = '[current_hash]'
   OR (statement_period = '[current_period]' AND account_id = '[current_account]');
```

## Amendment Processing Guidelines

### Identifying Amended Documents  
Claude should look for these indicators:
- File names containing "AMENDED", "CORRECTED", "REVISED"
- Version numbers (v2, Rev1, etc.) in filenames
- Later dates on documents covering same period
- Footnotes or headers indicating "This supersedes previous version"

### Amendment Linking Process
When Claude identifies an amendment:
1. **Find Original:** Search database for original document by period/account
2. **Ask User:** "I found this appears to be an amendment of [original_doc]. Should I:"
   - "Link as amendment and mark original as superseded?"  
   - "Process as separate document?"
   - "Replace the original data entirely?"
3. **Document Relationship:** Store link between original and amendment in database
4. **Flag Original:** Mark original as `superseded_by_amendment = true`

### Amendment Database Pattern
```sql
-- Store amendment relationships
UPDATE documents 
SET superseded_by_amendment = true, 
    superseded_by_document_id = [new_amendment_id]
WHERE id = [original_document_id];
```

## Document Processing Patterns

### Security-Specific Processing Rules
Claude should recognize these patterns and apply appropriate classifications:

#### FSIXX (Treasury Fund)
- **Security Type:** Money market / Government fund
- **Tax Treatment:** Fully taxable (federal and state)
- **Income Type:** Ordinary dividends
- **Claude Decision:** Auto-classify as `ordinary_dividend`, `federal_taxable = true`, `state_taxable = true`

#### SPAXX (Money Market)  
- **Security Type:** Money market fund
- **Tax Treatment:** Fully taxable (federal and state)
- **Income Type:** Ordinary dividends
- **Claude Decision:** Auto-classify as `ordinary_dividend`, `federal_taxable = true`, `state_taxable = true`

#### Georgia Municipal Bonds
- **Issuer Pattern:** Names containing "Georgia", "GA", "Atlanta", "Fulton County"
- **Tax Treatment:** Federal exempt, state exempt (for GA residents)
- **Claude Decision:** Set `federal_taxable = false`, `state_taxable = false`, `tax_category = 'municipal_interest'`

#### Non-Georgia Municipal Bonds
- **Issuer Patterns:** "California", "Michigan", "Ohio", etc. municipal bonds
- **Tax Treatment:** Federal exempt, state taxable (for GA residents)  
- **Claude Decision:** Set `federal_taxable = false`, `state_taxable = true`, `tax_category = 'municipal_interest'`

#### Milton Preschool Inc (Corporate Exempt)
- **Pattern:** Corporate entity with tax exemption status
- **Expected:** Official 1099 shows $0, informational shows actual amounts
- **Claude Decision:** Flag as `corporate_exemption = true`, store both official and informational data

## Tax Categorization Decision Rules

### Municipal Bond State Detection
Claude should parse security names intelligently:
```sql
-- Claude's tax classification logic
CASE 
    WHEN security_name ILIKE '%georgia%' OR security_name ILIKE '%GA %' 
         OR security_name ILIKE '%atlanta%' OR security_name ILIKE '%fulton%'
    THEN state_taxable = false  -- GA resident, GA bonds
    
    WHEN security_name ILIKE '%municipal%' OR security_name ILIKE '%muni%'
    THEN state_taxable = true   -- GA resident, non-GA municipal bonds
    
    ELSE state_taxable = true   -- Default for non-municipal securities
END
```

### Federal vs State Taxability Matrix
Claude should reference this decision matrix:

| Security Type | Federal Taxable | State Taxable (GA) | Notes |
|---------------|----------------|-------------------|--------|
| Money Market (FSIXX/SPAXX) | Yes | Yes | Ordinary income |
| GA Municipal Bonds | No | No | Fully exempt for GA residents |
| Non-GA Municipal | No | Yes | Fed exempt, state taxable |
| Corporate Dividends | Yes | Yes | Qualified vs ordinary |
| Treasury Securities | Yes | No | Fed taxable, state exempt |

## Claude Decision Points

### When to Ask for User Clarification
Claude should ALWAYS pause and ask when:
- Duplicate document suspected (any similarity > 70%)
- Security name doesn't clearly indicate issuer state  
- Tax treatment is ambiguous based on security type
- Cross-source data variance > $10
- Amendment relationship is unclear
- New document types not covered in this doctrine

### When to Flag for Review
Claude should create database flags when:
- Processing corporate exemption documents (expected pattern)
- Cross-source reconciliation shows variances
- Security classification required manual override
- New transaction patterns emerge

### When to Proceed with Confidence  
Claude can process automatically when:
- Clear FSIXX/SPAXX money market transactions
- Clearly identifiable GA vs non-GA municipal bonds
- Standard dividend/interest transactions with no duplicates detected
- Document format matches established patterns exactly

## Established Processing Patterns

### 1. Document Classification Hierarchy

#### Fidelity Documents
```markdown
Priority Order for Conflicting Data:
1. **Monthly Statements** - Most detailed, transaction-level data
2. **1099 Informational** - Complete tax picture for exempt entities  
3. **1099 Official** - IRS-reported amounts (may be $0 for corporate exemption)
4. **CSV Exports** - Backup validation, may have different perspectives

Rationale: Monthly statements provide complete transaction detail, while
1099 forms provide tax summaries that may exclude corporate exemption data.
```

#### Cross-Source Reconciliation Rules
```markdown
Expected Discrepancy Patterns:
1. **Corporate Exemption:** Official 1099 = $0, Informational = actual amounts
2. **QuickBooks vs Fidelity:** QB may include "PPR Interest" missing from Fidelity
3. **Timing Differences:** Settlement vs transaction date variations
4. **Rounding:** Minor differences < $1 acceptable, > $10 requires investigation

Flag Pattern: Create data_quality_flags for systematic review rather than
attempting automated resolution of significant discrepancies.
```

### 2. Tax Classification Standards

#### Municipal Bond Classification Matrix

| Bond Issuer State | Taxpayer State | Federal Taxable | State Taxable | Notes |
|------------------|----------------|-----------------|---------------|--------|
| Georgia (GA) | Georgia | false | false | Fully exempt for GA residents |
| California (CA) | Georgia | false | true | Fed exempt, GA state taxable |
| Michigan (MI) | Georgia | false | true | Fed exempt, GA state taxable |
| Ohio (OH) | Georgia | false | true | Fed exempt, GA state taxable |
| Private Activity | Any | false | varies | AMT preference item |

#### Security Type Tax Rules
```sql
-- Money Market Funds (FSIXX, SPAXX)
federal_taxable = true, state_taxable = true, tax_category = 'ordinary_dividend'

-- Municipal Bond Interest  
federal_taxable = false, 
state_taxable = (issuer_state_code != taxpayer_state_code),
tax_category = 'municipal_interest'

-- Corporate Dividends
federal_taxable = true, state_taxable = true, 
tax_category = CASE WHEN qualified THEN 'qualified_dividend' ELSE 'ordinary_dividend' END
```

### 3. Transaction Processing Standards

#### Amount Handling Rules
```markdown
Precision Requirements:
- All monetary amounts: NUMERIC(12,2) - exact decimal arithmetic
- Share quantities: NUMERIC(15,6) - handle fractional shares precisely  
- Percentages/rates: NUMERIC(8,4) - adequate precision for interest rates

Sign Conventions:
- Income (dividends, interest): Positive amounts
- Expenses (fees, withdrawals): Negative amounts
- Transfers: Sign indicates direction (+ = into account, - = out of account)
```

#### Date Handling Standards
```markdown
Date Priority:
1. **Settlement Date** - Use for QuickBooks integration (cash accounting)
2. **Transaction Date** - Use for grouping and reporting
3. **Record Date** - Reference only, not used for calculations

Validation Rules:
- Transaction dates must be within statement period
- Settlement dates typically 1-3 business days after transaction
- Future dates not allowed (flag as data quality issue)
```

### 4. Security Master Data Patterns

#### CUSIP and Symbol Handling
```markdown
Primary Key Strategy:
- Use CUSIP as primary key when available (most reliable)
- Fall back to symbol + name combination for non-CUSIP securities
- Maintain symbol-to-CUSIP mapping for cross-reference

Municipal Bond Issuer Detection:
- Parse security names for state indicators ("Atlanta GA", "California Muni")
- Use CUSIP prefix for systematic issuer identification
- Default to conservative tax treatment when issuer state unclear
```

#### Security Type Classification
```sql
-- Classification Logic
CASE 
    WHEN name ILIKE '%municipal%' OR name ILIKE '%muni%' THEN 'municipal_bond'
    WHEN symbol IN ('FSIXX', 'SPAXX') THEN 'money_market'  
    WHEN name ILIKE '%treasury%' OR name ILIKE '%government%' THEN 'government_fund'
    WHEN maturity_date IS NOT NULL THEN 'bond'
    ELSE 'equity_or_other'
END as security_type
```

## Corporate Tax Exemption Handling

### Milton Preschool Inc Pattern
```markdown
Expected Document Pattern:
1. **Official 1099:** All income boxes = $0.00, notation about exempt recipient
2. **Informational 1099:** Actual income amounts, "not furnished to IRS" disclaimer  
3. **Monthly Statements:** Detailed transactions showing actual dividend/interest activity

Processing Approach:
- Store BOTH official and informational 1099 data (is_official flag)
- Use informational amounts for internal analysis and reconciliation
- Flag the discrepancy as "corporate_exemption" (expected, not error)
- Maintain complete audit trail for tax preparation purposes
```

### Validation Rules for Corporate Exemption
```sql
-- Detect corporate exemption patterns
WITH corp_exemption_check AS (
    SELECT 
        account_id, 
        tax_year,
        SUM(CASE WHEN is_official = true THEN ordinary_dividends ELSE 0 END) as official_total,
        SUM(CASE WHEN is_official = false THEN ordinary_dividends ELSE 0 END) as info_total
    FROM tax_reports 
    WHERE form_type = '1099-DIV'
    GROUP BY account_id, tax_year
)
SELECT * FROM corp_exemption_check
WHERE official_total = 0 AND info_total > 0;  -- Corporate exemption pattern
```

## QuickBooks Integration Standards

### Cash Flow Focus Approach
```markdown
Export Philosophy: Treat brokerage like bank account reconciliation

INCLUDE (Cash Events):
- Dividends and interest received (actual cash in)
- Withdrawals and deposits (cash transfers)
- Bond redemptions (principal repayment)  
- Account fees (cash expenses)

EXCLUDE (Internal Events):  
- Security purchases/sales (position changes, not cash flow)
- Reinvestment transactions (automatic, no net cash change)
- Market value adjustments (unrealized gains/losses)
```

### QBO Transaction Mapping Standards
```markdown
Transaction Type Mapping:
- dividend/interest → DEPOSIT + appropriate income account
- withdrawal → DEBIT + transfer expense account  
- redemption → DEPOSIT + bond principal income account
- fee → FEE + investment expense account

FITID Format Standard:
[AccountNumber]_[YYYYMMDD]_[TransactionType]_[SecuritySymbol]_[SequenceNumber]
Example: Z40394067_20240131_DIV_FSIXX_001
```

## Data Quality Standards

### Validation Rule Hierarchy
```markdown
CRITICAL (Stop Processing):
- Invalid monetary amounts or precision loss
- Missing required fields (account, date, amount)
- Duplicate document import (same file hash)

WARNING (Flag for Review):
- Cross-source variances > $10
- Unusual transaction types or patterns
- Tax classification uncertainties
- Settlement date inconsistencies  

INFO (Log but Continue):
- Minor rounding differences < $1
- Corporate exemption discrepancies (expected)
- Known timing differences between sources
```

### Manual Review Triggers
```sql
-- Automatic flagging conditions
INSERT INTO data_quality_flags (document_id, flag_type, severity, description)
SELECT 
    document_id,
    'variance_investigation',
    'warning',
    'Cross-source variance exceeds $10 threshold'
FROM reconciliation_results
WHERE ABS(variance_amount) > 10;
```

## Processing Workflow Standards

### Document Import Sequence
```markdown
Standard Processing Order:
1. **Monthly Statements First** - Establishes transaction baseline
2. **1099 Forms Second** - Provides tax summary validation
3. **QuickBooks Exports Third** - External validation and gap identification
4. **Cross-Source Reconciliation Fourth** - Identify and flag discrepancies
5. **Generate Reports Fifth** - Summary analysis and QBO exports

Rationale: Monthly statements provide most granular data and should establish
the baseline for comparison with summary sources.
```

### Error Recovery Protocol
```markdown
Processing Failure Response:
1. **Preserve Source Document** - Never delete or modify original files
2. **Log Complete Error Details** - Full context for troubleshooting
3. **Flag for Manual Review** - Human intelligence for edge cases
4. **Partial Processing OK** - Complete what's possible, flag incomplete
5. **Audit Trail Essential** - Document all processing attempts and results
```

## Known Edge Cases & Handling

### 1. PPR Interest Gap
```markdown
Issue: QuickBooks shows ~$23K "PPR Interest" not present in Fidelity statements
Pattern: Appears monthly in QB, absent from monthly statements and 1099s
Handling: Flag as "missing_from_fidelity", include in reconciliation reports
Investigation: May be separate payment stream or different accounting treatment
```

### 2. Bond Redemption Timing
```markdown
Issue: Bond redemptions may appear on different dates in different sources
Pattern: Transaction date vs settlement date differences
Handling: Use settlement date for cash flow, note transaction date for reference
Cross-Reference: Match by CUSIP and amount within 5-day window
```

### 3. Dividend Timing Variations
```markdown
Issue: Monthly statement dates may differ from 1099 annual aggregation
Pattern: End-of-month vs beginning-of-next-month recording
Handling: Aggregate monthly transactions by calendar year for 1099 comparison
Tolerance: Accept minor timing differences within same tax year
```

## Evolution and Maintenance

### Pattern Recognition Process
```markdown
When encountering new patterns:
1. Document the pattern with specific examples
2. Determine if it represents systematic issue or edge case
3. Update processing rules if systematic
4. Add to manual review triggers if edge case
5. Update this doctrine document with decision rationale
```

### Periodic Review Schedule
```markdown
Monthly: Review data quality flags and resolution patterns
Quarterly: Analyze reconciliation variance trends  
Annually: Comprehensive doctrine review and tax rule updates
Ad-hoc: When encountering new document types or transaction patterns
```

## Related Configuration

- **[Tax Rules Configuration](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Detailed tax classification logic
- **[Account Mapping](/Users/richkernan/Projects/Finances/config/accounts-map.md)** - QuickBooks integration mappings
- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Technical implementation details

---

*This doctrine evolves based on real-world processing experience. Update it as new patterns emerge and edge cases are resolved.*