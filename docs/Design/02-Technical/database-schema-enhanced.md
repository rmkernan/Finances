# Enhanced Database Schema - Financial Data Management System

**Created:** 09/10/25 10:30AM ET  
**Updated:** 09/11/25 12:58PM ET - Added real_assets and liabilities tables for complete net worth tracking  
**Purpose:** Comprehensive database schema documentation for Claude-assisted financial data management system  
**Related:** [Original Phase 1 Schema](./database-schema.md)

---

## Architectural Overview

This enhanced schema supports a multi-entity financial data management system designed for Claude-assisted processing. The architecture accommodates:

- **Multiple Business Entities:** S-Corps, LLCs, and Individual taxpayers
- **Multi-Institution Support:** Fidelity, banks, credit unions, etc.
- **Document Processing Audit Trail:** Complete tracking of document ingestion and analysis
- **Tax Compliance:** Federal and state tax categorization with inter-entity transfers
- **Asset Management:** Investment performance tracking with strategic notes
- **Quarterly Tax Payments:** Estimated tax payment tracking and reconciliation
- **Net Worth Tracking:** Real assets (properties) and liabilities (mortgages, loans)

The schema maintains Claude-optimized design principles with JSONB flexibility while adding structured relationships for multi-entity complexity.

---

## Core Entity Tables

### Table: entities

**Purpose:** Master table for all business entities and individual taxpayers. Central hub for organizational structure and tax identity management.

| Column (*R = Req)  | Data Type   | Constraints                                                                     | Purpose/Source                                       |
|--------------------|-------------|---------------------------------------------------------------------------------|------------------------------------------------------|
| `id`               | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                                          | Auto-generated unique identifier                    |
| `entity_name` *R   | TEXT        | NOT NULL                                                                        | Legal entity name                                   |
| `entity_type` *R   | TEXT        | NOT NULL CHECK (entity_type IN ('individual', 's_corp', 'llc', 'other'))      | IRS entity classification                           |
| `tax_id` *R        | TEXT        | NOT NULL UNIQUE                                                                | EIN for entities, SSN for individuals               |
|                    |             |                                                                                 | (encrypted/hashed)                                  |
| `tax_id_display`   | TEXT        |                                                                                 | Last 4 digits for display purposes                  |
|                    |             |                                                                                 | (e.g., "***-**-1234")                               |
| `primary_taxpayer` | TEXT        |                                                                                 | Primary responsible party name                      |
| `tax_year_end`     | TEXT        | DEFAULT '12-31'                                                                | Tax year end (MM-DD format, e.g., "12-31", "09-30") |
| `georgia_resident` | BOOLEAN     | DEFAULT TRUE                                                                    | Georgia state tax residency status                  |
| `entity_status`    | TEXT        | DEFAULT 'active' CHECK (entity_status IN ('active', 'inactive', 'dissolved')) | Current operational status                          |
| `formation_date`   | DATE        |                                                                                 | Entity formation/birth date                         |
| `notes`            | TEXT        |                                                                                 | Claude context notes                                 |
| `created_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                                   | Record creation timestamp                           |
| `updated_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                                   | Last modification timestamp                         |

**Indexes:**
```sql
CREATE INDEX idx_entities_type_status ON entities(entity_type, entity_status);
CREATE INDEX idx_entities_tax_id ON entities(tax_id);
```

**Foreign Key References:**
- Referenced by: `institutions.entity_id`, `accounts.entity_id`, `tax_payments.entity_id`

**Example Data:**
```sql
INSERT INTO entities (entity_name, entity_type, tax_id, tax_id_display, primary_taxpayer) VALUES
('Milton Preschool Inc', 's_corp', '58-1234567', '***-**-4567', 'Rich Kernan'),
('Kernan Family Trust', 'trust', '59-7654321', '***-**-4321', 'Rich Kernan'),
('Rich Kernan', 'individual', '123-45-6789', '***-**-6789', 'Rich Kernan');
```

---

### Table: institutions

**Purpose:** Financial institutions that hold accounts for entities. Supports multiple institutions per entity for diversified financial management.

| Column (*R = Req)     | Data Type   | Constraints                                               | Purpose/Source                                                   |
|-----------------------|-------------|-----------------------------------------------------------|------------------------------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                     | Auto-generated unique identifier                                 |
| `entity_id` *R        | UUID (FK)   | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT       | Entity that manages this institution relationship                |
| `institution_name` *R | TEXT        | NOT NULL                                                  | Institution name (e.g., "Fidelity Investments", "SunTrust Bank") |
| `institution_type`    | TEXT        | CHECK (institution_type IN ('brokerage', 'bank',          | Type of financial institution                                    |
|                       |             | 'credit_union', 'insurance', 'retirement_plan', 'other')) |
| `routing_number`      | TEXT        |                                                           | ABA routing number for banks                                     |
| `swift_code`          | TEXT        |                                                           | SWIFT code for international institutions                        |
| `institution_address` | TEXT        |                                                           | Mailing address for tax documents                                |
| `primary_contact`     | JSONB       |                                                           | Contact information: {"name": "advisor name", "phone": "number", |
|                       |             |                                                           | "email": "address"}                                              |
| `login_credentials`   | JSONB       |                                                           | Encrypted login info: {"username": "encrypted", "url":           |
|                       |             |                                                           | "login_url", "notes": "2FA details"}                             |
| `document_delivery`   | JSONB       |                                                           | How tax docs are delivered: {"method": "electronic/mail",        |
|                       |             |                                                           | "email": "address", "special_instructions": ""}                  |
| `status`              | TEXT        | DEFAULT 'active' CHECK (status IN ('active',              | Current relationship status                                      |
|                       |             | 'inactive', 'closed'))                                    |                                                                  |
| `notes`               | TEXT        |                                                           | Claude context notes for institution-specific handling           |
| `created_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Record creation timestamp                                        |
| `updated_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Last modification timestamp                                      |

**Indexes:**
```sql
CREATE INDEX idx_institutions_entity ON institutions(entity_id);
CREATE INDEX idx_institutions_name_status ON institutions(institution_name, status);
```

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT (prevent deletion if accounts exist)

**Example Data:**
```sql
INSERT INTO institutions (entity_id, institution_name, institution_type, primary_contact) VALUES
('[milton-uuid]', 'Fidelity Investments', 'brokerage', '{"name": "John Advisor", "phone": "800-FIDELITY"}'),
('[individual-uuid]', 'SunTrust Bank', 'bank', '{"name": "Personal Banking", "phone": "800-SUNTRUST"}');
```

---

### Table: accounts (Enhanced)

