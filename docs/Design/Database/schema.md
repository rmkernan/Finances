# Enhanced Database Schema - Financial Data Management System

**Created:** 09/10/25 10:30AM ET
**Updated:** 09/11/25 12:58PM ET - Added real_assets and liabilities tables for complete net worth tracking
**Updated:** 09/17/25 3:15PM ET - Added source document mapping columns to transactions table
**Updated:** 09/18/25 1:45PM ET - Added positions and income_summaries tables, enhanced portfolio fields per Fidelity document map
**Updated:** 09/18/25 2:30PM ET - Added Comment column to all tables with practical metadata for PostgreSQL COMMENT ON COLUMN feature
**Updated:** 09/22/25 12:53PM ET - Added data processing workflow, enhanced foreign key documentation, aligned with Fidelity document map
**Updated:** 09/22/25 1:18PM ET - Added beginning_value and ending_value fields to doc_level_data table
**Updated:** 09/22/25 1:25PM ET - Removed redundant income_summaries table, marked Phase 2 tables (not yet implemented)
**Updated:** 09/22/25 3:11PM ET - Added sec_cusip, option fields, activity columns, bond_state, dividend_qualified to transactions table
**Updated:** 09/22/25 5:32PM ET - Made tax fields optional, transaction_date optional, clarified settlement_date vs transaction_date separation
**Updated:** 09/22/25 8:55PM ET - Verified doc_md5_hash column specification in documents table for duplicate prevention
**Updated:** 09/22/25 9:00PM ET - Added UNIQUE constraints, removed restrictive CHECKs, added archival support, improved account types
**Updated:** 09/22/25 9:10PM ET - Clarified two-stage duplicate prevention workflow using MD5 hashes at staging and database insert
**Updated:** 09/22/25 9:15PM ET - Added PostgreSQL COMMENT specifications for all tables and columns
**Updated:** 09/23/25 2:58PM - Added comprehensive design justification for document_accounts table and clarified doc_level_data as transcribed data
**Updated:** 09/23/25 3:52PM - Removed entity_id from institutions table (institutions now shared across entities) and added institution_name to accounts table as derived field
**Updated:** 09/23/25 6:15PM - Added data_mappings table for configuration-driven classification and sec_class column to transactions table for options tracking
**Purpose:** Comprehensive database schema documentation for Claude-assisted financial data management system
**Related:** [Original Phase 1 Schema](./database-schema.md)

---

## Architectural Overview

This enhanced schema supports a multi-entity financial data management system designed for Claude-assisted processing. The architecture accommodates:

- **Multiple Business Entities:** S-Corps, LLCs, and Individual taxpayers
- **Multi-Institution Support:** Fidelity, banks, credit unions, etc.
- **Document Processing Audit Trail:** Complete tracking of document ingestion and analysis
- **Configuration-Driven Classification:** Data mappings for flexible transaction and security categorization
- **Options Tracking:** Advanced support for option contract matching and P&L analysis
- **Tax Compliance:** Federal and state tax categorization with inter-entity transfers
- **Asset Management:** Investment performance tracking with strategic notes
- **Quarterly Tax Payments:** Estimated tax payment tracking and reconciliation
- **Net Worth Tracking:** Real assets (properties) and liabilities (mortgages, loans)

The schema maintains Claude-optimized design principles with JSONB flexibility while adding structured relationships for multi-entity complexity.

---

## Data Processing Workflow

### Document Processing Pipeline

The system follows a standardized workflow for converting financial documents into structured data:

```
1. Document Staging & Duplicate Check
   PDF/Image → /documents/inbox/ → /documents/2staged/
   - Generate MD5 hash using: md5sum filename.pdf
   - Query database for existing doc_md5_hash to detect duplicates
   - If duplicate found: Alert user, skip processing
   - If new: Continue to extraction

2. Data Extraction (Claude-assisted)
   - MD5 hash passed to sub-agents in extraction prompt
   - Institution Guide (e.g., fidelity-document-map.md) → JSON extraction
   - Source Labels → JSON Fields → Database Columns
   - Hash embedded in extraction JSON metadata

3. Data Validation
   - Account number matching to existing accounts
   - Entity association through account ownership
   - Transaction-level duplicate patterns

4. Database Insert with Duplicate Prevention
   - Documents table: Insert with doc_md5_hash (UNIQUE constraint prevents duplicates)
   - Document_accounts: Link to relevant accounts
   - Positions: Point-in-time holdings snapshots
   - Doc_level_data: Aggregated income and gains/losses
   - Transactions: Individual transaction records
   - If insert fails due to hash conflict: Handle as duplicate

5. Post-Processing
   Move to /documents/processed/ with extraction JSON saved
```

### Multi-Institution Support

While currently focused on Fidelity, the schema supports any institution through:
- Institution-specific extraction guides mapping to standard JSON fields
- Common database structure with institution-agnostic columns
- JSONB fields for institution-specific data that doesn't fit standard schema

---

## Core Entity Tables

### Table: entities

**Purpose:** Master table for all business entities and individual taxpayers. Central hub for organizational structure and tax identity management.

| Column (*R = Req)  | Data Type   | Constraints                                                              | Purpose/Source                                      |
|--------------------|-------------|--------------------------------------------------------------------------|-----------------------------------------------------|
| `id`               | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                                    | Auto-generated unique identifier                    |
| `entity_name` *R   | TEXT        | NOT NULL                                                                 | Legal entity name                                   |
| `entity_type` *R   | TEXT        | NOT NULL CHECK (entity_type IN ('individual', 's_corp', 'llc', 'other')) | IRS entity classification                           |
| `tax_id` *R        | TEXT        | NOT NULL UNIQUE                                                          | EIN for entities, SSN for individuals               |
|                    |             |                                                                          | (encrypted/hashed)                                  |
| `tax_id_display`   | TEXT        |                                                                          | Last 4 digits for display purposes                  |
|                    |             |                                                                          | (e.g., "***-**-1234")                               |
| `primary_taxpayer` | TEXT        |                                                                          | Primary responsible party name                      |
| `tax_year_end`     | TEXT        | DEFAULT '12-31'                                                          | Tax year end (MM-DD format, e.g., "12-31", "09-30") |
| `georgia_resident` | BOOLEAN     | DEFAULT TRUE                                                             | Georgia state tax residency status                  |
| `entity_status`    | TEXT        | DEFAULT 'active' CHECK (entity_status IN ('active', 'inactive'))         | Current operational status                          |
| `formation_date`   | DATE        |                                                                          | Entity formation/birth date                         |
| `notes`            | TEXT        |                                                                          | Claude context notes                                |
| `created_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                            | Record creation timestamp                           |
| `updated_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                            | Last modification timestamp                         |
**PostgreSQL Table Comment:**
```sql
COMMENT ON TABLE entities IS 'Master table for business entities and individual taxpayers - central hub for multi-entity financial management';
```

