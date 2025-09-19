-- Migration: Add Survey Workflow Fields to Documents Table
-- Created: 09/19/25 2:10PM ET
-- Purpose: Support filename-based duplicate checking during document survey phase
-- Author: Claude (based on user requirements analysis)

-- Add new columns to support document survey workflow
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS page_count INTEGER,
ADD COLUMN IF NOT EXISTS source_filename TEXT;

-- Add comments for clarity
COMMENT ON COLUMN documents.page_count IS 'Number of pages in the source document (from PDF analysis)';
COMMENT ON COLUMN documents.source_filename IS 'Human-friendly filename for duplicate checking (e.g., "Fid_Stmnt_2025-08_Brok+CMA.pdf")';

-- Create index for fast duplicate checking during survey
CREATE INDEX IF NOT EXISTS idx_documents_source_filename ON documents(source_filename);

-- Update existing schema documentation reference
COMMENT ON TABLE documents IS 'Enhanced for survey workflow: supports filename-based duplicate detection before processing';

-- Rollback instructions (for development use):
-- DROP INDEX IF EXISTS idx_documents_source_filename;
-- ALTER TABLE documents DROP COLUMN IF EXISTS source_filename;
-- ALTER TABLE documents DROP COLUMN IF EXISTS page_count;