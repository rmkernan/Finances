# Fidelity Statement Document Map

**Created:** 09/18/25 1:20PM ET
**Updated:** 09/21/25 5:27PM ET - Enhanced Holdings tables with required field indicators and critical extraction notes, organized bond-specific guidance under Bond Holdings table
**Updated:** 09/21/25 6:24PM ET - Added Options and Other holdings sections, fixed typos, corrected formatting inconsistencies, simplified extraction guidance to "copy as shown"
**Updated:** 09/22/25 - Enhanced extraction guidance: treat all values as valid (including "unavailable"), added footnote indicators, expanded option ticker parsing, clarified Other holdings examples
**Updated:** 09/22/25 10:45AM - Refactored to focus on navigation and location guidance, removed interpretive content
**Updated:** 09/22/25 11:20AM - Simplified to pure data location guide: removed redundant notes, interpretive content, and explanations
**Updated:** 09/22/25 12:30PM - Added Document Structure Overview section for navigation context
**Updated:** 09/22/25 1:52PM - Clarified multi-account structure and extraction requirements for ALL accounts
**Updated:** 09/23/25 10:07PM - Updated DB columns to match JSON: agency_ratings, next_call_date
**Updated:** 09/22/25 6:04PM - Added Core Account section, standardized est_yield to percentage format (not decimal)
**Updated:** 09/22/25 6:17PM - Clarified that Realized Gains section only appears when sales occurred (use null when absent)
**Updated:** 09/22/25 7:58PM - Enhanced data transcription guidance to clarify faithful copying of all values including "unavailable"
**Updated:** 09/22/25 8:02PM - Added ETP classification guidance to trust Fidelity's categorization rather than second-guessing
**Updated:** 09/23/25 4:25PM - Added extraction vs classification philosophy and mapping system guidance
**Updated:** 09/26/25 12:40PM - Added Net Account Value table section to align with updated doc_level_data schema
**Updated:** 09/26/25 1:15PM - Enhanced data handling rules and precision requirements to serve as authoritative parsing guide
**Updated:** 09/26/25 1:26PM - Enhanced field markers for extraction workflow
**Updated:** 09/26/25 5:00PM - Removed field markers, reverted to pure LLM extraction from PDF
**Updated:** 09/26/25 5:45PM - Final cleanup of all extraction guidance for pure LLM workflow
**Updated:** 09/28/25 4:22PM - Added numbered subsection structure to match activities mapping approach
**Updated:** 09/28/25 4:26PM - Reordered holdings subsections to match PDF navigation structure
**Updated:** 09/28/25 4:40PM - Added source field mapping to all 6 holdings subsections for section identification

**Purpose:** This document provides task-specific instructions, guidance, and resources for the Fidelity Statement Extractor Agent. It augments the guidance and instruction provided in the agent definition file. 

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

## Claude's Role as Financial Data Scribe

You are acting as a highly efficient data entry clerk who can read financial statements and transcribe them into structured JSON format.

**Your Task:** Read through Fidelity statements and copy every relevant attribute and value into JSON, exactly as a human would if manually entering data into a spreadsheet - just much faster.

**The Goal:** Convert paper/PDF statements into a structured database so users can query and analyze their financial portfolio through natural language conversations.

**How to Use This Map:** This document shows you:
- WHERE to find each piece of data in Fidelity statements related to financial positions/holdings
- WHAT to call each field in your JSON output
- HOW each field maps to database columns

**Your Approach:** Like a human data entry clerk, you'll:
1. Navigate to each section mentioned in this map
2. Find the attributes listed in the tables
3. **Copy the values exactly as shown** - transcribe faithfully:
   - "unavailable" → `"cost_basis": "unavailable"`
   - "--" → `"cost_basis": "--"`
   - "n/a" → `"cost_basis": "n/a"`
   - Blank field → `"cost_basis": null`
   - Negative in parentheses: "($1,250.00)" → `"-1250.00"`
   - ANY text value is valid - just transcribe it

**Precision Requirements:**
- Preserve exact numeric values including all decimal places as shown
- Maintain original formatting for dates, account numbers, and security identifiers
- Convert percentage displays: "5.25%" → `"5.250"` (as percentage, not decimal)
- For estimated yield: "4.88%" → `"4.880"` (NOT `"0.0488"`)
4. Structure them into the specified JSON format