**Purpose:** Individual financial accounts within institutions. Links entities to specific account numbers for transaction tracking and document association.

| Column (*R = Req)        | Data Type   | Constraints                                             | Purpose/Source                                          |
|--------------------------|-------------|---------------------------------------------------------|---------------------------------------------------------|
| `id`                     | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                   | Auto-generated unique identifier                        |
| `entity_id` *R           | UUID (FK)   | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT     | Entity that owns this account                           |
| `institution_id` *R      | UUID (FK)   | NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT | Institution holding this account                        |
| `account_number` *R      | TEXT        | NOT NULL                                                | Account number (encrypted/masked for security)          |
| `account_number_display` | TEXT        |                                                         | Last 4 digits for display (e.g., "****1234")            |
| `account_name`           | TEXT        |                                                         | Account nickname/description                            |
| `account_type` *R        | TEXT        | NOT NULL CHECK (account_type IN ('checking', 'savings', | Account classification                                  |
|                          |             | 'brokerage', 'ira', '401k', 'roth_ira', 'trust',        |                                                         |
|                          |             | 'business', 'money_market', 'cd'))                      |                                                         |
| `account_subtype`        | TEXT        |                                                         | Specific subtype (e.g., "traditional_ira",              |
|                          |             |                                                         | "roth_401k", "taxable_brokerage")                       |
| `tax_reporting_name`     | TEXT        |                                                         | Name as it appears on tax documents (may differ         |
|                          |             |                                                         | from account_name)                                      |
| `custodian_name`         | TEXT        |                                                         | Custodian name for retirement accounts                  |
| `account_opening_date`   | DATE        |                                                         | When account was opened                                 |
| `account_status`         | TEXT        | DEFAULT 'active' CHECK (account_status IN ('active',    | Current account status                                  |
|                          |             | 'inactive', 'closed', 'transferred'))                   |                                                         |
| `is_tax_deferred`        | BOOLEAN     | DEFAULT FALSE                                           | True for IRAs, 401ks, and other tax-deferred accounts   |
| `is_tax_free`            | BOOLEAN     | DEFAULT FALSE                                           | True for Roth accounts and tax-free investments         |
| `requires_rmd`           | BOOLEAN     | DEFAULT FALSE                                           | True if account requires Required Minimum Distributions |
| `beneficiary_info`       | JSONB       |                                                         | Beneficiary information: [{"name": "person",            |
|                          |             |                                                         | "relationship": "spouse", "percentage": 100}]           |
| `notes`                  | TEXT        |                                                         | Claude context notes for account-specific handling      |
| `created_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Record creation timestamp                               |
| `updated_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Last modification timestamp                             |

**Indexes:**
```sql
CREATE INDEX idx_accounts_entity ON accounts(entity_id);
CREATE INDEX idx_accounts_institution ON accounts(institution_id);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_composite ON accounts(entity_id, institution_id, account_status);
CREATE INDEX idx_accounts_tax_attributes ON accounts(is_tax_deferred, is_tax_free, requires_rmd) WHERE account_status = 'active';
```

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `institution_id` → `institutions(id)` ON DELETE RESTRICT

**Example Data:**
```sql
INSERT INTO accounts (entity_id, institution_id, account_number_display, account_name, account_type, is_tax_deferred) VALUES
('[milton-uuid]', '[fidelity-uuid]', '****4567', 'Milton Preschool Investment Account', 'brokerage', FALSE),
('[individual-uuid]', '[fidelity-uuid]', '****8901', 'Rich Kernan Traditional IRA', 'ira', TRUE);
```

---

## Document and Transaction Tables

### Table: documents (Enhanced)

**Purpose:** Stores document metadata and extraction results with enhanced multi-entity support and processing audit trail. Documents are globally unique by file, issued by exactly one institution, and link to one or more accounts via a join table. Each document is associated with a specific tax year.

| Column (*R = Req)          | Data Type   | Constraints                                                     | Purpose/Source                                        |
|----------------------------|-------------|-----------------------------------------------------------------|-------------------------------------------------------|
| `id`                       | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                           | Auto-generated unique identifier                      |
| `institution_id` *R        | UUID (FK)   | NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT         | Institution that issued document                      |
| `tax_year` *R              | INTEGER     | NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2035)          | Tax year the document pertains to                     |
| **Document Details**       |             |                                                                 |                                                       |
| `document_type` *R         | TEXT        | NOT NULL CHECK (document_type IN ('statement', '1099',          | Primary document classification                       |
|                            |             | 'quickbooks_export', 'bank_statement', 'tax_return', 'k1',      |                                                       |
|                            |             | 'receipt', 'invoice', 'other'))                                 |                                                       |
| `period_start`             | DATE        |                                                                 | Reporting period start date                           |
| `period_end`               | DATE        |                                                                 | Reporting period end date                             |
| **File Management**        |             |                                                                 |                                                       |
| `file_path` *R             | TEXT        | NOT NULL                                                        | Full path to stored document file                     |
| `file_name` *R             | TEXT        | NOT NULL                                                        | Original filename for reference                       |
| `file_size`                | INTEGER     |                                                                 | File size in bytes                                    |
| `file_hash` *R             | TEXT        | NOT NULL                                                        | SHA256 hash for duplicate detection (global unique)   |
| `mime_type`                | TEXT        | DEFAULT 'application/pdf'                                       | File MIME type                                        |
| **Amendment Tracking**     |             |                                                                 |                                                       |
| `is_amended`               | BOOLEAN     | DEFAULT FALSE                                                   | True if this document has been amended/corrected      |
| `amends_document_id`       | UUID (FK)   | REFERENCES documents(id) ON DELETE SET NULL                     | Original document this amends                         |
| `version_number`           | INTEGER     | DEFAULT 1                                                       | Version number for amended documents                  |
| **Processing Metadata**    |             |                                                                 |                                                       |
| `processed_at`             | TIMESTAMPTZ |                                                                 | When document processing completed                    |
| `processed_by`             | TEXT        | DEFAULT 'claude'                                                | Processing agent identifier                           |
| `extraction_method`        | TEXT        | DEFAULT 'claude_ai' CHECK (extraction_method IN ('claude_ai',   | How data was extracted                                |
|                            |             | 'ocr', 'manual', 'api_import'))                                 |                                                       |
| `extraction_confidence` *R | TEXT        | NOT NULL DEFAULT 'needs_review' CHECK (extraction_confidence IN | Claude's confidence in extraction accuracy            |
|                            |             | ('high', 'medium', 'low', 'needs_review', 'failed'))            |                                                       |
| `extraction_notes`         | TEXT        |                                                                 | Claude's observations and decision rationale          |
| `needs_human_review`       | BOOLEAN     | DEFAULT FALSE                                                   | Flag for human review required                        |
| `human_reviewed_at`        | TIMESTAMPTZ |                                                                 | When human review was completed                       |
| **Extraction Data**        |             |                                                                 |                                                       |
| `raw_extraction`           | JSONB       |                                                                 | Complete unprocessed extraction data                  |
| `structured_data`          | JSONB       |                                                                 | Parsed and validated structured data                  |
| `summary_data`             | JSONB       |                                                                 | High-level summary (1099 totals, statement summaries) |
| **Audit Trail**            |             |                                                                 |                                                       |
| `created_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Record creation timestamp                             |
| `updated_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Last modification timestamp                           |
| `imported_at`              | TIMESTAMPTZ | DEFAULT NOW()                                                   | When document was first imported                      |

