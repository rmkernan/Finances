# Process Document Command Template

**Created:** 09/09/25 5:28PM ET  
**Updated:** 09/09/25 5:40PM ET - Fixed SQL references for actual 3-table schema, added LOCAL db warnings  
**Purpose:** Claude Code command for processing new financial documents

## Command Overview

Use this command template to process new financial documents (PDFs, CSVs) and extract structured data into the database.

## Usage Instructions

```bash
# Copy this template and customize for specific document processing tasks
# Place documents in /documents/inbox/ then run processing
```

## Processing Workflow

### 1. Document Discovery
```bash
# Check for new documents in inbox
ls -la /Users/richkernan/Projects/Finances/documents/inbox/

# Identify document types and prepare processing plan
```

### 2. Document Analysis & Classification

#### For PDF Documents
```markdown
Read the document and determine:
1. Document type (monthly statement, 1099-DIV, 1099-INT, 1099-B, etc.)
2. Account information (account number, holder name, period covered)
3. Data extraction strategy based on document format
4. Expected transaction/tax data structure
```

#### For CSV Documents  
```markdown
Analyze the CSV structure:
1. Column headers and data format
2. Source system (Fidelity export, QuickBooks export, etc.)
3. Data validation requirements
4. Cross-reference needs with other documents
```

### 3. Data Extraction Process

#### ⚠️ CRITICAL: LOCAL DATABASE ONLY
**Use ONLY:** `psql postgresql://postgres:postgres@127.0.0.1:54322/postgres`  
**NEVER use:** Any `mcp__supabase__` commands - they connect to wrong database

#### Transaction Data Extraction
```sql
-- Extract and validate transaction data using LOCAL psql connection
-- Store in actual 3-table schema (accounts, documents, transactions)

INSERT INTO transactions (
    document_id, account_id, transaction_date, settlement_date, 
    transaction_type, description, amount, 
    security_info,  -- JSONB: {symbol, name, cusip, quantity, price}
    tax_category, federal_taxable, state_taxable,
    tax_details,    -- JSONB: {issuer_state, taxpayer_state, notes}
    source_transaction_id, needs_review, review_notes
) VALUES (...);
```

#### Tax Summary Storage (1099 Forms)
```sql
-- Store 1099 summary data in documents.summary_data JSONB field
UPDATE documents 
SET summary_data = '{
  "form_type": "1099-DIV",
  "tax_year": 2024,
  "ordinary_dividends": 1234.56,
  "qualified_dividends": 1000.00,
  "tax_exempt_interest": 234.56
}'::jsonb
WHERE id = [document_id];
```

### 4. Data Validation & Quality Checks

#### Required Validations
- [ ] All monetary amounts use NUMERIC precision
- [ ] Transaction dates fall within expected ranges  
- [ ] Tax classifications are complete and accurate
- [ ] Cross-source reconciliation identifies discrepancies
- [ ] Municipal bond state codes are properly assigned

#### Quality Flags to Check
```sql
-- Check extraction quality using LOCAL psql connection
SELECT extraction_confidence, extraction_notes, needs_review
FROM documents 
WHERE id = [current_document_id];

-- Check transactions needing review
SELECT * FROM transactions 
WHERE document_id = [current_document_id] 
AND needs_review = true;
```

### 5. File Management

#### After Successful Processing
```bash
# Move processed document to processed folder
mv "/Users/richkernan/Projects/Finances/documents/inbox/[filename]" \
   "/Users/richkernan/Projects/Finances/documents/processed/[filename]"

# Create processing record
```

#### If Processing Fails
```bash
# Keep document in inbox for retry
# Create error log with details
# Flag for manual review if needed
```

## Document-Specific Processing

### Fidelity Monthly Statements

#### Key Data to Extract
- Account holder and account number
- Statement period (start/end dates)
- All transaction details (date, type, amount, security)
- Security holdings and valuations
- Cash flow summaries

