-- Fix schema to match JSON extraction field names
-- Created: 09/23/25 8:45PM ET
-- Purpose: Align database schema with JSON extraction to maintain pure transcription in loader

-- 1. Rename columns to match JSON field names
ALTER TABLE positions
RENAME COLUMN agency_rating TO agency_ratings;

ALTER TABLE positions
RENAME COLUMN next_call TO next_call_date;

-- 2. Update or remove the option_type constraint to accept "Calls"/"Puts" from JSON
-- First drop the old constraint
ALTER TABLE positions
DROP CONSTRAINT IF EXISTS positions_option_type_check;

-- Add new constraint that accepts the JSON values
ALTER TABLE positions
ADD CONSTRAINT positions_option_type_check
CHECK (option_type IN ('Calls', 'Puts', 'CALL', 'PUT') OR option_type IS NULL);

-- 3. Update column comments to reflect the changes
COMMENT ON COLUMN positions.agency_ratings IS 'Credit rating agencies assessments (e.g., MOODYS Aa1 S&P AA+)';
COMMENT ON COLUMN positions.next_call_date IS 'Next call date for callable bonds';
COMMENT ON COLUMN positions.option_type IS 'Option type: Calls, Puts (from JSON) or CALL, PUT (legacy)';