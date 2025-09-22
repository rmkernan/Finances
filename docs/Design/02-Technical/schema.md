# Enhanced Database Schema - Financial Data Management System

**Created:** 09/10/25 10:30AM ET
**Updated:** 09/11/25 12:58PM ET - Added real_assets and liabilities tables for complete net worth tracking
**Updated:** 09/17/25 3:15PM ET - Added source document mapping columns to transactions table
**Updated:** 09/18/25 1:45PM ET - Added positions and income_summaries tables, enhanced portfolio fields per Fidelity document map
**Updated:** 09/18/25 2:30PM ET - Added Comment column to all tables with practical metadata for PostgreSQL COMMENT ON COLUMN feature
**Updated:** 09/22/25 12:53PM ET - Added data processing workflow, enhanced foreign key documentation, aligned with Fidelity document map
**Updated:** 09/22/25 1:18PM ET - Added beginning_value and ending_value fields to doc_level_data table
**Updated:** 09/22/25 1:25PM ET - Removed redundant income_summaries table, marked Phase 2 tables (not yet implemented)
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

## Data Processing Workflow

### Document Processing Pipeline

The system follows a standardized workflow for converting financial documents into structured data:

```
1. Document Ingestion
   PDF/Image → /documents/inbox/ → File hash generated for duplicate detection

2. Data Extraction (Claude-assisted)
   Institution Guide (e.g., fidelity-document-map.md) → JSON extraction
   Source Labels → JSON Fields → Database Columns

3. Data Validation
   - Account number matching to existing accounts
   - Entity association through account ownership
   - Duplicate detection via file_hash and transaction patterns

4. Database Insert
   - Documents table: Metadata and audit trail
   - Document_accounts: Link to relevant accounts
   - Positions: Point-in-time holdings snapshots
   - Doc_level_data: Aggregated income and gains/losses
   - Transactions: Individual transaction records

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
| `Comment`          |             |                                                                          |                                                     |
|--------------------|-------------|--------------------------------------------------------------------------|-----------------------------------------------------|
| Auto-generated unique identifier | Legal entity name from tax documents | IRS entity type classification | EIN for entities, SSN for individuals (encrypted/hashed) |
| Last 4 digits for display (e.g. "***-**-1234") | Primary responsible party name | Tax year end (MM-DD format, e.g. "12-31", "09-30") | Georgia state tax residency status |
| Current operational status | Entity formation/birth date | Claude context notes | Record creation timestamp |
| Last modification timestamp |

**Foreign Key References:**
- Referenced by: `institutions.entity_id`, `accounts.entity_id`, `tax_payments.entity_id`

---

### Table: institutions

**Purpose:** Financial institutions that hold accounts for entities. Supports multiple institutions per entity for diversified financial management.

| Column (*R = Req)     | Data Type   | Constraints                                               | Purpose/Source                                           |
|-----------------------|-------------|-----------------------------------------------------------|----------------------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                     |                                                          |
| `entity_id` *R        | UUID (FK)   | NOT NULL REFERENCES entities(id) ON DELETE RESTRICT       |                                                          |
| `institution_name` *R | TEXT        | NOT NULL                                                  | Institution name                                         |
| `institution_type`    | TEXT        | CHECK (institution_type IN ('brokerage', 'bank',          | Type of financial institution                            |
|                       |             | 'credit_union', 'insurance', 'retirement_plan', 'other')) |                                                          |
| `status`              | TEXT        | DEFAULT 'active' CHECK (status IN ('active',              | Current relationship status                              |
|                       |             | 'inactive', 'closed'))                                    |                                                          |
| `notes`               | TEXT        |                                                           | Claude context notes for institution-specific handling   |
| `created_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Record creation timestamp                                |
| `updated_at`          | TIMESTAMPTZ | DEFAULT NOW()                                             | Last modification timestamp                              |
| `Comment`             |             |                                                           |                                                          |
|-----------------------|-------------|-----------------------------------------------------------|----------------------------------------------------------|
| Auto-generated unique identifier | FK to entities table | Institution name (e.g. "Fidelity Investments", "SunTrust Bank") | Type of financial institution |
| Current relationship status | Claude context notes for institution-specific handling | Record creation timestamp | Last modification timestamp |

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT (prevent deletion if accounts exist)

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
|                          |             | 'business', 'money_market', 'cd'))                      |                                                         |
| `account_subtype`        | TEXT        |                                                         | Specific subtype (e.g., "traditional_ira",              |
|                          |             |                                                         | "roth_401k", "taxable_brokerage")                       |
| `account_opening_date`   | DATE        |                                                         | When account was opened                                 |
| `account_status`         | TEXT        | DEFAULT 'active' CHECK (account_status IN ('active',    | Current account status                                  |
|                          |             | 'inactive', 'closed', 'transferred'))                   |                                                         |
| `is_tax_deferred`        | BOOLEAN     | DEFAULT FALSE                                           | True for IRAs, 401ks, and other tax-deferred accounts   |
| `is_tax_free`            | BOOLEAN     | DEFAULT FALSE                                           | True for Roth accounts and tax-free investments         |
| `requires_rmd`           | BOOLEAN     | DEFAULT FALSE                                           | True if account requires Required Minimum Distributions |
| `notes`                  | TEXT        |                                                         | Claude context notes for account-specific handling      |
| `created_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Record creation timestamp                               |
| `updated_at`             | TIMESTAMPTZ | DEFAULT NOW()                                           | Last modification timestamp                             |
| `Comment`                |             |                                                         |                                                         |
|--------------------------|-------------|---------------------------------------------------------|---------------------------------------------------------|
| Auto-generated unique identifier | FK to entities table | FK to institutions table | Fidelity "Account #" field, JSON: account_number |
| Last 4 digits for display (e.g. "****1234") | Name on account | Account nickname/description | Account classification |
| Specific subtype (e.g. "traditional_ira", "roth_401k") | When account opened | Current account status | True for IRAs, 401ks, tax-deferred accounts |
| True for Roth accounts and tax-free investments | True if requires Required Minimum Distributions | Claude context notes for account-specific handling | Record creation timestamp |
| Last modification timestamp |

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `institution_id` → `institutions(id)` ON DELETE RESTRICT

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
| **Audit Trail**            |             |                                                                 |                                                       |
| `created_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Record creation timestamp                             |
| `updated_at`               | TIMESTAMPTZ | DEFAULT NOW()                                                   | Last modification timestamp                           |
| `imported_at`              | TIMESTAMPTZ | DEFAULT NOW()                                                   | When document was first imported                      |
| `Comment`                  |             |                                                                 |                                                       |
|----------------------------|-------------|-------------------------------------------------------------------|-------------------------------------------------------|
| Auto-generated unique identifier | FK to institutions table | Tax year document pertains to | Primary document classification |
| Reporting period start date | Reporting period end date | Full path to stored document file | Original filename for reference |
| File size in bytes | SHA256 hash for duplicate detection (global unique) | File MIME type | True if document has been amended/corrected |
| Original document this amends | Version number for amended documents | Total portfolio value at statement date | Portfolio value including accrued interest |
| Change in portfolio value for the period | Year-to-date portfolio change | When document processing completed | Processing agent identifier |
| Claude notes about extraction | Path to JSON file with full extraction data | Record creation timestamp | Last modification timestamp |
| When document was first imported |

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
| `transaction_date` *R     | DATE          | NOT NULL                                                          | Date transaction occurred                                 | Fidelity statements (Date MM/DD), Trade confirmations (Trade Date), 1099s (Payment Date) |
| `settlement_date`         | DATE          |                                                                   | Settlement/clearing date                                  | Trade confirmations (Settlement Date) |
| `transaction_type` *R     | TEXT          | NOT NULL CHECK (transaction_type IN ('dividend', 'interest',      | Transaction classification                                | Inferred from description patterns |
|                           |               | 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee',              |                                                           |  |
|                           |               | 'return_of_capital', 'assignment', 'redemption', 'reinvest',      |                                                           |  |
|                           |               | 'option_buy', 'option_sell', 'other'))                        |                                                           |  |
| `transaction_subtype`     | TEXT          |                                                                   | Detailed subtype (e.g., 'qualified_dividend',             | Fidelity statements (description parsing), 1099s (box types) |
|                           |               |                                                                   | 'municipal_interest', 'management_fee')                   |  |
| `description` *R          | TEXT          | NOT NULL                                                          | Transaction description from source document              | Fidelity statements (Description column), QuickBooks exports (Memo field) |
| `amount` *R               | NUMERIC(15,2) | NOT NULL CHECK (amount != 0)                                      | Transaction amount                                        | Fidelity statements (Amount column), 1099s (Box amounts), Trade confirmations (Net Amount) |
| **Security Information**  |               |                                                                   |                                                           |
| `security_name`           | TEXT          |                                                                   | Security name/description                                 | Fidelity statements (Security Name column) |
| `security_identifier`     | TEXT          |                                                                   | Symbol or CUSIP identifier                                | Fidelity statements (Symbol/CUSIP column) |
| `quantity`                | NUMERIC(15,6) |                                                                   | Number of shares/units in transaction                     | Fidelity statements (Quantity column) |
| `price_per_unit`          | NUMERIC(12,4) |                                                                   | Price per share/unit                                      | Fidelity statements (Price column) |
| `cost_basis`              | NUMERIC(15,2) |                                                                   | Total cost basis for this transaction                     | Fidelity statements (Total Cost Basis column) |
| `fees`                    | NUMERIC(10,2) |                                                                   | Transaction fees/costs                                    | Fidelity statements (Transaction Cost column) |
| `security_type`           | TEXT          | CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf',   | Type of security involved                                 |
|                           |               | 'money_market', 'cd', 'option', 'other'))                         |                                                           |
| `option_details`          | JSONB         |                                                                   | Options data: {"type": "PUT/CALL", "strike": 150,         |
|                           |               |                                                                   | "expiry": "2025-09-15", "underlying": "AAPL"}             |
| `bond_details`            | JSONB         |                                                                   | Bond data: {"accrued_interest": 200, "coupon_rate": 5.0,  |
|                           |               |                                                                   | "maturity": "2030-01-01", "call_date": "2025-09-30"}      |
| `source` *R               | TEXT          | NOT NULL CHECK (source IN ('statement','qb_export','ledger'))     | Origin of the transaction data                            |
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

**Foreign Key Constraints:**
- `entity_id` → `entities(id)` ON DELETE RESTRICT
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT
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
| cusip                             | cusip                | CUSIP                   | TEXT          |                                                     |
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