**Data Quality Rule:** Only report issues when fields are missing from PDF structure or illegible - NOT when they contain values like "unavailable"

## Document Structure Overview

**CRITICAL:** A single Fidelity statement PDF can contain MULTIPLE accounts. You must extract holdings data for ALL accounts in the document.

### Document Structure Pattern:
1. **Cover Page** - Portfolio value summary, contact info
2. **Portfolio Summary** - Lists ALL accounts in this statement
3. **For EACH Account in the statement:**
   - Account Summary with Net Account Value
   - Income Summary Table (for this account)
   - Realized Gains and Losses Table (for this account) - only present if sales occurred
   - Holdings Section (for this account) with numbered subsections:
     - **Section 1:** Mutual Funds subsection
     - **Section 2:** Exchange Traded Products subsection
     - **Section 3:** Stocks subsection
     - **Section 4:** Bonds subsection
     - **Section 5:** Options subsection
     - **Section 6:** Other subsection
4. **Activity** (OUT OF SCOPE for positions extraction)

**EXTRACTION REQUIREMENT:** You must iterate through EACH account listed in the "Accounts Included in This Report" section and extract ALL holdings for EACH account. Do not stop after the first account.

## Holdings Subsection Navigation Structure

**IMPORTANT:** The Holdings section for each account contains up to 6 numbered subsections that appear in order. Not all sections appear in every statement - presence depends on account holdings.

**Navigation Order in PDF:**
- **Section 1:** Mutual Funds - Actively managed fund holdings, money market funds, bond funds
- **Section 2:** Exchange Traded Products - ETFs, ETNs, and similar products
- **Section 3:** Stocks - Individual equity holdings and stock positions
- **Section 4:** Bonds - Corporate bonds, municipal bonds, treasuries
- **Section 5:** Options - Calls, puts, and complex option positions
- **Section 6:** Other - Miscellaneous holdings not fitting other categories

**Extraction Guidance:**
- Process subsections in the order they appear in the PDF
- Some subsections may be absent (e.g., no Options section if account holds no options)
- Each subsection has a clear header indicating the security type
- Extract ALL holdings from ALL present subsections for complete account coverage

**Source Field Values:**
Each holdings subsection requires a specific `source` value for section identification:
- **Section 1:** Mutual Funds → `source = "mutual_funds"`
- **Section 2:** Exchange Traded Products → `source = "exchange_traded_products"`
- **Section 3:** Stocks → `source = "stocks"`
- **Section 4:** Bonds → `source = "bonds"`
- **Section 5:** Options → `source = "options"`
- **Section 6:** Other → `source = "other"`


# Fidelity Statement Sections, subsections and attributes

## Portfolio Summary
Usually starts on page 2. may span several pages and ends at Account Summary

### Accounts Included in This Report
| Source Label       | JSON Field      | Database Column          | Type     | Notes                |
|--------------------|-----------------|--------------------------|----------|----------------------|
| Account Name       | account_name    | accounts.account_name    | TEXT     | From account header  |
| Account Number     | account_number  | accounts.account_number  | TEXT     | Exact as shown       |
| Beginning Value    | beginning_value | accounts.beg_value       | CURRENCY | Period start balance |
| Ending Value       | ending_value    | accounts.end_value       | CURRENCY | Period end balance   |


## Account Summary
There will be one or more account summary sub-sections, one for each account contained in the document, as listed in the "Accounts Included in This Report" section

### Net Account Value Section (at the account level)
Contains a table that shows cash flows and value changes for an account. It appears in the Account Summary section.

