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
**Updated:** 09/23/25 7:43PM - Added comprehensive duplicate detection with JSON hash tracking and source file audit trail
**Updated:** 09/23/25 8:00PM - Updated data types to match applied database migration (VARCHAR constraints for new columns)
**Updated:** 09/23/25 8:15PM - Removed extraction columns from documents, added source_json_hash to transactions/positions tables
**Updated:** 09/23/25 10:07PM - Renamed positions columns to match JSON: agency_rating→agency_ratings, next_call→next_call_date
**Updated:** 09/24/25 9:50AM - Added three-table mapping system (map_rules, map_conditions, map_actions) with CSV management workflow
**Updated:** 09/24/25 11:52AM - Updated JSON metadata column names: source_json_hash→json_output_md5_hash, added json_output_id column to documents table
**Updated:** 09/24/25 2:26PM - Added incremental JSON loading support: activities_loaded, activities_json_md5_hash, positions_loaded, positions_json_md5_hash columns to documents table
**Updated:** 09/24/25 2:43PM - Removed deprecated json_output_id and json_output_md5_hash columns from documents table (superseded by incremental loading columns)
**Updated:** 09/24/25 3:26PM - Completed three-table mapping system migration: deprecated data_mappings table, loader now uses map_rules/map_conditions/map_actions exclusively
**Updated:** 09/25/25 10:40PM - MAJOR: Simplified rule structure from 5 levels to 2 levels: Transaction Classification (Level 1) and Security Classification (Level 2)
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

4. Database Insert with Incremental Loading Support
   - Documents table: Insert with doc_md5_hash (UNIQUE constraint prevents PDF duplicates)
   - Check if document already exists (same PDF hash)
   - If new: Create document record, proceed with data loading
   - If exists: Check JSON hash for specific data type (activities/positions)
     - If JSON hash matches: Skip loading (duplicate JSON content)
     - If JSON hash differs: Warn and proceed (reprocessing scenario)
     - If data type not yet loaded: Proceed with incremental loading
   - Update appropriate timestamp (activities_loaded/positions_loaded) and JSON hash
   - Document_accounts: Link to relevant accounts
   - Load data: Positions and/or Transactions based on extraction type

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

| Column (*R = Req)  | Data Type   | Constraints                                                      | Purpose/Source                        |
|--------------------|-------------|------------------------------------------------------------------|---------------------------------------|
| `id`               | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()                            | Auto-generated unique identifier      |
| `entity_name` *R   | TEXT        | NOT NULL                                                         | Legal entity name                     |
| `entity_type` *R   | TEXT        | NOT NULL                                                         | IRS entity classification             |
| `tax_id` *R        | TEXT        | NOT NULL UNIQUE                                                  | EIN for entities, SSN for individuals |
|                    |             |                                                                  | (encrypted/hashed)                    |
| `tax_id_display`   | TEXT        |                                                                  | Last 4 digits for display purposes    |
|                    |             |                                                                  | (e.g., "***-**-1234")                 |
| `primary_taxpayer` | TEXT        |                                                                  | Primary responsible party name        |
| `tax_year_end`     | TEXT        | DEFAULT '12-31'                                                  | Tax year end (MM-DD)                  |
| `georgia_resident` | BOOLEAN     | DEFAULT TRUE                                                     | Georgia state tax residency status    |
| `entity_status`    | TEXT        | DEFAULT 'active' CHECK (entity_status IN ('active', 'inactive')) | Current operational status            |
| `formation_date`   | DATE        |                                                                  | Entity formation/birth date           |
| `notes`            | TEXT        |                                                                  | Claude context notes                  |
| `created_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                    | Record creation timestamp             |
| `updated_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                    | Last modification timestamp           |
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

| Column (*R = Req)     | Data Type   | Constraints                                  | Purpose/Source                      |
|-----------------------|-------------|----------------------------------------------|-------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()        | Auto-generated unique identifier    |
| `institution_name` *R | TEXT        | NOT NULL                                     | Institution name (e.g., "Fidelity") |
| `institution_type`    | TEXT        |                                              | Type of financial institution       |
| `status`              | TEXT        | DEFAULT 'active' CHECK (status IN ('active', | Current relationship status         |
|                       |             | 'inactive', 'closed'))                       |                                     |
| `notes`               | TEXT        |                                              | Claude context notes for            |
| `created_at`          | TIMESTAMPTZ | DEFAULT NOW()                                | Record creation timestamp           |
| `updated_at`          | TIMESTAMPTZ | DEFAULT NOW()                                | Last modification timestamp         |
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

| Column (*R = Req)        | Data Type   | Constraints                             | Purpose/Source                                          |
|--------------------------|-------------|-----------------------------------------|---------------------------------------------------------|
| `id`                     | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid()   | Auto-generated unique identifier                        |
| `entity_id` *R           | UUID (FK)   | NOT NULL REF's entities(id)             | Entity that owns this account                           |
| `institution_id` *R      | UUID (FK)   | NOT NULL REF's institutions(id)         | Institution holding this account                        |
| `account_number` *R      | TEXT        | NOT NULL                                | Account number (encrypted/masked for security)          |
| `account_number_display` | TEXT        |                                         | Last 4 digits for display (e.g., "****1234")            |
| `account_holder_name`    | TEXT        |                                         | Name of the account holder                              |
| `account_name`           | TEXT        |                                         | Account nickname/description                            |
| `account_type` *R        | TEXT        | NOT NULL                                | Account classification                                  |
| `account_subtype`        | TEXT        |                                         | Specific subtype (e.g., "traditional_ira",              |
|                          |             |                                         | "roth_401k", "taxable_brokerage")                       |
| `institution_name`       | TEXT        |                                         | Institution name (derived from institutions table)      |
| `account_opening_date`   | DATE        |                                         | When account was opened                                 |
| `account_status`         | TEXT        | DEFAULT 'active'                        | Current account status                                  |
| `is_tax_deferred`        | BOOLEAN     | DEFAULT FALSE                           | True for IRAs, 401ks, and other tax-deferred accounts   |
| `is_tax_free`            | BOOLEAN     | DEFAULT FALSE                           | True for Roth accounts and tax-free investments         |
| `requires_rmd`           | BOOLEAN     | DEFAULT FALSE                           | True if account requires Required Minimum Distributions |
| `notes`                  | TEXT        |                                         | Claude context notes for account-specific handling      |
| `created_at`             | TIMESTAMPTZ | DEFAULT NOW()                           | Record creation timestamp                               |
| `updated_at`             | TIMESTAMPTZ | DEFAULT NOW()                           | Last modification timestamp                             |
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

