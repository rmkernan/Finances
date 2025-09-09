# Document Processing Rules

**Created:** 09/09/25 5:18PM ET  
**Updated:** 09/09/25 5:18PM ET  
**Purpose:** Guidelines for Claude AI processing of financial documents  
**Related:** [Current Requirements](/Users/richkernan/Projects/Finances/docs/requirements/current-requirements.md)

## Processing Philosophy

Claude should extract financial data with **precision and skepticism** - validate everything, flag discrepancies, and maintain complete audit trails. Financial data requires zero-tolerance for errors.

## Document Type Classification

### Auto-Detection Rules

#### Fidelity Monthly Statements
**Identifying Markers:**
- Header contains "Statement Period" with date range
- Account number format "Z##-######" (e.g., "Z40-394067")  
- Contains "Milton Preschool Inc" or similar account holder name
- Transaction sections with "Date", "Description", "Amount" columns

**Processing Priority:** Extract all transactions, holdings, and cash flows

#### Fidelity 1099 Forms (PDF)
**Identifying Markers:**
- Title contains "Form 1099" with subtype (DIV, INT, B)
- Tax year prominently displayed
- Boxes with specific IRS form numbers (1a, 1b, 2a, etc.)
- "Copy B - For Recipient" or similar designation

**Special Handling:** Look for "INFORMATIONAL ONLY" or "not furnished to IRS" text