**Target Table:** `doc_level_data` with `doc_section = 'net_account_value'` with account_number from the Account Summary Header
| Source Label                               | JSON Field                  | Database Column                             | Type     | Notes                           |
|--------------------------------------------|-----------------------------|---------------------------------------------|----------|---------------------------------|
| Beginning Net Account Value (period)       | beg_net_acct_val_period     | doc_level_data.beg_net_acct_val_period     | CURRENCY | **REQ** Period start value      |
| Beginning Net Account Value (YTD)          | beg_net_acct_val_ytd        | doc_level_data.beg_net_acct_val_ytd        | CURRENCY | **REQ** YTD start value         |
| Additions (period)                         | additions_period            | doc_level_data.additions_period            | CURRENCY | Total additions this period     |
| Additions (YTD)                            | additions_ytd               | doc_level_data.additions_ytd               | CURRENCY | Total additions YTD             |
| Deposits (period)                          | deposits_period             | doc_level_data.deposits_period             | CURRENCY | Cash deposits this period       |
| Deposits (YTD)                             | deposits_ytd                | doc_level_data.deposits_ytd                | CURRENCY | Cash deposits YTD               |
| Exchanges In (period)                      | exchanges_in_period         | doc_level_data.exchanges_in_period         | CURRENCY | Transfers in this period        |
| Exchanges In (YTD)                         | exchanges_in_ytd            | doc_level_data.exchanges_in_ytd            | CURRENCY | Transfers in YTD                |
| Subtractions (period)                      | subtractions_period         | doc_level_data.subtractions_period         | CURRENCY | Total subtractions this period  |
| Subtractions (YTD)                         | subtractions_ytd            | doc_level_data.subtractions_ytd            | CURRENCY | Total subtractions YTD          |
| Withdrawals (period)                       | withdrawals_period          | doc_level_data.withdrawals_period          | CURRENCY | Cash withdrawals this period    |
| Withdrawals (YTD)                          | withdrawals_ytd             | doc_level_data.withdrawals_ytd             | CURRENCY | Cash withdrawals YTD            |
| Exchanges Out (period)                     | exchanges_out_period        | doc_level_data.exchanges_out_period        | CURRENCY | Transfers out this period       |
| Exchanges Out (YTD)                        | exchanges_out_ytd           | doc_level_data.exchanges_out_ytd           | CURRENCY | Transfers out YTD               |
| Transaction Costs, Fees & Charges (period) | transaction_costs_period    | doc_level_data.transaction_costs_period    | CURRENCY | Fees this period                |
| Transaction Costs, Fees & Charges (YTD)    | transaction_costs_ytd       | doc_level_data.transaction_costs_ytd       | CURRENCY | Fees YTD                        |
| Taxes Withheld (period)                    | taxes_withheld_period       | doc_level_data.taxes_withheld_period       | CURRENCY | Tax withholding this period     |
| Taxes Withheld (YTD)                       | taxes_withheld_ytd          | doc_level_data.taxes_withheld_ytd          | CURRENCY | Tax withholding YTD             |
| Change in Investment Value (period)        | change_in_inc_val_period    | doc_level_data.change_in_inc_val_period    | CURRENCY | **REQ** Market change period    |
| Change in Investment Value (YTD)           | change_in_inc_val_ytd       | doc_level_data.change_in_inc_val_ytd       | CURRENCY | Market change YTD               |
| Ending Net Account Value (period)          | ending_net_acct_val_period  | doc_level_data.ending_net_acct_val_period  | CURRENCY | **REQ** Period end value        |
| Ending Net Account Value (YTD)             | ending_net_acct_val_ytd     | doc_level_data.ending_net_acct_val_ytd     | CURRENCY | YTD end value                   |
| Accrued Interest (AI)                      | accrued_interest            | doc_level_data.accrued_interest            | CURRENCY | Bond accrued interest           |
| Ending Net Account Value Incl AI           | ending_net_acct_val_incl_ai | doc_level_data.ending_net_acct_val_incl_ai | CURRENCY | End value with accrued interest |

### Income Summary Section (at the account level)
Contains a table labeled Income Summary. It may span more than one page.