### Three-Table Mapping System

**Purpose:** User-editable rule-based system for automatic transaction classification. 

#### Table: map_rules

**Purpose:** Master rule definitions with business context and processing order.

| Column (*R = Req)     | Data Type   | Constraints                           | Purpose/Source                                        |
|-----------------------|-------------|---------------------------------------|-------------------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid() | Auto-generated unique identifier                      |
| `rule_name` *R        | TEXT        | NOT NULL                              | Human-readable rule name (e.g., "Muni Bond Interest") |
| `application_order` *R| INTEGER     | NOT NULL                              | Processing sequence (1=first, 5=last)                 |
| `rule_category` *R    | TEXT        | NOT NULL                              | Rule grouping (e.g., "Options Lifecycle")             |
| `problem_solved`      | TEXT        |                                       | Business justification for the rule                   |
| `created_at`          | TIMESTAMPTZ | DEFAULT NOW()                         | Record creation timestamp                             |
| `updated_at`          | TIMESTAMPTZ | DEFAULT NOW()                         | Last modification timestamp                           |

#### Table: map_conditions

**Purpose:** Trigger conditions for classification rules (IF logic with compound conditions).

| Column (*R = Req)     | Data Type   | Constraints                           | Purpose/Source                                    |
|-----------------------|-------------|---------------------------------------|---------------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid() | Auto-generated unique identifier                  |
| `rule_id` *R          | UUID (FK)   | NOT NULL REF's map_rules(id)          | Link to parent rule                 |
| `check_field` *R      | TEXT        | NOT NULL                              | Field to examine (e.g., "activities.description") |
| `match_operator` *R   | TEXT        | NOT NULL                              | Comparison operator ("contains", "equals")        |
| `match_value` *R      | TEXT        | NOT NULL                              | Value to match against                            |
| `logic_connector`     | TEXT        | DEFAULT 'AND'                         | Connector for multiple conditions ("AND", "OR")   |

#### Table: map_actions

**Purpose:** Actions taken when rules match (SET logic with multiple field updates).

| Column (*R = Req)     | Data Type   | Constraints                           | Purpose/Source                            |
|-----------------------|-------------|---------------------------------------|-------------------------------------------|
| `id`                  | UUID (PK)   | PRIMARY KEY DEFAULT gen_random_uuid() | Auto-generated unique identifier          |
| `rule_id` *R          | UUID (FK)   | NOT NULL REF's map_rules(id)          | Link to parent rule                       |
| `set_field` *R        | TEXT        | NOT NULL                              | Field to update (e.g., "activities.type") |
| `set_value` *R        | TEXT        | NOT NULL                              | Value to set                              |

### Human-Readable View

**Purpose:** Formats the three-table system into business-friendly IF-THEN rules.

```sql
CREATE VIEW mapping_rules_readable AS
SELECT
    r.rule_name,
    STRING_AGG(
        c.check_field || ' ' || c.match_operator || ' "' || c.match_value || '"',
        ' ' || c.logic_connector || ' '
        ORDER BY c.id
    ) as triggers,
    STRING_AGG(
        'SET ' || a.set_field || ' = "' || a.set_value || '"',
        '; '
        ORDER BY a.id
    ) as actions,
    r.problem_solved
FROM map_rules r
LEFT JOIN map_conditions c ON r.id = c.rule_id
LEFT JOIN map_actions a ON r.id = a.rule_id
GROUP BY r.id, r.rule_name, r.problem_solved
ORDER BY r.application_order;
```

### CSV Rule Management Workflow

**User-Friendly Editing Process:**

1. **CSV File:** `/config/mapping-rules.csv` - Human-readable format with columns:
   - Rule Name, Triggers, Actions, Problem Solved

2. **Excel Integration:**
   - User opens CSV in Excel for visual editing with formatting
   - Compound conditions: Use "AND"/"OR" (e.g., `activities.description contains "Muni Exempt Int" AND activities.section equals "dividends_interest_income"`)
   - Multiple actions: Separate with semicolons (e.g., `SET activities.type = "interest"; SET activities.subtype = "muni_exempt"`)

3. **Bulk Updates:**
   - User saves changes in Excel (keeps CSV format)
   - Claude reads updated CSV and parses into three database tables
   - Changes immediately apply to new transaction processing

4. **Real-time Classification:** Updated rules automatically apply to all future document processing

