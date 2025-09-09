# Database Schema - Phase 1 Simplified Schema

**Created:** 09/09/25 5:08PM ET  
**Updated:** 09/09/25 5:35PM ET - Simplified to Phase 1: 3 tables for Claude intelligence  
**Purpose:** Database schema optimized for Claude-assisted financial data management  
**Related:** [Full schema archive](/Users/richkernan/Projects/Finances/docs/archive/schema.md)

## Philosophy: Claude's Memory and Context System

This database serves as **Claude's memory and context system** for intelligent financial decision-making. Unlike traditional automated systems, this is designed for **Claude-assisted processing** where:

- **Claude analyzes** documents and makes intelligent extraction decisions
- **Database provides context** for Claude to understand account history and patterns  
- **Flexible JSONB fields** allow Claude to store nuanced observations and structured data
- **Simple schema** reduces cognitive overhead while maintaining audit capability

The goal is to augment Claude's intelligence with persistent memory, not to replace human judgment with rigid automation.

## Phase 1 Schema: 3 Tables Optimized for Claude Intelligence

```sql
-- Simplified Phase 1 Schema: 3 tables optimized for Claude's intelligence

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_number TEXT NOT NULL,
    institution TEXT NOT NULL,
    account_name TEXT,
    account_type TEXT,  -- 'Corporation', 'Individual'
    tax_id TEXT,
    status TEXT DEFAULT 'active',
    notes TEXT,  -- For Claude to record important context
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    
    -- Document identification
    document_type TEXT,  -- 'statement', '1099', 'quickbooks_export'
    document_subtype TEXT,  -- '1099-DIV', 'monthly', etc.
    period_start DATE,
    period_end DATE,
    
    -- File tracking
    file_path TEXT,
    file_hash TEXT,  -- For duplicate detection
    file_name TEXT,  -- Original filename for Claude's reference
    
    -- Amendment handling
    is_amended BOOLEAN DEFAULT FALSE,
    amends_document_id INTEGER REFERENCES documents(id),
    
    -- Processing metadata
    processed_at TIMESTAMP,
    extraction_confidence TEXT,  -- 'high', 'medium', 'needs_review'
    extraction_notes TEXT,  -- Claude's observations
    raw_extraction JSONB,  -- Full extraction for debugging
    
    -- 1099 summary data (when applicable)
    summary_data JSONB,  -- Flexible for various form types
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    account_id INTEGER REFERENCES accounts(id),
    
    -- Core transaction data
    transaction_date DATE,
    settlement_date DATE,
    transaction_type TEXT,
    description TEXT,
    amount NUMERIC(15,2),
    
    -- Security information (stored flexibly)
    security_info JSONB,  -- {cusip, symbol, name, quantity, price}
    
    -- Tax categorization
    tax_category TEXT,
    federal_taxable BOOLEAN,
    state_taxable BOOLEAN,
    tax_details JSONB,  -- Flexible for special cases
    
    -- Tracking
    source_transaction_id TEXT,  -- Original ID from source
    is_duplicate_of INTEGER REFERENCES transactions(id),
    needs_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Key Design Principles

### Claude-Optimized Structure
- **Simple integer PKs** - Easy for Claude to reference and remember
- **JSONB fields** - Allow Claude to store complex, nuanced data flexibly
- **Text notes fields** - Enable Claude to record observations and context
- **Confidence indicators** - Help Claude track extraction quality

### Flexible Data Storage
- **security_info JSONB** - No separate securities table needed in Phase 1
- **tax_details JSONB** - Handle complex tax scenarios without rigid schema
- **summary_data JSONB** - Store 1099 data flexibly without separate table
- **raw_extraction JSONB** - Full extraction data for debugging/reprocessing

## JSONB Field Examples

### security_info JSONB Structure
```json
{
  "cusip": "04780MWW5",
  "symbol": "FSIXX", 
  "name": "Fidelity Government Money Market Fund",
  "quantity": 1234.567,
  "price": 1.0000,
  "security_type": "money_market"
}
```

### tax_details JSONB Structure  
```json
{
  "issuer_state": "GA",
  "taxpayer_state": "GA", 
  "is_amt_preference": false,
  "section_199a_eligible": false,
  "special_notes": "Georgia municipal bond - double exempt"
}
```

### summary_data JSONB (1099-DIV)
```json
{
  "form_type": "1099-DIV",
  "tax_year": 2024,
  "ordinary_dividends": 1234.56,
  "qualified_dividends": 1000.00,
  "capital_gain_distributions": 234.56,
  "exempt_interest_dividends": 0.00
}
```

### raw_extraction JSONB Example
```json
{
  "extraction_method": "claude_pdf_analysis",
  "confidence_score": "high",
  "raw_text_segments": ["Transaction details from page 2..."],
  "claude_observations": "Clear dividend transaction, high confidence in amounts",
  "extraction_timestamp": "2025-09-09T15:30:00Z"
}
```

## Essential Indexes for Performance

```sql
-- Core lookup patterns for Claude
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);
CREATE INDEX idx_transactions_document ON transactions(document_id);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_account ON documents(account_id);

