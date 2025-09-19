-- Complete Database Schema for Financial Data Management System
-- Created: 01/18/25 3:30PM ET
-- Purpose: Fresh base migration incorporating all lessons learned from extraction testing

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE ENTITY TABLES
-- ============================================================================

-- Entities (S-Corps, LLCs, Individuals)
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('individual', 's_corp', 'llc', 'c_corp', 'partnership', 'trust')),
    tax_id TEXT UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE entities IS 'Master table for all business entities and individuals';
COMMENT ON COLUMN entities.tax_id IS 'EIN for businesses, SSN for individuals (encrypted)';

-- Financial Institutions
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    institution_type TEXT CHECK (institution_type IN ('brokerage', 'bank', 'credit_union', 'other')),
    routing_number TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE institutions IS 'Financial institutions (Fidelity, banks, etc.)';

-- Accounts linking entities to institutions
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT,
    account_number TEXT NOT NULL,
    account_holder_name TEXT,
    account_type TEXT CHECK (account_type IN ('checking', 'savings', 'brokerage', 'ira', 'roth_ira', '401k', 'credit_card', 'other')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(institution_id, account_number)
);

COMMENT ON TABLE accounts IS 'Financial accounts linking entities to institutions';
COMMENT ON COLUMN accounts.account_holder_name IS 'Full name(s) as shown on statements';

-- ============================================================================
-- DOCUMENT TRACKING
-- ============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_type TEXT NOT NULL CHECK (document_type IN ('statement', '1099', 'trade_confirm', 'other')),
    institution_id UUID REFERENCES institutions(id) ON DELETE RESTRICT,
    period_start DATE,
    period_end DATE,
    portfolio_value NUMERIC(15,2),
    file_name TEXT NOT NULL,
    file_hash TEXT UNIQUE,
    extraction_json_path TEXT,
    extraction_notes TEXT,
    amends_document_id UUID REFERENCES documents(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE documents IS 'Source documents with extraction metadata';
COMMENT ON COLUMN documents.extraction_json_path IS 'Path to JSON extraction file';
COMMENT ON COLUMN documents.amends_document_id IS 'Links to original document if this is an amendment';

-- Junction table for multi-account documents
CREATE TABLE document_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    UNIQUE(document_id, account_id)
);

COMMENT ON TABLE document_accounts IS 'Links documents to multiple accounts';

-- ============================================================================
-- FINANCIAL TRANSACTIONS
-- ============================================================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Core transaction data
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN (
        'dividend', 'interest', 'buy', 'sell',
        'transfer_in', 'transfer_out', 'fee',
        'return_of_capital', 'assignment',
        'redemption', 'reinvest',
        'option_buy', 'option_sell',
        'other'
    )),
    transaction_subtype TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount != 0),

    -- Security information
    security_name TEXT,
    security_identifier TEXT,
    quantity NUMERIC(15,6),
    price_per_unit NUMERIC(12,4),
    cost_basis NUMERIC(15,2),
    fees NUMERIC(10,2),
    security_type TEXT CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf', 'money_market', 'cd', 'option', 'other')),

    -- Complex instrument details
    option_details JSONB,
    bond_details JSONB,

    -- Source and tax categorization
    source TEXT NOT NULL CHECK (source IN ('statement', 'qb_export', 'ledger')),
    tax_category TEXT NOT NULL CHECK (tax_category IN (
        'ordinary_dividend', 'qualified_dividend',
        'municipal_interest', 'corporate_interest',
        'capital_gain_short', 'capital_gain_long',
        'return_of_capital', 'tax_exempt',
        'fee_expense', 'other'
    )),
    federal_taxable BOOLEAN NOT NULL,
    state_taxable BOOLEAN NOT NULL,
    tax_details JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE transactions IS 'All financial transactions';
COMMENT ON COLUMN transactions.option_details IS 'Options data: {"type": "PUT|CALL", "strike": 150.00, "expiry": "2025-09-15", "underlying": "AAPL", "contracts": 10}';
COMMENT ON COLUMN transactions.bond_details IS 'Bond data: {"accrued_interest": 200.00, "coupon_rate": 5.0, "maturity": "2030-01-01", "call_date": "2025-09-30", "cusip": "123456789"}';