**Example CSV Format:**
```csv
Rule Name,Triggers,Actions,Problem Solved
"Muni Bond Interest","activities.description contains ""Muni Exempt Int"" AND activities.section equals ""dividends_interest_income""","SET activities.type = ""interest""; SET activities.subtype = ""muni_exempt""","Municipal bonds in dividend section were taxed as dividends instead of tax-free interest"
"Opening Options Transaction","activities.description contains ""OPENING TRANSACTION""","SET activities.subtype = ""opening_transaction""","Options trades were classified as generic trades, preventing P&L matching"
```

### Rule Processing Logic

**SIMPLIFIED 2-LEVEL STRUCTURE** (as of 09/25/25):

Rules are applied in `application_order` sequence:

**Level 1: Transaction Classification** (application_order = 1)
- 18 rules that determine the primary transaction type and subtypes
- Includes: Options transactions, dividends, interest, deposits, withdrawals, transfers, core fund activity
- These rules set `transaction_type`, `transaction_subtype`, and sometimes `sec_class`
- **Foundation rules** - won't be overwritten by Level 2

**Level 2: Security Classification** (application_order = 2)
- 10 rules that identify security types for investment analysis
- Includes: Stock, Bond, ETF, Mutual Fund, REIT, Warrant, Options identification
- These rules primarily set `sec_class` as a fallback when Level 1 doesn't specify it
- **Fallback rules** - only apply if Level 1 didn't already classify the security

**Key Improvements in Simplified Structure:**
- Eliminated unnecessary complexity of 6 application levels
- Clear separation between transaction logic vs security classification
- Level 1 rules are foundational and won't be overwritten
- Level 2 provides security analysis without disrupting transaction classification
- Fixed "Return Of Capital" case sensitivity issue (now matches "Return Of Capital" not "Return of Capital")

**Cross-Table Support:** Ready for future triggers on `positions.security_type`, `accounts.account_type`, etc.

**Key Benefits:**
- **No code changes** needed to add new transaction patterns
- **User-controlled** classification rules via Excel interface
- **Consistent results** across all transaction processing
- **Audit trail** with business justification for each rule
- **Compound conditions** support complex matching scenarios
- **Multiple actions** per rule for comprehensive field updates


---

## Document and Transaction Tables

### Table: documents 

**Purpose:** Stores document metadata and extraction results with enhanced multi-entity support and processing audit trail. Documents are globally unique by file, issued by exactly one institution, and link to one or more accounts via a join table. Each document is associated with a specific tax year.

| Column (*R = Req)          | Data Type    | Constraints                             | Purpose/Source                                   |
|----------------------------|--------------|-----------------------------------------|--------------------------------------------------|
| `id`                       | UUID (PK)    | PRIMARY KEY DEFAULT gen_random_uuid()   | Auto-generated unique identifier                 |
| `institution_id` *R        | UUID (FK)    | NOT NULL REF'S institutions(id)         | Institution that issued document                 |
| `tax_year` *R              | INTEGER      | NOT NULL                                |                                                  |
| **Document Details**       |              |                                         |                                                  |
| `document_type` *R         | TEXT         | NOT NULL CHECK                          | Primary document classification                  |
| `period_start`             | DATE         |                                         | Reporting period start date                      |
| `period_end`               | DATE         |                                         | Reporting period end date                        |
| **File Management**        |              |                                         |                                                  |
| `file_path` *R             | TEXT         | NOT NULL                                | Full path to stored document file                |
| `file_name` *R             | TEXT         | NOT NULL                                | Original filename for reference                  |
| `file_size`                | INTEGER      |                                         | File size in bytes                               |
| `doc_md5_hash` *R          | TEXT         | NOT NULL UNIQUE                         | MD5 hash for duplicate detection (global unique) |
| `mime_type`                | TEXT         | DEFAULT 'application/pdf'               | File MIME type                                   |
| **Amendment Tracking**     |              |                                         |                                                  |
| `is_amended`               | BOOLEAN      | DEFAULT FALSE                           | True if this document has been amended/corrected |
| `amends_document_id`       | UUID (FK)    | REF's documents(id) ON DELETE SET NULL  | Original document this amends                    |
| `version_number`           | INTEGER      | DEFAULT 1                               | Version number for amended documents             |
| **Portfolio Summary**      |              |                                         |                                                  |
| `portfolio_value`          | NUMERIC(8,2) |                                         | Total portfolio value at statement date          |
| `portfolio_value_with_ai`  | NUMERIC(8,2) |                                         | Portfolio value including accrued interest       |
| `portfolio_change_period`  | NUMERIC(8,2) |                                         | Change in portfolio value for the period         |
| `portfolio_change_ytd`     | NUMERIC(8,2) |                                         | Year-to-date portfolio change                    |
| **Processing Metadata**    |              |                                         |                                                  |
| `processed_at`             | TIMESTAMPTZ  |                                         | When document processing completed               |
| `processed_by`             | TEXT         | DEFAULT 'claude'                        | Processing agent identifier                      |
| `extraction_notes`         | TEXT         |                                         | Claude's notes about the extraction              |
| `extraction_json_path`     | TEXT         |                                         | Path to JSON file with full extraction data      |
| **Incremental Loading**    |              |                                         |                                                  |
| `activities_loaded`        | TIMESTAMPTZ  |                                         | when activities/transactions were loaded         |
| `activities_json_md5_hash` | VARCHAR(32)  |                                         | MD5 hash  for duplicate prevention               |
| `positions_loaded`         | TIMESTAMPTZ  |                                         | when holdings/positions were loaded              |
| `positions_json_md5_hash`  | VARCHAR(32)  |                                         | MD5 hash for duplicate prevention                |
| **Archival Support**       |              |                                         |                                                  |
| `is_archived`              | BOOLEAN      | DEFAULT FALSE                           | True if document is archived (soft delete)       |
| **Audit Trail**            |              |                                         |                                                  |
| `created_at`               | TIMESTAMPTZ  | DEFAULT NOW()                           | Record creation timestamp                        |
| `updated_at`               | TIMESTAMPTZ  | DEFAULT NOW()                           | Last modification timestamp                      |
| `imported_at`              | TIMESTAMPTZ  | DEFAULT NOW()                           | When document was first imported                 |
| `Comment`                  |              |                                         |                                                  |

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

