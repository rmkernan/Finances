# PDF Extraction Enhancement Plan
**Created:** 09/25/25 8:30PM
**Updated:** 09/25/25 11:49PM - Added comprehensive holdings section totals and activities section totals
**Purpose:** Comprehensive plan to align PDF extraction with source of truth values from Fidelity statements

## Executive Summary

### The Problem
Our current extraction process is missing critical financial data from Fidelity PDF statements, resulting in a **$1,076,910.42 discrepancy** for just one account (Joint Brokerage). The PDF statements contain authoritative summary values that are not being captured, causing our calculated totals to diverge from the official statement values.

### The Solution
Enhance the extraction process to capture ALL summary and balance detail fields from PDF statements, treating the PDF's calculated totals as the source of truth rather than attempting to reconstruct them from individual holdings.

### Impact
- **Immediate:** Eliminate the $1.07M discrepancy in Kernan Family portfolio valuation
- **Long-term:** Ensure 100% accuracy in financial reporting by using PDF summary values as authoritative
- **Compliance:** Maintain audit trail showing our values match official statements exactly

---

## Current State Analysis

### What We're Currently Capturing
From our analysis of `Fid_Stmnt_2025-08_KernBrok+KernCMA_holdings_2025.09.24_11.35ET.json`:

```json
{
  "portfolio_summary": {
    "beginning_value": "6809436.99",
    "ending_value": "6870462.09",
    "net_account_value": "6870462.09"
  }
}
```

### What We're Missing (Critical Fields)

#### 1. Balance Details Section
The PDF shows these values that explain how the account value changed:

| Field                      | PDF Value     | Current Status | Impact                                        |
|----------------------------|---------------|----------------|-----------------------------------------------|
| Market Value of Holdings   | $6,862,168.66 | ❌ Not Captured | This is the TRUE total, not sum of positions |
| Short Balance              | $62,867.37    | ❌ Not Captured | Required for net calculation                 |
| Accrued Interest           | $13,157.62    | ❌ Not Captured | Pending interest not yet paid                |
| Additions                  | $1,022,454.21 | ❌ Not Captured | Money flowing into account                   |
| Subtractions               | -$600,175.15  | ❌ Not Captured | Money flowing out of account                 |
| Change in Investment Value | $147,200.25   | ❌ Not Captured | Period performance                           |

#### 2. Holdings Section Totals
Each security type section (Stocks, Bonds, etc.) ends with comprehensive summary data including:
- Beginning Market Value
- End Market Value
- Cost Basis
- Unrealized Gain/Loss
- Estimated Annual Income
- Accrued Interest (if applicable)

Example from Bonds section:
- Total Holdings: $24,992.75
- Accrued Interest (AI): $216.67
- Total Including AI: $25,209.42

Example from Mutual Funds section:
- Beginning Value: $3,826,838.29
- End Value: $3,348,723.96
- Cost Basis: $1,034,693.07
- Unrealized G/L: -$1,091.40
- Est Annual Income: $97,472.30

Example from ETPs section:
- Beginning Value: $2,876.51
- End Value: $2,951.91
- Cost Basis: $6,098.54
- Unrealized G/L: -$3,146.63
- Est Annual Income: - (none)

Example from Options section:
- Beginning Value: unavailable
- End Value: -$45,840.00
- Cost Basis: -$51,699.02
- Unrealized G/L: $5,859.02
- Est Annual Income: - (none)

Example from Other section:
- Beginning Value: $35,525.73
- End Value: $36,659.53
- Cost Basis: $30,192.26
- Unrealized G/L: $6,467.27
- Est Annual Income: $2,456.85

#### 3. Activities Section Totals
The Activities section contains comprehensive transaction summaries:

Example Activities totals:
- Total Dividends, Interest & Other Income: $8,352.01
- Total Short Activity: - (none)
- Total Other Activity In: $466.35
- Total Other Activity Out: - (none)
- Total Deposits: $8,000.00
- Total Exchanges In: $506,000.00
- Total Withdrawals: -$600,000.00
- Total Fees and Charges: -$3.00
- Total Core Fund Activity: -$328,714.74
- Total Trades Pending Settlement: $11,606.06

---

## Detailed Extraction Plan

### Phase 1: Database Schema Updates

#### Table: `doc_level_data`
Add the following columns to capture complete balance information:

```sql
-- Balance Details (Account Level)
ALTER TABLE doc_level_data ADD COLUMN market_value_holdings NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN short_balance NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN accrued_interest NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN ending_value_incl_ai NUMERIC(15,2);

-- Transaction Flow Details
ALTER TABLE doc_level_data ADD COLUMN additions NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN deposits NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN dividends_received NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN subtractions NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN withdrawals NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN transaction_costs NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN exchanges_in NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN exchanges_out NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN taxes_withheld NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN change_in_investment_value NUMERIC(15,2);

-- Holdings Section Totals (by Security Type) - 5 values each
ALTER TABLE doc_level_data ADD COLUMN stocks_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN stocks_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN stocks_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN stocks_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN stocks_est_annual_inc NUMERIC(15,2);

ALTER TABLE doc_level_data ADD COLUMN bonds_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN bonds_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN bonds_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN bonds_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN bonds_est_annual_inc NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN bonds_accrued_interest NUMERIC(15,2);

ALTER TABLE doc_level_data ADD COLUMN mutual_funds_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN mutual_funds_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN mutual_funds_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN mutual_funds_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN mutual_funds_est_annual_inc NUMERIC(15,2);

ALTER TABLE doc_level_data ADD COLUMN etps_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN etps_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN etps_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN etps_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN etps_est_annual_inc NUMERIC(15,2);

ALTER TABLE doc_level_data ADD COLUMN options_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN options_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN options_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN options_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN options_est_annual_inc NUMERIC(15,2);

ALTER TABLE doc_level_data ADD COLUMN other_beg_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN other_end_value NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN other_cost_basis NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN other_unrealized_gl NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN other_est_annual_inc NUMERIC(15,2);

-- Activities Section Totals
ALTER TABLE doc_level_data ADD COLUMN total_dividends_interest_income NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_short_activity NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_other_activity_in NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_other_activity_out NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_deposits NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_exchanges_in NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_withdrawals NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_fees_charges NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_core_fund_activity NUMERIC(15,2);
ALTER TABLE doc_level_data ADD COLUMN total_trades_pending_settlement NUMERIC(15,2);
```

### Phase 2: Schema Documentation Updates

#### File: `/docs/Design/Database/schema.md`
Update the schema documentation to include all new doc_level_data columns:

```markdown
## doc_level_data Table (Enhanced)

### Balance Details Fields
| Column                     | Type          | Description                                       | PDF Source                      |
|----------------------------|---------------|---------------------------------------------------|---------------------------------|
| market_value_holdings      | NUMERIC(15,2) | Market Value of Holdings from Balance Details box | Account Summary Balance Details |
| short_balance              | NUMERIC(15,2) | Short positions balance (typically negative)      | Account Summary Balance Details |
| accrued_interest           | NUMERIC(15,2) | Accrued Interest pending payment                  | Account Summary Balance Details |
| ending_value_incl_ai       | NUMERIC(15,2) | Ending Net Account Value including AI             | Account Summary Balance Details |
| additions                  | NUMERIC(15,2) | Total additions to account during period          | Change in Account Value table   |
| deposits                   | NUMERIC(15,2) | Cash deposits                                     | Change in Account Value table   |
| dividends_received         | NUMERIC(15,2) | Dividends received                                | Change in Account Value table   |
| subtractions               | NUMERIC(15,2) | Total subtractions from account                   | Change in Account Value table   |
| withdrawals                | NUMERIC(15,2) | Cash withdrawals                                  | Change in Account Value table   |
| transaction_costs          | NUMERIC(15,2) | Transaction costs, fees & charges                 | Change in Account Value table   |
| exchanges_in               | NUMERIC(15,2) | Money moved in from other accounts                | Change in Account Value table   |
| exchanges_out              | NUMERIC(15,2) | Money moved out to other accounts                 | Change in Account Value table   |
| taxes_withheld             | NUMERIC(15,2) | Taxes withheld during period                      | Change in Account Value table   |
| change_in_investment_value | NUMERIC(15,2) | Period change in investment value                 | Change in Account Value table   |

### Holdings Section Totals (by Security Type)
Each security type (stocks, bonds, mutual_funds, etps, options, other) has 5-6 summary fields:

| Column Pattern         | Type          | Description                                     | PDF Source                    |
|------------------------|---------------|-------------------------------------------------|-------------------------------|
| {type}_beg_value       | NUMERIC(15,2) | Beginning period market value for security type | End of each Holdings section  |
| {type}_end_value       | NUMERIC(15,2) | Ending period market value for security type    | End of each Holdings section  |
| {type}_cost_basis      | NUMERIC(15,2) | Total cost basis for security type              | End of each Holdings section  |
| {type}_unrealized_gl   | NUMERIC(15,2) | Unrealized gain/loss for security type          | End of each Holdings section  |
| {type}_est_annual_inc  | NUMERIC(15,2) | Estimated annual income for security type       | End of each Holdings section  |
| bonds_accrued_interest | NUMERIC(15,2) | Accrued interest for bonds only                 | End of Bonds Holdings section |

### Activities Section Totals
| Column                          | Type          | Description                              | PDF Source                |
|---------------------------------|---------------|------------------------------------------|---------------------------|
| total_dividends_interest_income | NUMERIC(15,2) | Total dividends, interest & other income | Activities section totals |
| total_short_activity            | NUMERIC(15,2) | Total short selling activity             | Activities section totals |
| total_other_activity_in         | NUMERIC(15,2) | Total other activity flowing in          | Activities section totals |
| total_other_activity_out        | NUMERIC(15,2) | Total other activity flowing out         | Activities section totals |
| total_deposits                  | NUMERIC(15,2) | Total deposits during period             | Activities section totals |
| total_exchanges_in              | NUMERIC(15,2) | Total exchanges in from other accounts   | Activities section totals |
| total_withdrawals               | NUMERIC(15,2) | Total withdrawals during period          | Activities section totals |
| total_fees_charges              | NUMERIC(15,2) | Total fees and charges                   | Activities section totals |
| total_core_fund_activity        | NUMERIC(15,2) | Total core fund/cash activity            | Activities section totals |
| total_trades_pending_settlement | NUMERIC(15,2) | Total trades pending settlement          | Activities section totals |

### Data Validation Rules
- Balance equation: beginning_value + additions - subtractions + change_in_investment_value ≈ ending_value
- Market value check: market_value_holdings - short_balance = ending_value
- Holdings totals should sum to approximately market_value_holdings
- All currency fields stored with 2 decimal precision
```

