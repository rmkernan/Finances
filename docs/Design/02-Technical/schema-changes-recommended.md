# Recommended Schema Changes for Activity Map Alignment

**Created:** 09/22/25 4:15PM ET
**Updated:** 09/22/25 2:54PM ET - Changed cusip to sec_cusip, removed constraint, expanded categories with examples, added option examples, removed core_fund table
**Purpose:** Table-centric recommendations to align database schema with Fidelity activity mapping requirements

## Critical Changes (Required for Basic Functionality)

### 1. transactions table - Add sec_cusip column
**Priority:** HIGH
**Impact:** Enables proper bond and fixed income tracking
```sql
ALTER TABLE transactions ADD COLUMN sec_cusip TEXT;
```
**Rationale:** The positions table has separate sec_ticker and sec_cusip columns. For consistency and proper bond tracking, transactions needs the same structure. Many Fidelity activities (especially bonds) only have CUSIP identifiers.

### 2. transactions table - Add missing activity columns
**Priority:** HIGH
**Impact:** Enables complete activity tracking
```sql
ALTER TABLE transactions
  ADD COLUMN reference_number TEXT,
  ADD COLUMN payee TEXT,
  ADD COLUMN payee_account TEXT,
  ADD COLUMN ytd_amount DECIMAL(15,2),
  ADD COLUMN balance DECIMAL(15,2),
  ADD COLUMN account_type TEXT;
```
**Rationale:** These fields are needed for:
- reference_number: Wire transfers, redemptions
- payee/payee_account: Bill payments
- ytd_amount: Year-to-date tracking for payments
- balance: Running balances for core fund activity
- account_type: Distinguishing cash vs margin transactions

## Important Changes (Data Quality & Consistency)

### 3. Create transaction_categories lookup table
**Priority:** MEDIUM
**Impact:** Enables hierarchical categorization for tax reporting and business entity tracking
```sql
CREATE TABLE transaction_categories (
  category_code TEXT PRIMARY KEY,
  category_name TEXT NOT NULL,
  parent_category TEXT,
  tax_relevant BOOLEAN DEFAULT false,
  description TEXT
);

-- Sample data:
INSERT INTO transaction_categories VALUES
  ('DIV_QUALIFIED', 'Qualified Dividends', 'INCOME', true, 'Eligible for lower tax rates'),
  ('DIV_ORDINARY', 'Ordinary Dividends', 'INCOME', true, 'Taxed as ordinary income'),
  ('INT_MUNI_GA', 'GA Municipal Interest', 'INCOME', true, 'Double tax-exempt for GA residents'),
  ('INT_MUNI_OTHER', 'Other Muni Interest', 'INCOME', true, 'Federal exempt only'),
  ('CAP_GAIN_LT', 'Long-term Capital Gain', 'TRADE', true, 'Held > 1 year'),
  ('CAP_GAIN_ST', 'Short-term Capital Gain', 'TRADE', true, 'Held < 1 year'),
  ('FEE_DEDUCTIBLE', 'Investment Fees', 'FEE', true, 'May be deductible for business entities'),
  ('TRANSFER_INTERNAL', 'Inter-account Transfer', 'TRANSFER', false, 'No tax impact');

-- Add foreign key to transactions
ALTER TABLE transactions
  ADD COLUMN category_code TEXT
  REFERENCES transaction_categories(category_code);
```
**Rationale:** With 4-5 S-Corps/LLCs plus personal accounts, proper categorization is essential for:
- Tax treatment differences between entities
- Georgia municipal bond double-exemption tracking
- Business expense deductibility
- Qualified vs ordinary dividend classification

## Enhancement Changes (Future Flexibility)

### 4. transactions table - Add option-specific columns
**Priority:** LOW
**Impact:** Better options tracking for complex derivatives
```sql
ALTER TABLE transactions
  ADD COLUMN option_type TEXT CHECK (option_type IN ('CALL', 'PUT')),
  ADD COLUMN strike_price DECIMAL(15,2),
  ADD COLUMN expiration_date DATE,
  ADD COLUMN underlying_symbol TEXT,
  ADD COLUMN contract_count INTEGER;
```

**Example transactions that would benefit:**
```
-- Example 1: Opening a PUT position
security_name: "PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION"
option_type: "PUT"
underlying_symbol: "COIN"
strike_price: 300.00
expiration_date: "2025-08-15"
contract_count: 1
description: "You Bought - OPENING TRANSACTION"

-- Example 2: Closing a CALL position
security_name: "CALL (AAPL) APPLE INC JAN 17 25 $150 (100 SHS) CLOSING TRANSACTION"
option_type: "CALL"
underlying_symbol: "AAPL"
strike_price: 150.00
expiration_date: "2025-01-17"
contract_count: 1
description: "You Sold - CLOSING TRANSACTION"

-- Example 3: Option assignment
security_name: "PUT (SPY) SPDR S&P 500 DEC 20 24 $450 (100 SHS)"
option_type: "PUT"
underlying_symbol: "SPY"
strike_price: 450.00
expiration_date: "2024-12-20"
description: "Assigned"
```

**Rationale:** Currently, option details are crammed into the security_name field as text. Structured columns enable:
- Tracking P&L by underlying security
- Monitoring expiration dates
- Calculating strike price distances
- Aggregating option income by strategy


## Implementation Order

### Phase 1: Critical Schema Fixes (Immediate)
1. Add sec_cusip column to transactions
2. Add reference_number, payee fields
3. Add balance, account_type fields

### Phase 2: Data Quality (Next Sprint)
4. Create transaction_categories table
5. Migrate existing data to new categories

### Phase 3: Enhancements (Future)
6. Add option-specific columns
7. Add appropriate indexes for performance

## Migration Considerations

- **Backward Compatibility:** All changes are additive (new columns/tables only)
- **Data Migration:** Existing transactions remain valid; new fields nullable initially
- **Testing Required:** Verify activity import scripts handle new schema
- **Documentation Updates:** Update all mapping documents after implementation

## Alternative Approach

If modifying the transactions table is not feasible, consider:

### Create transaction_extended table
```sql
CREATE TABLE transaction_extended (
  transaction_id INTEGER PRIMARY KEY REFERENCES transactions(id),
  sec_cusip TEXT,
  reference_number TEXT,
  payee TEXT,
  payee_account TEXT,
  -- other extended fields
);
```
This preserves the existing schema while adding needed fields via a 1:1 extension table.

## Impact Summary

- **High Priority Changes:** Enable complete Fidelity statement import
- **Medium Priority Changes:** Improve data quality and tax reporting
- **Low Priority Changes:** Enhance specific asset class handling

These changes align the database schema with the activity mapping requirements while maintaining consistency with the existing positions table structure.