| Column (*R = Req)   | Data Type   | Constraints                                    | Purpose/Source          |
|---------------------|-------------|------------------------------------------------|-------------------------|
| `document_id` *R    | UUID (FK)   | NOT NULL REF's documents(id) ON DELETE CASCADE | Linked document         |
| `account_id` *R     | UUID (FK)   | NOT NULL REF's accounts(id) ON DELETE RESTRICT | Linked account          |
| `created_at`        | TIMESTAMPTZ | DEFAULT NOW()                                  | Link creation timestamp |
| `Comment`           |             |                                                |                         |
|---------------------|-------------|------------------------------------------------|-------------------------|
| FK to documents table | FK to accounts table | Link creation timestamp |

**Constraints:**
- UNIQUE constraint on (document_id, account_id)

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT

---

### Table: transactions (Enhanced)

**Purpose:** Individual financial transactions extracted from documents, with enhanced multi-entity support and comprehensive tax categorization.

| Column (*R = Req)              | Data Type     | Constraints                                                       | Purpose/Source                                           |
|--------------------------------|---------------|-------------------------------------------------------------------|----------------------------------------------------------|
| `id`                           | UUID (PK)     | PRIMARY KEY DEFAULT gen_random_uuid()                             | Auto-generated unique identifier                         |
| `entity_id` *R                 | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT               | Entity this transaction belongs to                       |
| `document_id` *R               | UUID (FK)     | NOT NULL REF's documents(id) ON DELETE CASCADE               | Source document for audit trail                          |
| `account_id` *R                | UUID (FK)     | NOT NULL REF's accounts(id) ON DELETE RESTRICT               | Account where transaction occurred                       |
| **Transaction Core Data**      |               |                                                                   |                                                          |
| `transaction_date`             | DATE          |                                                                   | Date transaction occurred (trade date)                   |
| `settlement_date`              | DATE          |                                                                   | Settlement/clearing date                                 |
| `transaction_type` *R          | TEXT          | NOT NULL                                                          | Transaction classification                               |
| `transaction_subtype`          | TEXT          |                                                                   | Detailed subtype (e.g., 'qualified_dividend',            |
|                                |               |                                                                   | 'municipal_interest', 'management_fee')                  |
| `description` *R               | TEXT          | NOT NULL                                                          | Transaction description from source document             |
| `amount` *R                    | NUMERIC(8,2)  | NOT NULL                                                          | Transaction amount                                       |
| **Security Information**       |               |                                                                   |                                                          |
| `security_name`                | TEXT          |                                                                   | Security name/description                                |
| `security_identifier`          | TEXT          |                                                                   | Symbol/ticker identifier                                 |
| `sec_cusip`                    | TEXT          |                                                                   | CUSIP identifier for bonds                               |
| `quantity`                     | NUMERIC(8,6)  |                                                                   | Number of shares/units in transaction                    |
| `price_per_unit`               | NUMERIC(12,4) |                                                                   | Price per share/unit                                     |
| `cost_basis`                   | NUMERIC(8,2)  |                                                                   |                                                          |
| `fees`                         | NUMERIC(4,2)  |                                                                   | Transaction fees/costs                                   |
| `security_type`                | TEXT          |                                                                   | Type of security involved                                |
| `option_type`                  | TEXT          |                                                                   | Type of option contract                                  |
| `strike_price`                 | DECIMAL(3)    |                                                                   | Option strike price                                      |
| `expiration_date`              | DATE          |                                                                   | Option expiration date                                   |
| `underlying_symbol`            | TEXT          |                                                                   | Underlying symbol for options                            |
| `option_details`               | JSONB         |                                                                   | Options data: {"type": "PUT/CALL", "strike": 150,        |
|                                |               |                                                                   | "expiry": "2025-09-15", "underlying": "AAPL"}            |
| `bond_state`                   | TEXT          |                                                                   | State for muni bonds (e.g., 'GA', 'NY')                  |
| `dividend_qualified`           | BOOLEAN       |                                                                   | True if qualified dividend, false if ordinary            |
| `bond_details`                 | JSONB         |                                                                   | Bond data: {"accrued_interest": 200, "coupon_rate": 5.0, |
|                                |               |                                                                   | "maturity": "2030-01-01", "call_date": "2025-09-30"}     |
| `sec_class`                    | TEXT          |                                                                   | Security classification (call, put, stock, bond, etc.)   |
| `source` *R                    | TEXT          | NOT NULL                                                          | Origin of the transaction data                           |
| **Additional Activity Fields** |               |                                                                   |                                                          |
| `reference_number`             | TEXT          |                                                                   | Wire reference or transaction ID                         |
| `payee`                        | TEXT          |                                                                   | Bill payment recipient                                   |
| `payee_account`                | TEXT          |                                                                   | Payee account number (masked)                            |
| `ytd_amount`                   | NUMERIC(8,2)  |                                                                   | Year-to-date amount for recurring payments               |
| `balance`                      | NUMERIC(8,2)  |                                                                   | Running balance after transaction                        |
| `account_type`                 | TEXT          |                                                                   | Account type for transaction (e.g., 'CASH', 'MARGIN')    |
| **Tax Categorization**         |               |                                                                   |                                                          |
| `tax_category`                 | TEXT          |                                                                 | Primary tax treatment                                    |
| `federal_taxable`              | BOOLEAN       |                                                                   | True if taxable for federal purposes                     |
| `state_taxable`                | BOOLEAN       |                                                                   | True if taxable for state purposes (GA-specific)         |
| `tax_details`                  | JSONB         |                                                                   | Additional tax context: {"issuer_state": "GA",           |
|                                |               |                                                                   | "amt_preference": false, "section_199a": true}           |
| **Source Tracking**            |               |                                                                   |                                                          |
| `source_transaction_id`        | TEXT          |                                                                   | Original transaction ID from source system               |
| `source_reference`             | TEXT          |                                                                   | Additional source reference (confirmation number, etc.)  |
| **Transaction Relations**      |               |                                                                   |                                                          |
| `related_transaction_id`       | UUID (FK)     | REF's transactions(id) ON DELETE SET NULL                    | Related transaction (wash sales, corrections, reversals) |
| **Duplicate Detection**        |               |                                                                   |                                                          |
| `is_duplicate_of`              | UUID (FK)     | REF's transactions(id) ON DELETE SET NULL                    | References original transaction if this is a duplicate   |
| `duplicate_reason`             | TEXT          |                                                                   | Explanation of why marked as duplicate                   |
| **Archival Support**           |               |                                                                   |                                                          |
| `is_archived`                  | BOOLEAN       | DEFAULT FALSE                                                     | True if transaction is archived (soft delete)            |
| **Audit Trail**                |               |                                                                   |                                                          |
| `created_at`                   | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Record creation timestamp                                |
| `updated_at`                   | TIMESTAMPTZ   | DEFAULT NOW()                                                     | Last modification timestamp                              |
| `processed_by`                 | TEXT          | DEFAULT 'claude'                                                  | Processing agent identifier                              |
| `source_file`                  | VARCHAR(255)  |                                                                   | JSON extraction filename that created this record        |

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

