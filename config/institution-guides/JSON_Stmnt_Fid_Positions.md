# Fidelity JSON Output Specification

**Created:** 09/22/25 1:35PM ET
**Updated:** 09/22/25 6:04PM ET - Corrected est_yield format to percentage (e.g., 4.880) not decimal (0.0488)
**Updated:** 09/22/25 8:55PM ET - Added doc_md5_hash field to extraction_metadata for duplicate prevention
**Updated:** 09/24/25 11:44AM - Updated metadata attribute names: document_id→json_output_id, file_path→source_pdf_filepath, file_hash→json_output_md5_hash
**Updated:** 09/23/25 2:32PM - Added required account_type field to account-level metadata for loader compatibility
**Updated:** 09/23/25 2:37PM - Aligned data type rules with activities specification for consistency
**Updated:** 09/23/25 4:25PM - Added extraction vs classification philosophy and mapping system guidance
**Updated:** 09/24/25 10:30AM - Updated mapping system references to reflect new three-table configuration-driven approach with enhanced options and security classification
**Updated:** 09/25/25 1:52PM - Fixed extraction_timestamp format from ISO to YYYY.MM.DD_HH.MMET to match agent specifications
**Updated:** 09/26/25 12:45PM - Added complete doc_level_data sections (net_account_value, expanded income_summary, realized_gains) to align with updated schema
**Updated:** 09/26/25 1:45PM - Updated extraction workflow
**Updated:** 09/26/25 5:00PM - Removed hybrid workflow, reverted to pure LLM extraction from PDF
**Updated:** 09/26/25 5:45PM - Complete removal of all hybrid extraction references
**Purpose:** Formal specification for JSON output from Fidelity statement holdings extraction
**Related:** [Map_Stmnt_Fid_Positions.md](./Map_Stmnt_Fid_Positions.md)

## ⚙️ Extraction vs Classification Philosophy

**IMPORTANT:** This guide focuses on **pure transcription** from PDF statements. The extractor should capture data exactly as shown without interpretation or classification.

**Security and Position Classification:** Happens automatically in the loader using a sophisticated three-table configuration-driven mapping system:
- **Security types:** Enhanced classification of stocks, bonds, ETFs, mutual funds, and options
- **Options identification:** Precise call vs put classification with strike prices and expiration tracking
- **Bond categorization:** Municipal vs corporate bonds with proper tax treatment identification
- **Investment types:** ETFs, mutual funds, and complex instruments properly categorized
- **Multiple classification:** Single security can receive multiple classification attributes simultaneously

**System Architecture:**
- **map_rules:** Master rule definitions with business context and processing order
- **map_conditions:** Complex trigger logic supporting AND/OR compound conditions for security pattern matching
- **map_actions:** Multiple field updates per rule enabling comprehensive security classification

**Extractor Responsibility:** Accurate position data capture from PDF exactly as shown
**Loader Responsibility:** Security classification and categorization using configurable database-driven rules

**New Security Patterns:** When encountering unknown security types or patterns, the loader can accommodate new classification rules without code changes. Unknown securities receive generic classification and are flagged for potential rule creation.

### Security Description Handling
Extract security descriptions, CUSIPs, and symbols exactly as shown in the PDF. Do not attempt to standardize or categorize - the advanced mapping system handles complex security patterns:

**Enhanced Security Classification Examples:**
- "AAPL Apr 21 '25 $150 Call" → option type + call classification + expiration tracking
- "GA ST ATLANTA ARPT REV BDS" → bond type + municipal classification for tax-free treatment
- "VANGUARD TOTAL STK MKT ETF" → ETF classification with proper investment category

## Overview

This document defines the exact JSON structure that must be produced when extracting holdings data from Fidelity statements. The extraction process uses pure LLM extraction directly from PDF statements to produce a complete JSON file containing metadata, document information, and holdings data.

## File Naming Convention

Uses institution-statement-period-accounts-type-timestamp format:

```
Fid_Stmnt_YYYY-MM_[Accounts]_holdings_YYYY.MM.DD_HH.MMET.json
```

**Components:**
 - `Fid` - Institution code (Fidelity)
 - `Stmnt` - Document type (Statement)
 - `YYYY-MM` - Statement period (from document)
 - `[Accounts]` - Account labels from mappings (Brok, CMA, etc.)
 - `holdings` - Extraction type
 - `YYYY.MM.DD_HH.MMET` - Current extraction timestamp, e.g., "2025.09.25_13.35ET"

## Data Type Rules (As-Shown Policy)