**Indexes:**
```sql
-- Core lookups
CREATE INDEX idx_documents_institution ON documents(institution_id);
CREATE UNIQUE INDEX uq_documents_file_hash ON documents(file_hash);

-- Processing queries
CREATE INDEX idx_documents_processing ON documents(extraction_confidence, needs_human_review);
CREATE INDEX idx_documents_tax_year ON documents(tax_year);
CREATE INDEX idx_documents_type_period ON documents(document_type, period_start, period_end);

-- Amendment tracking
CREATE INDEX idx_documents_amendments ON documents(amends_document_id) WHERE amends_document_id IS NOT NULL;

-- JSONB indexes
CREATE INDEX idx_documents_raw_extraction ON documents USING GIN (raw_extraction);
CREATE INDEX idx_documents_structured_data ON documents USING GIN (structured_data);
CREATE INDEX idx_documents_summary_data ON documents USING GIN (summary_data);
```

**Foreign Key Constraints:**
- `institution_id` → `institutions(id)` ON DELETE RESTRICT
- `amends_document_id` → `documents(id)` ON DELETE SET NULL

---

### Table: document_accounts

**Purpose:** Many-to-many association between documents and accounts. Supports consolidated statements/1099s that list multiple accounts (and thus, multiple entities via accounts).

| Column (*R = Req)   | Data Type   | Constraints                                                     | Purpose/Source                                 |
|---------------------|-------------|-----------------------------------------------------------------|------------------------------------------------|
| `document_id` *R    | UUID (FK)   | NOT NULL REFERENCES documents(id) ON DELETE CASCADE            | Linked document                                |
| `account_id` *R     | UUID (FK)   | NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT            | Linked account                                 |
| `created_at`        | TIMESTAMPTZ | DEFAULT NOW()                                                   | Link creation timestamp                        |

**Constraints:**
```sql
ALTER TABLE document_accounts
  ADD CONSTRAINT uq_document_accounts UNIQUE (document_id, account_id);
```

**Indexes:**
```sql
CREATE INDEX idx_document_accounts_doc ON document_accounts(document_id);
CREATE INDEX idx_document_accounts_acct ON document_accounts(account_id);
```

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT

**Example JSONB Structures:**

**raw_extraction:**
```json
{
  "extraction_method": "claude_pdf_analysis",
  "confidence_score": "high",
  "raw_text_segments": ["Transaction details from page 2...", "Tax summary from page 5..."],
  "claude_observations": "Clear dividend transaction, high confidence in amounts",
  "extraction_timestamp": "2025-09-10T10:30:00Z",
  "processing_time_ms": 2340,
  "pages_processed": 8
}
```

**structured_data (1099-DIV):**
```json
{
  "form_type": "1099-DIV",
  "tax_year": 2024,
  "payer": {
    "name": "Fidelity Investments",
    "tin": "04-6123456",
    "address": "245 Summer St, Boston MA 02210"
  },
  "recipient": {
    "name": "Milton Preschool Inc",
    "tin": "58-1234567",
    "address": "123 Main St, Atlanta GA 30309"
  },
  "amounts": {
    "ordinary_dividends": 1234.56,
    "qualified_dividends": 1000.00,
    "capital_gain_distributions": 234.56,
    "exempt_interest_dividends": 0.00,
    "foreign_tax_paid": 0.00
  },
  "fatca_filing_required": false
}
```

**summary_data (Monthly Statement):**
```json
{
  "statement_period": "2024-01",
  "account_summary": {
    "beginning_balance": 125000.00,
    "ending_balance": 127500.00,
    "net_change": 2500.00
  },
  "transaction_counts": {
    "total_transactions": 15,
    "dividends": 8,
    "buy_transactions": 2,
    "sell_transactions": 1,
    "fees": 4
  },
  "tax_relevant_totals": {
    "ordinary_dividends": 1234.56,
    "qualified_dividends": 890.12,
    "capital_gains": 345.67
  }
}
```

---

### Table: transactions (Enhanced)

**Purpose:** Individual financial transactions extracted from documents, with enhanced multi-entity support and comprehensive tax categorization.