| DB Column                         | JSON Field           | Source Label            | Data Type     | Constraints                  |
|-----------------------------------|----------------------|-------------------------|---------------|------------------------------|
| **-- Metadata & Keys --**         |
| id                                | -                    | -                       | UUID          | PK gen_random_uuid()         |
| document_id                       | -                    | -                       | UUID          | NOT NULL REF's documents(id) |
| account_id                        | -                    | -                       | UUID          | NOT NULL REF's accounts(id)  |
| entity_id                         | -                    | -                       | UUID          | NOT NULL REF's entities(id)  |
| position_date                     | -                    | Statement Date          | DATE          | NOT NULL                     |
| account_number                    | account_number       | Account Number          | TEXT          | NOT NULL                     |
| **-- Security Identification --** |
| sec_ticker                        | sec_symbol           | Symbol/Ticker           | TEXT          |                              |
| cusip                             | sec_cusip            | CUSIP                   | TEXT          |                              |
| sec_name                          | sec_description      | Description             | TEXT          | NOT NULL                     |
| sec_type                          | sec_type             | Security Type           | TEXT          | NOT NULL                     |
| sec_subtype                       | sec_subtype          | Security Subtype        | TEXT          |                              |
| **-- Position Values --**         |
| beg_market_value                  | beg_market_value     | Beginning Market Value  | NUMERIC(8,2)  |                              |
| quantity                          | quantity             | Quantity                | NUMERIC(15,6) | NOT NULL                     |
| price                             | price_per_unit       | Price Per Unit          | NUMERIC(12,4) | NOT NULL                     |
| end_market_value                  | end_market_value     | Ending Market Value     | NUMERIC(8,2)  | NOT NULL                     |
| **-- Cost Basis & P&L --**        |
| cost_basis                        | cost_basis           | Total Cost Basis        | NUMERIC(8,2)  |                              |
| unrealized_gain_loss              | unrealized_gain_loss | Unrealized Gain/Loss    | NUMERIC(8,2)  |                              |
| **-- Income Estimates --**        |
| estimated_ann_inc                 | estimated_ann_inc    | Est Annual Income (EAI) | NUMERIC(8,2)  |                              |
| est_yield                         | est_yield            | Estimated Yield (EY)    | NUMERIC(5,4)  | CHECK (>= 0)                 |
| **-- Option-Specific --**         |
| underlying_symbol                 | underlying_symbol    | Underlying Symbol       | TEXT          |                              |
| strike_price                      | strike_price         | Strike Price            | NUMERIC(12,4) |                              |
| exp_date                          | expiration_date      | Expiration Date         | DATE          |                              |
| option_type                       | -                    | CALL/PUT                | TEXT          | CHECK (IN ('CALL','PUT'))    |
| **-- Bond-Specific --**           |
| maturity_date                     | maturity_date        | Maturity Date           | DATE          |                              |
| coupon_rate                       | coupon_rate          | Coupon Rate             | NUMERIC(5,3)  |                              |
| accrued_int                       | accrued_int          | Accrued Interest        | NUMERIC(8,2)  |                              |
| agency_ratings                    | agency_ratings       | Ratings                 | TEXT          |                              |
| next_call_date                    | next_call_date       | Next Call Date          | DATE          |                              |
| call_price                        | call_price           | Call Price              | NUMERIC(12,4) |                              |
| payment_freq                      | payment_freq         | Payment Frequency       | TEXT          |                              |
| bond_features                     | bond_features        | Bond Features           | TEXT          |                              |
| **-- Position Flags --**          |
| is_margin                         | -                    | -                       | BOOLEAN       | DEFAULT FALSE                |
| is_short                          | -                    | -                       | BOOLEAN       | DEFAULT FALSE                |
| **-- Audit Trail --**             |
| created_at                        | -                    | -                       | TIMESTAMPTZ   | DEFAULT NOW()                |
| updated_at                        | -                    | -                       | TIMESTAMPTZ   | DEFAULT NOW()                |
| source_file                       | -                    | -                       | VARCHAR(255)  | JSON extraction filename     |

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
| `entity_id` *R            | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT         | Entity making the tax payment                   |
| `account_id`              | UUID (FK)     | REF's accounts(id) ON DELETE RESTRICT                  | Account used for payment (if tracked)           |
| **Payment Details**       |               |                                                             |                                                 |
| `tax_year` *R             | INTEGER       | NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2030)      | Tax year payment applies to                     |
| `payment_type` *R         | TEXT          | NOT NULL CHECK (payment_type IN ('est_q1', 'est_q2',        | Type of tax payment                             |
|                           |               | 'estimated_q3', 'estimated_q4', 'extension', 'balance_due', |                                                 |
|                           |               | 'amended_return', 'penalty', 'interest'))                   |                                                 |
| `tax_authority` *R        | TEXT          | NOT NULL CHECK (tax_authority IN ('federal', 'georgia',     | Which government entity                         |
|                           |               | 'other_state'))                                             |                                                 |
| `payment_date` *R         | DATE          | NOT NULL                                                    | Date payment was made                           |
| `due_date`                | DATE          |                                                             | Original due date for payment                   |
| `amount` *R               | NUMERIC(8,2)  | NOT NULL CHECK (amount > 0)                                 | Payment amount                                  |
| **Calculation Details**   |               |                                                             |                                                 |
| `calculation_basis`       | JSONB         |                                                             | Calculation details: {"prior_year_tax": amount, |
|                           |               |                                                             | "current_year_estimate": amount, "method":      |
|                           |               |                                                             | "prior_year_safe_harbor"}                       |
| `estimated_income`        | NUMERIC(8,2) |                                                              | Estimated income for the year                   |
| `estimated_tax_liability` | NUMERIC(8,2) |                                                              | Estimated total tax liability                   |
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
| `source_entity_id` *R       | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT           | Entity sending money             |
| `source_account_id`         | UUID (FK)     | REF's accounts(id) ON DELETE RESTRICT                    | Source account (if tracked)      |
| **Destination Information** |               |                                                               |                                  |
| `destination_entity_id` *R  | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT           | Entity receiving money           |
| `destination_account_id`    | UUID (FK)     | REF's accounts(id) ON DELETE RESTRICT                    | Destination account (if tracked) |
| **Transfer Details**        |               |                                                               |                                  |
| `transfer_date` *R          | DATE          | NOT NULL                                                      | Date transfer occurred           |
| `amount` *R                 | NUMERIC(8,2) | NOT NULL CHECK (amount > 0)                                   | Transfer amount                   |
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
|-----------------------------|---------------|---------------------------------------------------------------|----------------------------------|
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
| `entity_id` *R               | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT        | Entity that owns the investment                        |
| `account_id`                 | UUID (FK)     | REF's accounts(id) ON DELETE RESTRICT                 | Specific account holding the security                  |
| **Security Identification**  |               |                                                            |                                                        |
| `symbol` *R                  | TEXT          | NOT NULL                                                   |.                 |
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
| `cost_basis`                 | NUMERIC(8,2) |                                                            | Total cost basis of position                           |
| `current_shares`             | NUMERIC(15,6) | CHECK (current_shares >= 0)                                | Current number of shares held                          |
| `unrealized_gain_loss`       | NUMERIC(8,2) |                                                            | Current unrealized gain/loss                           |
| `last_transaction_date`      | DATE          |                                                            | Date of last buy/sell transaction                      |
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
| `entity_id` *R      | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT  | Entity that owns this asset             |
| **Asset Details**   |               |                                                      |                                         |
| `asset_type` *R     | TEXT          | NOT NULL CHECK (asset_type IN ('primary_residence',  | Type of real asset                      |
|                     |               | 'rental_property', 'commercial_property', 'land',    |                                         |
|                     |               | 'vacation_home', 'vehicle', 'other'))                |                                         |
| `description` *R    | TEXT          | NOT NULL                                             | Asset description (e.g., "Address")     |
| `address`           | TEXT          |                                                      | Property address if applicable          |
| `purchase_date`     | DATE          |                                                      | When asset was acquired                 |
| `purchase_price`    | NUMERIC(8,2) |                                                      | Original purchase price                 |
| **Valuation**       |               |                                                      |                                         |
| `current_value` *R  | NUMERIC(8,2) | NOT NULL                                             | Current estimated value                 |
| `valuation_date` *R | DATE          | NOT NULL                                             | Date of current valuation               |
| `valuation_source`  | TEXT          |                                                      | Source of valuation (e.g. "Appraisal")  |
| **Income/Expense**  |               |                                                      |                                         |
| `monthly_income`    | NUMERIC(8,2) |                                                      | Rental income if applicable             |
| `monthly_expense`   | NUMERIC(8,2) |                                                      | Maintenance, HOA, insurance, taxes      |
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
| `entity_id` *R        | UUID (FK)     | NOT NULL REF's entities(id) ON DELETE RESTRICT      | Entity responsible for this liability |
| `real_asset_id`       | UUID (FK)     | REF's real_assets(id) ON DELETE SET NULL            | Linked asset (for mortgages)          |
| **Liability Details** |               |                                                          |                                       |
| `liability_type` *R   | TEXT          | NOT NULL CHECK (liability_type IN ('mortgage',           | Type of liability                     |
|                       |               | 'home_equity', 'auto_loan', 'business_loan',             |                                       |
|                       |               | 'personal_loan', 'other'))                               |                                       |
| `lender_name` *R      | TEXT          | NOT NULL                                                 | Name of lender/bank                   |
| `account_number`      | TEXT          |                                                          | Loan account number (masked)          |
| **Loan Terms**        |               |                                                          |                                       |
| `original_amount` *R  | NUMERIC(8,2) | NOT NULL                                                 | Original loan amount                  |
| `current_balance` *R  | NUMERIC(8,2) | NOT NULL                                                 | Current outstanding balance           |
| `interest_rate` *R    | NUMERIC(5,3)  | NOT NULL                                                 | Annual interest rate (e.g., 4.25%)    |
| `loan_start_date` *R  | DATE          | NOT NULL                                                 | When loan originated                  |
| `maturity_date`       | DATE          |                                                          | When loan will be paid off            |
| **Payment Info**      |               |                                                          |                                       |
| `monthly_payment` *R  | NUMERIC(8,2) | NOT NULL                                                 | Regular monthly payment amount        |
| `next_payment_date`   | DATE          |                                                          | Next payment due date                 |
| `escrow_amount`       | NUMERIC(8,2) |                                                          | Monthly escrow for taxes/insurance    |
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

