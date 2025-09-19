# Load Extraction Command

**Created:** 09/19/25 12:36PM ET
**Purpose:** Load JSON extraction files into the database
**Usage:** Run after extraction completes to populate database tables

## Command: `/load-extraction [filename]`

### Step 1: Validate Extraction File

```bash
# Check file exists
ls -la /documents/extractions/[filename]

# Validate JSON structure
python3 -m json.tool /documents/extractions/[filename] > /dev/null
```

### Step 2: Check for Duplicates

Before loading, check if this document was already processed:

```sql
-- Check by file hash
SELECT id, source_file_name, period_start, period_end, extraction_status
FROM documents
WHERE file_hash = '[hash_from_json]';

-- Check by period and institution
SELECT id, source_file_name, extraction_status
FROM documents
WHERE institution_id = (SELECT id FROM institutions WHERE name = '[institution]')
AND period_start = '[start_date]'
AND period_end = '[end_date]';
```

If duplicate found, ask: "Document for this period already exists. Replace (R), Skip (S), or Create Amendment (A)?"

### Step 3: Load Core Document Record

```sql
-- Insert document record
INSERT INTO documents (
    source_file_name,
    source_file_path,
    file_hash,
    document_type,
    institution_id,
    period_start,
    period_end,
    portfolio_value,
    extraction_json_path,
    extraction_status,
    extraction_timestamp
) VALUES (
    'Fid_Stmnt_2025-08_Brok&CMA.pdf',
    '/documents/processed/Fid_Stmnt_2025-08_Brok&CMA.pdf',
    '32967b1d3e40b2c544cc42e0c6f378e5',
    'statement',
    (SELECT id FROM institutions WHERE name = 'Fidelity'),
    '2025-08-01',
    '2025-08-31',
    6925062.03,
    '/documents/extractions/Fid_Stmnt_2025-08_Brok&CMA_2025.09.18_15.48ET.json',
    'completed',
    NOW()
) RETURNING id;
```

### Step 4: Link Document to Accounts

For each account in the extraction:

```sql
-- Ensure account exists
INSERT INTO accounts (
    entity_id,
    institution_id,
    account_number,
    account_holder_name,
    account_type
) VALUES (
    (SELECT id FROM entities WHERE name ILIKE '%kernan%'), -- Match by holder name
    (SELECT id FROM institutions WHERE name = 'Fidelity'),
    'Z24-527872',
    'RICHARD MICHAEL KERNAN - JOINT WROS - TOD',
    'GENERAL INVESTMENTS - FIDELITY ACCOUNT'
) ON CONFLICT (institution_id, account_number)
DO UPDATE SET account_holder_name = EXCLUDED.account_holder_name
RETURNING id;

-- Link document to account
INSERT INTO document_accounts (document_id, account_id)
VALUES ([document_id], [account_id]);
```

### Step 5: Load Transactions

For each transaction in the extraction:

```sql
INSERT INTO transactions (
    document_id,
    account_id,
    settlement_date,
    transaction_type,
    security_name,
    security_identifier,
    description,
    quantity,
    price_per_unit,
    amount,
    fees,
    option_details,
    entity_id
) VALUES (
    [document_id],
    [account_id],
    '2025-08-04',
    'buy', -- Mapped from 'BUY' in extraction
    'TESLA INC COM',
    '88160R101',
    'You Bought - ASSIGNED PUTS',
    500.000,
    305.00000,
    -152500.00,
    0.00,
    NULL, -- or JSONB for options
    (SELECT entity_id FROM accounts WHERE id = [account_id])
);
```

### Step 6: Load Positions (Current Holdings)

```sql
INSERT INTO positions (
    document_id,
    account_id,
    as_of_date,
    security_name,
    security_identifier,
    quantity,
    price,
    market_value,
    cost_basis,
    unrealized_gain_loss
) VALUES (
    [document_id],
    [account_id],
    '2025-08-31', -- Period end date
    'FIDELITY GOVERNMENT MONEY MARKET (SPAXX)',
    'SPAXX',
    82453.590,
    1.00,
    82453.59,
    82453.59,
    0.00
);
```

### Step 7: Load Income Summary

```sql
INSERT INTO income_summaries (
    document_id,
    account_id,
    period_start,
    period_end,
    taxable_income,
    tax_exempt_income,
    entity_id
) VALUES (
    [document_id],
    [account_id],
    '2025-08-01',
    '2025-08-31',
    123.45, -- From taxable_income_period
    0.00,   -- From tax_exempt_income_period
    (SELECT entity_id FROM accounts WHERE id = [account_id])
);
```

### Step 8: Update Processing Status

```sql
-- Mark document as loaded
UPDATE documents
SET extraction_status = 'loaded',
    extraction_notes = 'Successfully loaded ' ||
                      (SELECT COUNT(*) FROM transactions WHERE document_id = [document_id]) ||
                      ' transactions'
WHERE id = [document_id];
```

```bash
# Move source file to archived
mv /documents/processed/[filename].pdf /documents/archived/[filename].pdf
```

### Step 9: Validation Report

After loading, provide summary:

```sql
-- Summary query
SELECT
    'Document: ' || source_file_name,
    'Period: ' || period_start || ' to ' || period_end,
    'Accounts: ' || COUNT(DISTINCT da.account_id),
    'Transactions: ' || COUNT(DISTINCT t.id),
    'Positions: ' || COUNT(DISTINCT p.id),
    'Total Value: $' || portfolio_value
FROM documents d
LEFT JOIN document_accounts da ON d.id = da.document_id
LEFT JOIN transactions t ON d.id = t.document_id
LEFT JOIN positions p ON d.id = p.document_id
WHERE d.id = [document_id]
GROUP BY d.id, d.source_file_name, d.period_start, d.period_end, d.portfolio_value;
```

## Error Handling

If loading fails at any step:
1. Rollback the transaction
2. Update document status to 'load_failed'
3. Add error details to extraction_notes
4. Keep files in current locations for retry
5. Report specific failure to user

## Success Criteria

Loading is complete when:
- [ ] Document record created with proper links
- [ ] All accounts mapped to entities
- [ ] All transactions loaded with complete details
- [ ] Positions snapshot captured
- [ ] Income summary recorded
- [ ] Files moved to final locations
- [ ] Validation counts match extraction

## Notes

- This process assumes entities and institutions already exist in the database
- Account holder names help match accounts to entities
- Transaction types are normalized (BUY → buy, SELL → sell, etc.)
- Option and bond details use JSONB columns when present
- Each load is wrapped in a transaction for atomicity