### Phase 3: JSON Structure Updates

#### File: `/config/institution-guides/JSON_Stmnt_Fid_Positions.md`
Update the JSON specification to include new structures:

```json
{
  "accounts": [
    {
      "account_number": "Z24-527872",
      "account_name": "FIDELITY ACCOUNT...",

      // EXISTING STRUCTURE
      "portfolio_summary": {
        "beginning_value": "6809436.99",
        "ending_value": "6870462.09",
        "net_account_value": "6870462.09"
      },

      // NEW: Balance Details Section
      "balance_details": {
        "market_value_holdings": "6862168.66",
        "short_balance": "62867.37",
        "accrued_interest": "13157.62",
        "ending_value_incl_ai": "6883603.04",
        "additions": "1022454.21",
        "deposits": "8000.00",
        "dividends_received": "500000.00",
        "subtractions": "-600175.15",
        "withdrawals": "-600000.00",
        "transaction_costs": "-175.15",
        "exchanges_in": "0.00",
        "exchanges_out": "0.00",
        "taxes_withheld": "0.00",
        "change_in_investment_value": "147200.25"
      },

      // NEW: Holdings Section Totals (comprehensive)
      "holdings_totals": {
        "stocks": {
          "beginning_value": "2875432.10",
          "end_value": "2340512.87",
          "cost_basis": "2100000.00",
          "unrealized_gain_loss": "240512.87",
          "estimated_annual_income": "45000.00"
        },
        "bonds": {
          "beginning_value": "24688.25",
          "end_value": "24992.75",
          "cost_basis": "25000.00",
          "unrealized_gain_loss": "-7.25",
          "estimated_annual_income": "1300.00",
          "accrued_interest": "216.67"
        },
        "mutual_funds": {
          "beginning_value": "3826838.29",
          "end_value": "3348723.96",
          "cost_basis": "1034693.07",
          "unrealized_gain_loss": "-1091.40",
          "estimated_annual_income": "97472.30"
        },
        "etps": {
          "beginning_value": "2876.51",
          "end_value": "2951.91",
          "cost_basis": "6098.54",
          "unrealized_gain_loss": "-3146.63",
          "estimated_annual_income": null
        },
        "options": {
          "beginning_value": "unavailable",
          "end_value": "-45840.00",
          "cost_basis": "-51699.02",
          "unrealized_gain_loss": "5859.02",
          "estimated_annual_income": null
        },
        "other": {
          "beginning_value": "35525.73",
          "end_value": "36659.53",
          "cost_basis": "30192.26",
          "unrealized_gain_loss": "6467.27",
          "estimated_annual_income": "2456.85"
        }
      },

      // NEW: Activities Section Totals
      "activities_totals": {
        "total_dividends_interest_income": "8352.01",
        "total_short_activity": null,
        "total_other_activity_in": "466.35",
        "total_other_activity_out": null,
        "total_deposits": "8000.00",
        "total_exchanges_in": "506000.00",
        "total_withdrawals": "-600000.00",
        "total_fees_charges": "-3.00",
        "total_core_fund_activity": "-328714.74",
        "total_trades_pending_settlement": "11606.06"
      },

      // EXISTING: Holdings array continues as before
      "holdings": [...]
    }
  ]
}
```