**Target Table:** `doc_level_data` with `doc_section = 'income_summary'` with account_number from the Account Summary Header
| Source Label                            | JSON Field              | Database Column                        | Type     | Notes                      |
|-----------------------------------      |-------------------------|----------------------------------------|----------|----------------------------|
| Taxable Total (period)                  | taxable_total_period    | doc_level_data.taxable_total_period    | CURRENCY | Fidelity's  total          |
| Taxable Total (YTD)                     | taxable_total_ytd       | doc_level_data.taxable_total_ytd       | CURRENCY | Fidelity's YTD total       |
| Taxable Dividends (period)              | divs_taxable_period     | doc_level_data.divs_taxable_period     | CURRENCY | Doc period's taxable divs  |
| Taxable Dividends (YTD)                 | divs_taxable_ytd        | doc_level_data.divs_taxable_ytd        | CURRENCY | YTD taxable divs           |
| Short-term Capital Gains (period).      | stcg_taxable_period     | doc_level_data.stcg_taxable_period     | CURRENCY | Doc period's ST gains      |
| Short-term Capital Gains (YTD)          | stcg_taxable_ytd        | doc_level_data.stcg_taxable_ytd        | CURRENCY | YTD short-term gains       |
| Taxable Interest (period)               | int_taxable_period      | doc_level_data.int_taxable_period      | CURRENCY | Doc period's taxable int   |
| Taxable Interest (YTD)                  | int_taxable_ytd         | doc_level_data.int_taxable_ytd         | CURRENCY | YTD taxable int            |
| Long-term Capital Gains (period)        | ltcg_taxable_period     | doc_level_data.ltcg_taxable_period     | CURRENCY | Doc period's LT gains      |
| Long-term Capital Gains (YTD)           | ltcg_taxable_ytd        | doc_level_data.ltcg_taxable_ytd        | CURRENCY | YTD long-term gains        |
| Tax-exempt Total (period)               | tax_exempt_total_period | doc_level_data.tax_exempt_total_period | CURRENCY | Fidelity's  total          |
| Tax-exempt Total (YTD)                  | tax_exempt_total_ytd    | doc_level_data.tax_exempt_total_ytd    | CURRENCY | Fidelity's YTD total       |
| Tax-exempt Dividends (period)           | divs_tax_exempt_period  | doc_level_data.divs_tax_exempt_period  | CURRENCY | Doc period's exempt divs   |
| Tax-exempt Dividends (YTD)              |  divs_tax_exempt_ytd    | doc_level_data.divs_tax_exempt_ytd     | CURRENCY | YTD tax-exempt divs        |
| Tax-exempt Interest (period)            | int_tax_exempt_period   | doc_level_data.int_tax_exempt_period   | CURRENCY | Doc period's exempt int    |
| Tax-exempt Interest (YTD)               | int_tax_exempt_ytd      | doc_level_data.int_tax_exempt_ytd      | CURRENCY | YTD tax-exempt int         |
| Short-term Capital Gains Tax-Ex (period)| stcg_tax_ex_period      | doc_level_data.stcg_tax_ex_period      | CURRENCY | Doc period's tax-ex ST gains|
| Short-term Capital Gains Tax-Ex (YTD)   |  stcg_tax_ex_ytd        | doc_level_data.stcg_tax_ex_ytd         | CURRENCY | YTD tax-ex ST gains         |
| Long-term Capital Gains Tax-Ex (period) | ltcg_tax_ex_period      | doc_level_data.ltcg_tax_ex_period      | CURRENCY | Doc period's tax-ex LT gains|
| Long-term Capital Gains Tax-Ex (YTD)    | ltcg_tax_ex_ytd         | doc_level_data.ltcg_tax_ex_ytd         | CURRENCY | YTD tax-ex LT gains         |
| Return of Capital (period)              | roc_period              | doc_level_data.roc_period              | CURRENCY | Doc period's ROC           |
| Return of Capital (YTD)                 | roc_ytd                 | doc_level_data.roc_ytd                 | CURRENCY | YTD return of capital      |
| Grand Total (period)                    | incsumm_total_period    | doc_level_data.incsumm_total_period    | CURRENCY | Income summary grand total |
| Grand Total (YTD)                       | incsumm_total_ytd       | doc_level_data.incsumm_total_ytd       | CURRENCY | Income summary YTD total   |

 

### Realized Gains and Losses from Sales Section
Contains a table that shows realized long-term and short-term gains and losses.
**Target Table:** `doc_level_data` with `doc_section = 'realized_gains'` with account_number from the Account Summary Header
**Important:** This section only appears when securities were sold during the period. If not present in the statement, set all realized_gains fields to null in the JSON. This is normal and expected.