**PostgreSQL Column Comments:**
```sql
COMMENT ON COLUMN entities.id IS 'Auto-generated unique identifier for entity';
COMMENT ON COLUMN entities.entity_name IS 'Legal entity name as registered with IRS/state';
COMMENT ON COLUMN entities.entity_type IS 'IRS classification: individual, s_corp, llc, or other';
COMMENT ON COLUMN entities.tax_id IS 'EIN for entities, SSN for individuals - store encrypted/hashed';
COMMENT ON COLUMN entities.tax_id_display IS 'Last 4 digits only for UI display (e.g. ***-**-1234)';
COMMENT ON COLUMN entities.primary_taxpayer IS 'Primary responsible party or individual name';
COMMENT ON COLUMN entities.tax_year_end IS 'Fiscal year end in MM-DD format, defaults to calendar year 12-31';
COMMENT ON COLUMN entities.georgia_resident IS 'True if Georgia resident for state tax purposes';
COMMENT ON COLUMN entities.entity_status IS 'Active or inactive - controls whether entity appears in dropdowns';
COMMENT ON COLUMN entities.formation_date IS 'Date entity was formed or individual birth date';
COMMENT ON COLUMN entities.notes IS 'Free-form notes for Claude context about this entity';
COMMENT ON COLUMN entities.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN entities.updated_at IS 'Timestamp when record was last modified - updated by trigger';
```

**Foreign Key References:**
- Referenced by: `institutions.entity_id`, `accounts.entity_id`, `tax_payments.entity_id`

---

### Table: institutions

**Purpose:** Financial institutions that hold accounts. Institutions are shared across all entities - one Fidelity record serves multiple entities through their accounts.

| Column (*R = Req)     | Data Type   | Constraints                                               | Purpose/Source                                           |
|-----------------------|-------------|-----------------------------------------------------------|----------------------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                     | Auto-generated unique identifier                         |
| `institution_name` *R | TEXT        | NOT NULL                                                  | Institution name (e.g., "Fidelity", "Bank of America")  |
| `institution_type`    | TEXT        | CHECK (institution_type IN ('brokerage', 'bank',          | Type of financial institution                            |
|                       |             | 'credit_union', 'insurance', 'retirement_plan', 'other')) |                                                          |
| `status`              | TEXT        | DEFAULT 'active' CHECK (status IN ('active',              | Current relationship status                              |
|                       |             | 'inactive', 'closed'))                                    |                                                          |
| `notes`               | TEXT        |                                                           | Claude context notes for institution-specific handling   |
| `created_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Record creation timestamp                                |
| `updated_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Last modification timestamp                              |
**PostgreSQL Table Comment:**
```sql
COMMENT ON TABLE institutions IS 'Financial institutions holding accounts - supports multiple institutions per entity';
```

**PostgreSQL Table Comment:**
```sql
COMMENT ON TABLE institutions IS 'Financial institutions holding accounts - shared across all entities (no entity_id foreign key)';
```

**PostgreSQL Column Comments:**
```sql
COMMENT ON COLUMN institutions.id IS 'Auto-generated unique identifier';
COMMENT ON COLUMN institutions.institution_name IS 'Official institution name (e.g. Fidelity, Bank of America)';
COMMENT ON COLUMN institutions.institution_type IS 'Classification: brokerage, bank, credit_union, insurance, retirement_plan, other';
COMMENT ON COLUMN institutions.status IS 'Active, inactive, or closed - tracks current relationship status';
COMMENT ON COLUMN institutions.notes IS 'Institution-specific processing notes for Claude';
COMMENT ON COLUMN institutions.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN institutions.updated_at IS 'Timestamp when record was last modified - updated by trigger';
```

**Foreign Key Constraints:**
- None - institutions are shared across entities via accounts table relationships

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
| `account_holder_name`    | TEXT        |                                                         | Name of the account holder                              |
| `account_name`           | TEXT        |                                                         | Account nickname/description                            |
| `account_type` *R        | TEXT        | NOT NULL CHECK (account_type IN ('checking', 'savings', | Account classification                                  |
|                          |             | 'brokerage', 'ira', '401k', 'roth_ira', 'trust',        |                                                         |
|                          |             | 'business', 'money_market', 'cd', 'hsa',                |                                                         |
|                          |             | 'cash_management'))                                     |                                                         |
| `account_subtype`        | TEXT        |                                                         | Specific subtype (e.g., "traditional_ira",              |
|                          |             |                                                         | "roth_401k", "taxable_brokerage")                       |
| `institution_name`       | TEXT        |                                                         | Institution name (derived from institutions table)      |
| `account_opening_date`   | DATE        |                                                         | When account was opened                                 |
| `account_status`         | TEXT        | DEFAULT 'active' CHECK (account_status IN ('active',    | Current account status                                  |
|                          |             | 'inactive', 'closed', 'transferred'))                   |                                                         |
| `is_tax_deferred`        | BOOLEAN     | DEFAULT FALSE                                           | True for IRAs, 401ks, and other tax-deferred accounts   |
| `is_tax_free`            | BOOLEAN     | DEFAULT FALSE                                           | True for Roth accounts and tax-free investments         |
| `requires_rmd`           | BOOLEAN     | DEFAULT FALSE                                           | True if account requires Required Minimum Distributions |
| `notes`                  | TEXT        |                                                         | Claude context notes for account-specific handling      |
| `created_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Record creation timestamp                               |
| `updated_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Last modification timestamp                             |
**PostgreSQL Table Comment:**
```sql
COMMENT ON TABLE accounts IS 'Individual financial accounts within institutions - links entities to account numbers with UNIQUE constraint preventing duplicates';
```

