-- Migration: 20250917202218_baseline_enhanced_schema.sql
-- Created: 09/17/25 3:20PM ET
-- Purpose: Complete enhanced schema for Claude-assisted financial data management
-- Based on: /docs/Design/02-Technical/database-schema-enhanced.md
-- Replaces: Phase 1 schema with full 10-table enhanced multi-entity design

-- =================================================================
-- Enhanced Database Schema - Financial Data Management System
-- =================================================================

-- -----------------------------------------------------------------
-- TABLE: entities
-- Purpose: Master table for all business entities and individual taxpayers
-- -----------------------------------------------------------------

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('individual', 's_corp', 'llc', 'partnership', 'c_corp', 'trust')),
    tax_id TEXT NOT NULL UNIQUE,
    tax_id_display TEXT,
    primary_taxpayer TEXT,
    tax_year_end TEXT DEFAULT '12-31',
    georgia_resident BOOLEAN DEFAULT TRUE,
    entity_status TEXT DEFAULT 'active' CHECK (entity_status IN ('active', 'inactive', 'dissolved')),
    formation_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: institutions
-- Purpose: Financial institutions that hold accounts for entities
-- -----------------------------------------------------------------

CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    institution_name TEXT NOT NULL,
    institution_type TEXT CHECK (institution_type IN ('brokerage', 'bank', 'credit_union', 'insurance', 'retirement_plan', 'other')),
    routing_number TEXT,
    swift_code TEXT,
    institution_address TEXT,
    primary_contact JSONB,
    login_credentials JSONB,
    document_delivery JSONB,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'closed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: accounts
-- Purpose: Individual financial accounts within institutions
-- -----------------------------------------------------------------

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT,
    account_number TEXT NOT NULL,
    account_number_display TEXT,
    account_name TEXT,
    account_type TEXT NOT NULL CHECK (account_type IN ('checking', 'savings', 'brokerage', 'ira', '401k', 'roth_ira', 'trust', 'business', 'money_market', 'cd')),
    account_subtype TEXT,
    tax_reporting_name TEXT,
    custodian_name TEXT,
    account_opening_date DATE,
    account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'inactive', 'closed', 'transferred')),
    is_tax_deferred BOOLEAN DEFAULT FALSE,
    is_tax_free BOOLEAN DEFAULT FALSE,
    requires_rmd BOOLEAN DEFAULT FALSE,
    beneficiary_info JSONB,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: documents
-- Purpose: Stores document metadata and extraction results
-- -----------------------------------------------------------------

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE RESTRICT,
    tax_year INTEGER NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2035),

    -- Document Details
    document_type TEXT NOT NULL CHECK (document_type IN ('statement', '1099', 'quickbooks_export', 'bank_statement', 'tax_return', 'k1', 'receipt', 'invoice', 'other')),
    period_start DATE,
    period_end DATE,

    -- File Management
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    file_hash TEXT NOT NULL,
    mime_type TEXT DEFAULT 'application/pdf',

    -- Amendment Tracking
    is_amended BOOLEAN DEFAULT FALSE,
    amends_document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    version_number INTEGER DEFAULT 1,

    -- Processing Metadata
    processed_at TIMESTAMPTZ,
    processed_by TEXT DEFAULT 'claude',
    extraction_method TEXT DEFAULT 'claude_ai' CHECK (extraction_method IN ('claude_ai', 'ocr', 'manual', 'api_import')),
    extraction_confidence TEXT NOT NULL DEFAULT 'needs_review' CHECK (extraction_confidence IN ('high', 'medium', 'low', 'needs_review', 'failed')),
    extraction_notes TEXT,
    needs_human_review BOOLEAN DEFAULT FALSE,
    human_reviewed_at TIMESTAMPTZ,

    -- Extraction Data
    raw_extraction JSONB,
    structured_data JSONB,
    summary_data JSONB,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: document_accounts
-- Purpose: Many-to-many association between documents and accounts
-- -----------------------------------------------------------------

CREATE TABLE document_accounts (
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_document_accounts UNIQUE (document_id, account_id)
);