| Source Label                       | JSON Field        | Database Column               | Type     | Notes                      |
|------------------------------------|------------------|-------------------------------|----------|-----------------------------|
| Net Short-term Gain/Loss (period)  | netstgl_period   | doc_level_data.netstgl_period | CURRENCY | Net ST gain/loss for period |
| Net Short-term Gain/Loss (YTD)     | netstgl_ytd      | doc_level_data.netstgl_ytd    | CURRENCY | Net ST gain/loss YTD        |
| Short-term Gain (period)           | stg_period       | doc_level_data.stg_period     | CURRENCY | ST gains only for period    |
| Short-term Gain (YTD)              | stg_ytd          | doc_level_data.stg_ytd        | CURRENCY | ST gains only YTD           |
| Net Long-term Gain/Loss (period)   | netltgl_period   | doc_level_data.netltgl_period | CURRENCY | Net LT gain/loss for period |
| Net Long-term Gain/Loss (YTD)      | netltgl_ytd      | doc_level_data.netltgl_ytd    | CURRENCY | Net LT gain/loss YTD        |
| Long-term Gain (period)            | ltg_period       | doc_level_data.ltg_period     | CURRENCY | LT gains only for period    |
| Long-term Gain (YTD)               | ltg_ytd          | doc_level_data.ltg_ytd        | CURRENCY | LT gains only YTD           |
| Net Gain/Loss (period)             | net_gl_period    | doc_level_data.net_gl_period  | CURRENCY | Total net gain/loss period  |
| Net Gain/Loss (YTD)                | net_gl_ytd       | doc_level_data.net_gl_ytd     | CURRENCY | Total net gain/loss YTD     |


### Holdings
There is one holding section per Account listed in the document. This section contains account holdings divided by holdings type and subtype. Each security type has specific attributes to extract.

#### 1. Mutual Fund Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Mutual Funds" | **Security Subtype:** "Stock Funds", "Bond Funds", "Short-Term Funds"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                           |
|-------------------------|----------------------|--------------------------------|----------|---------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Mutual Funds" |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header   |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier    |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                         |
| Symbol/Ticker           | sec_symbol           | positions.sec_symbol           | TEXT     | **REQ** - From parentheses      |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                 |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                         |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ** - NAV                   |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                         |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                 |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                 |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                 |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As % (e.g., 5.100 not 0.051).   |

##### Core Account (Part of Mutual Funds)
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Core Account" | **Security Subtype:** "Money Market" (typically)

| Source Label            | JSON Field           | Database Column                | Type     | Notes                            |
|-------------------------|----------------------|--------------------------------|----------|----------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Core Account"  |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - Usually "Money Market" |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier     |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                          |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - From parentheses       |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                  |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                          |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ** - Usually 1.0000         |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                          |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY | Usually "not applicable"         |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY | Usually "not applicable"         |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                  |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As & (e.g., 4.880 not 0.0488)    |

**Common Core Account Types:**
- FIDELITY GOVERNMENT MONEY MARKET (SPAXX)
- FIDELITY TREASURY MONEY MARKET (FZFXX)
- Other Fidelity money market funds

#### 2. Exchange Traded Products Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Exchange Traded Products" | **Security Subtype:** "Equity ETPs" (or other ETP types)

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                       |
|-------------------------|----------------------|--------------------------------|----------|---------------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Exchange Traded Products" |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header               |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier                |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                                     |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - Extract from parentheses          |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                             |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                                     |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                                     |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                                     |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                             |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                             |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                             |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As percentage (e.g., 5.100 not 0.051)|

##### ETP Classification Guidance
Fidelity groups various traded products under "Exchange Traded Products":
- Traditional ETFs (Exchange Traded Funds)
- ETNs (Exchange Traded Notes)
- Closed-end funds that trade like stocks
- Some specialty funds that trade on exchanges

**Classification Rule:**
- If Fidelity lists it under "Exchange Traded Products" → use `"sec_type": "ETPs"`
- Don't try to reclassify based on ticker or underlying type
- Copy Fidelity's categorization exactly as shown