**PostgreSQL Column Comments:**
```sql
COMMENT ON COLUMN accounts.id IS 'Auto-generated unique identifier';
COMMENT ON COLUMN accounts.entity_id IS 'Links to entities table - which entity owns this account';
COMMENT ON COLUMN accounts.institution_id IS 'Links to institutions table - where account is held';
COMMENT ON COLUMN accounts.account_number IS 'Full account number - should be encrypted/masked in production';
COMMENT ON COLUMN accounts.account_number_display IS 'Last 4 digits for UI display (e.g. ****1234)';
COMMENT ON COLUMN accounts.account_holder_name IS 'Name as shown on account statements';
COMMENT ON COLUMN accounts.account_name IS 'User-friendly nickname for the account';
COMMENT ON COLUMN accounts.account_type IS 'Primary classification: checking, savings, brokerage, ira, 401k, etc.';
COMMENT ON COLUMN accounts.account_subtype IS 'Detailed subtype like traditional_ira, roth_401k, taxable_brokerage';
COMMENT ON COLUMN accounts.institution_name IS 'Institution name for readability - derived from institutions table on INSERT/UPDATE';
COMMENT ON COLUMN accounts.account_opening_date IS 'Date account was opened with institution';
COMMENT ON COLUMN accounts.account_status IS 'Active, inactive, closed, or transferred';
COMMENT ON COLUMN accounts.is_tax_deferred IS 'True for traditional IRAs, 401ks - taxes paid on withdrawal';
COMMENT ON COLUMN accounts.is_tax_free IS 'True for Roth accounts - no taxes on qualified withdrawals';
COMMENT ON COLUMN accounts.requires_rmd IS 'True if Required Minimum Distributions apply (traditional retirement accounts)';
COMMENT ON COLUMN accounts.notes IS 'Account-specific processing notes for Claude';
COMMENT ON COLUMN accounts.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN accounts.updated_at IS 'Timestamp when record was last modified - updated by trigger';
```

**Unique Constraints:**
- UNIQUE(institution_id, account_number) - Prevents duplicate accounts within same institution

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `institution_id` → `institutions(id)` ON DELETE RESTRICT

---

## Configuration and Classification Tables

### Table: data_mappings

**Purpose:** Configuration table for mapping source values to standardized types and subtypes. Enables data-driven classification of transactions, securities, and other domain-specific categorization without code changes.

| Column (*R = Req)    | Data Type   | Constraints                                               | Purpose/Source                                          |
|----------------------|-------------|-----------------------------------------------------------|---------------------------------------------------------|
| `id`                 | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                     | Auto-generated unique identifier                        |
| `mapping_type` *R    | TEXT        | NOT NULL                                                  | Category: 'transaction_descriptions', 'security_patterns', etc. |
| `source_value` *R    | TEXT        | NOT NULL                                                  | Original value from source data                         |
| `target_type` *R     | TEXT        | NOT NULL                                                  | Standardized type to map to                             |
| `target_subtype`     | TEXT        |                                                           | Optional subtype for additional categorization           |
| `notes`              | TEXT        |                                                           | Human-readable explanation                              |
| `created_at`         | TIMESTAMPTZ | DEFAULT NOW()                                             | Record creation timestamp                               |
| `updated_at`         | TIMESTAMPTZ | DEFAULT NOW()                                             | Last modification timestamp                             |

**PostgreSQL Table Comment:**
```sql
COMMENT ON TABLE data_mappings IS 'Configuration table for mapping source values to standardized types and subtypes - enables data-driven classification';
```

**PostgreSQL Column Comments:**
```sql
COMMENT ON COLUMN data_mappings.id IS 'Auto-generated unique identifier';
COMMENT ON COLUMN data_mappings.mapping_type IS 'Category of mapping: transaction_descriptions, security_patterns, account_types, etc.';
COMMENT ON COLUMN data_mappings.source_value IS 'Original value from source data that needs classification';
COMMENT ON COLUMN data_mappings.target_type IS 'Standardized type to map the source value to';
COMMENT ON COLUMN data_mappings.target_subtype IS 'Optional subtype for additional granular categorization';
COMMENT ON COLUMN data_mappings.notes IS 'Human-readable explanation of the mapping rule';
COMMENT ON COLUMN data_mappings.created_at IS 'Timestamp when mapping rule was created';
COMMENT ON COLUMN data_mappings.updated_at IS 'Timestamp when mapping rule was last modified - updated by trigger';
```

**Unique Constraints:**
- UNIQUE(mapping_type, source_value) - Prevents duplicate mappings for same type/value combination

**Indexes:**
```sql
-- Fast lookups during data processing
CREATE UNIQUE INDEX idx_data_mappings_lookup ON data_mappings(mapping_type, source_value);
CREATE INDEX idx_data_mappings_type ON data_mappings(mapping_type);
```

**Configuration-Driven Classification System:**

This table supports a flexible mapping system where source data values can be classified without code changes:

1. **Transaction Descriptions:** Map Fidelity transaction descriptions to standardized transaction types
   - Example: "REINVESTMENT" → type: "reinvest", subtype: "dividend_reinvestment"
   - Example: "SHORT TERM CAP GAIN" → type: "capital_gain", subtype: "short_term"

2. **Security Patterns:** Classify securities based on symbol or description patterns
   - Example: "CALL" options → type: "option", subtype: "call"
   - Example: Municipal bonds → type: "bond", subtype: "municipal"

3. **Options Tracking Support:** Essential for matching option transactions and calculating P&L
   - Example: "AAPL Apr 21 '25 $150 Call" → sec_class: "call", underlying: "AAPL"
   - Enables matching buy/sell transactions for same option contract

4. **Data Mapping Types:**
   - `transaction_descriptions`: Map transaction descriptions to transaction_type/subtype
   - `security_patterns`: Classify securities by symbol/name patterns
   - `account_types`: Standardize account type classifications
   - `tax_categories`: Map income types to tax treatment

