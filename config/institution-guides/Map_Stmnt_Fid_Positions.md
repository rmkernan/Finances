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
**Purpose:** Navigation guide for locating and extracting positions/holdings data from Fidelity statements

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
   - ANY text value is valid - just transcribe it
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
   - Holdings Section (for this account)
     - Stocks subsection
     - Bonds subsection
     - Mutual Funds subsection
     - Exchange Traded Products subsection
     - Options subsection
     - Other subsection
4. **Activity** (OUT OF SCOPE for positions extraction)

**EXTRACTION REQUIREMENT:** You must iterate through EACH account listed in the "Accounts Included in This Report" section and extract ALL holdings for EACH account. Do not stop after the first account.

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
There will be one or more account summary sections, one for each account contained in the document, as listed in the "Accounts Included in This Report" section

| Source Label      | JSON Field      | Database Column               | Type     | Notes                 |
|-------------------|-----------------|-------------------------------|----------|-----------------------|
| Net Account Value | net_acct_value  | doc_level_data.net_acct_value | CURRENCY | under Account Summary |


### Income Summary Table (at the account level)
This is a table labeled Income Summary under each Account Summary section. It may span more than one page. 

**Target Table:** `doc_level_data` with `doc_section = 'income_summary_table'` with account_number from the Account Summary Header
| Source Label                      | JSON Field              | Database Column                        | Type     | Notes                      |
|-----------------------------------|-------------------------|----------------------------------------|----------|----------------------------|
| Taxable Total (period)            | taxable_total_period    | doc_level_data.taxable_total_period    | CURRENCY | Fidelity's  total          |
| Taxable Total (YTD)               | taxable_total_ytd       | doc_level_data.taxable_total_ytd       | CURRENCY | Fidelity's YTD total       |
| Taxable Dividends (period)        | divs_taxable_period     | doc_level_data.divs_taxable_period     | CURRENCY | Doc period's taxable divs  |
| Taxable Dividends (YTD)           | divs_taxable_ytd        | doc_level_data.divs_taxable_ytd        | CURRENCY | YTD taxable divs           |
| Short-term Capital Gains (period) | stcg_taxable_period     | doc_level_data.stcg_taxable_period     | CURRENCY | Doc period's ST gains      |
| Short-term Capital Gains (YTD)    | stcg_taxable_ytd        | doc_level_data.stcg_taxable_ytd        | CURRENCY | YTD short-term gains       |
| Taxable Interest (period)         | int_taxable_period      | doc_level_data.int_taxable_period      | CURRENCY | Doc period's taxable int   |
| Taxable Interest (YTD)            | int_taxable_ytd         | doc_level_data.int_taxable_ytd         | CURRENCY | YTD taxable int            |
| Long-term Capital Gains (period)  | ltcg_taxable_period     | doc_level_data.ltcg_taxable_period     | CURRENCY | Doc period's LT gains      |
| Long-term Capital Gains (YTD)     | ltcg_taxable_ytd        | doc_level_data.ltcg_taxable_ytd        | CURRENCY | YTD long-term gains        |
| Tax-exempt Total (period)         | tax_exempt_total_period | doc_level_data.tax_exempt_total_period | CURRENCY | Fidelity's  total          |
| Tax-exempt Total (YTD)            | tax_exempt_total_ytd    | doc_level_data.tax_exempt_total_ytd    | CURRENCY | Fidelity's YTD total       |
| Tax-exempt Dividends (period)     | divs_tax_exempt_period  | doc_level_data.divs_tax_exempt_period  | CURRENCY | Doc period's exempt divs   |
| Tax-exempt Dividends (YTD)        | divs_tax_exempt_ytd     | doc_level_data.divs_tax_exempt_ytd     | CURRENCY | YTD tax-exempt divs        |
| Tax-exempt Interest (period)      | int_tax_exempt_period   | doc_level_data.int_tax_exempt_period   | CURRENCY | Doc period's exempt int    |
| Tax-exempt Interest (YTD)         | int_tax_exempt_ytd      | doc_level_data.int_tax_exempt_ytd      | CURRENCY | YTD tax-exempt int         |
| Return of Capital (period)        | roc_period              | doc_level_data.roc_period              | CURRENCY | Doc period's ROC           |
| Return of Capital (YTD)           | roc_ytd                 | doc_level_data.roc_ytd                 | CURRENCY | YTD return of capital      |
| Grand Total (period)              | grand_total_period      | doc_level_data.grand_total_period      | CURRENCY | Fidelity's grand total     |
| Grand Total (YTD)                 | grand_total_ytd         | doc_level_data.grand_total_ytd         | CURRENCY | Fidelity's YTD grand total |