#### Fidelity 1099 CSV Files
**Identifying Markers:**
- Headers include fields like "Form Type", "Box 1a", "Box 2a"
- Account number in standard Fidelity format
- Numeric values in currency format ($#,###.##)
- May show $0.00 for all income fields (corporate exemption)

#### QuickBooks Export CSV
**Identifying Markers:**
- Headers include "Date", "Account", "Type", "Amount"
- Contains account names like "Investment Income" or specific fund names
- Date format MM/DD/YYYY
- Transaction descriptions containing "PPR Interest" or similar

## Extraction Rules by Document Type

### Monthly Statement Processing

#### Transaction Extraction
```
For each transaction row:
1. Extract transaction_date (format validation required)
2. Extract description (full text, include security symbols)
3. Extract amount (convert to NUMERIC, preserve sign)
4. Classify transaction_type based on description keywords:
   - "DIVIDEND" → "dividend"
   - "INTEREST" → "interest" 
   - "REDEMPTION" → "redemption"
   - "WITHDRAWAL" → "withdrawal"
   - "DEPOSIT" → "deposit"
```

#### Security Identification
```
For dividend/interest transactions:
1. Extract security symbol from description (FSIXX, SPAXX, etc.)
2. Look for CUSIP if available (format: #########)
3. Extract security name (may be abbreviated)
4. Note: Full security details may require separate securities master data
```

#### Tax Classification Logic
```sql
-- Money Market Funds (FSIXX, SPAXX)
federal_taxable = true, state_taxable = true, tax_category = 'ordinary_dividend'

-- Municipal Bond Interest (look for state indicators)
IF description contains "GA", "Georgia" → 
   federal_taxable = false, state_taxable = false, issuer_state_code = 'GA'
IF description contains "CA", "California" → 
   federal_taxable = false, state_taxable = true, issuer_state_code = 'CA'
```

### 1099 Form Processing

#### 1099-DIV Extraction
```
Required Fields:
- Box 1a: Ordinary dividends → ordinary_dividends
- Box 1b: Qualified dividends → qualified_dividends  
- Box 2a: Capital gain distributions → capital_gain_distributions
- Box 12: Exempt interest dividends → exempt_interest_dividends

Validation Rules:
- Box 1b (qualified) should be <= Box 1a (ordinary)
- Exempt interest (Box 12) should have federal_taxable = false
- Flag if all boxes = $0.00 (potential corporate exemption)
```

#### 1099-INT Extraction
```
Required Fields:
- Box 1: Interest income → interest_income
- Box 8: Tax-exempt interest → tax_exempt_interest

Tax Treatment:
- Box 1 → federal_taxable = true, state_taxable = true
- Box 8 → federal_taxable = false, state_taxable = [depends on issuer state]
```

#### 1099-B Extraction
```
Required Fields:
- Proceeds (total sales proceeds) → proceeds
- Cost basis (if reported) → cost_basis
- Gain/loss calculations → realized_gain_loss

Special Handling:
- Municipal bond redemptions at par = no gain/loss
- Look for "REDEMPTION" vs "SALE" in descriptions
```

#### Official vs Informational Detection
```
Informational 1099 Markers:
- "INFORMATIONAL ONLY" text anywhere on form
- "not furnished to the IRS" disclaimer
- "exempt recipient for 1099 reporting purposes"

Database Storage:
- Official forms: is_official = true
- Informational forms: is_official = false
- BOTH may exist for same account/year - store separately
```

### CSV Processing Rules

#### Fidelity CSV Format
```
Expected Headers: Form Type, Account Number, Box 1a, Box 1b, Box 2a, etc.
Processing:
1. Validate account number matches expected format
2. Check for all-zero income amounts (corporate exemption indicator)
3. Extract proceeds data for bond redemptions
4. Cross-reference with PDF versions for validation
```

#### QuickBooks Export Format
```
Expected Headers: Date, Type, Account, Amount, Description
Key Processing:
1. Filter to investment-related accounts only
2. Look for "PPR Interest" transactions (often missing from Fidelity)
3. Extract monthly dividend patterns
4. Sum totals for reconciliation with Fidelity sources
```

## Data Validation & Quality Assurance

### Critical Validations

#### Amount Precision
```
- All monetary amounts MUST use NUMERIC types
- Preserve exact cents: $4,329.68 not $4,329.68000001
- Validate sum totals match statement subtotals where available
- Flag any amount that appears to have floating-point corruption
```

#### Date Consistency
```
- Transaction dates must be within statement period
- Settlement dates (if available) typically 1-3 days after transaction
- Tax year must match document year
- Flag any dates that seem inconsistent or impossible
```

#### Cross-Source Reconciliation
```
Monthly Statement vs 1099:
- Dividend totals should match between sources (within rounding)
- Interest payments should aggregate to 1099 tax-exempt interest
- Flag significant discrepancies (>$10 variance)

QuickBooks vs Fidelity:
- Look for transactions present in QB but missing from Fidelity
- Example: "PPR Interest" payments not appearing on monthly statements
- Flag timing differences (same transaction, different dates)
```

### Error Handling & Flagging

#### Document Processing Errors
```
CRITICAL ERRORS (stop processing):
- Cannot identify document type after full analysis
- Corrupted PDF that cannot be read
- CSV format completely unrecognized

WARNING FLAGS (continue with notes):
- Unusual transaction types not in standard categories
- Amounts that don't follow expected patterns
- Missing expected data fields
- Suspicious all-zero amounts in tax forms
```

#### Data Quality Flags
```sql
-- Create flags table for tracking data quality issues
CREATE TABLE data_quality_flags (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    transaction_id UUID REFERENCES transactions(id),
    flag_type TEXT NOT NULL,    -- "discrepancy", "missing_data", "validation_error"
    severity TEXT NOT NULL,     -- "critical", "warning", "info"
    description TEXT NOT NULL,
    flagged_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);
```

## Municipal Bond Tax Intelligence

### State-Specific Rules (Georgia Resident)

#### Georgia Municipal Bonds
```sql
-- Atlanta Airport, Cobb County, etc.
federal_taxable = false
state_taxable = false  
tax_category = 'municipal_interest'
issuer_state_code = 'GA'
```

#### Out-of-State Municipal Bonds
```sql
-- California, Michigan, Ohio, etc.
federal_taxable = false
state_taxable = true   -- Georgia taxes out-of-state municipal interest
tax_category = 'municipal_interest'
issuer_state_code = [actual state code]
```

#### Private Activity Bonds
```sql
-- Special AMT treatment
federal_taxable = false
state_taxable = false (typically)
is_amt_preference = true  -- Important for AMT calculations
tax_category = 'private_activity_bond'
```

### Bond Identification Methods
```
From Security Names:
- "Atlanta GA Airport" → issuer_state_code = 'GA'
- "California Municipal" → issuer_state_code = 'CA'
- "Auburn ME" → issuer_state_code = 'ME'

From CUSIP Lookup:
- First 6 characters identify issuer
- Can cross-reference with municipal bond databases
- May require external CUSIP-to-issuer mapping
```

## Corporate Tax Exemption Handling

### Milton Preschool Inc Specifics

#### Expected Patterns
```
Official 1099 Forms:
- All income boxes = $0.00
- "exempt recipient for 1099 reporting purposes" notation
- Still shows bond redemption proceeds (not income)

Informational 1099 Forms:  
- Shows actual income amounts ($29,515 dividends, $8,900 exempt interest)
- "INFORMATIONAL ONLY - not furnished to IRS" disclaimer
- Same bond redemption proceeds as official form
```

#### Processing Logic
```sql
-- Store both versions separately
INSERT INTO tax_reports (account_id, tax_year, form_type, is_official, ordinary_dividends)
VALUES (account_id, 2024, '1099-DIV', true, 0.00);    -- Official

INSERT INTO tax_reports (account_id, tax_year, form_type, is_official, ordinary_dividends)  
VALUES (account_id, 2024, '1099-DIV', false, 29515.27); -- Informational

-- Flag the discrepancy
INSERT INTO data_quality_flags (document_id, flag_type, severity, description)
VALUES (doc_id, 'corporate_exemption', 'info', 
        'Corporate exemption: Official 1099 shows $0, informational shows $29,515');
```

## QuickBooks Integration Processing

### Transaction Categorization for QBO Export

#### Include in QBO (Cash Flow Events)
```
Transaction Types to Export:
- Dividends → DEPOSIT, Category: "Investment Income - Dividends"
- Interest → DEPOSIT, Category: "Investment Income - Interest"  
- Bond Redemptions → DEPOSIT, Category: "Investment Income - Bond Principal"
- Withdrawals → WITHDRAWAL, Category: "Transfer to Operating"
- Deposits → DEPOSIT, Category: "Transfer from Operating"
- Account Fees → FEE, Category: "Investment Fees"
```

#### Exclude from QBO (Internal Transactions)
```
Do NOT Export:
- Security purchases/sales (only care about cash impact)
- Reinvestment transactions (wash transactions)
- Position rebalancing between funds
- Share quantity changes without cash impact
```

#### QBO Transaction Format
```
OFX Format Requirements:
- Unique transaction ID (prevent duplicates)
- Standard banking transaction types (DEPOSIT, WITHDRAWAL, FEE)
- Clear memo fields with security identification
- Settlement dates (not transaction dates)
```

## Error Recovery & Manual Review

### When to Flag for Manual Review

#### Automatic Review Triggers
```
1. Cross-source discrepancies > $10
2. Unusual transaction types not in predefined categories
3. Tax-exempt amounts without proper state classification
4. Corporate 1099 discrepancies (official vs informational)
5. Processing errors or incomplete extractions
```

#### Manual Review Workflow
```sql
-- Create review queue
CREATE TABLE manual_review_queue (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    priority TEXT NOT NULL,     -- "high", "medium", "low"
    issue_description TEXT NOT NULL,
    assigned_to TEXT,
    status TEXT DEFAULT 'pending', -- "pending", "in_review", "resolved"
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
```

## Performance Considerations

### Processing Speed Targets
- **Single PDF Statement (20 pages):** < 30 seconds
- **1099 Form (2-3 pages):** < 10 seconds  
- **CSV File (any size):** < 5 seconds
- **Cross-validation queries:** < 2 seconds

### Batch Processing Guidelines
```
Recommended Processing Order:
1. Process all monthly statements first (complete transaction data)
2. Process 1099 forms (tax summaries for reconciliation)
3. Process QuickBooks exports (external validation)
4. Run cross-source reconciliation
5. Generate data quality reports
```

## Related Documentation

- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Table structures and relationships
- **[Tax Rules Configuration](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax classification logic
- **[QuickBooks Integration](/Users/richkernan/Projects/Finances/docs/technical/quickbooks-integration.md)** - QBO export specifications
- **[Sample Data Analysis](/Users/richkernan/Projects/Finances/docs/archive/context.md)** - Real-world examples and edge cases

---

*These processing rules are based on analysis of real financial documents with known complexities. Prioritize accuracy and audit trail over processing speed.*