**Example Mapping Queries:**
```sql
-- Find transaction type for a description
SELECT target_type, target_subtype
FROM data_mappings
WHERE mapping_type = 'transaction_descriptions'
AND source_value = 'REINVESTMENT';

-- Classify a security based on description
SELECT target_type, target_subtype
FROM data_mappings
WHERE mapping_type = 'security_patterns'
AND 'AAPL Apr 21 25 $150 Call' ILIKE '%' || source_value || '%';
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
| `doc_md5_hash` *R          | TEXT        | NOT NULL UNIQUE                                                | MD5 hash for duplicate detection (global unique)      |
| `mime_type`                | TEXT        | DEFAULT 'application/pdf'                                       | File MIME type                                        |
| **Amendment Tracking**     |             |                                                                 |                                                       |
| `is_amended`               | BOOLEAN     | DEFAULT FALSE                                                   | True if this document has been amended/corrected      |
| `amends_document_id`       | UUID (FK)   | REFERENCES documents(id) ON DELETE SET NULL                     | Original document this amends                         |
| `version_number`           | INTEGER     | DEFAULT 1                                                       | Version number for amended documents                  |
| **Portfolio Summary**      |             |                                                                 |                                                       |
| `portfolio_value`          | NUMERIC(15,2) |                                                               | Total portfolio value at statement date               |
| `portfolio_value_with_ai`  | NUMERIC(15,2) |                                                               | Portfolio value including accrued interest            |
| `portfolio_change_period`  | NUMERIC(15,2) |                                                               | Change in portfolio value for the period              |
| `portfolio_change_ytd`     | NUMERIC(15,2) |                                                               | Year-to-date portfolio change                         |
| **Processing Metadata**    |             |                                                                 |                                                       |
| `processed_at`             | TIMESTAMPTZ |                                                                 | When document processing completed                    |
| `processed_by`             | TEXT        | DEFAULT 'claude'                                                | Processing agent identifier                           |
| `extraction_notes`         | TEXT        |                                                                 | Claude's notes about the extraction                   |
| `extraction_json_path`     | TEXT        |                                                                 | Path to JSON file with full extraction data           |
| **Archival Support**       |             |                                                                 |                                                       |
| `is_archived`              | BOOLEAN     | DEFAULT FALSE                                                   | True if document is archived (soft delete)            |
| **Audit Trail**            |             |                                                                 |                                                       |
| `created_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Record creation timestamp                             |
| `updated_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Last modification timestamp                           |
| `imported_at`              | TIMESTAMPTZ | DEFAULT NOW()                                                   | When document was first imported                      |
| `Comment`                  |             |                                                                 |                                                       |
|----------------------------|-------------|-------------------------------------------------------------------|-------------------------------------------------------|
| Auto-generated unique identifier | FK to institutions table | Tax year document pertains to | Primary document classification |
| Reporting period start date | Reporting period end date | Full path to stored document file | Original filename for reference |
| File size in bytes | MD5 hash for duplicate detection (UNIQUE constraint) | File MIME type | True if document has been amended/corrected |
| Original document this amends | Version number for amended documents | Total portfolio value at statement date | Portfolio value including accrued interest |
| Change in portfolio value for the period | Year-to-date portfolio change | When document processing completed | Processing agent identifier |
| Claude notes about extraction | Path to JSON file with full extraction data | Record creation timestamp | Last modification timestamp |
| When document was first imported |

**Unique Constraints:**
- UNIQUE(doc_md5_hash) - Prevents duplicate document uploads

**Foreign Key Constraints:**
- `institution_id` → `institutions(id)` ON DELETE RESTRICT
- `amends_document_id` → `documents(id)` ON DELETE SET NULL

---

### Table: document_accounts

**Purpose:** Many-to-many association between documents and accounts. Supports consolidated statements/1099s that list multiple accounts (and thus, multiple entities via accounts).

**Key Relationships:**
- One document can contain data for multiple accounts (consolidated statements)
- Each account links to exactly one entity (the owner)
- Therefore, one document can span multiple entities through their accounts

**Design Justification:**
This junction table is **absolutely essential** for the document-centric architecture:

1. **Real-world requirement:** Fidelity consolidated statements cover multiple accounts in one PDF
   - Example: `Fidelity_2025-08_Brok+CMA.pdf` contains both brokerage (Z40-394067) and IRA (Z27-375656) accounts
   - One document → Multiple accounts → Multiple entities (through account ownership)

2. **Alternative approaches fail:**
   - **Add account_id to documents:** Can't handle consolidated statements covering multiple accounts
   - **Use PostgreSQL arrays:** Breaks foreign key constraints and complicates queries
   - **Infer from transactions:** Circular dependency during data loading + can't represent empty sections

3. **Essential query patterns:**
   ```sql
   -- Find all accounts in a document
   SELECT a.* FROM accounts a
   JOIN document_accounts da ON a.id = da.account_id
   WHERE da.document_id = 'doc-uuid'

   -- Find all documents for an account
   SELECT d.* FROM documents d
   JOIN document_accounts da ON d.id = da.document_id
   WHERE da.account_id = 'account-uuid'
   ```

| Column (*R = Req)   | Data Type   | Constraints                                                     | Purpose/Source                                 |
|---------------------|-------------|-----------------------------------------------------------------|------------------------------------------------|
| `document_id` *R    | UUID (FK)   | NOT NULL REFERENCES documents(id) ON DELETE CASCADE            | Linked document                                |
| `account_id` *R     | UUID (FK)   | NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT            | Linked account                                 |
| `created_at`        | TIMESTAMPTZ | DEFAULT NOW()                                                   | Link creation timestamp                        |
| `Comment`           |             |                                                                 |                                                |
|---------------------|-------------|-------------------------------------------------------------------|------------------------------------------------|
| FK to documents table | FK to accounts table | Link creation timestamp |

**Constraints:**
- UNIQUE constraint on (document_id, account_id)

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT

---

### Table: transactions (Enhanced)

**Purpose:** Individual financial transactions extracted from documents, with enhanced multi-entity support and comprehensive tax categorization.

| Column (*R = Req)         | Data Type     | Constraints                                                       | Purpose/Source                                            | Source Documents |
|---------------------------|---------------|-------------------------------------------------------------------|-----------------------------------------------------------|------------------|
| `id`                      | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                             | Auto-generated unique identifier                          |
| `entity_id` *R            | UUID (FK)     | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT               | Entity this transaction belongs to                        |
| `document_id` *R          | UUID (FK)     | NOT NULL REFERENCES documents(id) ON DELETE CASCADE               | Source document for audit trail                           |
| `account_id` *R           | UUID (FK)     | NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT               | Account where transaction occurred                        |
| **Transaction Core Data** |               |                                                                   |                                                           |
| `transaction_date`        | DATE          |                                                                   | Date transaction occurred (trade date)                    | Fidelity statements (Date MM/DD), Trade confirmations (Trade Date), 1099s (Payment Date) |
| `settlement_date`         | DATE          |                                                                   | Settlement/clearing date                                  | Fidelity statements (Settlement Date column), Trade confirmations (Settlement Date) |
| `transaction_type` *R     | TEXT          | NOT NULL CHECK (transaction_type IN ('dividend', 'interest',      | Transaction classification                                | Inferred from description patterns |
|                           |               | 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee',              |                                                           |  |
|                           |               | 'return_of_capital', 'assignment', 'redemption', 'reinvest',      |                                                           |  |
|                           |               | 'option_buy', 'option_sell', 'other'))                        |                                                           |  |
| `transaction_subtype`     | TEXT          |                                                                   | Detailed subtype (e.g., 'qualified_dividend',             | Fidelity statements (description parsing), 1099s (box types) |
|                           |               |                                                                   | 'municipal_interest', 'management_fee')                   |  |
| `description` *R          | TEXT          | NOT NULL                                                          | Transaction description from source document              | Fidelity statements (Description column), QuickBooks exports (Memo field) |
| `amount` *R               | NUMERIC(15,2) | NOT NULL                                                          | Transaction amount                                        | Fidelity statements (Amount column), 1099s (Box amounts), Trade confirmations (Net Amount) |
| **Security Information**  |               |                                                                   |                                                           |
| `security_name`           | TEXT          |                                                                   | Security name/description                                 | Fidelity statements (Security Name column) |
| `security_identifier`     | TEXT          |                                                                   | Symbol/ticker identifier                                  | Fidelity statements (Symbol column) |
| `sec_cusip`               | TEXT          |                                                                   | CUSIP identifier for bonds                                | Fidelity statements (CUSIP column) |
| `quantity`                | NUMERIC(15,6) |                                                                   | Number of shares/units in transaction                     | Fidelity statements (Quantity column) |
| `price_per_unit`          | NUMERIC(12,4) |                                                                   | Price per share/unit                                      | Fidelity statements (Price column) |
| `cost_basis`              | NUMERIC(15,2) |                                                                   | Total cost basis for this transaction                     | Fidelity statements (Total Cost Basis column) |
| `fees`                    | NUMERIC(10,2) |                                                                   | Transaction fees/costs                                    | Fidelity statements (Transaction Cost column) |
| `security_type`           | TEXT          | CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf',   | Type of security involved                                 |
|                           |               | 'money_market', 'cd', 'option', 'cash', 'other'))                 |                                                           |
| `option_type`             | TEXT          | CHECK (option_type IN ('CALL', 'PUT'))                            | Type of option contract                                   |
| `strike_price`            | DECIMAL(15,2) |                                                                   | Option strike price                                       |
| `expiration_date`         | DATE          |                                                                   | Option expiration date                                    |
| `underlying_symbol`       | TEXT          |                                                                   | Underlying symbol for options                             |
| `option_details`          | JSONB         |                                                                   | Options data: {"type": "PUT/CALL", "strike": 150,         |
|                           |               |                                                                   | "expiry": "2025-09-15", "underlying": "AAPL"}             |
| `bond_state`              | TEXT          |                                                                   | State for municipal bonds (e.g., 'GA', 'NY')             |
| `dividend_qualified`      | BOOLEAN       |                                                                   | True if qualified dividend, false if ordinary             |
| `bond_details`            | JSONB         |                                                                   | Bond data: {"accrued_interest": 200, "coupon_rate": 5.0,  |
|                           |               |                                                                   | "maturity": "2030-01-01", "call_date": "2025-09-30"}      |
| `sec_class`               | TEXT          |                                                                   | Security classification (call, put, stock, bond, etc.)    |
| `source` *R               | TEXT          | NOT NULL                                                          | Origin of the transaction data                            |
| **Additional Activity Fields** |          |                                                                   |                                                           |
| `reference_number`        | TEXT          |                                                                   | Wire reference or transaction ID                          | Fidelity statements (Reference column) |
| `payee`                   | TEXT          |                                                                   | Bill payment recipient                                    | Fidelity statements (Payee column) |
| `payee_account`           | TEXT          |                                                                   | Payee account number (masked)                             | Fidelity statements (Payee Account column) |
| `ytd_amount`              | NUMERIC(15,2) |                                                                   | Year-to-date amount for recurring payments                | Fidelity statements (YTD Payments column) |
| `balance`                 | NUMERIC(15,2) |                                                                   | Running balance after transaction                         | Fidelity statements (Balance column) |
| `account_type`            | TEXT          |                                                                   | Account type for transaction (e.g., 'CASH', 'MARGIN')     | Fidelity statements (Account Type column) |
| **Tax Categorization**    |               |                                                                   |                                                           |
| `tax_category`            | TEXT          | CHECK (tax_category IN ('ordinary_dividend',                      | Primary tax treatment                                     |
|                           |               | 'qualified_dividend', 'municipal_interest', 'corporate_interest', |                                                           |
|                           |               | 'capital_gain_short', 'capital_gain_long', 'return_of_capital',   |                                                           |
|                           |               | 'tax_exempt', 'fee_expense', 'other'))                            |                                                           |
| `federal_taxable`         | BOOLEAN       |                                                                   | True if taxable for federal purposes                      |
| `state_taxable`           | BOOLEAN       |                                                                   | True if taxable for state purposes (GA-specific)          |
| `tax_details`             | JSONB         |                                                                   | Additional tax context: {"issuer_state": "GA",            |
|                           |               |                                                                   | "amt_preference": false, "section_199a": true}            |
| **Source Tracking**       |               |                                                                   |                                                           |
| `source_transaction_id`   | TEXT          |                                                                   | Original transaction ID from source system                |
| `source_reference`        | TEXT          |                                                                   | Additional source reference (confirmation number, etc.)   |
| **Transaction Relations** |               |                                                                   |                                                           |
| `related_transaction_id`  | UUID (FK)     | REFERENCES transactions(id) ON DELETE SET NULL                    | Related transaction (wash sales, corrections, reversals)  |
| **Duplicate Detection**   |               |                                                                   |                                                           |
| `is_duplicate_of`         | UUID (FK)     | REFERENCES transactions(id) ON DELETE SET NULL                    | References original transaction if this is a duplicate    |
| `duplicate_reason`        | TEXT          |                                                                   | Explanation of why marked as duplicate                    |
| **Archival Support**      |               |                                                                   |                                                           |
| `is_archived`             | BOOLEAN       | DEFAULT FALSE                                                     | True if transaction is archived (soft delete)             |
| **Audit Trail**           |               |                                                                   |                                                           |
| `created_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Record creation timestamp                                 |
| `updated_at`              | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Last modification timestamp                               |
| `processed_by`            | TEXT          | DEFAULT 'claude'                                                  | Processing agent identifier                               |
| `Comment`                 |               |                                                                   |                                                           |
|---------------------------|---------------|-------------------------------------------------------------------|-----------------------------------------------------------|
| Auto-generated unique identifier | FK to entities table | FK to documents table | FK to accounts table |
| Fidelity Date MM/DD, Trade Date, Payment Date | Settlement/clearing date | Inferred from description patterns | Fidelity description parsing, 1099 box types |
| Fidelity Description column, QuickBooks Memo | Fidelity Amount column, 1099 box amounts | Fidelity Security Name column | Fidelity Symbol/CUSIP column |
| Number of shares/units in transaction | Price per share/unit | Total cost basis for tax purposes | Transaction fees/costs |
| Type of security involved | Origin of transaction data | Primary tax treatment for fed/state | True if taxable for federal purposes |
| True if taxable for state purposes (GA-specific) | Additional tax context JSON | Original transaction ID from source | Additional source reference |
| References original if duplicate | Explanation why marked duplicate | Record creation timestamp | Last modification timestamp |
| Processing agent identifier |