-- JSONB field indexes (PostgreSQL GIN indexes)
CREATE INDEX idx_transactions_security_info ON transactions USING GIN (security_info);
CREATE INDEX idx_documents_summary_data ON documents USING GIN (summary_data);
```

## Duplicate Detection Strategy

### Document-Level Deduplication
- **file_hash** prevents importing same document twice
- Claude can compare file_name patterns for similar documents
- **amends_document_id** links corrected/amended documents

### Transaction-Level Deduplication  
- **source_transaction_id** tracks original transaction IDs from source systems
- **is_duplicate_of** allows marking duplicates while preserving audit trail
- Claude can use **security_info** and amounts to identify potential duplicates

### Amendment Handling
```sql
-- Original document
INSERT INTO documents (id, file_hash, file_name, is_amended) 
VALUES (1, 'abc123', 'statement_jan.pdf', FALSE);

-- Amended document that replaces it
INSERT INTO documents (id, file_hash, file_name, is_amended, amends_document_id)
VALUES (2, 'def456', 'statement_jan_corrected.pdf', TRUE, 1);
```

## Claude Usage Patterns

### Confidence Tracking
```sql
-- High confidence extraction
UPDATE documents SET 
  extraction_confidence = 'high',
  extraction_notes = 'Clear PDF with perfect OCR, all amounts validated'
WHERE id = 123;

-- Needs review
UPDATE documents SET 
  extraction_confidence = 'needs_review',
  extraction_notes = 'Handwritten amounts, OCR uncertain on some figures'
WHERE id = 124;
```

### Complex Tax Scenarios
```sql
-- Georgia municipal bond (state and federal exempt)
INSERT INTO transactions (tax_category, federal_taxable, state_taxable, tax_details)
VALUES ('municipal_interest', FALSE, FALSE, 
  '{"issuer_state": "GA", "taxpayer_state": "GA", "double_exempt": true}');

-- Out-of-state municipal (federal exempt, state taxable)  
INSERT INTO transactions (tax_category, federal_taxable, state_taxable, tax_details)
VALUES ('municipal_interest', FALSE, TRUE,
  '{"issuer_state": "CA", "taxpayer_state": "GA", "double_exempt": false}');
```

## Phase 1 Limitations and Future Expansions

### What's NOT in Phase 1
- **No securities table** - Security data stored in JSONB instead
- **No tax_reports table** - 1099 data stored in documents.summary_data JSONB
- **No QuickBooks integration** - Focus on PDF/statement processing first
- **No complex constraints** - Rely on Claude's intelligence for validation

### Future Phase Considerations
- **Phase 2**: Add securities master table if JSONB becomes insufficient
- **Phase 3**: Add dedicated tax_reports table for complex reconciliation
- **Phase 4**: QuickBooks integration and automated categorization
- **Phase 5**: Multi-entity support and consolidated reporting

## Data Quality Guidelines for Claude

### Critical Validations
- **Always link transactions to documents** - Essential for audit trail
- **Use NUMERIC for all dollar amounts** - Prevents floating-point errors
- **Record extraction confidence** - Helps identify data quality issues
- **Populate review flags** - Mark uncertain extractions for human review

### Claude Decision Points
- **When to mark needs_review**: OCR uncertainty, unusual transactions, missing data
- **When to flag duplicates**: Same amount, date, and security within tolerance
- **Tax categorization**: Use judgment for complex scenarios, document in tax_details
- **Amendment handling**: Link amended documents, mark originals appropriately

## Related Documentation

- **[Full Schema Archive](/Users/richkernan/Projects/Finances/docs/archive/schema.md)** - Complete original schema design
- **[Supabase Setup Guide](../decisions/001-supabase-over-sqlite.md)** - Database deployment

---

*This Phase 1 schema prioritizes Claude's cognitive efficiency while maintaining essential audit capabilities for financial data management.*