All values are captured exactly as shown in the PDF. Do not normalize, convert, or reformat.
- Dates: store exactly as shown (e.g., "AUG 29 25", "11/01/29").
- Currency: keep "$" and commas (e.g., "$533,825.00").
- Quantities: keep sign and formatting as shown (e.g., "-10.000", "2,315,122.290").
- Prices: keep decimal places as shown (e.g., "213.5300").
- Percentages: keep the percent sign and up to two decimals as shown (e.g., "4.54%", "0.39%").
- Placeholders: if the source shows "-", record "-"; if it shows "unavailable"/"not applicable", record the exact text; if truly blank/missing, use `null`.
- Identifiers and account numbers: copy exactly as shown.

## Complete JSON Structure for Holdings Extraction

```json
{
  "extraction_metadata": {
    "json_output_id": "fid_stmnt_2025-08_kernbrok_kerncma_holdings",
    "source_pdf_filepath": "/path/to/statement.pdf",
    "json_output_md5_hash": "[CALCULATE: Use hashlib.md5() on final JSON content]",
    "doc_md5_hash": "md5_hash_of_source_pdf",
    "extraction_type": "holdings",
    "extraction_timestamp": "2025.09.25_13.35ET",
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

      "net_account_value": {
        "beg_net_acct_val_period": "500000.00",
        "beg_net_acct_val_ytd": "480000.00",
        "additions_period": "5000.00",
        "additions_ytd": "45000.00",
        "deposits_period": "5000.00",
        "deposits_ytd": "40000.00",
        "exchanges_in_period": "0.00",
        "exchanges_in_ytd": "5000.00",
        "subtractions_period": "1000.00",
        "subtractions_ytd": "8000.00",
        "withdrawals_period": "0.00",
        "withdrawals_ytd": "5000.00",
        "exchanges_out_period": "0.00",
        "exchanges_out_ytd": "2000.00",
        "transaction_costs_period": "50.00",
        "transaction_costs_ytd": "400.00",
        "taxes_withheld_period": "950.00",
        "taxes_withheld_ytd": "600.00",
        "change_in_inc_val_period": "21000.00",
        "change_in_inc_val_ytd": "8000.00",
        "ending_net_acct_val_period": "525000.00",
        "ending_net_acct_val_ytd": "525000.00",
        "accrued_interest": "437.50",
        "ending_net_acct_val_incl_ai": "525437.50"
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
        "stcg_tax_ex_period": "0.00",
        "stcg_tax_ex_ytd": "0.00",
        "int_tax_exempt_period": "200.00",
        "int_tax_exempt_ytd": "1600.00",
        "ltcg_tax_ex_period": "0.00",
        "ltcg_tax_ex_ytd": "0.00",
        "roc_period": "0.00",
        "roc_ytd": "0.00",
        "incsumm_total_period": "1700.00",
        "incsumm_total_ytd": "13600.00"
      },

      "realized_gains": {
        "netstgl_period": "300.00",
        "netstgl_ytd": "2300.00",
        "stg_period": "500.00",
        "stg_ytd": "3500.00",
        "netltgl_period": "4000.00",
        "netltgl_ytd": "12000.00",
        "ltg_period": "5000.00",
        "ltg_ytd": "15000.00",
        "net_gl_period": "4300.00",
        "net_gl_ytd": "14300.00"
      },

      "holdings": [
        {
          "source": "stocks",
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
          "source": "bonds",
          "sec_type": "Bonds",
          "sec_subtype": "Municipal Bonds",
          "sec_symbol": null,
          "cusip": "880558HN4",
          "sec_description": "TENNESSEE ST ENERGY ACQUISITI REF-BD TAXABLE",
          "maturity_date": "09/01/25",
          "coupon_rate": "5.25%",
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
          "next_call_date": "11/01/25",
          "call_price": "100.00",
          "payment_freq": "SEMIANNUALLY",
          "bond_features": "PRE-REFUNDED"
        },
        {
          "source": "options",
          "sec_type": "Options",
          "sec_subtype": "Calls",
          "sec_symbol": null,
          "cusip": null,
          "sec_description": "CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS)",
          "underlying_symbol": "GOOG",
          "strike_price": "$215",
          "expiration_date": "SEP 12 25",
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
          "source": "mutual_funds",
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
          "source": "exchange_traded_products",
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
          "source": "other",
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
      ,
      "holdings_subsection_totals": [
        {
          "section": "Mutual Funds",
          "subsection_label": "Stock Funds",
          "percent_of_account_holdings": "0%",
          "beg_market_value": "$21,839.13",
          "end_market_value": "$22,814.85",
          "cost_basis": "$21,355.50",
          "unrealized_gain_loss": "$1,459.35",
          "estimated_ann_inc": "$412.08",
          "est_yield": "1.29%"
        }
      ],
      "holdings_section_totals": [
        {
          "section": "Stocks",
          "subsection_label": null,
          "percent_of_account_holdings": "35%",
          "beg_market_value": "$1,414,604.80",
          "end_market_value": "$2,340,512.87",
          "cost_basis": "$1,925,109.38",
          "unrealized_gain_loss": "$415,403.49",
          "estimated_ann_inc": "$24,984.29"
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
- `source` (one of: `mutual_funds`, `exchange_traded_products`, `stocks`, `bonds`, `options`, `other`)
- `sec_type`
- `sec_subtype` (as shown in the statement, or best-effort for "Other")
- `sec_description`
- `quantity`
- `price_per_unit`
- `end_market_value`

### Conditional Fields
- `sec_symbol`: Required for stocks, mutual funds, ETPs, options; null for bonds unless shown
- `sec_identifiers`: Optional (e.g., ISIN/SEDOL) for stocks/preferred when present
- `cusip`: Required for bonds; null for others
- `maturity_date`: Required for bonds only (store as shown)
- `coupon_rate`: Required for bonds only (store as shown)
- `accrued_int`: Required for bonds only (store as shown)
- `underlying_symbol`, `strike_price`, `expiration_date`: Required for options only (store as shown)

### Optional Fields (Can be null)
- `beg_market_value`, `cost_basis`, `unrealized_gain_loss`, `estimated_ann_inc`, `est_yield`
- Bond optional fields: `agency_ratings`, `next_call_date`, `call_price`, `payment_freq`, `bond_features`
- Totals arrays: any field may be `null` if truly absent; keep "-" when shown

## LLM Extraction Instructions

**IMPORTANT:** You are extracting all holdings data directly from the PDF statement.

### Your Extraction Task:
1. **Read PDF statement** - Extract all holdings and document-level data
2. **Create complete JSON** - Generate full JSON structure from scratch
3. **Extract all fields** - Capture all data points from the PDF
4. **Complete doc_level_data** - All 20+ summary fields must be extracted
5. **Calculate MD5 hash** - Hash the completed JSON content
6. **Include all accounts** - Process every account in the statement

### Fields You Must Extract:
- **All holdings data:** `source`, `sec_type`, `sec_subtype`, `sec_description`, `quantity`, `price_per_unit`, `end_market_value`, `cost_basis`, `beg_market_value`, `estimated_ann_inc`, `est_yield`, `unrealized_gain_loss` (all stored as shown)
- **Security info:** `sec_symbol`, `sec_identifiers` (when present), `cusip`
- **Bonds:** `maturity_date`, `coupon_rate`, `accrued_int`, `agency_ratings`, `next_call_date`, `call_price`, `payment_freq`, `bond_features` (as shown)
- **Options:** `underlying_symbol`, `strike_price`, `expiration_date` (as shown). Long/short is implied solely by the sign of `quantity`; do not add a separate `position` field.
- **Account metadata:** `account_number`, `account_name`, `account_type`
- **Document-Level:** Complete `net_account_value`, `income_summary`, `realized_gains` sections
- **Holdings Totals:** `holdings_subsection_totals[]`, `holdings_section_totals[]` (as shown)

## Validation Rules

Scribe-only extraction. Validation is limited to structural presence of required fields. No numeric/date normalization or format validation is required in this spec. Values are captured exactly as shown in the source document.

### Source Field Allowed Values
`source` must be one of: `mutual_funds`, `exchange_traded_products`, `stocks`, `bonds`, `options`, `other`.

## Example: Handling Special Cases

### Missing Values
Statement shows: "unavailable"
JSON output: "unavailable"

### Negative Values
Statement shows: "($1,250.00)" or "-1,250.00"
JSON output: keep exactly as shown

### Percentages
Statement shows: "5.25%"
JSON output: `"5.25%"`

### Estimated Yield Format
Statement shows: "4.88%"
JSON output: `"4.88%"`

### Options Description Parsing
Statement shows: "CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS)"
JSON outputs:
- `"sec_description"`: Full text as shown
- `"source"`: `"options"`
- `"strike_price"`: `"$215"`
- `"expiration_date"`: `"SEP 12 25"`

---

*This specification ensures consistent, complete JSON output that can be reliably processed by the Python database loader.*