| DB Column                          | JSON Field                  | Source Label                               | Data Type    | Constraints                 |
|------------------------------------|-----------------------------|--------------------------------------------|--------------|-----------------------------|
| **-- Metadata & Keys --**          |
| id (PK)                            | -                           | -                                          | UUID         | gen_random_uuid()           |
| document_id (req)                  | -                           | -                                          | UUID         | NOT NULL REF'S documents.id |
| account_id  (req)                  | -                           | -                                          | UUID         | REF's accounts(id)     |
| account_number (req)               | account_number              | Account Number                             | TEXT         | NOT NULL                    |
| doc_section                        | -                           | -                                          | TEXT         | NOT NULL                    |
| as_of_date                         | -                           | Statement Date                             | DATE         | NOT NULL                    |
| **-- Net Acct Value --**           |
| beg_net_acct_val_period (req)      | beg_net_acct_val_period     | Beginning Net Account Value (period)       | NUMERIC(8,2) |                             |
| beg_net_acct_val_ytd (req)         | beg_net_acct_val_ytd        | Beginning Net Account Value (YTD)          | NUMERIC(8,2) |                             |
| additions_period                   | additions_period            | Additions (period)                         | NUMERIC(8,2) |                             |
| additions_ytd                      | additions_ytd               | Additions (YTD)                            | NUMERIC(8,2) |                             |
| deposits_period                    | deposits_period             | Deposits (period)                          | NUMERIC(8,2) |                             |
| deposits_ytd                       | deposits_ytd                | Deposits (YTD)                             | NUMERIC(8,2) |                             |
| exchanges_in_period                | exchanges_in_period         | Exchanges In (period)                      | NUMERIC(8,2) |                             |
| exchanges_in_ytd                   | exchanges_in_ytd            | Exchanges In (YTD)                         | NUMERIC(8,2) |                             |
| subtractions_period                | subtractions_period         | Subtractions (period)                      | NUMERIC(8,2) |                             |
| subtractions_ytd                   | subtractions_ytd            | Subtractions (YTD)                         | NUMERIC(8,2) |                             |
| withdrawals_period                 | withdrawals_period          | Withdrawals (period)                       | NUMERIC(8,2) |                             |
| withdrawals_ytd                    | withdrawals_ytd             | Withdrawals (YTD)                          | NUMERIC(8,2) |                             |
| exchanges_out_period               | exchanges_out_period        | Exchanges Out (period)                     | NUMERIC(8,2) |                             |
| exchanges_out_ytd                  | exchanges_out_ytd           | Exchanges Out (YTD)                        | NUMERIC(8,2) |                             |
| transaction_costs_period           | transaction_costs_period    | Transaction Costs, Fees & Charges (period) | NUMERIC(8,2) |                             |
| transaction_costs_ytd              | transaction_costs_ytd       | Transaction Costs, Fees & Charges (YTD)    | NUMERIC(8,2) |                             |
| taxes_withheld_period              | taxes_withheld_period       | Taxes Withheld (period)                    | NUMERIC(8,2) |                             |
| taxes_withheld_ytd                 | taxes_withheld_ytd          | Taxes Withheld (YTD)                       | NUMERIC(8,2) |                             |
| change_in_inc_val_period  (req)    | change_in_inc_val_period    | Change in Investment Value (period)        | NUMERIC(8,2) |                             |
| change_in_inc_val_ytd              | change_in_inc_val_ytd       | Change in Investment Value (YTD)           | NUMERIC(8,2) |                             |
| ending_net_acct_val_period (req)   | ending_net_acct_val_period  | Ending Net Account Value (period)          | NUMERIC(8,2) |                             |
| ending_net_acct_val_ytd            | ending_net_acct_val_ytd     | Ending Net Account Value (YTD)             | NUMERIC(8,2) |                             |
| accrued_interest                   | accrued_interest            | Accrued Interest (AI)                      | NUMERIC(8,2) |                             |
| ending_net_acct_val_incl_ai        | ending_net_acct_val_incl_ai | Ending Net Account Value Incl AI           | NUMERIC(8,2) |                             |
| **Fid Acct Income Summary**        |
| taxable_total_period               | taxable_total_period        | Taxable Total (period)                     | NUMERIC(8,2) |                             |
| taxable_total_ytd                  | taxable_total_ytd           | Taxable Total (YTD)                        | NUMERIC(8,2) |                             |
| divs_taxable_period                | divs_taxable_period         | Taxable Dividends (period)                 | NUMERIC(8,2) |                             |
| divs_taxable_ytd                   | divs_taxable_ytd            | Taxable Dividends (YTD)                    | NUMERIC(8,2) |                             |
| stcg_taxable_period                | stcg_taxable_period         | Short-term Capital Gains (period)          | NUMERIC(8,2) |                             |
| stcg_taxable_ytd                   | stcg_taxable_ytd            | Short-term Capital Gains (YTD)             | NUMERIC(8,2) |                             |
| int_taxable_period                 | int_taxable_period          | Taxable Interest (period)                  | NUMERIC(8,2) |                             |
| int_taxable_ytd                    | int_taxable_ytd             | Taxable Interest (YTD)                     | NUMERIC(8,2) |                             |
| ltcg_taxable_period                | ltcg_taxable_period         | Long-term Capital Gains (period)           | NUMERIC(8,2) |                             |
| ltcg_taxable_ytd                   | ltcg_taxable_ytd            | Long-term Capital Gains (YTD)              | NUMERIC(8,2) |                             |
| tax_exempt_total_period            | tax_exempt_total_period     | Tax-exempt Total (period)                  | NUMERIC(8,2) |                             |
| tax_exempt_total_ytd               | tax_exempt_total_ytd        | Tax-exempt Total (YTD)                     | NUMERIC(8,2) |                             |
| divs_tax_exempt_period             | divs_tax_exempt_period      | Tax-exempt Dividends (period)              | NUMERIC(8,2) |                             |
| divs_tax_exempt_ytd                | divs_tax_exempt_ytd         | Tax-exempt Dividends (YTD)                 | NUMERIC(8,2) |                             |
| stcg_tax_ex_period                 | stcg_tax_ex_period          | Short-term Capital Gains (period)          | NUMERIC(8,2) |                             |
| stcg_tax_ex_ytd                    | stcg_tax_ex_ytd             | Short-term Capital Gains (YTD)             | NUMERIC(8,2) |                             |
| int_tax_exempt_period              | int_tax_exempt_period       | Tax-exempt Interest (period)               | NUMERIC(8,2) |                             |
| int_tax_exempt_ytd                 | int_tax_exempt_ytd          | Tax-exempt Interest (YTD)                  | NUMERIC(8,2) |                             |
| ltcg_tax_ex_period                 | ltcg_taxable_period         | Long-term Capital Gains (period)           | NUMERIC(8,2) |                             |
| ltcg_tax_ex_ytd                    | ltcg_taxable_ytd            | Long-term Capital Gains (YTD)              | NUMERIC(8,2) |                             |
| roc_period                         | roc_period                  | Return of Capital (period)                 | NUMERIC(8,2) |                             |
| roc_ytd                            | roc_ytd                     | Return of Capital (YTD)                    | NUMERIC(8,2) |                             |
| incsumm_total_period               | grand_total_period          | Grand Total (period)                       | NUMERIC(8,2) |                             |
| incsumm_total_ytd                  | grand_total_ytd             | Grand Total (YTD)                          | NUMERIC(8,2) |                             |
| **Realized Gains/Loss from Sales** |                             |                                            |              |                             |
| netstgl_period                     | st_gain_period              | Net Short-term Gain/Loss (period)          | NUMERIC(8,2) |                             |
| netstgl_ytd                        | st_gain_ytd                 | Net Short-term Gain/Loss (YTD)             | NUMERIC(8,2) |                             |
| stg_period                         | st_gain_period              | Short-term Gain (period)                   | NUMERIC(8,2) |                             |
| stg_ytd                            | st_gain_ytd                 | Short-term Gain (YTD)                      | NUMERIC(8,2) |                             |
| netltgl_period                     | lt_gain_period              | Net Long-term Gain/Loss (period)           | NUMERIC(8,2) |                             |
| netltgl_ytd                        | lt_gain_ytd                 | Net Long-term Gain/Loss (YTD)              | NUMERIC(8,2) |                             |
| ltg_period                         | lt_gain_period              | Long-term Gain (period)                    | NUMERIC(8,2) |                             |
| ltg_ytd                            | lt_gain_ytd                 | Long-term Gain (YTD)                       | NUMERIC(8,2) |                             |
| net_gl_period                      | net_gain_loss_period        | Net Gain/Loss (period)                     | NUMERIC(8,2) |                             |
| net_gl_ytd                         | net_gain_loss_ytd           | Net Gain/Loss (YTD)                        | NUMERIC(8,2) |                             |
| **-- Audit Trail --**              |
| created_at                         | -                           | -                                          | TIMESTAMPTZ  | DEFAULT NOW()               |
| updated_at                         | -                           | -                                          | TIMESTAMPTZ  | DEFAULT NOW()               |

**Unique Constraints:**
- UNIQUE(document_id, account_id, doc_section) - Prevents duplicate summary data for same document/account/section

**Foreign Key Constraints:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `account_id` → `accounts(id)` ON DELETE RESTRICT

**Important:** This table contains **transcribed data** pulled directly from PDF income summary and realized gains sections. On documents with multiple accounts, this data spans accounts and represents document-level totals as shown in the source PDF. We are NOT deriving or calculating this data - we are transcribing it exactly as it appears in the financial statements for audit trail and reconciliation purposes.