**PostgreSQL Column Comments (Selected):**
```sql
COMMENT ON COLUMN transactions.sec_class IS 'Security classification for options tracking and analysis: call, put, stock, bond, etc.';
COMMENT ON COLUMN transactions.underlying_symbol IS 'Underlying symbol for option contracts - enables option chain analysis';
COMMENT ON COLUMN transactions.strike_price IS 'Strike price for option contracts';
COMMENT ON COLUMN transactions.expiration_date IS 'Expiration date for option contracts';
COMMENT ON COLUMN transactions.option_type IS 'CALL or PUT for option contracts';
```

**Options Tracking Support:**

The `sec_class` column enables sophisticated options tracking and transaction matching:

1. **Option Classification:** Classify options as 'call' or 'put' based on security description
   - Uses data_mappings table to parse option descriptions
   - Example: "AAPL Apr 21 '25 $150 Call" → sec_class: "call"

2. **Transaction Matching:** Match related option transactions for P&L calculation
   - Buy and sell transactions for same option contract
   - Exercise and assignment tracking
   - Expiration handling

3. **Security Analysis:** Group transactions by security class for reporting
   - Separate analysis of stock vs option vs bond transactions
   - Performance tracking by security type
   - Risk management and exposure analysis

**Example Options Queries:**
```sql
-- Find all option transactions
SELECT * FROM transactions
WHERE sec_class IN ('call', 'put')
ORDER BY transaction_date DESC;

-- Match option buy/sell pairs
SELECT
    underlying_symbol,
    strike_price,
    expiration_date,
    sec_class,
    SUM(CASE WHEN transaction_type = 'option_buy' THEN quantity ELSE 0 END) as bought,
    SUM(CASE WHEN transaction_type = 'option_sell' THEN quantity ELSE 0 END) as sold
FROM transactions
WHERE sec_class IN ('call', 'put')
GROUP BY underlying_symbol, strike_price, expiration_date, sec_class;

-- Options P&L analysis
SELECT
    underlying_symbol,
    sec_class,
    COUNT(*) as transaction_count,
    SUM(amount) as net_amount,
    AVG(price_per_unit) as avg_price
FROM transactions
WHERE sec_class IN ('call', 'put')
  AND transaction_date >= '2024-01-01'
GROUP BY underlying_symbol, sec_class
ORDER BY net_amount DESC;
```

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT
- `related_transaction_id` → `transactions(id)` ON DELETE SET NULL
- `is_duplicate_of` → `transactions(id)` ON DELETE SET NULL