| Column (*R = Req)         | Data Type     | Constraints                                                       | Purpose/Source                                            |
|---------------------------|---------------|-------------------------------------------------------------------|-----------------------------------------------------------|
| `id`                      | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                             | Auto-generated unique identifier                          |
| `entity_id` *R            | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT               | Entity this transaction belongs to                        |
| `document_id` *R          | UUID (FK)     | NOT NULL REFERENCES documents(id) ON DELETE CASCADE               | Source document for audit trail                           |
| `account_id` *R           | UUID (FK)     | NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT               | Account where transaction occurred                        |
| **Transaction Core Data** |               |                                                                   |                                                           |
| `transaction_date` *R     | DATE          | NOT NULL                                                          | Date transaction occurred                                 |
| `settlement_date`         | DATE          |                                                                   | Settlement/clearing date                                  |
| `transaction_type` *R     | TEXT          | NOT NULL CHECK (transaction_type IN ('dividend', 'interest',      | Transaction classification                                |
|                           |               | 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee',              |                                                           |
|                           |               | 'return_of_capital', 'assignment',other'))                        |                                                           |
| `transaction_subtype`     | TEXT          |                                                                   | Detailed subtype (e.g., 'qualified_dividend',             |
|                           |               |                                                                   | 'municipal_interest', 'management_fee')                   |
| `description` *R          | TEXT          | NOT NULL                                                          | Transaction description from source document              |
| `amount` *R               | NUMERIC(15,2) | NOT NULL CHECK (amount != 0)                                      | Transaction amount                                        |
| `source` *R               | TEXT          | NOT NULL CHECK (source IN ('statement','qb_export','ledger'))     | Origin of the transaction data                            |
| **Security Information**  |               |                                                                   |                                                           |
| `security_info`           | JSONB         |                                                                   | Security details: {"cusip": "string", "symbol": "string", |
|                           |               |                                                                   | "name": "string", "quantity": number, "price": number}    |
| `security_type`           | TEXT          | CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf',   | Type of security involved                                 |
|                           |               | 'money_market', 'cd', 'option', 'other'))                         |                                                           |
| **Tax Categorization**    |               |                                                                   |                                                           |
| `tax_category` *R         | TEXT          | NOT NULL CHECK (tax_category IN ('ordinary_dividend',             | Primary tax treatment                                     |
|                           |               | 'qualified_dividend', 'municipal_interest', 'corporate_interest', |                                                           |
|                           |               | 'capital_gain_short', 'capital_gain_long', 'return_of_capital',   |                                                           |
|                           |               | 'tax_exempt', 'fee_expense', 'other'))                            |                                                           |
| `federal_taxable` *R      | BOOLEAN       | NOT NULL                                                          | True if taxable for federal purposes                      |
| `state_taxable` *R        | BOOLEAN       | NOT NULL                                                          | True if taxable for state purposes (GA-specific)          |
| `tax_details`             | JSONB         |                                                                   | Additional tax context: {"issuer_state": "GA",            |
|                           |               |                                                                   | "amt_preference": false, "section_199a": true}            |
| **Source Tracking**       |               |                                                                   |                                                           |
| `source_transaction_id`   | TEXT          |                                                                   | Original transaction ID from source system                |
| `source_reference`        | TEXT          |                                                                   | Additional source reference (confirmation number, etc.)   |
| **Duplicate Detection**   |               |                                                                   |                                                           |
| `is_duplicate_of`         | UUID (FK)     | REFERENCES transactions(id) ON DELETE SET NULL                    | References original transaction if this is a duplicate    |
| `duplicate_reason`        | TEXT          |                                                                   | Explanation of why marked as duplicate                    |
| **Quality Control**       |               |                                                                   |                                                           |
| `needs_review`            | BOOLEAN       | DEFAULT FALSE                                                     | Flag for transactions requiring human review              |
| `review_notes`            | TEXT          |                                                                   | Notes from review process                                 |
| `confidence_score`        | DECIMAL(3,2)  | CHECK (confidence_score >= 0 AND confidence_score <= 1)           | Extraction confidence (0.0 to 1.0)                        |
| **Audit Trail**           |               |                                                                   |                                                           |
| `created_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Record creation timestamp                                 |
| `updated_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Last modification timestamp                               |
| `processed_by`            | TEXT          | DEFAULT 'claude'                                                  | Processing agent identifier                               |

**Indexes:**
```sql
-- Core lookups
CREATE INDEX idx_transactions_entity ON transactions(entity_id);
CREATE INDEX idx_transactions_document ON transactions(document_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);

-- Date and amount queries
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_date_entity ON transactions(entity_id, transaction_date);
CREATE INDEX idx_transactions_amount ON transactions(amount) WHERE ABS(amount) > 100; -- Only index significant amounts

-- Tax categorization
CREATE INDEX idx_transactions_tax_category ON transactions(tax_category);
CREATE INDEX idx_transactions_taxable ON transactions(federal_taxable, state_taxable);
CREATE INDEX idx_transactions_tax_federal ON transactions(federal_taxable, transaction_date) WHERE federal_taxable = true;
CREATE INDEX idx_transactions_tax_state ON transactions(state_taxable, transaction_date) WHERE state_taxable = true;

-- Security analysis
CREATE INDEX idx_transactions_security_type ON transactions(security_type) WHERE security_type IS NOT NULL;
CREATE INDEX idx_transactions_security_info ON transactions USING GIN (security_info);

-- Quality control
CREATE INDEX idx_transactions_review ON transactions(needs_review) WHERE needs_review = true;
CREATE INDEX idx_transactions_duplicates ON transactions(is_duplicate_of) WHERE is_duplicate_of IS NOT NULL;

-- Source tracking
CREATE INDEX idx_transactions_source ON transactions(source_transaction_id) WHERE source_transaction_id IS NOT NULL;

-- JSONB indexes
CREATE INDEX idx_transactions_tax_details ON transactions USING GIN (tax_details);
```

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT
- `is_duplicate_of` → `transactions(id)` ON DELETE SET NULL

**Example Security Info JSONB:**
```json
{
  "cusip": "04780MWW5",
  "symbol": "FSIXX",
  "name": "Fidelity Government Money Market Fund",
  "quantity": 1234.567,
  "price": 1.0000,
  "security_type": "money_market",
  "exchange": "N/A"
}
```

**Example Tax Details JSONB:**
```json
{
  "issuer_state": "GA",
  "taxpayer_state": "GA",
  "is_amt_preference": false,
  "section_199a_eligible": false,
  "special_notes": "Georgia municipal bond - double exempt",
  "tax_equivalent_yield": 4.2,
  "withholding_rate": 0.0
}
```

---

## Tax and Transfer Management Tables

### Table: tax_payments

**Purpose:** Tracks quarterly estimated tax payments and annual tax liabilities for each entity. Essential for cash flow management and tax compliance.

| Column (*R = Req)         | Data Type     | Constraints                                                 | Purpose/Source                                  |
|---------------------------|---------------|-------------------------------------------------------------|-------------------------------------------------|
| `id`                      | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                       | Auto-generated unique identifier                |
| `entity_id` *R            | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT         | Entity making the tax payment                   |
| `account_id`              | UUID (FK)     | REFERENCES accounts(id) ON DELETE RESTRICT                  | Account used for payment (if tracked)           |
| **Payment Details**       |               |                                                             |                                                 |
| `tax_year` *R             | INTEGER       | NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2030)      | Tax year payment applies to                     |
| `payment_type` *R         | TEXT          | NOT NULL CHECK (payment_type IN ('est_q1', 'est_q2',        | Type of tax payment                             |
|                           |               | 'estimated_q3', 'estimated_q4', 'extension', 'balance_due', |                                                 |
|                           |               | 'amended_return', 'penalty', 'interest'))                   |                                                 |
| `tax_authority` *R        | TEXT          | NOT NULL CHECK (tax_authority IN ('federal', 'georgia',     | Which government entity                         |
|                           |               | 'other_state'))                                             |                                                 |
| `payment_date` *R         | DATE          | NOT NULL                                                    | Date payment was made                           |
| `due_date`                | DATE          |                                                             | Original due date for payment                   |
| `amount` *R               | NUMERIC(15,2) | NOT NULL CHECK (amount > 0)                                 | Payment amount                                  |
| **Calculation Details**   |               |                                                             |                                                 |
| `calculation_basis`       | JSONB         |                                                             | Calculation details: {"prior_year_tax": amount, |
|                           |               |                                                             | "current_year_estimate": amount, "method":      |
|                           |               |                                                             | "prior_year_safe_harbor"}                       |
| `estimated_income`        | NUMERIC(15,2) |                                                             | Estimated income for the year                   |
| `estimated_tax_liability` | NUMERIC(15,2) |                                                             | Estimated total tax liability                   |
| **Status and Review**     |               |                                                             |                                                 |
| `notes`                   | TEXT          |                                                             | Additional context and notes                    |
| **Audit Trail**           |               |                                                             |                                                 |
| `created_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                               | Record creation timestamp                       |
| `updated_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                               | Last modification timestamp                     |