-- ============================================================================
-- PORTFOLIO POSITIONS
-- ============================================================================

CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Position details
    as_of_date DATE NOT NULL,
    security_name TEXT NOT NULL,
    security_identifier TEXT,
    security_type TEXT CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf', 'money_market', 'cd', 'option', 'other')),

    -- Values and quantities
    quantity NUMERIC(15,6) NOT NULL,
    price NUMERIC(12,4),
    market_value NUMERIC(15,2),
    cost_basis NUMERIC(15,2),
    unrealized_gain_loss NUMERIC(15,2),

    -- Options-specific
    option_details JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(account_id, as_of_date, security_identifier)
);

COMMENT ON TABLE positions IS 'Portfolio holdings at specific points in time';
COMMENT ON COLUMN positions.option_details IS 'Options position: {"type": "PUT|CALL", "strike": 150.00, "expiry": "2025-09-15", "underlying": "AAPL", "contracts": 10}';

-- ============================================================================
-- INCOME TRACKING
-- ============================================================================

CREATE TABLE income_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Income breakdown
    taxable_income NUMERIC(12,2),
    tax_exempt_income NUMERIC(12,2),
    qualified_dividends NUMERIC(12,2),
    ordinary_dividends NUMERIC(12,2),
    interest_income NUMERIC(12,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(account_id, period_start, period_end)
);

COMMENT ON TABLE income_summaries IS 'Period income summaries from statements';

-- ============================================================================
-- TAX AND COMPLIANCE
-- ============================================================================

CREATE TABLE tax_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    tax_year INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    payment_type TEXT NOT NULL CHECK (payment_type IN ('estimated_federal', 'estimated_state', 'extension_federal', 'extension_state', 'final_federal', 'final_state', 'other')),
    amount NUMERIC(12,2) NOT NULL,
    check_number TEXT,
    confirmation_number TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tax_payments IS 'Track quarterly estimated and other tax payments';

-- ============================================================================
-- INTER-ENTITY TRANSFERS
-- ============================================================================

CREATE TABLE transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    to_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    from_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,
    to_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,
    transfer_date DATE NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    transfer_type TEXT CHECK (transfer_type IN ('distribution', 'contribution', 'loan', 'repayment', 'other')),
    description TEXT NOT NULL,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE transfers IS 'Track money movement between entities';

-- ============================================================================
-- INVESTMENT NOTES
-- ============================================================================

CREATE TABLE asset_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    security_identifier TEXT NOT NULL,
    security_name TEXT NOT NULL,
    note_date DATE NOT NULL DEFAULT CURRENT_DATE,
    note_type TEXT CHECK (note_type IN ('strategy', 'price_target', 'alert', 'review', 'other')),
    note_text TEXT NOT NULL,
    target_price NUMERIC(12,4),
    alert_price NUMERIC(12,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE asset_notes IS 'Investment strategy notes and price targets';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_transactions_entity_date ON transactions(entity_id, transaction_date);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);
CREATE INDEX idx_transactions_security ON transactions(security_identifier);
CREATE INDEX idx_transactions_option_details ON transactions USING gin (option_details);
CREATE INDEX idx_transactions_bond_details ON transactions USING gin (bond_details);

CREATE INDEX idx_positions_entity_date ON positions(entity_id, as_of_date);
CREATE INDEX idx_positions_account_date ON positions(account_id, as_of_date);
CREATE INDEX idx_positions_security ON positions(security_identifier);

CREATE INDEX idx_documents_period ON documents(period_start, period_end);
CREATE INDEX idx_documents_hash ON documents(file_hash);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all tables with updated_at
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at()',
            t, t);
    END LOOP;
END $$;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully at %', NOW();
    RAISE NOTICE 'Ready for Fidelity statement extraction with support for:';
    RAISE NOTICE '  - Complex options transactions';
    RAISE NOTICE '  - Bond redemptions and details';
    RAISE NOTICE '  - Dividend reinvestments';
    RAISE NOTICE '  - Multi-entity tracking';
    RAISE NOTICE '  - Tax categorization';
END $$;