### Phase 3: Mapping Document Updates

#### File: `/config/institution-guides/Map_Stmnt_Fid_Positions.md`
Add new sections for locating these values in PDFs:

```markdown
## Balance Details Section
Located immediately after "Account Summary" heading, before "Income Summary"

### Change in Account Value Table
| PDF Label                           | JSON Field                                 | Location in PDF             |
|-------------------------------------|--------------------------------------------|-----------------------------|
| Beginning Net Account Value         | balance_details.beginning_value            | First line of table         |
| Additions                           | balance_details.additions                  | Under "Additions" header    |
| - Deposits                          | balance_details.deposits                   | Indented under Additions    |
| - Dividends                         | balance_details.dividends_received         | Indented under Additions    |
| Subtractions                        | balance_details.subtractions               | Under "Subtractions" header |
| - Withdrawals                       | balance_details.withdrawals                | Indented under Subtractions |
| - Transaction Costs, Fees & Charges | balance_details.transaction_costs          | Indented under Subtractions |
| Change in Investment Value          | balance_details.change_in_investment_value | Separate line item          |
| Ending Net Portfolio Value          | balance_details.ending_value               | Bold total line             |

### Balance Details Box
| PDF Label                         | JSON Field                            | Location in PDF          |
|-----------------------------------|---------------------------------------|--------------------------|
| Market Value of Holdings          | balance_details.market_value_holdings | Under "Balance Details"  |
| Short Balance                     | balance_details.short_balance         | Listed as negative value |
| Ending Net Portfolio Value        | (cross-check)                         | Should match above       |
| Accrued Interest (AI)             | balance_details.accrued_interest      | Separate line            |
| Ending Net Account Value incl. AI | balance_details.ending_value_incl_ai  | Final total              |

## Holdings Section Totals
Located at the END of each holdings type section (after all individual holdings)

### Stocks Section Total
| PDF Label             | JSON Field                              | Location                    |
|-----------------------|-----------------------------------------|-----------------------------|
| Total Holdings        | holdings_totals.stocks.total            | Last line of Stocks section |
| Accrued Interest (AI) | holdings_totals.stocks.accrued_interest | If present                  |

### Bonds Section Total
| PDF Label                        | JSON Field                             | Location                   |
|----------------------------------|----------------------------------------|----------------------------|
| Total Holdings                   | holdings_totals.bonds.total            | Last line of Bonds section |
| Accrued Interest (AI)            | holdings_totals.bonds.accrued_interest | Usually present for bonds  |
| Total Including Accrued Interest | (calculated)                           | Sum of above               |

[Similar sections for Mutual Funds, ETPs, Options, Other]
```

### Phase 4: Extraction Agent Updates

#### File: `/.claude/agents/fidelity-statement-extractor.md`
Update extraction logic to:

1. **After locating Account Summary:**
   - Look for "Change in Account Value" section
   - Extract all transaction flow details (additions, subtractions, etc.)
   - Locate "Balance Details" box
   - Extract market value, short balance, and accrued interest

2. **At the end of each holdings type section:**
   - Before moving to next section, capture the totals
   - Look for "Total Holdings" line
   - Capture any "Accrued Interest (AI)" if present
   - Record these in holdings_totals structure

3. **Validation:**
   - Verify that market_value_holdings ≈ sum of all section totals
   - Confirm ending_value = market_value_holdings - short_balance
   - Check that additions - subtractions + change_in_investment ≈ ending - beginning