**Indexes:**
```sql
CREATE INDEX idx_tax_payments_entity ON tax_payments(entity_id);
CREATE INDEX idx_tax_payments_year ON tax_payments(tax_year);
CREATE INDEX idx_tax_payments_type ON tax_payments(payment_type);
CREATE INDEX idx_tax_payments_authority ON tax_payments(tax_authority);
CREATE INDEX idx_tax_payments_date ON tax_payments(payment_date);
CREATE INDEX idx_tax_payments_due_date ON tax_payments(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tax_payments_entity_year ON tax_payments(entity_id, tax_year, payment_type);
CREATE INDEX idx_tax_payments_calculation_basis ON tax_payments USING GIN (calculation_basis);
```

**Example Calculation Basis JSONB:**
```json
{
  "method": "prior_year_safe_harbor",
  "prior_year_tax": 15000.00,
  "safe_harbor_percentage": 100,
  "quarterly_amount": 3750.00,
  "current_year_estimate": 18000.00,
  "income_sources": [
    {"type": "s_corp_distribution", "amount": 60000},
    {"type": "investment_income", "amount": 8000}
  ]
}
```

---

### Table: transfers

**Purpose:** Tracks money movements between entities and accounts. Critical for inter-entity loan tracking and tax compliance.

| Column (*R = Req)           | Data Type     | Constraints                                                   | Purpose/Source                   |
|-----------------------------|---------------|---------------------------------------------------------------|----------------------------------|
| `id`                        | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                         | Auto-generated unique identifier |
| **Source Information**      |               |                                                               |                                  |
| `source_entity_id` *R       | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT           | Entity sending money             |
| `source_account_id`         | UUID (FK)     | REFERENCES accounts(id) ON DELETE RESTRICT                    | Source account (if tracked)      |
| **Destination Information** |               |                                                               |                                  |
| `destination_entity_id` *R  | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT           | Entity receiving money           |
| `destination_account_id`    | UUID (FK)     | REFERENCES accounts(id) ON DELETE RESTRICT                    | Destination account (if tracked) |
| **Transfer Details**        |               |                                                               |                                  |
| `transfer_date` *R          | DATE          | NOT NULL                                                      | Date transfer occurred           |
| `amount` *R                 | NUMERIC(15,2) | NOT NULL CHECK (amount > 0)                                   | Transfer amount                  |
| `transfer_type` *R          | TEXT          | NOT NULL CHECK (transfer_type IN ('loan', 'distribution',     | Nature of the transfer           |
|                             |               | 'capital_contribution', 'reimbursement', 'gift', 'repayment', |                                  |
|                             |               | 'other'))                                                     |                                  |
| `purpose` *R                | TEXT          | NOT NULL                                                      | Business purpose description     |
| **Status and Review**       |               |                                                               |                                  |
| `notes`                     | TEXT          |                                                               | Additional context and details   |
| **Audit Trail**             |               |                                                               |                                  |
| `created_at`                | TIMESTAMPTZ   | DEFAULT NOW()                                                 | Record creation timestamp        |
| `updated_at`                | TIMESTAMPTZ   | DEFAULT NOW()                                                 | Last modification timestamp      |

**Indexes:**
```sql
CREATE INDEX idx_transfers_source_entity ON transfers(source_entity_id);
CREATE INDEX idx_transfers_dest_entity ON transfers(destination_entity_id);
CREATE INDEX idx_transfers_date ON transfers(transfer_date);
CREATE INDEX idx_transfers_type ON transfers(transfer_type);
CREATE INDEX idx_transfers_loans ON transfers(is_loan) WHERE is_loan = true;
CREATE INDEX idx_transfers_outstanding ON transfers(outstanding_balance) WHERE outstanding_balance > 0;
CREATE INDEX idx_transfers_entities ON transfers(source_entity_id, destination_entity_id, transfer_date);
CREATE INDEX idx_transfers_repayment_schedule ON transfers USING GIN (repayment_schedule);
CREATE INDEX idx_transfers_related ON transfers USING GIN (related_transactions);
```

**Foreign Key Constraints:**
- `source_entity_id` → `entities(id)` ON DELETE RESTRICT
- `destination_entity_id` → `entities(id)` ON DELETE RESTRICT
- `source_account_id` → `accounts(id)` ON DELETE RESTRICT
- `destination_account_id` → `accounts(id)` ON DELETE RESTRICT
- CHECK CONSTRAINT: `source_entity_id != destination_entity_id` (prevent self-transfers)

**Example Repayment Schedule JSONB:**
```json
{
  "frequency": "monthly",
  "payment_amount": 500.00,
  "start_date": "2024-01-01",
  "payment_day": 1,
  "auto_payment": true,
  "remaining_payments": 18,
  "next_payment_date": "2024-11-01"
}
```

---

## Asset Management Tables

### Table: asset_notes

**Purpose:** Investment strategy notes and price targets for securities. Supports investment decision-making and performance tracking.

