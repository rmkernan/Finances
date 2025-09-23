# Clean Database Migration - Financial Data Management System

**Created:** 09/23/25 11:35AM ET
**Purpose:** Minimal migration implementing only the schema requirements - no speculative indexes
**Status:** Ready for execution on blank database

## Overview

This migration creates only what's specified in the schema document:
- 8 Phase 1 tables with required columns
- Required constraints (UNIQUE, CHECK, NOT NULL)
- Foreign key relationships
- Automatic timestamp triggers
- PostgreSQL comments for documentation

**NO SPECULATIVE INDEXES** - Add only when proven necessary by actual query performance.

## Execution Instructions

1. Connect to database: `psql postgresql://postgres:postgres@127.0.0.1:54322/postgres`
2. Wipe existing data: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`
3. Run this migration script
4. Verify with provided queries

---

## SQL Migration Script

```sql
-- ============================================
-- PHASE 1: CORE TABLES
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

-- Table: transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    transaction_date DATE,
    settlement_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('dividend', 'interest', 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee', 'return_of_capital', 'assignment', 'redemption', 'reinvest', 'option_buy', 'option_sell', 'other')),
    transaction_subtype TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
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
    reference_number TEXT,
    payee TEXT,
    payee_account TEXT,
    ytd_amount NUMERIC(15,2),
    balance NUMERIC(15,2),
    account_type TEXT,
    tax_category TEXT CHECK (tax_category IN ('ordinary_dividend', 'qualified_dividend', 'municipal_interest', 'corporate_interest', 'capital_gain_short', 'capital_gain_long', 'return_of_capital', 'tax_exempt', 'fee_expense', 'other')),
    federal_taxable BOOLEAN,
    state_taxable BOOLEAN,
    tax_details JSONB,
    source_transaction_id TEXT,
    source_reference TEXT,
    related_transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    is_duplicate_of UUID REFERENCES transactions(id) ON DELETE SET NULL,
    duplicate_reason TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
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
    sec_ticker TEXT,
    cusip TEXT,
    sec_name TEXT NOT NULL,
    sec_type TEXT NOT NULL,
    sec_subtype TEXT,
    beg_market_value NUMERIC(15,2),
    quantity NUMERIC(15,6) NOT NULL,
    price NUMERIC(12,4) NOT NULL,
    end_market_value NUMERIC(15,2) NOT NULL,
    cost_basis NUMERIC(15,2),
    unrealized_gain_loss NUMERIC(15,2),
    estimated_ann_inc NUMERIC(15,2),
    est_yield NUMERIC(5,4) CHECK (est_yield >= 0),
    underlying_symbol TEXT,
    strike_price NUMERIC(12,4),
    exp_date DATE,
    option_type TEXT CHECK (option_type IN ('CALL','PUT')),
    maturity_date DATE,
    coupon_rate NUMERIC(5,3),
    accrued_int NUMERIC(15,2),
    agency_rating TEXT,
    next_call DATE,
    call_price NUMERIC(12,4),
    payment_freq TEXT,
    bond_features TEXT,
    is_margin BOOLEAN DEFAULT FALSE,
    is_short BOOLEAN DEFAULT FALSE,
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
    net_acct_value NUMERIC(15,2),
    beg_value NUMERIC(15,2),
    end_value NUMERIC(15,2),
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
    tax_exempt_total_period NUMERIC(15,2),
    tax_exempt_total_ytd NUMERIC(15,2),
    divs_tax_exempt_period NUMERIC(15,2),
    divs_tax_exempt_ytd NUMERIC(15,2),
    int_tax_exempt_period NUMERIC(15,2),
    int_tax_exempt_ytd NUMERIC(15,2),
    roc_period NUMERIC(15,2),
    roc_ytd NUMERIC(15,2),
    grand_total_period NUMERIC(15,2),
    grand_total_ytd NUMERIC(15,2),
    st_gain_period NUMERIC(15,2),
    st_loss_period NUMERIC(15,2),
    lt_gain_ytd NUMERIC(15,2),
    lt_loss_ytd NUMERIC(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, account_id, doc_section)
);

