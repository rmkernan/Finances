-- Migration: 001_20250109_create_financial_tables.sql
-- Created: 01/09/25 
-- Purpose: Initial Phase 1 schema for Claude-assisted financial data management
-- Based on: /docs/technical/database-schema.md

-- =================================================================
-- Phase 1 Schema: 3 Tables Optimized for Claude Intelligence
-- =================================================================

-- -----------------------------------------------------------------
-- TABLE: accounts
-- Purpose: Store financial account information across institutions
-- Design: Simple structure optimized for Claude's context system
-- -----------------------------------------------------------------

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

-- -----------------------------------------------------------------
-- TABLE: documents  
-- Purpose: Track all financial documents (statements, 1099s, etc.)
-- Design: JSONB fields for flexible data storage and Claude notes
-- -----------------------------------------------------------------

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

-- -----------------------------------------------------------------
-- TABLE: transactions
-- Purpose: Individual financial transactions extracted from documents
-- Design: NUMERIC for money fields, JSONB for flexible security data
-- -----------------------------------------------------------------

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    account_id INTEGER REFERENCES accounts(id),
    
    -- Core transaction data
    transaction_date DATE,
    settlement_date DATE,
    transaction_type TEXT,
    description TEXT,
    amount NUMERIC(15,2),  -- Critical: NUMERIC for financial precision
    
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

-- =================================================================
-- INDEXES: Essential for Performance and Claude Query Patterns
-- =================================================================

-- Core lookup patterns for Claude
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);
CREATE INDEX idx_transactions_document ON transactions(document_id);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_account ON documents(account_id);

-- JSONB field indexes (PostgreSQL GIN indexes)
CREATE INDEX idx_transactions_security_info ON transactions USING GIN (security_info);
CREATE INDEX idx_documents_summary_data ON documents USING GIN (summary_data);

-- =================================================================
-- COMMENTS: Additional context for future developers/Claude
-- =================================================================

COMMENT ON TABLE accounts IS 'Financial account information across institutions - optimized for Claude context system';
COMMENT ON TABLE documents IS 'Financial documents with flexible JSONB storage for Claude-extracted data';
COMMENT ON TABLE transactions IS 'Individual transactions with NUMERIC precision for financial amounts';

COMMENT ON COLUMN transactions.amount IS 'CRITICAL: Uses NUMERIC(15,2) to prevent floating-point errors in financial calculations';
COMMENT ON COLUMN documents.raw_extraction IS 'Full Claude extraction data for debugging and reprocessing';
COMMENT ON COLUMN transactions.security_info IS 'Flexible JSONB storage: {cusip, symbol, name, quantity, price, security_type}';
COMMENT ON COLUMN documents.summary_data IS 'JSONB for 1099 summaries: {form_type, tax_year, ordinary_dividends, etc}';
COMMENT ON COLUMN transactions.tax_details IS 'Complex tax scenarios: {issuer_state, taxpayer_state, special_notes}';

-- =================================================================
-- MIGRATION COMPLETE
-- =================================================================
-- This migration creates the Phase 1 schema as specified in 
-- /docs/technical/database-schema.md
-- 
-- Key features:
-- - 3 tables optimized for Claude's intelligence
-- - JSONB fields for flexible data storage  
-- - NUMERIC types for financial precision
-- - Comprehensive indexes for performance
-- - Full audit trail capability
-- =================================================================