**Examples:**
- VTI (Vanguard ETF) → "ETPs" (if that's where Fidelity puts it)
- ARKK (Innovation ETF) → "ETPs"
- Some bond funds → May appear as "ETPs" instead of "Mutual Funds"

**This is normal Fidelity categorization - trust the source document classification.**

#### 3. Stock Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Stocks" | **Security Subtype:** Determined by description content

| Source Label            | JSON Field           | Database Column                | Type     | Notes                              |
|-------------------------|----------------------|--------------------------------|----------|------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Stocks"          |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - See determination rules  |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier       |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                            |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - From parentheses         |
| Identifiers             | sec_identifiers      | positions.sec_identifiers      | TEXT     | e.g. ISIN, SEDOL, etc.             |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                    |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                            |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                            |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                            |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                    |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                    |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                    |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As percentage (e.g., 5.100 not 0.051)|

##### Stock Description Parsing
The stock description can contain extra identifiers like ISIN or SEDOL numbers.

**Pattern:** `[SECURITY_NAME] [IDENTIFIERS] ([TICKER])`

**Extraction Logic:**
- **`sec_description`**: Capture the core security name, which is the text up to the ISIN, SEDOL, or other long identifier string.
- **`sec_symbol`**: Extract from parentheses.
- **`sec_identifiers`**: Capture any remaining identifiers like ISIN or SEDOL numbers as a single text string.

**Example:** "ENBRIDGE INC 6.68304% PFD ISIN #CA29250N6679 SEDOL #BF67P82 (EBGEF)"
- `sec_description`: "ENBRIDGE INC 6.68304% PFD"
- `sec_symbol`: "EBGEF"
- `sec_identifiers`: "ISIN #CA29250N6679 SEDOL #BF67P82"

**Subtype Determination:**
- "Preferred Stock" if contains: PFD, PREFERRED, or dividend rate (e.g., "6.68304%")
- "Common Stock" otherwise

**Examples:**
- "AT&T INC COM USD1 (T)" → "Common Stock"
- "ENBRIDGE INC 6.68304% PFD (EBGEF)" → "Preferred Stock"
- "BOXFORD LANE CAP CORP CAL NT 27 5.00000% 01/31/2027 PFD (OXLCZ)" → "Preferred Stock"

#### 4. Bond Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Bonds" | **Security Subtype:** "Corporate Bonds" or "Municipal Bonds"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                  |
|-------------------------|----------------------|--------------------------------|----------|----------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Bonds"               |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header          |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier           |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                                |
| CUSIP                   | cusip                | positions.cusip                | TEXT     | **REQ** - From detail line             |
| Maturity Date           | maturity_date        | positions.maturity_date        | DATE     | **REQ** - MM/DD/YY format              |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                        |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                                |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                                |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                                |
| Accrued Interest        | accrued_int          | positions.accrued_int          | CURRENCY | **REQ** - Italic below market value    |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                        |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                        |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                        |
| Coupon Rate             | coupon_rate          | positions.coupon_rate          | NUMBER   | **REQ** - From last column             |
| Ratings                 | agency_ratings       | positions.agency_ratings       | TEXT     | Optional - From detail line            |
| Next Call Date          | next_call_date       | positions.next_call_date       | DATE     | Optional - Only if callable            |
| Call Price              | call_price           | positions.call_price           | NUMBER   | Optional - Only if callable            |
| Payment Frequency       | payment_freq         | positions.payment_freq         | TEXT     | **REQ** - From detail line             |
| Bond Features           | bond_features        | positions.bond_features        | TEXT     | Optional - Special features if present |

##### Bond Description & Detail Line Parsing
The full description for a bond holding is typically split into two lines within the statement's "Description" column.

- **Line 1 (The Name):** This is the human-readable name of the bond. This full line should be extracted as the `sec_description`.
- **Line 2 (The Detail Line):** This is a structured text block immediately following the name, containing the CUSIP, ratings, call information, and other key attributes. This line must be parsed to populate several different fields.

**Pattern (Detail Line):** `[BOND_FEATURES] [RATINGS] [FREQUENCY] [CALL_INFO] CUSIP: [CUSIP_NUMBER]`

**Extraction Logic (from Detail Line):**
- **`cusip`**: Extract the value that always appears at the end of the line, after "CUSIP:".
- **`agency_ratings`**: Extract any text matching "MOODYS [rating]" and/or "S&P [rating]".
- **`payment_freq`**: Extract the payment frequency (e.g., "SEMIANNUALLY", "ANNUALLY").
- **`next_call_date`**: Extract the date following "NEXT CALL DATE" or "CONT CALL".
- **`call_price`**: Extract the number following an "@" symbol or near the call date.
- **`bond_features`**: Extract any remaining descriptive text at the beginning of the line (e.g., "FIXED COUPON", "PRE-REFUNDED").

**Complete Example:**
- **Input Line 1:** "M TENNESSEE ST SCH BD AUTH HIGHER EDL FACS"
- **Input Line 2:** "FIXED COUPON PRE-REFUNDED 11/01/2025 @ 100.000 MOODYS Aa1 S&P AA+ SEMIANNUALLY CONT CALL 11/01/2025 CUSIP: 880558HN4"

- **Resulting JSON Fields:**
  - `sec_description`: "M TENNESSEE ST SCH BD AUTH HIGHER EDL FACS"
  - `cusip`: "880558HN4"
  - `agency_ratings`: "MOODYS Aa1 S&P AA+"
  - `payment_freq`: "SEMIANNUALLY"
  - `next_call_date`: "11/01/2025"
  - `call_price`: "100.000"
  - `bond_features`: "FIXED COUPON PRE-REFUNDED"

#### 5. Options
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Options" | **Security Subtype:** "Calls" or "Puts"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                               |
|-------------------------|----------------------|--------------------------------|----------|-------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Options"          |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - "Calls" or "Puts"         |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier        |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ** - The full description line |
| Symbol/Ticker           | sec_symbol           | positions.sec_symbol           | TEXT     | **REQ** - The full option symbol    |
| Underlying Symbol       | underlying_symbol    | positions.underlying_symbol    | TEXT     | **REQ** - From description parsing  |
| Strike Price            | strike_price         | positions.strike_price         | CURRENCY | **REQ** - From description parsing  |
| Expiration Date         | expiration_date      | positions.exp_date             | DATE     | **REQ** - From description parsing  |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                             |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                             |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY | Copy exactly as shown               |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                             |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                     |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                     |

##### Option Description Parsing
The option description line contains multiple structured attributes.

**Pattern:** `[SIDE] ([UNDERLYING]) [NAME] [EXP_DATE] $[STRIKE] [SHARES] ([FULL_SYMBOL]) [POSITION_TYPE]`

**Extraction Logic:**
- **`sec_subtype`**: "Puts" if description starts with `PUT`, "Calls" if it starts with `CALL`.
- **`underlying_symbol`**: Extract from the first set of parentheses.
- **`expiration_date`**: The date following the underlying name (e.g., "AUG 29 25").
- **`strike_price`**: The number following the dollar sign.
- **`sec_symbol`**: Capture the full, structured option symbol from the second set of parentheses (e.g., "TSLA250829P300").

**Example:** "M PUT (TSLA) TESLA INC COM AUG 29 25 $300 (100 SHS) (TSLA250829P300) SHT"
- `sec_subtype`: "Puts"
- `underlying_symbol`: "TSLA"
- `expiration_date`: "AUG 29 25"
- `strike_price`: "300"
- `sec_symbol`: "TSLA250829P300"

#### 6. Other Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Other" | **Security Subtype:** Derived from description

| Source Label            | JSON Field           | Database Column                | Type     | Notes                             |
|-------------------------|----------------------|--------------------------------|----------|-----------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Other"          |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | Derive from description           |
| Source                  | source               | positions.source               | TEXT     | **REQ** - Section identifier     |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                           |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | Extract if present in parentheses |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                   |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                           |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                           |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                           |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                   |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                   |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                   |
| Estimated Yield (EY)    | est_yield            | positions.eai_percentage       | NUMBER   |                                   |

**Common "Other" Types (with examples from statements):**
- REITs: "ANNALY CAPITAL MANAGEMENT INC COM NEW (NLY)"
- Partnerships: "MPLX LP COM UNIT REP LTD (MPLX)"
- Trusts: "CAMDEN PROPERTY TRUST SBI USD0.01 (CPT)"
- Warrants: "THE CANNABIST CO HLDGS CO 0.14 RESTRICTED WTS EXP 05/29/2027"
- Specialty: "NET LEASE OFFICE PROPERTIES COM (NLOP)"
- Income trusts: "WP CAREY INC COM (WPC)"



## Pattern Recognition Tips

### Finding Data in the Statement

**Holdings Section**
- Table with columns: Description | Quantity | Price | Market Value | Cost Basis | Gain/Loss
- Bonds: Market value on top, accrued interest in italics below
- Options: May show "unavailable" for some values


## Special Cases

### Bonds
- CUSIP: From detail line below description
- Accrued interest: Italic number under market value
- Call date: Look for "NEXT CALL DATE MM/DD/YYYY"

### Options
- Description pattern: TYPE SYMBOL COMPANY EXPIRY STRIKE
- Values may show "unavailable"

### Data Format Notes
- Include minus signs when present
- Include any prefixes (M, S) or suffixes (SHT) as part of the description
- "unavailable" is a value you'll encounter - transcribe it as-is
- Superscript markers (t, B, TF) are part of the text