| Column (*R = Req)            | Data Type     | Constraints                                                | Purpose/Source                                         |
|------------------------------|---------------|------------------------------------------------------------|--------------------------------------------------------|
| `id`                         | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                      | Auto-generated unique identifier                       |
| `entity_id` *R               | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT        | Entity that owns the investment                        |
| `account_id`                 | UUID (FK)     | REFERENCES accounts(id) ON DELETE RESTRICT                 | Specific account holding the security                  |
| **Security Identification**  |               |                                                            |                                                        |
| `symbol` *R                  | TEXT          | NOT NULL                                                   | Security symbol (e.g., "AAPL", "VTSAX")                |
| `cusip`                      | TEXT          |                                                            | CUSIP identifier                                       |
| `security_name`              | TEXT          |                                                            | Full security name                                     |
| `security_type`              | TEXT          | CHECK (security_type IN ('stock', 'etf', 'mutual_fund',    | Type of security                                       |
|                              |               | 'bond','option', 'other'))                                 |                                                        |
| **Price Targets and Limits** |               |                                                            |                                                        |
| `buy_below`                  | NUMERIC(12,4) | CHECK (buy_below > 0)                                      | Purchase price target/limit                            |
| `sell_above`                 | NUMERIC(12,4) | CHECK (sell_above > 0)                                     | Sale price target                                      |
| `stop_loss`                  | NUMERIC(12,4) | CHECK (stop_loss > 0)                                      | Stop loss price                                        |
| `current_price`              | NUMERIC(12,4) | CHECK (current_price > 0)                                  | Last known price                                       |
| `price_updated_at`           | TIMESTAMPTZ   |                                                            | When price was last updated                            |
| **Performance Tracking**     |               |                                                            |                                                        |
| `cost_basis`                 | NUMERIC(15,2) |                                                            | Total cost basis of position                           |
| `current_shares`             | NUMERIC(15,6) | CHECK (current_shares >= 0)                                | Current number of shares held                          |
| `unrealized_gain_loss`       | NUMERIC(15,2) |                                                            | Current unrealized gain/loss                           |
| `last_transaction_date`      | DATE          |                                                            | Date of last buy/sell transaction                      |
| **Alerts and Monitoring**    |               |                                                            |                                                        |
| `alert_enabled`              | BOOLEAN       | DEFAULT FALSE                                              | True if price alerts are active                        |
| `alert_conditions`           | JSONB         |                                                            | Alert conditions: {"price_above": X, "price_below": Y} |
| `dividend_yield`             | NUMERIC(5,4)  | CHECK (dividend_yield >= 0)                                | Current dividend yield                                 |
| `next_dividend_date`         | DATE          |                                                            | Expected next dividend payment date                    |
| **Research and Notes**       |               |                                                            |                                                        |
| `research_notes`             | TEXT          |                                                            | Ongoing research and analysis notes                    |
| `review_frequency`           | TEXT          | CHECK (review_frequency IN ('weekly', 'monthly',           | How often to review                                    |
|                              |               | 'quarterly, 'annually))                                    |                                                        |
| `next_review_date`           | DATE          |                                                            | Scheduled next review date                             |
| **Status**                   |               |                                                            |                                                        |
| `status`                     | TEXT          | DEFAULT 'active' CHECK (status IN ('active', 'watch_list', | Current status                                         |
|                              |               | 'sold', 'deprecated'))                                     |                                                        |
| `notes`                      | TEXT          |                                                            | General notes and observations                         |
| **Audit Trail**              |               |                                                            |                                                        |
| `created_at`                 | TIMESTAMPTZ   | DEFAULT NOW()                                              | Record creation timestamp                              |
| `updated_at`                 | TIMESTAMPTZ   | DEFAULT NOW()                                              | Last modification timestamp                            |

**Indexes:**
```sql
CREATE INDEX idx_asset_notes_entity ON asset_notes(entity_id);
CREATE INDEX idx_asset_notes_account ON asset_notes(account_id) WHERE account_id IS NOT NULL;
CREATE INDEX idx_asset_notes_symbol ON asset_notes(symbol);
CREATE INDEX idx_asset_notes_status ON asset_notes(status);
CREATE INDEX idx_asset_notes_review_date ON asset_notes(next_review_date) WHERE next_review_date IS NOT NULL;
CREATE INDEX idx_asset_notes_alerts ON asset_notes(alert_enabled) WHERE alert_enabled = true;
CREATE INDEX idx_asset_notes_alert_conditions ON asset_notes USING GIN (alert_conditions);
CREATE INDEX idx_asset_notes_tags ON asset_notes USING GIN (tags);
```

**Example Alert Conditions JSONB:**
```json
{
  "price_above": 150.00,
  "price_below": 120.00,
  "volume_spike": {
    "enabled": true,
    "threshold_multiplier": 2.0
  },
  "dividend_announcement": true,
  "earnings_date": "2024-02-01"
}
```

**Example Tags JSONB:**
```json
["growth", "large_cap", "tech", "dividend_growth", "core_holding"]
```

---

## Net Worth Tracking Tables

### Table: real_assets

**Purpose:** Track physical properties and other non-financial assets for net worth calculation.

| Column (*R = Req)   | Data Type     | Constraints                                          | Purpose/Source                          |
|---------------------|---------------|------------------------------------------------------|-----------------------------------------|
| `id`                | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                | Auto-generated unique identifier        |
| `entity_id` *R      | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT  | Entity that owns this asset             |
| **Asset Details**   |               |                                                      |                                         |
| `asset_type` *R     | TEXT          | NOT NULL CHECK (asset_type IN ('primary_residence',  | Type of real asset                      |
|                     |               | 'rental_property', 'commercial_property', 'land',    |                                         |
|                     |               | 'vacation_home', 'vehicle', 'other'))                |                                         |
| `description` *R    | TEXT          | NOT NULL                                             | Asset description (e.g., "Address")     |
| `address`           | TEXT          |                                                      | Property address if applicable          |
| `purchase_date`     | DATE          |                                                      | When asset was acquired                 |
| `purchase_price`    | NUMERIC(15,2) |                                                      | Original purchase price                 |
| **Valuation**       |               |                                                      |                                         |
| `current_value` *R  | NUMERIC(15,2) | NOT NULL                                             | Current estimated value                 |
| `valuation_date` *R | DATE          | NOT NULL                                             | Date of current valuation               |
| `valuation_source`  | TEXT          |                                                      | Source of valuation (e.g. "Appraisal")  |
| **Income/Expense**  |               |                                                      |                                         |
| `monthly_income`    | NUMERIC(15,2) |                                                      | Rental income if applicable             |
| `monthly_expense`   | NUMERIC(15,2) |                                                      | Maintenance, HOA, insurance, taxes      |
| **Status**          |               |                                                      |                                         |
| `status`            | TEXT          | DEFAULT 'active' CHECK (status IN ('active',         |                                         |
|                     |               | 'pending_sale', | Current status                     |                                         |
|                     |               | 'sold', 'transferred'))                              |                                         |
| `notes`             | TEXT          |                                                      | Additional notes                        |
| **Audit Trail**     |               |                                                      |                                         |
| `created_at`        | TIMESTAMPTZ   | DEFAULT NOW()                                        | Record creation timestamp               |
| `updated_at`        | TIMESTAMPTZ   | DEFAULT NOW()                                        | Last modification timestamp             |

**Indexes:**
```sql
CREATE INDEX idx_real_assets_entity ON real_assets(entity_id);
CREATE INDEX idx_real_assets_type ON real_assets(asset_type);
CREATE INDEX idx_real_assets_status ON real_assets(status);
```