---

 ### Table: positions

  **Purpose:** Point-in-time snapshots of holdings/positions extracted from statements. Each row represents one security position at a specific date.

| DB Column                         | JSON Field           | Source Label            | Data Type     | Constraints                                         |
|-----------------------------------|----------------------|-------------------------|---------------|-----------------------------------------------------|
| **-- Metadata & Keys --**         |
| id                                | -                    | -                       | UUID          | PRIMARY KEY DEFAULT gen_random_uuid()               |
| document_id                       | -                    | -                       | UUID          | NOT NULL REFERENCES documents(id) ON DELETE CASCADE |
| account_id                        | -                    | -                       | UUID          | NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT |
| entity_id                         | -                    | -                       | UUID          | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT |
| position_date                     | -                    | Statement Date          | DATE          | NOT NULL                                            |
| account_number                    | account_number       | Account Number          | TEXT          | NOT NULL                                            |
| **-- Security Identification --** |
| sec_ticker                        | sec_symbol           | Symbol/Ticker           | TEXT          |                                                     |
| cusip                             | sec_cusip            | CUSIP                   | TEXT          |                                                     |
| sec_name                          | sec_description      | Description             | TEXT          | NOT NULL                                            |
| sec_type                          | sec_type             | Security Type           | TEXT          | NOT NULL                                            |
| sec_subtype                       | sec_subtype          | Security Subtype        | TEXT          |                                                     |
| **-- Position Values --**         |
| beg_market_value                  | beg_market_value     | Beginning Market Value  | NUMERIC(15,2) |                                                     |
| quantity                          | quantity             | Quantity                | NUMERIC(15,6) | NOT NULL                                            |
| price                             | price_per_unit       | Price Per Unit          | NUMERIC(12,4) | NOT NULL                                            |
| end_market_value                  | end_market_value     | Ending Market Value     | NUMERIC(15,2) | NOT NULL                                            |
| **-- Cost Basis & P&L --**        |
| cost_basis                        | cost_basis           | Total Cost Basis        | NUMERIC(15,2) |                                                     |
| unrealized_gain_loss              | unrealized_gain_loss | Unrealized Gain/Loss    | NUMERIC(15,2) |                                                     |
| **-- Income Estimates --**        |
| estimated_ann_inc                 | estimated_ann_inc    | Est Annual Income (EAI) | NUMERIC(15,2) |                                                     |
| est_yield                         | est_yield            | Estimated Yield (EY)    | NUMERIC(5,4)  | CHECK (>= 0)                                        |
| **-- Option-Specific --**         |
| underlying_symbol                 | underlying_symbol    | Underlying Symbol       | TEXT          |                                                     |
| strike_price                      | strike_price         | Strike Price            | NUMERIC(12,4) |                                                     |
| exp_date                          | expiration_date      | Expiration Date         | DATE          |                                                     |
| option_type                       | -                    | CALL/PUT                | TEXT          | CHECK (IN ('CALL','PUT'))                           |
| **-- Bond-Specific --**           |
| maturity_date                     | maturity_date        | Maturity Date           | DATE          |                                                     |
| coupon_rate                       | coupon_rate          | Coupon Rate             | NUMERIC(5,3)  |                                                     |
| accrued_int                       | accrued_int          | Accrued Interest        | NUMERIC(15,2) |                                                     |
| agency_rating                     | agency_ratings       | Ratings                 | TEXT          |                                                     |
| next_call                         | next_call_date       | Next Call Date          | DATE          |                                                     |
| call_price                        | call_price           | Call Price              | NUMERIC(12,4) |                                                     |
| payment_freq                      | payment_freq         | Payment Frequency       | TEXT          |                                                     |
| bond_features                     | bond_features        | Bond Features           | TEXT          |                                                     |
| **-- Position Flags --**          |
| is_margin                         | -                    | -                       | BOOLEAN       | DEFAULT FALSE                                       |
| is_short                          | -                    | -                       | BOOLEAN       | DEFAULT FALSE                                       |
| **-- Audit Trail --**             |
| created_at                        | -                    | -                       | TIMESTAMPTZ   | DEFAULT NOW()                                       |
| updated_at                        | -                    | -                       | TIMESTAMPTZ   | DEFAULT NOW()                                       |

