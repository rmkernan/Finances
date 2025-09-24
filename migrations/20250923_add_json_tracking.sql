-- Add JSON tracking columns for duplicate detection and audit trail
-- Created: 09/23/25 12:00PM ET
-- Purpose: Add JSON hash and filename columns for robust duplicate detection

-- Add JSON tracking to documents table
ALTER TABLE documents
ADD COLUMN extraction_md5_hash VARCHAR(32),
ADD COLUMN extraction_filename VARCHAR(255);

-- Add source file tracking to transactions table
ALTER TABLE transactions
ADD COLUMN source_file VARCHAR(255);

-- Add source file tracking to positions table
ALTER TABLE positions
ADD COLUMN source_file VARCHAR(255);

-- Create indexes for performance
CREATE INDEX idx_documents_extraction_hash ON documents(extraction_md5_hash);
CREATE INDEX idx_transactions_source_file ON transactions(source_file);
CREATE INDEX idx_positions_source_file ON positions(source_file);

-- Add comments for documentation
COMMENT ON COLUMN documents.extraction_md5_hash IS 'MD5 hash of JSON extraction content (excluding timestamps) for duplicate detection';
COMMENT ON COLUMN documents.extraction_filename IS 'Original JSON extraction filename for audit trail';
COMMENT ON COLUMN transactions.source_file IS 'JSON filename that created this transaction record';
COMMENT ON COLUMN positions.source_file IS 'JSON filename that created this position record';