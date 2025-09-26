# Fidelity CSV to JSON Mapping Document

**Created:** 09/26/25 2:15PM - CSV column mapping for Python extraction script
**Purpose:** Define exact mappings from Fidelity CSV export columns to JSON structure for holdings extraction

## CSV File Structure

Fidelity CSV exports have two main sections:

### 1. Account Summary Header (Lines 1-2)
Contains account-level totals and income summary

### 2. Holdings Detail (Starting Line 6+)
Contains position-by-position details grouped by account and security type

## CSV Column Mappings

### Account Summary Section (Line 2)

| CSV Column Name | JSON Field Path | Data Type | Notes |
|-----------------|-----------------|-----------|-------|
| Account Type | accounts[].account_name | TEXT | "Joint CMA", "Joint Brokerage", etc. |
| Account | accounts[].account_number | TEXT | Account identifier (e.g., Z27375656) |
| Beginning mkt Value | accounts[].beginning_value | CURRENCY | Period start market value |
| Change in Investment | accounts[].net_account_value.change_in_inc_val_period | CURRENCY | Market value change |
| Ending mkt Value | accounts[].ending_value | CURRENCY | Period end market value |
| Short Balance | - | CURRENCY | Skip if blank |
| Ending Net Value | accounts[].net_account_value.ending_net_acct_val_period | CURRENCY | Net value including short balance |
| Dividends This Period | accounts[].income_summary.divs_taxable_period | CURRENCY | Period dividends (taxable only) |
| Dividends Year to Date | accounts[].income_summary.divs_taxable_ytd | CURRENCY | YTD dividends (taxable only) |
| Interest This Year | accounts[].income_summary.int_taxable_period | CURRENCY | Period interest (taxable only) |
| Interest Year to Date | accounts[].income_summary.int_taxable_ytd | CURRENCY | YTD interest (taxable only) |
| Total This Period | accounts[].income_summary.incsumm_total_period | CURRENCY | Period total income |
| Total Year to Date | accounts[].income_summary.incsumm_total_ytd | CURRENCY | YTD total income |

### Holdings Detail Section (Line 6+)

| CSV Column Name | JSON Field Path | Data Type | Notes |
|-----------------|-----------------|-----------|-------|
| Symbol/CUSIP | holdings[].sec_symbol OR holdings[].cusip | TEXT | Symbol for stocks/funds, CUSIP for bonds |
| Description | holdings[].sec_description | TEXT | Full security name |
| Quantity | holdings[].quantity | NUMBER | Shares/units owned |
| Price | holdings[].price_per_unit | CURRENCY | Current price per share |
| Beginning Value | holdings[].beg_market_value | CURRENCY | Value at period start |
| Ending Value | holdings[].end_market_value | CURRENCY | Value at period end |
| Cost Basis | holdings[].cost_basis | CURRENCY | Original cost (may be "not applicable") |

## Security Type Detection Rules

The CSV groups holdings by type with headers like:
- "Stocks"
- "Bonds"
- "Mutual Funds"
- "Core Account"
- "Options" (if present)

Each account's holdings start with the account number on its own line (e.g., "Z27375656")

## Special Handling Rules

### 1. Account Number Lines
Lines containing only account numbers (e.g., "Z27375656") indicate the start of that account's holdings

### 2. Security Type Headers
Lines with security type names ("Stocks", "Bonds", etc.) set the `sec_type` for subsequent holdings

### 3. Subtotal Lines
Lines starting with "Subtotal of" should be skipped (summary rows)

### 4. Symbol/CUSIP Determination
- If contains only letters/numbers and is 1-5 characters: `sec_symbol`
- If contains numbers and is 9 characters: `cusip`
- Options may have longer symbols with expiration info

### 5. Cost Basis
- Value "not applicable" → `null` in JSON
- Numeric values → preserve as string with 2 decimals

### 6. Options Parsing (if present)
Options descriptions contain embedded data:
- Extract underlying symbol from parentheses
- Extract strike price from description
- Extract expiration date from description

Example: "CALL (AAPL) APPLE INC JAN 17 25 $180" →
- `underlying_symbol`: "AAPL"
- `strike_price`: "180.00"
- `expiration_date`: "2025-01-17"

### 7. Missing/Empty Values
- Empty cells → `null` in JSON
- Zero values → preserve as "0.00"

## Multi-Account Handling

A single CSV may contain multiple accounts. The parser must:
1. Read account summary lines (line 2+) to identify all accounts
2. Parse holdings section to assign positions to correct accounts
3. Match account numbers between summary and holdings sections

## File Naming Convention

The Python script should generate filenames following:
```
Fid_Stmnt_YYYY-MM_[AccountLabels]_holdings_YYYY.MM.DD_HH.MMET.json
```

Where:
- `YYYY-MM` = Statement period from PDF/CSV
- `[AccountLabels]` = Mapped account names from account-mappings.json
- Timestamp = Current extraction time

## Required Lookups

The Python script must load:
1. `/config/account-mappings.json` - For account label generation
2. This mapping document - For field mappings

## Output Requirements

The script must create a JSON file with:
- All CSV-available fields populated (marked with (C) in Map_Stmnt_Fid_Positions.md)
- Non-CSV fields set to `null` for LLM augmentation
- Proper structure per JSON_Stmnt_Fid_Positions.md specification
- MD5 hash calculation for duplicate prevention

## CSV Column Availability Summary

**Available in CSV:**
- ✅ Account numbers and names
- ✅ Beginning/ending market values
- ✅ Security symbols and descriptions
- ✅ Quantities and prices
- ✅ Cost basis (for most securities)
- ✅ Period/YTD taxable dividends and interest
- ✅ Change in investment value

**NOT Available in CSV (PDF-only):**
- ❌ Estimated yields
- ❌ Unrealized gains/losses
- ❌ Tax-exempt income
- ❌ Bond details (maturity, coupon, ratings)
- ❌ Complete Net Account Value table
- ❌ Realized gains/losses
- ❌ Accrued interest