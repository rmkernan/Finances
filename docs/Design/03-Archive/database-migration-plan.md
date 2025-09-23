# Database Migration Plan - Phase 1 Tables Only

**Created:** 2025-09-22
**Updated:** 09/22/25 9:08PM ET - Added UNIQUE constraints, removed restrictive CHECKs, added archival columns, improved types
**Purpose:** SQL commands to create the Phase 1 tables described in schema.md
**Status:** Ready for execution on blank Supabase database

## Overview

This plan creates only the tables and relationships needed for Phase 1 document processing:
- Core entity management (entities, institutions, accounts)
- Document tracking (documents, document_accounts)
- Transaction data (transactions, positions, doc_level_data)

Phase 2 tables (tax_payments, transfers, asset_notes, real_assets, liabilities) are excluded.

## Execution Order

Tables must be created in dependency order:

1. **entities** - No dependencies
2. **institutions** - Depends on entities
3. **accounts** - Depends on entities, institutions
4. **documents** - Depends on institutions
5. **document_accounts** - Depends on documents, accounts
6. **transactions** - Depends on entities, documents, accounts
7. **positions** - Depends on documents, accounts, entities
8. **doc_level_data** - Depends on documents, accounts

## SQL Migration Script

```sql
-- ============================================
-- PHASE 1: CORE ENTITY TABLES
-- ============================================

-- Table: entities
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('individual', 's_corp', 'llc', 'other')),
    tax_id TEXT NOT NULL UNIQUE,
    tax_id_display TEXT,
    primary_taxpayer TEXT,
    tax_year_end TEXT DEFAULT '12-31',
    georgia_resident BOOLEAN DEFAULT TRUE,
    entity_status TEXT DEFAULT 'active' CHECK (entity_status IN ('active', 'inactive')),
    formation_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: institutions
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    institution_name TEXT NOT NULL,
    institution_type TEXT CHECK (institution_type IN ('brokerage', 'bank', 'credit_union', 'insurance', 'retirement_plan', 'other')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'closed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT,
    account_number TEXT NOT NULL,
    account_number_display TEXT,
    account_holder_name TEXT,
    account_name TEXT,
    account_type TEXT NOT NULL CHECK (account_type IN ('checking', 'savings', 'brokerage', 'ira', '401k', 'roth_ira', 'trust', 'business', 'money_market', 'cd', 'hsa', 'cash_management')),
    account_subtype TEXT,
    account_opening_date DATE,
    account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'inactive', 'closed', 'transferred')),
    is_tax_deferred BOOLEAN DEFAULT FALSE,
    is_tax_free BOOLEAN DEFAULT FALSE,
    requires_rmd BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(institution_id, account_number)
);

-- ============================================
-- PHASE 1: DOCUMENT TABLES
-- ============================================

-- Table: documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT,
    tax_year INTEGER NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2035),
    document_type TEXT NOT NULL CHECK (document_type IN ('statement', '1099', 'quickbooks_export', 'bank_statement', 'tax_return', 'k1', 'receipt', 'invoice', 'other')),
    period_start DATE,
    period_end DATE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    doc_md5_hash TEXT NOT NULL UNIQUE,
    mime_type TEXT DEFAULT 'application/pdf',
    is_amended BOOLEAN DEFAULT FALSE,
    amends_document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    version_number INTEGER DEFAULT 1,
    portfolio_value NUMERIC(15,2),
    portfolio_value_with_ai NUMERIC(15,2),
    portfolio_change_period NUMERIC(15,2),
    portfolio_change_ytd NUMERIC(15,2),
    processed_at TIMESTAMPTZ,
    processed_by TEXT DEFAULT 'claude',
    extraction_notes TEXT,
    extraction_json_path TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: document_accounts (join table)
CREATE TABLE document_accounts (
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, account_id)
);

-- ============================================
-- PHASE 1: TRANSACTION TABLES
-- ============================================

-- Table: transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    -- Core transaction data
    transaction_date DATE,
    settlement_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('dividend', 'interest', 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee', 'return_of_capital', 'assignment', 'redemption', 'reinvest', 'option_buy', 'option_sell', 'other')),
    transaction_subtype TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    -- Security information
    security_name TEXT,
    security_identifier TEXT,
    sec_cusip TEXT,
    quantity NUMERIC(15,6),
    price_per_unit NUMERIC(12,4),
    cost_basis NUMERIC(15,2),
    fees NUMERIC(10,2),
    security_type TEXT CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf', 'money_market', 'cd', 'option', 'cash', 'other')),
    option_type TEXT CHECK (option_type IN ('CALL', 'PUT')),
    strike_price DECIMAL(15,2),
    expiration_date DATE,
    underlying_symbol TEXT,
    option_details JSONB,
    bond_state TEXT,
    dividend_qualified BOOLEAN,
    bond_details JSONB,
    source TEXT NOT NULL,
    -- Additional activity fields
    reference_number TEXT,
    payee TEXT,
    payee_account TEXT,
    ytd_amount NUMERIC(15,2),
    balance NUMERIC(15,2),
    account_type TEXT,
    -- Tax categorization
    tax_category TEXT CHECK (tax_category IN ('ordinary_dividend', 'qualified_dividend', 'municipal_interest', 'corporate_interest', 'capital_gain_short', 'capital_gain_long', 'return_of_capital', 'tax_exempt', 'fee_expense', 'other')),
    federal_taxable BOOLEAN,
    state_taxable BOOLEAN,
    tax_details JSONB,
    -- Source tracking
    source_transaction_id TEXT,
    source_reference TEXT,
    -- Transaction relations
    related_transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    -- Duplicate detection
    is_duplicate_of UUID REFERENCES transactions(id) ON DELETE SET NULL,
    duplicate_reason TEXT,
    -- Archival support
    is_archived BOOLEAN DEFAULT FALSE,
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_by TEXT DEFAULT 'claude'
);

-- Table: positions
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    position_date DATE NOT NULL,
    account_number TEXT NOT NULL,
    -- Security identification
    sec_ticker TEXT,
    cusip TEXT,
    sec_name TEXT NOT NULL,
    sec_type TEXT NOT NULL,
    sec_subtype TEXT,
    -- Position values
    beg_market_value NUMERIC(15,2),
    quantity NUMERIC(15,6) NOT NULL,
    price NUMERIC(12,4) NOT NULL,
    end_market_value NUMERIC(15,2) NOT NULL,
    -- Cost basis & P&L
    cost_basis NUMERIC(15,2),
    unrealized_gain_loss NUMERIC(15,2),
    -- Income estimates
    estimated_ann_inc NUMERIC(15,2),
    est_yield NUMERIC(5,4) CHECK (est_yield >= 0),
    -- Option-specific
    underlying_symbol TEXT,
    strike_price NUMERIC(12,4),
    exp_date DATE,
    option_type TEXT CHECK (option_type IN ('CALL','PUT')),
    -- Bond-specific
    maturity_date DATE,
    coupon_rate NUMERIC(5,3),
    accrued_int NUMERIC(15,2),
    agency_rating TEXT,
    next_call DATE,
    call_price NUMERIC(12,4),
    payment_freq TEXT,
    bond_features TEXT,
    -- Position flags
    is_margin BOOLEAN DEFAULT FALSE,
    is_short BOOLEAN DEFAULT FALSE,
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, account_id, position_date, sec_ticker, cusip)
);

-- Table: doc_level_data
CREATE TABLE doc_level_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,
    account_number TEXT NOT NULL,
    doc_section TEXT NOT NULL,
    as_of_date DATE NOT NULL,
    -- Account summary
    net_acct_value NUMERIC(15,2),
    beg_value NUMERIC(15,2),
    end_value NUMERIC(15,2),
    -- Income summary: Taxable
    taxable_total_period NUMERIC(15,2),
    taxable_total_ytd NUMERIC(15,2),
    divs_taxable_period NUMERIC(15,2),
    divs_taxable_ytd NUMERIC(15,2),
    stcg_taxable_period NUMERIC(15,2),
    stcg_taxable_ytd NUMERIC(15,2),
    int_taxable_period NUMERIC(15,2),
    int_taxable_ytd NUMERIC(15,2),
    ltcg_taxable_period NUMERIC(15,2),
    ltcg_taxable_ytd NUMERIC(15,2),
    -- Income summary: Tax exempt
    tax_exempt_total_period NUMERIC(15,2),
    tax_exempt_total_ytd NUMERIC(15,2),
    divs_tax_exempt_period NUMERIC(15,2),
    divs_tax_exempt_ytd NUMERIC(15,2),
    int_tax_exempt_period NUMERIC(15,2),
    int_tax_exempt_ytd NUMERIC(15,2),
    -- Income summary: Other
    roc_period NUMERIC(15,2),
    roc_ytd NUMERIC(15,2),
    grand_total_period NUMERIC(15,2),
    grand_total_ytd NUMERIC(15,2),
    -- Realized gains/losses
    st_gain_period NUMERIC(15,2),
    st_loss_period NUMERIC(15,2),
    lt_gain_ytd NUMERIC(15,2),
    lt_loss_ytd NUMERIC(15,2),
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, account_id, doc_section)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Entity indexes
CREATE INDEX idx_entities_tax_id ON entities(tax_id);
CREATE INDEX idx_entities_status ON entities(entity_status);

-- Institution indexes
CREATE INDEX idx_institutions_entity_id ON institutions(entity_id);
CREATE INDEX idx_institutions_name ON institutions(institution_name);

-- Account indexes
CREATE INDEX idx_accounts_entity_id ON accounts(entity_id);
CREATE INDEX idx_accounts_institution_id ON accounts(institution_id);
CREATE INDEX idx_accounts_number ON accounts(account_number);
CREATE INDEX idx_accounts_status ON accounts(account_status);

-- Document indexes
CREATE INDEX idx_documents_institution_id ON documents(institution_id);
CREATE INDEX idx_documents_tax_year ON documents(tax_year);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_file_hash ON documents(doc_md5_hash);
CREATE INDEX idx_documents_period_dates ON documents(period_start, period_end);

-- Document_accounts indexes
CREATE INDEX idx_document_accounts_document_id ON document_accounts(document_id);
CREATE INDEX idx_document_accounts_account_id ON document_accounts(account_id);

-- Transaction indexes
CREATE INDEX idx_transactions_entity_id ON transactions(entity_id);
CREATE INDEX idx_transactions_document_id ON transactions(document_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_security ON transactions(security_identifier);
CREATE INDEX idx_transactions_duplicate ON transactions(is_duplicate_of);

-- Positions indexes
CREATE INDEX idx_positions_document_id ON positions(document_id);
CREATE INDEX idx_positions_account_id ON positions(account_id);
CREATE INDEX idx_positions_entity_id ON positions(entity_id);
CREATE INDEX idx_positions_date ON positions(position_date);
CREATE INDEX idx_positions_ticker ON positions(sec_ticker);

-- Doc_level_data indexes
CREATE INDEX idx_doc_level_data_document_id ON doc_level_data(document_id);
CREATE INDEX idx_doc_level_data_account_id ON doc_level_data(account_id);
CREATE INDEX idx_doc_level_data_date ON doc_level_data(as_of_date);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_doc_level_data_updated_at BEFORE UPDATE ON doc_level_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- TABLE AND COLUMN COMMENTS FOR DOCUMENTATION
-- ============================================

-- Entities table comments
COMMENT ON TABLE entities IS 'Master table for business entities and individual taxpayers - central hub for multi-entity financial management';
COMMENT ON COLUMN entities.tax_id IS 'EIN for entities, SSN for individuals - store encrypted/hashed';
COMMENT ON COLUMN entities.tax_id_display IS 'Last 4 digits only for UI display (e.g. ***-**-1234)';
COMMENT ON COLUMN entities.georgia_resident IS 'True if Georgia resident for state tax purposes';
COMMENT ON COLUMN entities.notes IS 'Free-form notes for Claude context about this entity';

-- Institutions table comments
COMMENT ON TABLE institutions IS 'Financial institutions holding accounts - supports multiple institutions per entity';
COMMENT ON COLUMN institutions.institution_type IS 'Classification: brokerage, bank, credit_union, insurance, retirement_plan, other';
COMMENT ON COLUMN institutions.notes IS 'Institution-specific processing notes for Claude';

-- Accounts table comments
COMMENT ON TABLE accounts IS 'Individual financial accounts - UNIQUE constraint prevents duplicate account numbers within same institution';
COMMENT ON COLUMN accounts.account_number IS 'Full account number - should be encrypted/masked in production';
COMMENT ON COLUMN accounts.account_number_display IS 'Last 4 digits for UI display (e.g. ****1234)';
COMMENT ON COLUMN accounts.is_tax_deferred IS 'True for traditional IRAs, 401ks - taxes paid on withdrawal';
COMMENT ON COLUMN accounts.is_tax_free IS 'True for Roth accounts - no taxes on qualified withdrawals';
COMMENT ON COLUMN accounts.requires_rmd IS 'True if Required Minimum Distributions apply';

-- Documents table comments
COMMENT ON TABLE documents IS 'Financial documents with MD5 hash duplicate prevention - hash checked at staging and enforced by UNIQUE constraint';
COMMENT ON COLUMN documents.doc_md5_hash IS 'MD5 hash (NOT SHA-256) for duplicate detection - UNIQUE constraint prevents duplicates';
COMMENT ON COLUMN documents.is_archived IS 'Soft delete flag - true means hidden from normal queries but retained for audit';
COMMENT ON COLUMN documents.tax_year IS 'Tax year document pertains to - may differ from calendar year for fiscal year entities';
COMMENT ON COLUMN documents.amends_document_id IS 'Links to original document if this is a correction/amendment';
COMMENT ON COLUMN documents.extraction_json_path IS 'Path to JSON file containing full extraction data from Claude sub-agents';

-- Document_accounts table comments
COMMENT ON TABLE document_accounts IS 'Many-to-many link between documents and accounts - supports consolidated statements covering multiple accounts';
COMMENT ON COLUMN document_accounts.document_id IS 'Document containing information about the account';
COMMENT ON COLUMN document_accounts.account_id IS 'Account referenced in the document';

-- Transactions table comments
COMMENT ON TABLE transactions IS 'Individual financial transactions from all sources - statements, 1099s, QuickBooks exports';
COMMENT ON COLUMN transactions.transaction_date IS 'Trade date when transaction occurred - may be null for pending transactions';
COMMENT ON COLUMN transactions.settlement_date IS 'Settlement/clearing date - typically T+2 for securities';
COMMENT ON COLUMN transactions.amount IS 'Transaction amount - can be zero for stock splits or position adjustments';
COMMENT ON COLUMN transactions.security_type IS 'Includes cash as a type for money market sweeps';
COMMENT ON COLUMN transactions.source IS 'Origin of data - no CHECK constraint to allow flexibility';
COMMENT ON COLUMN transactions.bond_state IS 'State for municipal bonds - important for Georgia tax exemption';
COMMENT ON COLUMN transactions.dividend_qualified IS 'True for qualified dividends (lower tax rate), false for ordinary';
COMMENT ON COLUMN transactions.related_transaction_id IS 'Links related transactions - wash sales, corrections, reversals';
COMMENT ON COLUMN transactions.is_duplicate_of IS 'Points to original if this is detected as duplicate';
COMMENT ON COLUMN transactions.is_archived IS 'Soft delete flag for old transactions - retained for audit';
COMMENT ON COLUMN transactions.tax_category IS 'Primary tax treatment classification';
COMMENT ON COLUMN transactions.federal_taxable IS 'True if subject to federal income tax';
COMMENT ON COLUMN transactions.state_taxable IS 'True if subject to Georgia state tax';

-- Positions table comments
COMMENT ON TABLE positions IS 'Point-in-time holdings snapshots from statements - UNIQUE constraint prevents duplicate positions';
COMMENT ON COLUMN positions.position_date IS 'Statement date for this position snapshot';
COMMENT ON COLUMN positions.sec_ticker IS 'Trading symbol for stocks, ETFs, mutual funds';
COMMENT ON COLUMN positions.cusip IS 'CUSIP identifier - especially important for bonds';
COMMENT ON COLUMN positions.unrealized_gain_loss IS 'Current market value minus cost basis';
COMMENT ON COLUMN positions.estimated_ann_inc IS 'Estimated Annual Income from dividends/interest';
COMMENT ON COLUMN positions.est_yield IS 'Estimated yield percentage';
COMMENT ON COLUMN positions.is_margin IS 'True if position held in margin account';
COMMENT ON COLUMN positions.is_short IS 'True if short position';

-- Doc_level_data table comments
COMMENT ON TABLE doc_level_data IS 'IMPORTANT: Derived/cached summary data from documents - NOT source of truth, can be recalculated from transactions';
COMMENT ON COLUMN doc_level_data.doc_section IS 'Section identifier like income_summary or realized_gains';
COMMENT ON COLUMN doc_level_data.account_number IS 'Account this summary pertains to';
COMMENT ON COLUMN doc_level_data.taxable_total_period IS 'Total taxable income for statement period';
COMMENT ON COLUMN doc_level_data.taxable_total_ytd IS 'Year-to-date taxable income through statement date';
COMMENT ON COLUMN doc_level_data.tax_exempt_total_period IS 'Tax-exempt income (municipal bonds) for period';
COMMENT ON COLUMN doc_level_data.tax_exempt_total_ytd IS 'Year-to-date tax-exempt income';
COMMENT ON COLUMN doc_level_data.divs_taxable_period IS 'Taxable dividends (ordinary + qualified) for period';
COMMENT ON COLUMN doc_level_data.int_tax_exempt_period IS 'Tax-exempt interest (muni bonds) for period - Georgia exemption eligible';
```

## Execution Instructions

1. **Connect to Supabase:** Use the connection details from `supabase status`
2. **Run the script:** Execute the SQL commands in order using psql or Supabase Studio
3. **Verify creation:** Check that all 8 tables and their indexes exist

## Post-Migration Verification

Run these queries to verify the schema:

```sql
-- List all tables
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Expected result: 8 tables
-- accounts, doc_level_data, document_accounts, documents,
-- entities, institutions, positions, transactions

-- Check foreign key relationships
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;

-- Check indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

## Notes

- All UUID primary keys use `gen_random_uuid()` for automatic generation
- All tables include `created_at` and `updated_at` timestamps with automatic update triggers
- Foreign key constraints use appropriate CASCADE/RESTRICT rules based on business logic
- Check constraints enforce valid enum values for categorization fields
- Indexes are created on all foreign keys and commonly queried fields