### Realized Gains and Losses from Sales Table
**Target Table:** `doc_level_data` with `doc_section = 'real_gain_loss_table'` with account_number from the Account Summary Header
**Important:** This section only appears when securities were sold during the period. If not present in the statement, set all realized_gains fields to null in the JSON. This is normal and expected.
| Source Label             | JSON Field     | Database Column               | Type     | Notes  |
|--------------------------|----------------|-------------------------------|----------|--------|
| Short-term Gain (period) | st_gain_period | doc_level_data.st_gain_period | CURRENCY |        |
| Short-term Loss (period) | st_loss_period | doc_level_data.st_loss_period | CURRENCY |        |
| Long-term Gain (YTD)     | lt_gain_ytd    | doc_level_data.lt_gain_ytd    | CURRENCY |        |
| Long-term Loss (YTD)     | lt_loss_ytd    | doc_level_data.lt_loss_ytd    | CURRENCY |        |


### Holdings
There is one holding section per account listed in the document. This section contains account holdings divided by holdings type and subtype. Each security type has specific attributes to extract.

#### Stock Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Stocks" | **Security Subtype:** Determined by description content

| Source Label            | JSON Field           | Database Column                | Type     | Notes                              |
|-------------------------|----------------------|--------------------------------|----------|------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Stocks"          |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - See determination rules  |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                            |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - From parentheses         |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                    |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                            |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                            |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                            |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                    |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                    |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                    |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As percentage (e.g., 5.100 not 0.051)|

**Subtype Determination:**
- "Preferred Stock" if contains: PFD, PREFERRED, or dividend rate (e.g., "6.68304%")
- "Common Stock" otherwise

**Examples:**
- "AT&T INC COM USD1 (T)" → "Common Stock"
- "ENBRIDGE INC 6.68304% PFD (EBGEF)" → "Preferred Stock"
- "BOXFORD LANE CAP CORP CAL NT 27 5.00000% 01/31/2027 PFD (OXLCZ)" → "Preferred Stock"

#### Bond Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Bonds" | **Security Subtype:** "Corporate Bonds" or "Municipal Bonds"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                  |
|-------------------------|----------------------|--------------------------------|----------|----------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Bonds"               |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header          |
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

##### Bond Detail Line Parsing
Bonds have a detail line immediately below the description containing structured attributes. Parse as follows:

**Pattern:** `[COUPON_TYPE] [RATINGS] [FREQUENCY] [CALL_INFO] CUSIP: [CUSIP_NUMBER]`

**Examples:**
```
[FIXED COUPON PRE-REFUNDED 11/01/2025 @ 100.000] [MOODYS Aa1 S&P AA+] [SEMIANNUALLY]  [CONT CALL 11/01/2025] [CUSIP: 880558HN4]
[FIXED COUPON] [MOODYS Ba1 S&P BB+] [SEMIANNUALLY] [NEXT CALL DATE 09/05/2025] [CUSIP: 74348GRW2]
[FIXED COUPON] [S&P A] [SEMIANNUALLY] [EXTRAORDINARY CALL] [CUSIP: 499527BV0]
[FIXED COUPON] [MOODYS Aa1] [SEMIANNUALLY] [NEXT CALL DATE 09/30/2025 100.00] [CUSIP: 432074EU2]
```

**Parsing Pattern:**
- CUSIP: Always at end after "CUSIP:"
- Agency Ratings: "MOODYS [rating]" and/or "S&P [rating]"
- Payment Frequency: SEMIANNUALLY, ANNUALLY, etc.
- Call Date: After "NEXT CALL DATE" or "CONT CALL"
- Call Price: Number following "@" or before CUSIP
- Bond Features: PRE-REFUNDED, etc. if present


