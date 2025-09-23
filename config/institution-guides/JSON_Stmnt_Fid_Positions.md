# Fidelity JSON Output Specification

**Created:** 09/22/25 1:35PM ET
**Updated:** 09/22/25 6:04PM ET - Corrected est_yield format to percentage (e.g., 4.880) not decimal (0.0488)
**Updated:** 09/22/25 8:55PM ET - Added doc_md5_hash field to extraction_metadata for duplicate prevention
**Updated:** 09/23/25 2:32PM - Added required account_type field to account-level metadata for loader compatibility
**Updated:** 09/23/25 2:37PM - Aligned data type rules with activities specification for consistency
**Updated:** 09/23/25 4:25PM - Added extraction vs classification philosophy and mapping system guidance
**Purpose:** Formal specification for JSON output from Fidelity statement extraction
**Related:** [Map_Stmnt_Fid_Positions.md](./Map_Stmnt_Fid_Positions.md)

## ⚙️ Extraction vs Classification Philosophy

**IMPORTANT:** This guide focuses on **pure transcription** from PDF statements. The extractor should capture data exactly as shown without interpretation or classification.

**Transaction Classification:** Happens automatically in the loader using the configuration-driven mapping system (`/config/data-mappings.json`):
- **Transaction types:** dividend vs interest vs trade categorization
- **Security classification:** call vs put options identification
- **Lifecycle tracking:** opening/closing transactions and assignments
- **Tax categories:** municipal bonds vs regular interest separation

**Extractor Responsibility:** Accurate data capture from PDF
**Loader Responsibility:** Data classification and categorization

**New Patterns:** When encountering new transaction types, add patterns to `/config/data-mappings.json` rather than modifying extraction logic.

## Overview

This document defines the exact JSON structure that must be produced when extracting data from Fidelity statements. The extraction process produces a single JSON file containing metadata, document information, and holdings data.

## File Naming Convention

```
{file_hash}_holdings_{YYYYMMDD_HHMMSS}.json
```

Example: `a3b5c7d9e1f3_holdings_20240922_143000.json`

## Data Type Rules

| Data Type | Format | Example | Notes |
|-----------|--------|---------|-------|
| Dates | `YYYY-MM-DD` | `"2024-08-31"` | ISO 8601 format |
| Currency | String with 2 decimals | `"17525.00"` | Preserve precision, negative for debits |
| Quantities | String with 6 decimals | `"100.000000"` | Preserve all decimal places shown |
| Prices | String with 4 decimals | `"175.2500"` | Preserve all decimal places |
| Percentages | Decimal string | `"0.0525"` | 5.25% = "0.0525" |
| Missing values | `null` | `null` | Not "unavailable" or empty string |
| Account numbers | String | `"X12-123456"` | Preserve format exactly |
| Symbols/CUSIPs | String | `"AAPL"`, `"912828XX5"` | Uppercase as shown |

## Complete JSON Structure for Holdings Extraction