**Unique Constraints:**
- UNIQUE(document_id, account_id, position_date, sec_ticker, cusip) - Prevents duplicate positions from same document

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT
- `entity_id` → `entities(id)` ON DELETE RESTRICT

---

## Tax and Transfer Management Tables

> **Phase 2 - Not Yet Implemented**
> The following tables are designed for future functionality and will not be created in the initial database build.
> They support manual entry and QuickBooks integration planned for Phase 2.

### Table: tax_payments (Phase 2)

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
| `Comment`                 |               |                                                             |                                                 |
|---------------------------|---------------|-------------------------------------------------------------|-------------------------------------------------|
| Auto-generated unique identifier | FK to entities table | FK to accounts table (if tracked) | Tax year payment applies to |
| Type of tax payment (est_q1, est_q2, etc.) | Which government entity (federal, georgia, other_state) | Date payment was made | Original due date for payment |
| Payment amount | Calculation details JSON | Estimated income for the year | Estimated total tax liability |
| Additional context and notes | Record creation timestamp | Last modification timestamp |



---

### Table: transfers (Phase 2)

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
| `Comment`                   |               |                                                               |                                  |
|-----------------------------|---------------|---------------------------------------------------------------|-------------------------------------|
| Auto-generated unique identifier | FK to entities table (source) | FK to accounts table (source) | FK to entities table (destination) |
| FK to accounts table (destination) | Date transfer occurred | Transfer amount | Nature of the transfer |
| Business purpose description | Additional context and details | Record creation timestamp | Last modification timestamp |


**Foreign Key Constraints:**
- `source_entity_id` → `entities(id)` ON DELETE RESTRICT
- `destination_entity_id` → `entities(id)` ON DELETE RESTRICT
- `source_account_id` → `accounts(id)` ON DELETE RESTRICT
- `destination_account_id` → `accounts(id)` ON DELETE RESTRICT
- CHECK CONSTRAINT: `source_entity_id != destination_entity_id` (prevent self-transfers)


---

## Asset Management Tables

> **Phase 2 - Not Yet Implemented**
> The following tables support investment strategy tracking and net worth calculation through manual data entry.
> They will be implemented in Phase 2 after core document processing is operational.

### Table: asset_notes (Phase 2)

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
| `Comment`                    |               |                                                            |                                                        |
|------------------------------|---------------|------------------------------------------------------------|---------------------------------------------------------|
| Auto-generated unique identifier | FK to entities table | FK to accounts table | Security ticker symbol (e.g. "AAPL", "VTSAX") |
| CUSIP identifier | Full security name | Type of security | Purchase price target/limit |
| Sale price target | Stop loss price | Last known price | When price was last updated |
| Total cost basis of position | Current number of shares held | Current unrealized gain/loss | Date of last buy/sell transaction |
| True if price alerts are active | Alert conditions JSON | Current dividend yield | Expected next dividend payment date |
| Ongoing research and analysis notes | How often to review | Scheduled next review date | Current status |
| General notes and observations | Record creation timestamp | Last modification timestamp |



---

## Net Worth Tracking Tables

### Table: real_assets (Phase 2)

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
| `Comment`           |               |                                                      |                                         |
|---------------------|---------------|------------------------------------------------------|------------------------------------------|
| Auto-generated unique identifier | FK to entities table | Type of real asset | Asset description (e.g. "Address") |
| Property address if applicable | When asset was acquired | Original purchase price | Current estimated value |
| Date of current valuation | Source of valuation (e.g. "Appraisal") | Rental income if applicable | Maintenance, HOA, insurance, taxes |
| Current status | Additional notes | Record creation timestamp | Last modification timestamp |


---