#### Tax Classification Logic
```markdown
Apply municipal bond tax rules:
- Georgia bonds: federal_taxable=false, state_taxable=false
- Out-of-state bonds: federal_taxable=false, state_taxable=true
- Money market dividends: both taxable
- Validate against known security master data
```

### Fidelity 1099 Forms

#### Official vs Informational Detection
```markdown
Check for markers:
- "INFORMATIONAL ONLY" text
- "not furnished to IRS" disclaimers
- "exempt recipient for 1099 reporting purposes"

Store both versions separately with is_official flag:
- Official (reported to IRS): typically $0 for corporate exemption
- Informational (actual amounts): shows real dividend/interest income
```

#### Box-by-Box Extraction
```markdown
1099-DIV:
- Box 1a: Ordinary dividends
- Box 1b: Qualified dividends  
- Box 2a: Capital gain distributions
- Box 12: Exempt interest dividends

1099-INT:
- Box 1: Interest income
- Box 8: Tax-exempt interest

1099-B:
- Proceeds from bond redemptions
- Cost basis (if available)
- Realized gains/losses
```

### QuickBooks Export CSV

#### Reconciliation Focus
```markdown
Primary goal: Identify transactions missing from Fidelity sources
- Look for "PPR Interest" payments
- Compare dividend timing and amounts
- Flag discrepancies for investigation
- Sum totals for cross-validation
```

## Error Handling

### Common Processing Errors

#### PDF Reading Issues
```markdown
If Claude cannot read PDF clearly:
1. Check if file is corrupted or password-protected
2. Try alternative extraction methods
3. Flag for manual review with specific error details
4. Do not proceed with partial/uncertain data
```

#### Data Format Issues
```markdown
If extracted data seems inconsistent:
1. Validate against expected patterns from similar documents
2. Cross-check amounts and dates for reasonableness
3. Flag unusual values or formats
4. Prefer conservative extraction over aggressive interpretation
```

#### Tax Classification Uncertainty
```markdown
If tax treatment is unclear:
1. Default to most conservative (taxable) treatment
2. Flag for manual review with specific uncertainty
3. Reference municipal bond issuer state if available
4. Do not guess - accuracy is critical for tax compliance
```

### Manual Review Triggers

#### Automatic Review Required
- Cross-source discrepancies > $10
- Unrecognized transaction types
- Tax-exempt amounts without state classification
- Corporate exemption discrepancies (official vs informational)
- Processing errors or incomplete extractions

## Success Validation

### Processing Complete Checklist
- [ ] Document classified correctly and completely processed
- [ ] All extracted data stored in appropriate database tables
- [ ] Data validation rules passed without critical errors
- [ ] File moved to processed folder with proper timestamp
- [ ] Any data quality flags documented and appropriate
- [ ] Cross-source reconciliation completed if applicable

### Output Summary Template
```markdown
## Processing Summary

**Document:** [filename]
**Type:** [document_type - document_subtype]  
**Period:** [start_date] to [end_date]
**Account:** [account_number - account_name]

### Extracted Data
- **Transactions:** [count] transactions totaling $[amount]
- **Tax Data:** [1099 form summaries if applicable]
- **Securities:** [count] unique securities referenced

### Data Quality
- **Validations:** [passed/failed counts]
- **Warnings:** [list any warnings or manual review items]
- **Cross-Reference:** [reconciliation notes if applicable]

### Next Steps
- [Any follow-up actions needed]
- [Manual review items if flagged]
```

## Related Resources

- **[Processing Rules](/Users/richkernan/Projects/Finances/docs/technical/processing-rules.md)** - Detailed extraction guidelines
- **[Database Schema](/Users/richkernan/Projects/Finances/docs/technical/database-schema.md)** - Table structures and relationships
- **[Tax Rules Config](/Users/richkernan/Projects/Finances/config/tax-rules.md)** - Tax classification logic
- **[Sample Documents](/Users/richkernan/Projects/Finances/docs/archive/context.md)** - Real examples with known patterns

---

*Always prioritize accuracy over speed when processing financial documents. Flag uncertainties for manual review rather than making assumptions.*