#### Mutual Fund Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Mutual Funds" | **Security Subtype:** "Stock Funds", "Bond Funds", "Short-Term Funds"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                              |
|-------------------------|----------------------|--------------------------------|----------|------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Mutual Funds"    |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header      |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                            |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - From parentheses         |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                    |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                            |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ** - NAV                      |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                            |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                    |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                    |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                    |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As percentage (e.g., 5.100 not 0.051)|

#### Exchange Traded Products Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Exchange Traded Products" | **Security Subtype:** "Equity ETPs" (or other ETP types)

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                       |
|-------------------------|----------------------|--------------------------------|----------|---------------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Exchange Traded Products" |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - From section header               |
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

#### Options
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Options" | **Security Subtype:** "Calls" or "Puts"

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                      |
|-------------------------|----------------------|--------------------------------|----------|--------------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Options"                 |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - "Calls" or "Puts"                |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                                    |
| Underlying Symbol       | underlying_symbol    | positions.underlying_symbol    | TEXT     | **REQ** - Extract from description         |
| Strike Price            | strike_price         | positions.strike_price         | CURRENCY | **REQ** - Extract from description         |
| Expiration Date         | expiration_date      | positions.exp_date             | DATE     | **REQ** - MM/DD/YY format from description |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                                    |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ**                                    |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY | Copy exactly as shown                      |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                                    |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY |                                            |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY |                                            |


**Description Pattern:**
`[CALL/PUT] ([SYMBOL]) [UNDERLYING NAME] [EXP DATE] $[STRIKE] (100 SHS)`

**Examples:**
- "CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS)"
- "PUT (TSLA) TESLA INC COM AUG 29 25 $300 (100 SHS)"
- "M PUT (NVDA) NVIDIA CORPORATION AUG 29 25 $175 (100 SHS) SHT"

**Option Ticker Pattern (when present):**
`[SYMBOL][YYMMDD][C/P][STRIKE]`
Example: `GOOG250912C215` → GOOG, 250912, C, 215


#### Core Account
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Core Account" | **Security Subtype:** "Money Market" (typically)

| Source Label            | JSON Field           | Database Column                | Type     | Notes                                  |
|-------------------------|----------------------|--------------------------------|----------|----------------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Core Account"        |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | **REQ** - Usually "Money Market"       |
| Description             | sec_description      | positions.sec_name             | TEXT     | **REQ**                                |
| Symbol/Ticker           | sec_symbol           | positions.sec_ticker           | TEXT     | **REQ** - From parentheses             |
| Beginning Market Value  | beg_market_value     | positions.beg_market_value     | CURRENCY |                                        |
| Quantity                | quantity             | positions.quantity             | NUMBER   | **REQ**                                |
| Price Per Unit          | price_per_unit       | positions.price                | CURRENCY | **REQ** - Usually 1.0000               |
| Ending Market Value     | end_market_value     | positions.end_market_value     | CURRENCY | **REQ**                                |
| Total Cost Basis        | cost_basis           | positions.cost_basis           | CURRENCY | Usually "not applicable"               |
| Unrealized Gain/Loss    | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY | Usually "not applicable"               |
| Est Annual Income (EAI) | estimated_ann_inc    | positions.estimated_ann_inc    | CURRENCY |                                        |
| Estimated Yield (EY %)  | est_yield            | positions.est_yield            | NUMBER   | As percentage (e.g., 4.880 not 0.0488)|

**Common Core Account Types:**
- FIDELITY GOVERNMENT MONEY MARKET (SPAXX)
- FIDELITY TREASURY MONEY MARKET (FZFXX)
- Other Fidelity money market funds

#### Other Holdings
**Target Table:** `positions` with `account_number` from Account Summary Header
**Security Type:** "Other" | **Security Subtype:** Derived from description

| Source Label            | JSON Field           | Database Column                | Type     | Notes                             |
|-------------------------|----------------------|--------------------------------|----------|-----------------------------------|
| Security Type           | sec_type             | positions.sec_type             | TEXT     | **REQ** - Always "Other"          |
| Security Subtype        | sec_subtype          | positions.sec_subtype          | TEXT     | Derive from description           |
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