---

### Table: liabilities

**Purpose:** Track mortgages and long-term loans for net worth calculation. NOT for credit cards or inter-entity loans.

| Column (*R = Req)     | Data Type     | Constraints                                              | Purpose/Source                        |
|-----------------------|---------------|----------------------------------------------------------|---------------------------------------|
| `id`                  | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                    | Auto-generated unique identifier      |
| `entity_id` *R        | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT      | Entity responsible for this liability |
| `real_asset_id`       | UUID (FK)     | REFERENCES real_assets(id) ON DELETE SET NULL            | Linked asset (for mortgages)          |
| **Liability Details** |               |                                                          |                                       |
| `liability_type` *R   | TEXT          | NOT NULL CHECK (liability_type IN ('mortgage',           | Type of liability                     |
|                       |               | 'home_equity', 'auto_loan', 'business_loan',             |                                       |
|                       |               | 'personal_loan', 'other'))                               |                                       |
| `lender_name` *R      | TEXT          | NOT NULL                                                 | Name of lender/bank                   |
| `account_number`      | TEXT          |                                                          | Loan account number (masked)          |
| **Loan Terms**        |               |                                                          |                                       |
| `original_amount` *R  | NUMERIC(15,2) | NOT NULL                                                 | Original loan amount                  |
| `current_balance` *R  | NUMERIC(15,2) | NOT NULL                                                 | Current outstanding balance           |
| `interest_rate` *R    | NUMERIC(5,3)  | NOT NULL                                                 | Annual interest rate (e.g., 4.25%)    |
| `loan_start_date` *R  | DATE          | NOT NULL                                                 | When loan originated                  |
| `maturity_date`       | DATE          |                                                          | When loan will be paid off            |
| **Payment Info**      |               |                                                          |                                       |
| `monthly_payment` *R  | NUMERIC(15,2) | NOT NULL                                                 | Regular monthly payment amount        |
| `next_payment_date`   | DATE          |                                                          | Next payment due date                 |
| `escrow_amount`       | NUMERIC(15,2) |                                                          | Monthly escrow for taxes/insurance    |
| **Status**            |               |                                                          |                                       |
| `status`              | TEXT          | DEFAULT 'active' CHECK (status IN ('active', 'paid_off', | Current status                        |
|                       |               | 'refinanced', 'transferred'))                            |                                       |
| `notes`               | TEXT          |                                                          | Additional notes                      |
| **Audit Trail**       |               |                                                          |                                       |
| `created_at`          | TIMESTAMPTZ   | DEFAULT NOW()                                            | Record creation timestamp             |
| `updated_at`          | TIMESTAMPTZ   | DEFAULT NOW()                                            | Last modification timestamp           |

**Indexes:**
```sql
CREATE INDEX idx_liabilities_entity ON liabilities(entity_id);
CREATE INDEX idx_liabilities_asset ON liabilities(real_asset_id) WHERE real_asset_id IS NOT NULL;
CREATE INDEX idx_liabilities_type ON liabilities(liability_type);
CREATE INDEX idx_liabilities_status ON liabilities(status);
CREATE INDEX idx_liabilities_maturity ON liabilities(maturity_date) WHERE status = 'active';
```

---

## Database Constraints and Data Integrity

### Table-Level Constraints

**entities table:**
```sql
-- Ensure tax_year_end format
ALTER TABLE entities ADD CONSTRAINT chk_tax_year_end_format 
CHECK (tax_year_end ~ '^\d{2}-\d{2}$');

-- Ensure valid entity types
ALTER TABLE entities ADD CONSTRAINT chk_entity_type_valid 
CHECK (entity_type IN ('individual', 's_corp', 'llc', 'partnership', 'c_corp', 'trust'));
```

**accounts table:**
```sql
-- Prevent conflicting tax attributes
ALTER TABLE accounts ADD CONSTRAINT chk_tax_attributes_exclusive 
CHECK (NOT (is_tax_deferred = true AND is_tax_free = true));

-- Ensure account number security
ALTER TABLE accounts ADD CONSTRAINT chk_account_number_masked 
CHECK (account_number_display ~ '^\*\*\*\*\d{4}$');
```

**documents table:**
```sql
-- Ensure period logic
ALTER TABLE documents ADD CONSTRAINT chk_period_dates 
CHECK (period_start <= period_end);

-- Ensure amendment chain integrity
ALTER TABLE documents ADD CONSTRAINT chk_amendment_not_self 
CHECK (id != amends_document_id);
```

**transactions table:**
```sql
-- Ensure non-zero amounts
ALTER TABLE transactions ADD CONSTRAINT chk_amount_nonzero 
CHECK (amount != 0);

-- Prevent self-referential duplicates
ALTER TABLE transactions ADD CONSTRAINT chk_duplicate_not_self 
CHECK (id != is_duplicate_of);
```

**transfers table:**
```sql
-- Prevent self-transfers
ALTER TABLE transfers ADD CONSTRAINT chk_no_self_transfer 
CHECK (source_entity_id != destination_entity_id);

-- Ensure loan logic
ALTER TABLE transfers ADD CONSTRAINT chk_loan_fields 
CHECK (
    (is_loan = false) OR 
    (is_loan = true AND outstanding_balance IS NOT NULL AND outstanding_balance >= 0)
);
```

### Referential Integrity Rules

**Cascade Rules:**
- `documents.id` → `transactions.document_id` ON DELETE CASCADE (transactions belong to documents)
- All other entity/account references use ON DELETE RESTRICT to prevent data loss

**Data Validation Rules:**
- All monetary amounts use NUMERIC(15,2) for precision
- All timestamps use TIMESTAMPTZ for timezone awareness
- JSONB fields have GIN indexes for efficient querying
- File hashes use SHA256 for reliable duplicate detection

---

## Performance Optimization

### Query Optimization Patterns

**Most Common Queries:**

1. **Entity Portfolio View:**
```sql
-- Optimized with idx_transactions_entity_date
SELECT t.*, a.account_name, d.document_type
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN documents d ON t.document_id = d.id
WHERE t.entity_id = $1 
AND t.transaction_date >= $2
ORDER BY t.transaction_date DESC;
```

2. **Tax Year Summary:**
```sql
-- Optimized with idx_transactions_tax_federal and idx_transactions_tax_state
SELECT 
    tax_category,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM transactions t
JOIN documents d ON t.document_id = d.id
WHERE t.entity_id = $1 
AND d.tax_year = $2
AND t.federal_taxable = true
GROUP BY tax_category
ORDER BY total_amount DESC;
```