### Table: liabilities (Phase 2)

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
| `Comment`             |               |                                                          |                                       |
|-----------------------|---------------|----------------------------------------------------------|---------------------------------------|
| Auto-generated unique identifier | FK to entities table | FK to real_assets table (for mortgages) | Type of liability |
| Name of lender/bank | Loan account number (masked) | Original loan amount | Current outstanding balance |
| Annual interest rate (e.g. 4.25%) | When loan originated | When loan will be paid off | Regular monthly payment amount |
| Next payment due date | Monthly escrow for taxes/insurance | Current status | Additional notes |
| Record creation timestamp | Last modification timestamp |


---
### Table: doc_level_data

  **Purpose:** Document-level aggregated data from Income Summary and Realized Gains/Losses tables in statements.

| DB Column                            | JSON Field              | Source Label                      | Data Type     | Constraints                                                        |
|--------------------------------------|-------------------------|-----------------------------------|---------------|--------------------------------------------------------------------|
| **-- Metadata & Keys --**            |
| id                                   | -                       | -                                 | UUID          | PRIMARY KEY DEFAULT gen_random_uuid()                              |
| document_id                          | -                       | -                                 | UUID          | NOT NULL REFERENCES documents(id) ON DELETE CASCADE                |
| account_id                           | -                       | -                                 | UUID          | REFERENCES accounts(id) ON DELETE RESTRICT                         |
| account_number                       | account_number          | Account Number                    | TEXT          | NOT NULL                                                           |
| doc_section                          | -                       | -                                 | TEXT          | NOT NULL                                                           |
| as_of_date                           | -                       | Statement Date                    | DATE          | NOT NULL                                                           |
| **-- Account Summary --**            |
| net_acct_value                       | net_acct_value          | Net Account Value                 | NUMERIC(15,2) |                                                                    |
| beg_value                            | beginning_value         | Beginning Value                   | NUMERIC(15,2) |                                                                    |
| end_value                            | ending_value            | Ending Value                      | NUMERIC(15,2) |                                                                    |
| **-- Income Summary: Taxable --**    |
| taxable_total_period                 | taxable_total_period    | Taxable Total (period)            | NUMERIC(15,2) |                                                                    |
| taxable_total_ytd                    | taxable_total_ytd       | Taxable Total (YTD)               | NUMERIC(15,2) |                                                                    |
| divs_taxable_period                  | divs_taxable_period     | Taxable Dividends (period)        | NUMERIC(15,2) |                                                                    |
| divs_taxable_ytd                     | divs_taxable_ytd        | Taxable Dividends (YTD)           | NUMERIC(15,2) |                                                                    |
| stcg_taxable_period                  | stcg_taxable_period     | Short-term Capital Gains (period) | NUMERIC(15,2) |                                                                    |
| stcg_taxable_ytd                     | stcg_taxable_ytd        | Short-term Capital Gains (YTD)    | NUMERIC(15,2) |                                                                    |
| int_taxable_period                   | int_taxable_period      | Taxable Interest (period)         | NUMERIC(15,2) |                                                                    |
| int_taxable_ytd                      | int_taxable_ytd         | Taxable Interest (YTD)            | NUMERIC(15,2) |                                                                    |
| ltcg_taxable_period                  | ltcg_taxable_period     | Long-term Capital Gains (period)  | NUMERIC(15,2) |                                                                    |
| ltcg_taxable_ytd                     | ltcg_taxable_ytd        | Long-term Capital Gains (YTD)     | NUMERIC(15,2) |                                                                    |
| **-- Income Summary: Tax Exempt --** |
| tax_exempt_total_period              | tax_exempt_total_period | Tax-exempt Total (period)         | NUMERIC(15,2) |                                                                    |
| tax_exempt_total_ytd                 | tax_exempt_total_ytd    | Tax-exempt Total (YTD)            | NUMERIC(15,2) |                                                                    |
| divs_tax_exempt_period               | divs_tax_exempt_period  | Tax-exempt Dividends (period)     | NUMERIC(15,2) |                                                                    |
| divs_tax_exempt_ytd                  | divs_tax_exempt_ytd     | Tax-exempt Dividends (YTD)        | NUMERIC(15,2) |                                                                    |
| int_tax_exempt_period                | int_tax_exempt_period   | Tax-exempt Interest (period)      | NUMERIC(15,2) |                                                                    |
| int_tax_exempt_ytd                   | int_tax_exempt_ytd      | Tax-exempt Interest (YTD)         | NUMERIC(15,2) |                                                                    |
| **-- Income Summary: Other --**      |
| roc_period                           | roc_period              | Return of Capital (period)        | NUMERIC(15,2) |                                                                    |
| roc_ytd                              | roc_ytd                 | Return of Capital (YTD)           | NUMERIC(15,2) |                                                                    |
| grand_total_period                   | grand_total_period      | Grand Total (period)              | NUMERIC(15,2) |                                                                    |
| grand_total_ytd                      | grand_total_ytd         | Grand Total (YTD)                 | NUMERIC(15,2) |                                                                    |
| **-- Realized Gains/Losses --**      |
| st_gain_period                       | st_gain_period          | Short-term Gain (period)          | NUMERIC(15,2) |                                                                    |
| st_loss_period                       | st_loss_period          | Short-term Loss (period)          | NUMERIC(15,2) |                                                                    |
| lt_gain_ytd                          | lt_gain_ytd             | Long-term Gain (YTD)              | NUMERIC(15,2) |                                                                    |
| lt_loss_ytd                          | lt_loss_ytd             | Long-term Loss (YTD)              | NUMERIC(15,2) |                                                                    |
| **-- Audit Trail --**                |
| created_at                           | -                       | -                                 | TIMESTAMPTZ   | DEFAULT NOW()                                                      |
| updated_at                           | -                       | -                                 | TIMESTAMPTZ   | DEFAULT NOW()                                                      |

**Unique Constraints:**
- UNIQUE(document_id, account_id, doc_section) - Prevents duplicate summary data for same document/account/section

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT

**Important:** This table contains **transcribed data** pulled directly from PDF income summary and realized gains sections. On documents with multiple accounts, this data spans accounts and represents document-level totals as shown in the source PDF. We are NOT deriving or calculating this data - we are transcribing it exactly as it appears in the financial statements for audit trail and reconciliation purposes.
