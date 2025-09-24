-- Fix JSON hash design: Move hash tracking from documents to transactions/positions
-- Created: 09/23/25 8:15PM ET
-- Purpose: Each PDF creates 2 JSONs, so hash tracking belongs with the data, not the document

-- Drop incorrect columns from documents table
ALTER TABLE documents
DROP COLUMN IF EXISTS extraction_md5_hash,
DROP COLUMN IF EXISTS extraction_filename;

-- Drop the index that was on extraction_md5_hash
DROP INDEX IF EXISTS idx_documents_extraction_hash;

-- Add JSON hash tracking to transactions table
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS source_json_hash VARCHAR(32);

-- Add JSON hash tracking to positions table
ALTER TABLE positions
ADD COLUMN IF NOT EXISTS source_json_hash VARCHAR(32);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_json_hash ON transactions(source_json_hash);
CREATE INDEX IF NOT EXISTS idx_positions_json_hash ON positions(source_json_hash);

-- Add documentation comments
COMMENT ON COLUMN transactions.source_json_hash IS 'MD5 hash of activities JSON that created this transaction';
COMMENT ON COLUMN positions.source_json_hash IS 'MD5 hash of holdings JSON that created this position';