-- -----------------------------------------------------------------
-- TABLE: transactions
-- Purpose: Individual financial transactions extracted from documents
-- -----------------------------------------------------------------

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Transaction Core Data
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('dividend', 'interest', 'buy', 'sell', 'transfer_in', 'transfer_out', 'fee', 'return_of_capital', 'assignment', 'other')),
    transaction_subtype TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount != 0),
    source TEXT NOT NULL CHECK (source IN ('statement', 'qb_export', 'ledger')),

    -- Security Information
    security_info JSONB,
    security_type TEXT CHECK (security_type IN ('stock', 'bond', 'mutual_fund', 'etf', 'money_market', 'cd', 'option', 'other')),

    -- Tax Categorization
    tax_category TEXT NOT NULL CHECK (tax_category IN ('ordinary_dividend', 'qualified_dividend', 'municipal_interest', 'corporate_interest', 'capital_gain_short', 'capital_gain_long', 'return_of_capital', 'tax_exempt', 'fee_expense', 'other')),
    federal_taxable BOOLEAN NOT NULL,
    state_taxable BOOLEAN NOT NULL,
    tax_details JSONB,

    -- Source Tracking
    source_transaction_id TEXT,
    source_reference TEXT,

    -- Duplicate Detection
    is_duplicate_of UUID REFERENCES transactions(id) ON DELETE SET NULL,
    duplicate_reason TEXT,

    -- Quality Control
    needs_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_by TEXT DEFAULT 'claude'
);

-- -----------------------------------------------------------------
-- TABLE: tax_payments
-- Purpose: Tracks quarterly estimated tax payments and annual tax liabilities
-- -----------------------------------------------------------------

CREATE TABLE tax_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Payment Details
    tax_year INTEGER NOT NULL CHECK (tax_year >= 2020 AND tax_year <= 2030),
    payment_type TEXT NOT NULL CHECK (payment_type IN ('est_q1', 'est_q2', 'estimated_q3', 'estimated_q4', 'extension', 'balance_due', 'amended_return', 'penalty', 'interest')),
    tax_authority TEXT NOT NULL CHECK (tax_authority IN ('federal', 'georgia', 'other_state')),
    payment_date DATE NOT NULL,
    due_date DATE,
    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),

    -- Calculation Details
    calculation_basis JSONB,
    estimated_income NUMERIC(15,2),
    estimated_tax_liability NUMERIC(15,2),

    -- Status and Review
    notes TEXT,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: transfers
-- Purpose: Tracks money movements between entities and accounts
-- -----------------------------------------------------------------

CREATE TABLE transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source Information
    source_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    source_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Destination Information
    destination_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    destination_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Transfer Details
    transfer_date DATE NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    transfer_type TEXT NOT NULL CHECK (transfer_type IN ('loan', 'distribution', 'capital_contribution', 'reimbursement', 'gift', 'repayment', 'other')),
    purpose TEXT NOT NULL,

    -- Status and Review
    notes TEXT,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent self-transfers
    CONSTRAINT chk_no_self_transfer CHECK (source_entity_id != destination_entity_id)
);

-- -----------------------------------------------------------------
-- TABLE: asset_notes
-- Purpose: Investment strategy notes and price targets for securities
-- -----------------------------------------------------------------

CREATE TABLE asset_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,

    -- Security Identification
    symbol TEXT NOT NULL,
    cusip TEXT,
    security_name TEXT,
    security_type TEXT CHECK (security_type IN ('stock', 'etf', 'mutual_fund', 'bond', 'option', 'other')),

    -- Price Targets and Limits
    buy_below NUMERIC(12,4) CHECK (buy_below > 0),
    sell_above NUMERIC(12,4) CHECK (sell_above > 0),
    stop_loss NUMERIC(12,4) CHECK (stop_loss > 0),
    current_price NUMERIC(12,4) CHECK (current_price > 0),
    price_updated_at TIMESTAMPTZ,

    -- Performance Tracking
    cost_basis NUMERIC(15,2),
    current_shares NUMERIC(15,6) CHECK (current_shares >= 0),
    unrealized_gain_loss NUMERIC(15,2),
    last_transaction_date DATE,

    -- Alerts and Monitoring
    alert_enabled BOOLEAN DEFAULT FALSE,
    alert_conditions JSONB,
    dividend_yield NUMERIC(5,4) CHECK (dividend_yield >= 0),
    next_dividend_date DATE,

    -- Research and Notes
    research_notes TEXT,
    review_frequency TEXT CHECK (review_frequency IN ('weekly', 'monthly', 'quarterly', 'annually')),
    next_review_date DATE,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'watch_list', 'sold', 'deprecated')),
    notes TEXT,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: real_assets
