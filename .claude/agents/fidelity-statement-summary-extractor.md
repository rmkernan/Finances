# Fidelity Statement Summary Extractor Agent (PDF-Only Data)

**Created:** 09/26/25 12:45PM - Focused PDF extraction for data not in CSV
**Purpose:** Extract document-level summary data from PDFs that isn't available in CSV exports

## Extraction Focus Areas

### 1. Income Summary Table (CRITICAL for taxes)
Extract from "Account Income Summary" section:
- **Taxable Income Breakdown:**
  - Taxable dividends (period/YTD)
  - Taxable interest (period/YTD)
  - Short-term capital gains distributions (period/YTD)
  - Long-term capital gains distributions (period/YTD)
- **Tax-Exempt Income Breakdown:**
  - Tax-exempt dividends (period/YTD)
  - Tax-exempt interest (period/YTD)
  - Municipal bond interest (period/YTD)
- **Other Income:**
  - Return of capital (period/YTD)
  - Grand totals (period/YTD)

### 2. Realized Gains/Losses Section
Extract from "Realized Gain/Loss from Sales" table:
- Net short-term gains/losses (period/YTD)
- Net long-term gains/losses (period/YTD)
- Total net gains/losses (period/YTD)
- Individual sale details if needed

### 3. Account Cash Flow Summary
Extract from account summary sections:
- **Additions:**
  - Deposits (period/YTD)
  - Exchanges in (period/YTD)
  - Other additions (period/YTD)
- **Subtractions:**
  - Withdrawals (period/YTD)
  - Exchanges out (period/YTD)
  - Transaction costs & fees (period/YTD)
  - Taxes withheld (period/YTD)

### 4. Account Net Value Changes
Extract beginning/ending values with YTD comparisons:
- Beginning net account value (period/YTD)
- Change in investment value (period/YTD)
- Ending net account value (period/YTD)
- Accrued interest adjustments

## Data NOT to Extract (Available in CSV)

**SKIP these sections entirely:**
- ❌ Current positions/holdings tables
- ❌ Individual security details
- ❌ Position quantities and prices
- ❌ Cost basis for current holdings
- ❌ Basic account totals already in CSV

## Extraction Output

Generate JSON with ONLY the document-level summary data:

```json
{
  "extraction_metadata": {
    "extraction_type": "document_summary",
    "csv_companion_file": "Statement8312025.csv",
    "pages_processed": [1, 2, 15, 16],  // Only summary pages
    "extraction_timestamp": "2025.09.26_12.45ET"
  },

  "document_data": {
    "institution": "Fidelity",
    "statement_date": "2025-08-31",
    "period_start": "2025-08-01",
    "period_end": "2025-08-31"
  },

  "account_summaries": [
    {
      "account_number": "Z27375656",

      "income_summary": {
        "taxable_dividends_period": "163.23",
        "taxable_dividends_ytd": "3155.88",
        "taxable_interest_period": "22.52",
        "taxable_interest_ytd": "135.98",
        "tax_exempt_interest_period": null,
        "tax_exempt_interest_ytd": null,
        // ... other income fields
      },

      "realized_gains": {
        "net_stgl_period": null,
        "net_stgl_ytd": null,
        "net_ltgl_period": null,
        "net_ltgl_ytd": null
      },

      "cash_flows": {
        "deposits_period": null,
        "deposits_ytd": null,
        "withdrawals_period": null,
        "withdrawals_ytd": null,
        "fees_period": null,
        "fees_ytd": null
      }
    }
  ]
}
```

## Benefits of This Approach

1. **Reduced Processing:** ~70% less PDF content to analyze
2. **Faster Extraction:** Focus on 4-5 pages instead of 20+
3. **Higher Accuracy:** No complex position parsing needed
4. **Tax Focus:** Prioritizes tax-critical data extraction
5. **Complementary:** Works alongside CSV position data

## Integration with CSV Data

The loader will:
1. First load positions from CSV (fast, accurate)
2. Then load summary data from this PDF extraction
3. Combine both for complete financial picture
4. Use CSV for current state, PDF for historical flows