-- ============================================
-- AUTOMATIC TIMESTAMP TRIGGERS
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
-- DOCUMENTATION COMMENTS
-- ============================================

-- Table comments
COMMENT ON TABLE entities IS 'Master table for business entities and individual taxpayers - central hub for multi-entity financial management';
COMMENT ON TABLE institutions IS 'Financial institutions holding accounts - supports multiple institutions per entity';
COMMENT ON TABLE accounts IS 'Individual financial accounts - UNIQUE constraint prevents duplicate account numbers within same institution';
COMMENT ON TABLE documents IS 'Financial documents with MD5 hash duplicate prevention - hash checked at staging and enforced by UNIQUE constraint';
COMMENT ON TABLE document_accounts IS 'Many-to-many link between documents and accounts - supports consolidated statements covering multiple accounts';
COMMENT ON TABLE transactions IS 'Individual financial transactions from all sources - statements, 1099s, QuickBooks exports';
COMMENT ON TABLE positions IS 'Point-in-time holdings snapshots from statements - UNIQUE constraint prevents duplicate positions';
COMMENT ON TABLE doc_level_data IS 'IMPORTANT: Derived/cached summary data from documents - NOT source of truth, can be recalculated from transactions';

-- Critical column comments
COMMENT ON COLUMN entities.tax_id IS 'EIN for entities, SSN for individuals - store encrypted/hashed';
COMMENT ON COLUMN entities.tax_id_display IS 'Last 4 digits only for UI display (e.g. ***-**-1234)';
COMMENT ON COLUMN entities.georgia_resident IS 'True if Georgia resident for state tax purposes';
COMMENT ON COLUMN accounts.account_number IS 'Full account number - should be encrypted/masked in production';
COMMENT ON COLUMN accounts.account_number_display IS 'Last 4 digits for UI display (e.g. ****1234)';
COMMENT ON COLUMN accounts.is_tax_deferred IS 'True for traditional IRAs, 401ks - taxes paid on withdrawal';
COMMENT ON COLUMN accounts.is_tax_free IS 'True for Roth accounts - no taxes on qualified withdrawals';
COMMENT ON COLUMN documents.doc_md5_hash IS 'MD5 hash (NOT SHA-256) for duplicate detection - UNIQUE constraint prevents duplicates';
COMMENT ON COLUMN documents.is_archived IS 'Soft delete flag - true means hidden from normal queries but retained for audit';
COMMENT ON COLUMN transactions.amount IS 'Transaction amount - can be zero for stock splits or position adjustments';
COMMENT ON COLUMN transactions.source IS 'Origin of data - no CHECK constraint to allow flexibility';
COMMENT ON COLUMN transactions.bond_state IS 'State for municipal bonds - important for Georgia tax exemption';
COMMENT ON COLUMN transactions.dividend_qualified IS 'True for qualified dividends (lower tax rate), false for ordinary';
COMMENT ON COLUMN transactions.related_transaction_id IS 'Links related transactions - wash sales, corrections, reversals';
COMMENT ON COLUMN transactions.is_archived IS 'Soft delete flag for old transactions - retained for audit';
```

## Verification Queries

After migration, run these to verify success:

```sql
-- List all tables (should show 8)
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify UNIQUE constraints exist
SELECT con.conname, tab.relname FROM pg_constraint con
JOIN pg_class tab ON con.conrelid = tab.oid
WHERE con.contype = 'u' ORDER BY tab.relname;

-- Test a basic insert
INSERT INTO entities (entity_name, entity_type, tax_id)
VALUES ('Test Entity', 'individual', 'TEST-123')
RETURNING id, entity_name;

-- Clean up test
DELETE FROM entities WHERE entity_name = 'Test Entity';
```

---

## What This Migration Does NOT Include

- **No speculative indexes** - Add only when query performance proves need
- **No Phase 2 tables** - tax_payments, transfers, etc. (add later)
- **No optimization features** - Focus on correctness first

## Ready for Production

This creates exactly what the schema specifies:
- All required tables and columns
- All constraints for data integrity
- All foreign key relationships
- Automatic timestamp management
- Self-documenting via comments

Add indexes later based on actual query patterns and performance measurements.