3. **Document Processing Queue:**
```sql
-- Optimized with idx_documents_processing
SELECT id, file_name, extraction_confidence, needs_human_review
FROM documents
WHERE extraction_confidence IN ('needs_review', 'failed')
OR needs_human_review = true
ORDER BY imported_at DESC;
```

### Index Strategy

**Composite Indexes for Common Filters:**
```sql
-- Multi-column indexes for frequent query patterns
CREATE INDEX idx_transactions_entity_date_type ON transactions(entity_id, transaction_date, transaction_type);
CREATE INDEX idx_accounts_entity_status_type ON accounts(entity_id, account_status, account_type);
-- Documents no longer carry entity_id; join via document_accounts → accounts for entity scoping
```

**Partial Indexes for Efficiency:**
```sql
-- Index only active/relevant records
CREATE INDEX idx_accounts_active ON accounts(entity_id, account_type) WHERE account_status = 'active';
CREATE INDEX idx_transfers_active_loans ON transfers(source_entity_id, destination_entity_id) WHERE is_loan = true AND status = 'active';
CREATE INDEX idx_asset_notes_monitored ON asset_notes(symbol, entity_id) WHERE status = 'active' AND alert_enabled = true;
```

### Maintenance Considerations

**Regular Maintenance Tasks:**
1. **VACUUM ANALYZE** monthly on high-transaction tables
2. **REINDEX** JSONB GIN indexes quarterly
3. **Update table statistics** after bulk imports
4. **Archive old documents** after 7+ years (configurable)

**Monitoring Queries:**
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Monitor table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::text) DESC;
```

---

## Common Query Examples

### Multi-Entity Financial Summary
```sql
-- Consolidated income summary across all entities
WITH entity_income AS (
    SELECT 
        e.entity_name,
        e.entity_type,
        SUM(CASE WHEN t.federal_taxable THEN t.amount ELSE 0 END) as federal_taxable_income,
        SUM(CASE WHEN t.state_taxable THEN t.amount ELSE 0 END) as state_taxable_income,
        SUM(t.amount) as total_income
    FROM entities e
    JOIN transactions t ON e.id = t.entity_id
    JOIN documents d ON t.document_id = d.id
    WHERE d.tax_year = 2024
    AND t.transaction_type IN ('dividend', 'interest')
    AND t.amount > 0
    GROUP BY e.id, e.entity_name, e.entity_type
)
SELECT * FROM entity_income
ORDER BY federal_taxable_income DESC;
```

### Inter-Entity Transfer Analysis
```sql
-- Analyze loan relationships between entities
SELECT 
    se.entity_name as lender,
    de.entity_name as borrower,
    t.amount,
    t.transfer_date,
    t.outstanding_balance,
    t.interest_rate,
    CASE 
        WHEN t.outstanding_balance > 0 THEN 'Outstanding'
        WHEN t.status = 'paid_off' THEN 'Paid Off'
        ELSE t.status
    END as loan_status
FROM transfers t
JOIN entities se ON t.source_entity_id = se.id
JOIN entities de ON t.destination_entity_id = de.id
WHERE t.is_loan = true
ORDER BY t.transfer_date DESC;
```

### Tax Document Processing Status
```sql
-- Monitor document processing pipeline by entity via account links
WITH doc_links AS (
    SELECT d.id as document_id,
           d.document_type,
           d.tax_year,
           d.extraction_confidence,
           d.needs_human_review,
           d.processed_at,
           a.entity_id
    FROM documents d
    JOIN document_accounts da ON da.document_id = d.id
    JOIN accounts a ON da.account_id = a.id
    WHERE d.tax_year = 2024
)
SELECT 
    e.entity_name,
    dl.document_type,
    COUNT(*) as total_docs,
    COUNT(CASE WHEN dl.extraction_confidence = 'high' THEN 1 END) as high_confidence,
    COUNT(CASE WHEN dl.needs_human_review THEN 1 END) as needs_review,
    COUNT(CASE WHEN dl.processed_at IS NOT NULL THEN 1 END) as processed,
    ROUND(100.0 * COUNT(CASE WHEN dl.extraction_confidence = 'high' THEN 1 END) / COUNT(*), 1) as confidence_pct,
    ROUND(100.0 * COUNT(CASE WHEN dl.processed_at IS NOT NULL THEN 1 END) / COUNT(*), 1) as processed_pct
FROM doc_links dl
JOIN entities e ON dl.entity_id = e.id
GROUP BY e.entity_name, dl.document_type
ORDER BY e.entity_name, dl.document_type;
```

### Investment Performance Dashboard
```sql
-- Asset performance with strategy notes
SELECT 
    e.entity_name,
    an.symbol,
    an.security_name,
    an.current_shares,
    an.cost_basis,
    an.current_price * an.current_shares as current_value,
    an.unrealized_gain_loss,
    CASE 
        WHEN an.cost_basis > 0 THEN 
            ROUND(100.0 * an.unrealized_gain_loss / an.cost_basis, 2)
        ELSE NULL
    END as return_pct,
    an.investment_thesis,
    an.risk_level,
    an.next_review_date
FROM asset_notes an
JOIN entities e ON an.entity_id = e.id
WHERE an.status = 'active'
AND an.current_shares > 0
ORDER BY an.unrealized_gain_loss DESC;
```

---

## Data Migration and Evolution

### Version Control Strategy
- All schema changes tracked in `/supabase/migrations/`
- Each migration includes rollback instructions
- Test migrations on development database first
- Document breaking changes in migration comments

### Complete Table Summary

The schema now includes **10 core tables**:
1. **entities** - Business entities and individuals
2. **institutions** - Financial institutions  
3. **accounts** - Financial accounts
4. **documents** - Source documents with extraction metadata
5. **transactions** - Financial transactions
6. **tax_payments** - Quarterly tax tracking
7. **transfers** - Inter-entity money movements
8. **asset_notes** - Investment strategies
9. **real_assets** - Properties and physical assets
10. **liabilities** - Mortgages and long-term debt

### Expected Evolution Path
1. **Phase 2:** Add QuickBooks integration tables
2. **Phase 3:** Add budget tracking and forecasting
3. **Phase 4:** Add advanced tax optimization features
4. **Phase 5:** Add multi-year trend analysis

This enhanced schema provides a robust foundation for Claude-assisted financial data management with complete net worth tracking while maintaining flexibility for future enhancements.

---

*This enhanced schema documentation provides comprehensive column-level details, relationships, constraints, and optimization strategies for the Financial Data Management System. It serves as both a technical reference and implementation guide for Claude instances working with this database.|