-- Purpose: Track physical properties and other non-financial assets
-- -----------------------------------------------------------------

CREATE TABLE real_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,

    -- Asset Details
    asset_type TEXT NOT NULL CHECK (asset_type IN ('primary_residence', 'rental_property', 'commercial_property', 'land', 'vacation_home', 'vehicle', 'other')),
    description TEXT NOT NULL,
    address TEXT,
    purchase_date DATE,
    purchase_price NUMERIC(15,2),

    -- Valuation
    current_value NUMERIC(15,2) NOT NULL,
    valuation_date DATE NOT NULL,
    valuation_source TEXT,

    -- Income/Expense
    monthly_income NUMERIC(15,2),
    monthly_expense NUMERIC(15,2),

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending_sale', 'sold', 'transferred')),
    notes TEXT,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- TABLE: liabilities
-- Purpose: Track mortgages and long-term loans for net worth calculation
-- -----------------------------------------------------------------

CREATE TABLE liabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    real_asset_id UUID REFERENCES real_assets(id) ON DELETE SET NULL,

    -- Liability Details
    liability_type TEXT NOT NULL CHECK (liability_type IN ('mortgage', 'home_equity', 'auto_loan', 'business_loan', 'personal_loan', 'other')),
    lender_name TEXT NOT NULL,
    account_number TEXT,

    -- Loan Terms
    original_amount NUMERIC(15,2) NOT NULL,
    current_balance NUMERIC(15,2) NOT NULL,
    interest_rate NUMERIC(5,3) NOT NULL,
    loan_start_date DATE NOT NULL,
    maturity_date DATE,

    -- Payment Info
    monthly_payment NUMERIC(15,2) NOT NULL,
    next_payment_date DATE,
    escrow_amount NUMERIC(15,2),

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paid_off', 'refinanced', 'transferred')),
    notes TEXT,

    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =================================================================
-- INDEXES: Essential for Performance and Claude Query Patterns
-- =================================================================

-- Core entity lookups
CREATE INDEX idx_entities_type_status ON entities(entity_type, entity_status);
CREATE INDEX idx_entities_tax_id ON entities(tax_id);

-- Institution relationships
CREATE INDEX idx_institutions_entity ON institutions(entity_id);
CREATE INDEX idx_institutions_name_status ON institutions(institution_name, status);

-- Account management
CREATE INDEX idx_accounts_entity ON accounts(entity_id);
CREATE INDEX idx_accounts_institution ON accounts(institution_id);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_composite ON accounts(entity_id, institution_id, account_status);
CREATE INDEX idx_accounts_tax_attributes ON accounts(is_tax_deferred, is_tax_free, requires_rmd) WHERE account_status = 'active';

-- Document processing
CREATE INDEX idx_documents_institution ON documents(institution_id);
CREATE UNIQUE INDEX uq_documents_file_hash ON documents(file_hash);
CREATE INDEX idx_documents_processing ON documents(extraction_confidence, needs_human_review);
CREATE INDEX idx_documents_tax_year ON documents(tax_year);
CREATE INDEX idx_documents_type_period ON documents(document_type, period_start, period_end);
CREATE INDEX idx_documents_amendments ON documents(amends_document_id) WHERE amends_document_id IS NOT NULL;