```json
{
  "extraction_metadata": {
    "document_id": "generated_uuid",
    "file_path": "/path/to/statement.pdf",
    "file_hash": "sha256_hash_of_file",
    "doc_md5_hash": "md5_hash_of_file",
    "extraction_type": "holdings",
    "extraction_timestamp": "2024-09-22T13:35:00Z",
    "extractor_version": "1.0",
    "pages_processed": 25,
    "extraction_notes": []
  },

  "document_data": {
    "institution": "Fidelity",
    "statement_date": "2024-08-31",
    "period_start": "2024-08-01",
    "period_end": "2024-08-31"
  },

  "accounts": [
    {
      "account_number": "X12-123456",
      "account_name": "INDIVIDUAL - TOD",
      "account_holder_name": "JOHN DOE",
      "account_type": "brokerage",

      "portfolio_summary": {
        "beginning_value": "500000.00",
        "ending_value": "525000.00",
        "net_account_value": "525000.00"
      },

      "income_summary": {
        "taxable_total_period": "1500.00",
        "taxable_total_ytd": "12000.00",
        "divs_taxable_period": "800.00",
        "divs_taxable_ytd": "6400.00",
        "stcg_taxable_period": "0.00",
        "stcg_taxable_ytd": "0.00",
        "int_taxable_period": "700.00",
        "int_taxable_ytd": "5600.00",
        "ltcg_taxable_period": "0.00",
        "ltcg_taxable_ytd": "0.00",
        "tax_exempt_total_period": "200.00",
        "tax_exempt_total_ytd": "1600.00",
        "divs_tax_exempt_period": "0.00",
        "divs_tax_exempt_ytd": "0.00",
        "int_tax_exempt_period": "200.00",
        "int_tax_exempt_ytd": "1600.00",
        "roc_period": "0.00",
        "roc_ytd": "0.00",
        "grand_total_period": "1700.00",
        "grand_total_ytd": "13600.00"
      },

      "realized_gains": {
        "st_gain_period": "500.00",
        "st_loss_period": "-200.00",
        "lt_gain_ytd": "5000.00",
        "lt_loss_ytd": "-1000.00"
      },

      "holdings": [
        {
          "sec_type": "Stocks",
          "sec_subtype": "Common Stock",
          "sec_symbol": "AAPL",
          "cusip": null,
          "sec_description": "APPLE INC COM",
          "beg_market_value": "17000.00",
          "quantity": "100.000000",
          "price_per_unit": "175.25",
          "end_market_value": "17525.00",
          "cost_basis": "15000.00",
          "unrealized_gain_loss": "2525.00",
          "estimated_ann_inc": "88.00",
          "est_yield": "0.500"
        },
        {
          "sec_type": "Bonds",
          "sec_subtype": "Municipal Bonds",
          "sec_symbol": null,
          "cusip": "880558HN4",
          "sec_description": "TENNESSEE ST ENERGY ACQUISITI REF-BD TAXABLE",
          "maturity_date": "2025-09-01",
          "coupon_rate": "0.0525",
          "beg_market_value": "95000.00",
          "quantity": "100000.000000",
          "price_per_unit": "98.75",
          "end_market_value": "98750.00",
          "accrued_int": "437.50",
          "cost_basis": "100000.00",
          "unrealized_gain_loss": "-1250.00",
          "estimated_ann_inc": "5250.00",
          "est_yield": null,
          "agency_ratings": "MOODYS Aa1 S&P AA+",
          "next_call_date": "2025-11-01",
          "call_price": "100.00",
          "payment_freq": "SEMIANNUALLY",
          "bond_features": "PRE-REFUNDED"
        },
        {
          "sec_type": "Options",
          "sec_subtype": "Calls",
          "sec_symbol": null,
          "cusip": null,
          "sec_description": "CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS)",
          "underlying_symbol": "GOOG",
          "strike_price": "215.00",
          "expiration_date": "2025-09-12",
          "beg_market_value": null,
          "quantity": "1.000000",
          "price_per_unit": "5.50",
          "end_market_value": "550.00",
          "cost_basis": "300.00",
          "unrealized_gain_loss": "250.00",
          "estimated_ann_inc": null,
          "est_yield": null
        },
        {
          "sec_type": "Mutual Funds",
          "sec_subtype": "Stock Funds",
          "sec_symbol": "VTSAX",
          "cusip": null,
          "sec_description": "VANGUARD TOTAL STOCK MARKET INDEX FUND ADMIRAL SHARES",
          "beg_market_value": "50000.00",
          "quantity": "400.123456",
          "price_per_unit": "131.25",
          "end_market_value": "52516.20",
          "cost_basis": "48000.00",
          "unrealized_gain_loss": "4516.20",
          "estimated_ann_inc": "800.00",
          "est_yield": "1.520"
        },
        {
          "sec_type": "Exchange Traded Products",
          "sec_subtype": "Equity ETPs",
          "sec_symbol": "SPY",
          "cusip": null,
          "sec_description": "SPDR S&P 500 ETF TRUST",
          "beg_market_value": "20000.00",
          "quantity": "45.000000",
          "price_per_unit": "450.75",
          "end_market_value": "20283.75",
          "cost_basis": "18000.00",
          "unrealized_gain_loss": "2283.75",
          "estimated_ann_inc": "270.00",
          "est_yield": "1.330"
        },
        {
          "sec_type": "Other",
          "sec_subtype": "REIT",
          "sec_symbol": "NLY",
          "cusip": null,
          "sec_description": "ANNALY CAPITAL MANAGEMENT INC COM NEW",
          "beg_market_value": "10000.00",
          "quantity": "500.000000",
          "price_per_unit": "19.85",
          "end_market_value": "9925.00",
          "cost_basis": "11000.00",
          "unrealized_gain_loss": "-1075.00",
          "estimated_ann_inc": "1300.00",
          "est_yield": "13.100"
        }
      ]
    }
  ]
}
```

## Field Completeness Rules

### Required Fields (Never null)
- All metadata fields (including `doc_md5_hash`)
- `account_number`
- `sec_type`
- `sec_description`
- `quantity`
- `price_per_unit`
- `end_market_value`

### Conditional Fields
- `sec_symbol`: Required for stocks, funds, ETPs; null for bonds
- `cusip`: Required for bonds; null for others
- `maturity_date`: Required for bonds only
- `coupon_rate`: Required for bonds only
- `accrued_int`: Required for bonds only
- `underlying_symbol`, `strike_price`, `expiration_date`: Required for options only

### Optional Fields (Can be null)
- `beg_market_value`: May show "unavailable" → null
- `cost_basis`: May be missing
- `unrealized_gain_loss`: May be missing
- `estimated_ann_inc`: May be missing
- `est_yield`: May be missing
- Bond optional fields: `agency_ratings`, `next_call_date`, `call_price`, `payment_freq`, `bond_features`

## Extraction Instructions for Claude

1. **One JSON file per document** containing all accounts found
2. **Preserve exact values** - Copy numbers exactly as shown (including decimal places)
3. **Handle "unavailable"** - Convert to `null` in JSON
4. **Include all holdings** - Even those with zero or negative values
5. **Maintain order** - Holdings in same order as document
6. **Ask if uncertain** - If data location unclear or values ambiguous, ask user for guidance

## Validation Rules

The Python loader will validate:
1. Required fields are not null
2. Numeric strings can be parsed as decimals
3. Dates are valid ISO 8601 format
4. Account numbers match expected patterns
5. Security types are from allowed values

## Example: Handling Special Cases

### Missing Values
Statement shows: "unavailable"
JSON output: `null`

### Negative Values
Statement shows: "($1,250.00)" or "-1,250.00"
JSON output: `"-1250.00"`

### Percentages
Statement shows: "5.25%"
JSON output: `"5.250"` (as percentage to 3 decimal places, not as decimal)

### Estimated Yield Format
Statement shows: "4.88%"
JSON output: `"4.880"` (NOT `"0.0488"`)
JSON output: `"0.0525"`

### Options Description Parsing
Statement shows: "CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS)"
JSON outputs:
- `"sec_description"`: Full text as shown
- `"underlying_symbol"`: `"GOOG"`
- `"strike_price"`: `"215.00"`
- `"expiration_date"`: `"2025-09-12"`

---

*This specification ensures consistent, complete JSON output that can be reliably processed by the Python database loader.*