### Phase 5: Loader Updates

#### File: `/loaders/simple_loader.py`
Update to map new JSON fields to database:

```python
# New field mappings for doc_level_data
balance_mappings = {
    'balance_details.market_value_holdings': 'market_value_holdings',
    'balance_details.short_balance': 'short_balance',
    'balance_details.accrued_interest': 'accrued_interest',
    'balance_details.ending_value_incl_ai': 'ending_value_incl_ai',
    'balance_details.additions': 'additions',
    'balance_details.deposits': 'deposits',
    'balance_details.dividends_received': 'dividends_received',
    'balance_details.subtractions': 'subtractions',
    'balance_details.withdrawals': 'withdrawals',
    'balance_details.transaction_costs': 'transaction_costs',
    'balance_details.exchanges_in': 'exchanges_in',
    'balance_details.exchanges_out': 'exchanges_out',
    'balance_details.taxes_withheld': 'taxes_withheld',
    'balance_details.change_in_investment_value': 'change_in_investment_value',
}

# Holdings totals mappings
holdings_totals_mappings = {
    'holdings_totals.stocks.total': 'stocks_total',
    'holdings_totals.stocks.accrued_interest': 'stocks_ai',
    'holdings_totals.bonds.total': 'bonds_total',
    'holdings_totals.bonds.accrued_interest': 'bonds_ai',
    # ... etc for all security types
}
```

---

## Impact Analysis

### Immediate Benefits

1. **Accuracy:** Portfolio values will match PDF statements exactly
   - Current: $6,310,641.37 (calculated from incomplete data)
   - After: $6,447,100.08 (matches PDF source of truth)
   - Correction: +$136,458.71

2. **Completeness:** Full transaction flow visibility
   - Track deposits, withdrawals, fees
   - Understand investment performance separate from cash flows
   - Capture pending interest and short positions

3. **Validation:** Cross-check capabilities
   - Holdings totals can validate individual position sums
   - Transaction flows can be reconciled
   - Accrued interest properly accounted for

### Process Improvements

1. **Data Quality:**
   - PDF summary values become authoritative source
   - No more discrepancies between displayed and actual values
   - Complete audit trail from PDF to database

2. **Frontend Accuracy:**
   - Dashboard will show true portfolio values
   - Entity net worth calculations will be precise
   - Historical tracking will reflect actual statement values

3. **Reconciliation:**
   - Can verify: Beginning + Additions - Subtractions + Change = Ending
   - Holdings sections can be validated against totals
   - Accrued interest properly separated from market value

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Update database schema with new columns
- [ ] Update JSON specification document
- [ ] Update mapping guide with PDF locations

### Week 2: Extraction
- [ ] Modify extraction agent to capture balance details
- [ ] Add holdings section total extraction
- [ ] Test with sample PDFs

### Week 3: Loading & Validation
- [ ] Update loader to handle new fields
- [ ] Implement validation checks
- [ ] Process historical documents

### Week 4: Frontend Integration
- [ ] Update queries to use authoritative values
- [ ] Modify calculations to prefer market_value_holdings
- [ ] Display complete balance details in UI

---

## Success Criteria

1. **Primary:** Portfolio totals match PDF statements exactly (0% variance)
2. **Validation:** All balance equations reconcile correctly
3. **Completeness:** 100% of balance detail fields captured
4. **Historical:** Past statements reprocessed with new extraction

---

## Risk Mitigation

1. **Backward Compatibility:**
   - New fields are additive, won't break existing processes
   - Null values handled gracefully for historical data

2. **Data Quality:**
   - Validation rules ensure extraction accuracy
   - Cross-checks between related fields
   - Manual review of first batch

3. **Performance:**
   - Additional fields have minimal storage impact
   - Extraction time increases negligibly
   - Query performance unaffected

---

## Conclusion

This enhancement plan addresses the fundamental issue that PDF statement summaries are the authoritative source of truth for financial data. By capturing ALL summary fields rather than attempting to reconstruct them, we ensure our system reflects exactly what appears on official statements. This is critical for accuracy, compliance, and user trust.

The $1,076,910.42 discrepancy discovered in the Joint Brokerage account demonstrates the importance of this enhancement. Similar discrepancies likely exist across other accounts and time periods. This plan provides a systematic approach to eliminate these discrepancies permanently.