-- Document-account associations
CREATE INDEX idx_document_accounts_doc ON document_accounts(document_id);
CREATE INDEX idx_document_accounts_acct ON document_accounts(account_id);

-- Transaction analysis
CREATE INDEX idx_transactions_entity ON transactions(entity_id);
CREATE INDEX idx_transactions_document ON transactions(document_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_date_entity ON transactions(entity_id, transaction_date);
CREATE INDEX idx_transactions_amount ON transactions(amount) WHERE ABS(amount) > 100;
CREATE INDEX idx_transactions_tax_category ON transactions(tax_category);
CREATE INDEX idx_transactions_taxable ON transactions(federal_taxable, state_taxable);
CREATE INDEX idx_transactions_tax_federal ON transactions(federal_taxable, transaction_date) WHERE federal_taxable = true;
CREATE INDEX idx_transactions_tax_state ON transactions(state_taxable, transaction_date) WHERE state_taxable = true;
CREATE INDEX idx_transactions_security_type ON transactions(security_type) WHERE security_type IS NOT NULL;
CREATE INDEX idx_transactions_review ON transactions(needs_review) WHERE needs_review = true;
CREATE INDEX idx_transactions_duplicates ON transactions(is_duplicate_of) WHERE is_duplicate_of IS NOT NULL;
CREATE INDEX idx_transactions_source ON transactions(source_transaction_id) WHERE source_transaction_id IS NOT NULL;

-- Tax payment tracking
CREATE INDEX idx_tax_payments_entity ON tax_payments(entity_id);
CREATE INDEX idx_tax_payments_year ON tax_payments(tax_year);
CREATE INDEX idx_tax_payments_type ON tax_payments(payment_type);
CREATE INDEX idx_tax_payments_authority ON tax_payments(tax_authority);
CREATE INDEX idx_tax_payments_date ON tax_payments(payment_date);
CREATE INDEX idx_tax_payments_due_date ON tax_payments(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tax_payments_entity_year ON tax_payments(entity_id, tax_year, payment_type);

-- Transfer management
CREATE INDEX idx_transfers_source_entity ON transfers(source_entity_id);
CREATE INDEX idx_transfers_dest_entity ON transfers(destination_entity_id);
CREATE INDEX idx_transfers_date ON transfers(transfer_date);
CREATE INDEX idx_transfers_type ON transfers(transfer_type);
CREATE INDEX idx_transfers_entities ON transfers(source_entity_id, destination_entity_id, transfer_date);

-- Asset management
CREATE INDEX idx_asset_notes_entity ON asset_notes(entity_id);
CREATE INDEX idx_asset_notes_account ON asset_notes(account_id) WHERE account_id IS NOT NULL;
CREATE INDEX idx_asset_notes_symbol ON asset_notes(symbol);
CREATE INDEX idx_asset_notes_status ON asset_notes(status);
CREATE INDEX idx_asset_notes_review_date ON asset_notes(next_review_date) WHERE next_review_date IS NOT NULL;
CREATE INDEX idx_asset_notes_alerts ON asset_notes(alert_enabled) WHERE alert_enabled = true;

-- Real asset tracking
CREATE INDEX idx_real_assets_entity ON real_assets(entity_id);
CREATE INDEX idx_real_assets_type ON real_assets(asset_type);
CREATE INDEX idx_real_assets_status ON real_assets(status);

-- Liability tracking
CREATE INDEX idx_liabilities_entity ON liabilities(entity_id);
CREATE INDEX idx_liabilities_asset ON liabilities(real_asset_id) WHERE real_asset_id IS NOT NULL;
CREATE INDEX idx_liabilities_type ON liabilities(liability_type);
CREATE INDEX idx_liabilities_status ON liabilities(status);
CREATE INDEX idx_liabilities_maturity ON liabilities(maturity_date) WHERE status = 'active';

-- JSONB indexes for flexible queries
CREATE INDEX idx_documents_raw_extraction ON documents USING GIN (raw_extraction);
CREATE INDEX idx_documents_structured_data ON documents USING GIN (structured_data);
CREATE INDEX idx_documents_summary_data ON documents USING GIN (summary_data);
CREATE INDEX idx_transactions_security_info ON transactions USING GIN (security_info);
CREATE INDEX idx_transactions_tax_details ON transactions USING GIN (tax_details);
CREATE INDEX idx_tax_payments_calculation_basis ON tax_payments USING GIN (calculation_basis);
CREATE INDEX idx_asset_notes_alert_conditions ON asset_notes USING GIN (alert_conditions);

-- =================================================================
-- TABLE CONSTRAINTS
-- =================================================================

-- Ensure tax_year_end format
ALTER TABLE entities ADD CONSTRAINT chk_tax_year_end_format
CHECK (tax_year_end ~ '^\d{2}-\d{2}$');

-- Prevent conflicting tax attributes
ALTER TABLE accounts ADD CONSTRAINT chk_tax_attributes_exclusive
CHECK (NOT (is_tax_deferred = true AND is_tax_free = true));

-- Ensure period logic
ALTER TABLE documents ADD CONSTRAINT chk_period_dates
CHECK (period_start IS NULL OR period_end IS NULL OR period_start <= period_end);

-- Ensure amendment chain integrity
ALTER TABLE documents ADD CONSTRAINT chk_amendment_not_self
CHECK (id != amends_document_id);

-- Prevent self-referential duplicates
ALTER TABLE transactions ADD CONSTRAINT chk_duplicate_not_self
CHECK (id != is_duplicate_of);

-- =================================================================
-- COMMENTS: Additional context for future developers/Claude
-- =================================================================

COMMENT ON TABLE entities IS 'Master table for all business entities and individual taxpayers - central hub for organizational structure';
COMMENT ON TABLE institutions IS 'Financial institutions that hold accounts for entities - supports multiple institutions per entity';
COMMENT ON TABLE accounts IS 'Individual financial accounts within institutions - links entities to specific account numbers';
COMMENT ON TABLE documents IS 'Source documents with extraction metadata - supports multi-account documents via junction table';
COMMENT ON TABLE document_accounts IS 'Many-to-many association between documents and accounts - handles consolidated statements';
COMMENT ON TABLE transactions IS 'Individual financial transactions with comprehensive tax categorization and source tracking';
COMMENT ON TABLE tax_payments IS 'Quarterly estimated tax payments and annual tax liabilities for compliance tracking';
COMMENT ON TABLE transfers IS 'Inter-entity money movements and loans for multi-entity financial management';
COMMENT ON TABLE asset_notes IS 'Investment strategy notes and price targets for securities performance tracking';
COMMENT ON TABLE real_assets IS 'Physical properties and non-financial assets for complete net worth calculation';
COMMENT ON TABLE liabilities IS 'Mortgages and long-term debt for net worth tracking - excludes inter-entity loans and credit cards';

COMMENT ON COLUMN transactions.amount IS 'CRITICAL: Uses NUMERIC(15,2) to prevent floating-point errors in financial calculations';
COMMENT ON COLUMN documents.raw_extraction IS 'Complete unprocessed extraction data from Claude for debugging and reprocessing';
COMMENT ON COLUMN transactions.security_info IS 'Flexible JSONB storage: {cusip, symbol, name, quantity, price, security_type}';
COMMENT ON COLUMN documents.summary_data IS 'High-level summary data: 1099 totals, statement summaries for quick reference';
COMMENT ON COLUMN transactions.tax_details IS 'Complex tax scenarios: {issuer_state, taxpayer_state, amt_preference, section_199a}';

-- =================================================================
-- MIGRATION COMPLETE
-- =================================================================
-- This migration creates the complete enhanced schema as specified in
-- /docs/Design/02-Technical/database-schema-enhanced.md
--
-- Key features:
-- - 10 tables with comprehensive multi-entity support
-- - JSONB fields for flexible data storage with source document mappings
-- - NUMERIC types for financial precision
-- - Complete indexes for performance optimization
-- - Full audit trail and data lineage capability
-- - Support for complex tax scenarios and inter-entity transfers
-- =================================================================