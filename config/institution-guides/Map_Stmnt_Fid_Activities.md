# Fidelity Statement Activity Document Map

**Created:** 09/22/25 3:45PM ET
**Updated:** 09/22/25 2:17PM ET - Aligned with positions map: separated ticker/CUSIP, added sec_ prefix to JSON fields, standardized naming conventions
**Updated:** 09/22/25 5:21PM ET - Added multi-line description parsing guidance and Bill Payments section details
**Updated:** 09/22/25 6:13PM ET - Clarified bond redemption pricing, dividend reinvestment dual-entry, and null handling based on agent feedback
**Updated:** 09/22/25 8:02PM ET - Enhanced bond redemption section with specific examples and clarified normal null price behavior
**Updated:** 09/23/25 4:25PM - Added extraction vs classification philosophy and mapping system guidance
**Updated:** 09/24/25 10:30AM - Updated mapping system references to reflect new three-table configuration-driven approach with enhanced transaction lifecycle tracking
**Updated:** 09/26/25 1:15PM - Added comprehensive field handling rules and precision requirements to serve as authoritative parsing guide
**Updated:** 09/26/25 6:30PM - Added source field mappings for all numbered activity sections
**Updated:** 09/26/25 6:59PM - Added account structure guidance, clarified Other Activity source assignment, and added total activity fields
**Updated:** 09/28/25 3:11PM - Enhanced faithful transcription principle and added variable statement content guidance
**Updated:** 09/28/25 3:47PM - Added section 11 (Trades Pending Settlement) with trade_date field and pending flag attribute
**Updated:** 09/28/25 4:00PM - Added section-level total fields to all 11 activity sections for comprehensive statement reconciliation

**Purpose:** This document provides task-specific instructions, guidance, and resources for the Fidelity Statement Extractor Agent. It augments the guidance and instruction provided in the agent definition file. 

## ⚙️ Extraction vs Classification Philosophy

**IMPORTANT:** This guide focuses on **pure transcription** from PDF statements. The extractor should capture data exactly as shown without interpretation or classification.

**Transaction Classification:** Happens automatically in the loader using a sophisticated three-table configuration-driven mapping system:
- **Transaction types:** dividend vs interest vs trade categorization with precise subtypes
- **Options lifecycle:** Enhanced tracking of opening/closing transactions with call/put identification
- **Complex conditions:** Support for compound matching rules (e.g., specific descriptions in specific sections)
- **Tax categorization:** Accurate municipal bond vs dividend classification for proper tax treatment
- **Multiple field updates:** Single transaction can trigger multiple classification actions simultaneously

**System Architecture:**
- **map_rules:** Master rule definitions with business context and processing order
- **map_conditions:** Complex trigger logic supporting AND/OR compound conditions for transaction pattern matching
- **map_actions:** Multiple field updates per rule enabling comprehensive transaction classification

**Extractor Responsibility:** Accurate transaction data capture from PDF exactly as shown
**Loader Responsibility:** Transaction classification using configurable database-driven rules with user-friendly management interface

**New Transaction Patterns:** When encountering unknown transaction types, the loader can accommodate new classification rules through a user-friendly CSV interface without code changes. Unknown patterns receive generic classification and are flagged for potential rule creation.

### Transaction Description Handling
Extract transaction descriptions exactly as shown in the PDF. Do not attempt to standardize or categorize - the advanced mapping system handles complex transaction patterns:

**CORE PRINCIPLE: Faithful Transcription**
Extract whatever value is actually present, regardless of what it is. Only blank/empty fields become `null`.

**Field Value Handling Rules:**
- **Any visible value** → extract exactly as shown (numbers, letters, dashes, "n/a", "--", "unavailable", etc.)
- **Truly blank/empty field** → use `null` in JSON
- **Dashes ("-")** → transcribe as `"-"` (this is a value, not blank)
- **"n/a" or "N/A"** → transcribe exactly as shown
- **"unavailable"** → transcribe as `"unavailable"`
- **Negative in parentheses:** "($1,250.00)" → `"-1250.00"`
- **Zero amounts:** Use `"0.00"` for explicit zeros, `null` for blank/missing
- **Any other text/symbols** → transcribe exactly as they appear

**Precision Requirements:**
- Preserve exact numeric values including all decimal places as shown
- Maintain original formatting for dates, account numbers, and reference numbers
- Sign conventions: Purchases/debits negative, sales/credits positive

**Enhanced Transaction Classification Examples:**
- "OPENING TRANSACTION - BUY 5 CALL (AAPL)" → opening_transaction subtype + call classification + options tracking
- "CLOSING TRANSACTION - SELL PUT" → closing_transaction subtype + put classification for P&L matching
- "Muni Exempt Int" in dividends_interest_income section → interest/muni_exempt (tax-free municipal bond classification)
- "ASSIGNED CALLS" → assignment subtype + call classification for tax reporting
- "Dividend Received" → dividend/received classification with qualified dividend determination
- "Interest Earned" → interest/deposit classification separate from dividend income


## Claude's Role as Financial Activity Transcriber

You are extracting transaction and activity data from Fidelity statements to create a comprehensive record of all financial activities.

**Your Task:** Identify and extract all transaction activities, cash flows, and account events from Fidelity statements into structured JSON format.

**The Goal:** Convert all account activity from PDF statements into a structured format for transaction analysis and reconciliation.

**Document Structure Note:** A single Fidelity statement PDF contains activity for MULTIPLE accounts. You must extract activity data for ALL accounts listed in the document.

**Account Structure:** Each statement contains one or more account summary sections. Each account section shows:
- Account owner's name
- Account number
- Account activity section with numbered subsections (1-10 as described below)

**Account Number Extraction:** The account number for each transaction comes from the account header section that precedes the activity data. This account number must be included with every transaction record to identify which account the activity belongs to.

**Variable Statement Content:** Not every statement will contain all 11 activity sections. Extract only the sections and attributes that are actually present in the specific statement. Look for all possible attributes within each section, but only extract what is visible. Different statements may have different combinations of activity types depending on account activity during the statement period.

## Activity Section Structure

The Activity section appears after the Holdings section for each account and contains:

1. **Securities Bought & Sold** - Trading transactions
2. **Dividends, Interest & Other Income** - Income transactions
3. **Short Activity** - Short position activities
4. **Other Activity In/Out** - Options expirations, assignments, etc.
5. **Deposits** - Cash deposits into account
6. **Withdrawals** - Cash withdrawals from account
7. **Exchanges In/Out** - Transfers between accounts
8. **Fees and Charges** - Account fees
9. **Cards, Checking & Bill Payments** - Card and bill pay transactions
10. **Core Fund Activity** - Money market fund transactions
11. **Trades Pending Settlement** - Unsettled trades with future settlement dates

## 1. Securities Bought & Sold

**Target Table:** `transactions` `source = 'sec_bot_sold'`
**Location:** First subsection under Activity for each account

| Source Label              | JSON Field       | Database Column             | Type     | Notes                      |
|---------------------------|------------------|-----------------------------|----------|----------------------------|
| Settlement Date           | settlement_date  | transactions.sett_date      | DATE     | MM/DD format               |
| Security Name             | sec_description  | transactions.security_name  | TEXT     | extract text exactly       |
| Symbol/CUSIP              | symbol_cusip     | transactions.symbol_cusip   | TEXT     | extract text exactly       |
| Description               | description      | transactions.desc    | TEXT     | extract text exactly       |
| Quantity                  | quantity         | transactions.quantity       | NUMBER   | Shares/units traded        |
| Price                     | price_per_unit   | transactions.price_per_unit | CURRENCY | Per share price            |
| Total Cost Basis          | cost_basis       | transactions.cost_basis     | CURRENCY | For sales only             |
| Transaction Cost          | transaction_cost | transactions.fees           | CURRENCY | Commission/fees            |
| Amount                    | amount           | transactions.amount         | CURRENCY | Total transaction amount   |
| Total Securities Bought   | total_sec_bot    | transactions.section_total  | CURRENCY | Section subtotal for purch |
| Total Securities Sold     | total_sec_sold   | transactions.section_total  | CURRENCY | Section subtotal for sales |
| Net Securities Bot & Sold | net_sec_act      | transactions.section_total  | CURRENCY | Net activity for section   |


## 2. Dividends, Interest & Other Income

**Target Table:** `transactions` with `source = 'div_int_income'`
**Location:** After Securities Bought & Sold

| Source Label        | JSON Field       | Database Column                  | Type     | Notes                |
|---------------------|------------------|----------------------------------|----------|----------------------|
| Settlement Date     | settlement_date  | transactions.sett_date           | DATE     | MM/DD format         |
| Security Name       | sec_description  | transactions.security_name       | TEXT     | Full security name   |
| Symbol/CUSIP        | symbol_cusip     | transactions.symbol_cusip        | TEXT     | extract text exactly |
| Description         | description      | transactions.desc         | TEXT     | Type of income       |
| Quantity            | quantity         | transactions.quantity            | NUMBER   | For reinvestments    |
| Price               | price_per_unit   | transactions.price_per_unit      | CURRENCY | For reinvestments    |
| Amount              | amount           | transactions.amount              | CURRENCY | Income amount        |
| Ttl Div, Int & Other Inc | total_div_int_inc | transactions.section_total | CURRENCY | Section subtotal     |


## 3. Short Activity

**Target Table:** `transactions` with `source = 'short_activity'`
OUT OF SCOPE


## 4. Other Activity In/Out

**Target Table:** `transactions` with `source = 'other_activity_in'` or `source = 'other_activity_out'`
**Location:** Separate sections for options/assignments

**Source Assignment:** Use section header to determine source value:
- If section header reads "Other Activity In" → use `source = 'other_activity_in'`
- If section header reads "Other Activity Out" → use `source = 'other_activity_out'`

### Other Activity In
| Source Label    | JSON Field       | Database Column                  | Type     | Notes                          |
|-----------------|------------------|----------------------------------|----------|--------------------------------|
| Settlement Date | settlement_date  | transactions.sett_date           | DATE     | MM/DD format                   |
| Security Name   | sec_description  | transactions.security_name       | TEXT     | Option/security description    |
| Symbol/CUSIP    | symbol_cusip     | transactions.symbol_cusip        | TEXT     | extract text exactly           |
| Description     | description      | transactions.desc         | TEXT     | "Expired", "Return Of Capital" |
| Quantity        | quantity         | transactions.quantity            | NUMBER   | Contract quantity              |
| Cost Basis      | cost_basis       | transactions.cost_basis          | CURRENCY | Original cost                  |
| Amount          | amount           | transactions.amount              | CURRENCY | Transaction amount             |

### Other Activity Out
| Source Label            | JSON Field       | Database Column             | Type     | Notes                |
|-------------------------|------------------|-----------------------------|----------|----------------------|
| Settlement Date         | settlement_date  | transactions.sett_date      | DATE     | MM/DD format         |
| Security Name           | sec_description  | transactions.security_name  | TEXT     | Option description   |
| Symbol/CUSIP            | symbol_cusip     | transactions.symbol_cusip   | TEXT     | extract text exactly |
| Description             | description      | transactions.desc    | TEXT     | "Assigned"           |
| Quantity                | quantity         | transactions.quantity       | NUMBER   | Contracts assigned   |
| Total Other Activity In  | total_act_in    | transactions.section_total  | CURRENCY | Section subtotal     |
| Total Other Activity Out | total_act_out   | transactions.section_total  | CURRENCY | Section subtotal     |

## 5. Deposits

**Target Table:** `transactions` with `source = 'deposits'`
**Location:** Separate section

| Source Label   | JSON Field  | Database Column               | Type     | Notes               |
|----------------|-------------|-------------------------------|----------|---------------------|
| Date           | date        | transactions.sett_date        | DATE     | MM/DD format        |
| Reference      | reference   | transactions.reference_number | TEXT     | Internal reference  |
| Description    | description | transactions.desc      | TEXT     | Deposit description |
| Amount         | amount      | transactions.amount           | CURRENCY | Deposit amount      |
| Total Deposits | total_dep   | transactions.section_total    | CURRENCY | Section subtotal    |

## 6. Withdrawals

**Target Table:** `transactions` with `source = 'withdrawals'`
**Location:** Separate section

| Source Label   | JSON Field     | Database Column            | Type     | Notes                  |
|----------------|----------------|----------------------------|----------|------------------------|
| Date           | date           | transactions.sett_date     | DATE     | MM/DD format           |
| Reference      | reference      | transactions.reference_number | TEXT     | Extract all text       |
| Description    | description    | transactions.desc   | TEXT     | Withdrawal description |
| Amount         | amount         | transactions.amount        | CURRENCY | Withdrawal amount      |
| Total Withdrwls| total_withdrwls| transactions.section_total | CURRENCY | Section subtotal       |

**Common Patterns:**
- Wire transfers show destination bank details
- Format: "Wire Tfr To Bank [Reference] [Bank Name] [Account ending]"

## 7. Exchanges In/Out

**Target Table:** `transactions` with `source = 'exchanges_in'` or `source = 'exchanges_out'`
**Location:** Separate sections

| Source Label        | JSON Field      | Database Column              | Type     | Notes                         |
|---------------------|-----------------|------------------------------|----------|------------------------------ |
| Date                | date            | transactions.sett_date       | DATE     | MM/DD format                  |
| Security Name       | sec_description | transactions.security_name   | TEXT     | Account identifier            |
| Symbol/CUSIP        | symbol_cusip    | transactions.symbol_cusip    | TEXT     | extract text exactly          |
| Description         | description     | transactions.desc     | TEXT     | "Transferred From/To"         | 
| Amount              | amount          | transactions.amount          | CURRENCY | Transfer amount               |
| Total Exchanges In  | total_exch_in   | transactions.section_total   | CURRENCY | Section subtotal for xfers in |
| Total Exchanges Out | total_exch_out  | transactions.section_total   | CURRENCY | Section subtotal for xfers out|

## 8. Fees and Charges

**Target Table:** `transactions` with `source = 'fees_charges'`
**Location:** Separate section

| Source Label.          | JSON Field         | Database Column            | Type     | Notes                 |
|------------------------|--------------------|----------------------------|----------|-----------------------|
| Date                   | date               | transactions.sett_date     | DATE     | MM/DD format          |
| Description            | description        | transactions.desc          | TEXT     | Fee description       |
| Amount                 | amount             | transactions.amount        | CURRENCY | Fee amount (negative) |
| Total Fees and Charges | total_fees_charges | transactions.section_total | CURRENCY | Section subtotal      |

## 9. Cards, Checking & Bill Payments

**Target Table:** `transactions` with `source = 'bill_payments'`
**Location:** Separate section in cash management accounts

| Source Label    | JSON Field     | Database Column            | Type     | Notes                  |
|-----------------|----------------|----------------------------|----------|------------------------|
| Post Date       | post_date      | transactions.sett_date     | DATE     | MM/DD format           |
| Payee           | payee          | transactions.payee         | TEXT     | Bill payment recipient |
| Payee Account   | payee_account  | transactions.payee_account | TEXT     | Masked account number  |
| Amount          | amount         | transactions.amount        | CURRENCY | Payment amount (neg)   |
| YTD Payments    | ytd_payments   | transactions.ytd_amount    | CURRENCY | Year-to-date total     |
| Total Bill Paym | total_bill_pay | transactions.section_total | CURRENCY | Section subtotal       |

**Example from statement:**
```
Post Date  Payee                   Payee Account      Amount        YTD Payments
08/29      CHASE CARD SERVICES     ************5793   -$18,132.00   $61,534.00
```

## 10. Core Fund Activity

**Target Table:** `transactions` with `source = 'core_fund'`
**Location:** Detailed money market fund transactions

| Source Label        | JSON Field      | Database Column             | Type     | Notes                      |
|---------------------|-----------------|-----------------------------|----------|----------------------------|
| Settlement Date     | settlement_date | transactions.sett_date      | DATE     | MM/DD format               |
| Account Type        | account_type    | transactions.account_type   | TEXT     | "CASH"                     |
| Transaction         | transaction     | transactions.desc           | TEXT     | "You Bought" or "You Sold" |
| Description         | sec_description | transactions.security_name  | TEXT     | Core fund name             |
| Quantity            | quantity        | transactions.quantity       | NUMBER   | Shares                     |
| Price               | price_per_unit  | transactions.price_per_unit | CURRENCY | Usually $1.0000            |
| Amount              | amount          | transactions.amount         | CURRENCY | Transaction amount         |
| Balance             | balance         | transactions.balance        | CURRENCY | Running balance            |
| Total Core Fund Act | total_core      | transactions.section_total  | CURRENCY | Section subtotal           |


## 11. Trades Pending Settlement

**Target Table:** `transactions` with `source = 'trades_pending'`
**Location:** Section showing unsettled trades with future settlement dates

| Source Label     | JSON Field       | Database Column                  | Type     | Notes                      |
|------------------|------------------|----------------------------------|----------|----------------------------|
| Trade Date       | trade_date       | transactions.trade_date          | DATE     | MM/DD format               |
| Settlement Date  | settlement_date  | transactions.sett_date           | DATE     | MM/DD format (future)      |
| Security Name    | sec_description  | transactions.security_name       | TEXT     | extract text exactly       |
| Symbol/CUSIP     | symbol_cusip     | transactions.symbol_cusip        | TEXT     | extract text exactly       |
| Description      | description      | transactions.desc         | TEXT     | extract text exactly       |
| Quantity         | quantity         | transactions.quantity            | NUMBER   | Shares/units traded        |
| Price            | price_per_unit   | transactions.price_per_unit      | CURRENCY | Per share price            |
| Total Cost Basis | cost_basis       | transactions.cost_basis          | CURRENCY | For sales only             |
| Amount           | amount           | transactions.amount              | CURRENCY | Total transaction amount   |
| Status           | pending          | transactions.pending             | BOOLEAN  | Always true for this section |
| Total Trades Pending Settlement | total_trades_pending | transactions.section_total | CURRENCY | Section subtotal |

**Note:** These transactions have already occurred (trade_date) but have not yet settled (settlement_date is in the future). Extract all the same fields as Securities Bought & Sold, but include both trade_date and settlement_date, and mark pending as true.


## Special Parsing Considerations

### Multi-line Security Descriptions
Securities (especially bonds and complex options) often span multiple lines in the PDF. Concatenate all lines that are part of the same transaction into a single description field.

**Bond Example:**
```
PDF shows:
WISCONSIN ST HEALTH & EDL FACS
AUTH REV
05.00000% 11/15/2027 FULL CALL PAYOUT
#REOR R6006628610000

Extract as single description:
"WISCONSIN ST HEALTH & EDL FACS AUTH REV 05.00000% 11/15/2027 FULL CALL PAYOUT #REOR R6006628610000"
```

**Option Example:**
```
PDF shows:
PUT (COIN) COINBASE GLOBAL INC
AUG 15 25 $300 (100 SHS) OPENING
TRANSACTION

Extract as single description:
"PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION"
```

### Option Transactions
Options show additional details in the security name:
- Contract type: CALL or PUT
- Underlying symbol in parentheses
- Expiration date
- Strike price
- Position: OPENING or CLOSING TRANSACTION

Example: "PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION"

### Bond Redemption Transactions
Bonds being called or maturing show complex descriptions with embedded data:

**Typical Redemption Description Pattern:**
`[ISSUER] REV [RATE]% [MATURITY] [REDEMPTION_TYPE] PAYOUT #[REFERENCE_ID]`

**Examples:**
- `WISCONSIN ST HEALTH & EDL FACS AUTH REV 05.00000% 11/15/2027 FULL CALL PAYOUT #REOR R6006628610000`
- `CLIFTON TEX HIGHER ED FIN CORP ED REV 05.00000% 08/15/2025 REDEMPTION PAYOUT #REOR R6006569090000`

**Redemption Transaction Rules:**
- Copy full description exactly as shown (don't truncate reference numbers)
- **Price handling**: When price shows "-" for redemptions, use "-" (this is normal)
- **Cost basis**: Usually null for redemptions (this is normal)
- **All attributes**: Use null for blank/missing values (not "0.00"), Otherwise, extract whatever value is present
- Reference numbers (#REOR, etc.) are part of the description

**This is normal bond redemption behavior - not a parsing challenge**

## Data Extraction Order

For each account in the statement:
1. Extract all Securities Bought & Sold
2. Extract all Dividends, Interest & Other Income
3. Extract Short Activity (if present)
4. Extract Other Activity In/Out (if present)
5. Extract Deposits
6. Extract Withdrawals
7. Extract Exchanges In/Out (if present)
8. Extract Fees and Charges
9. Extract Cards, Checking & Bill Payments (if present)
10. Extract Core Fund Activity (if detailed)
11. Extract Trades Pending Settlement (if present)

## Required Fields for All Transactions

Every transaction record should include all values present for all attributes. If an attribute is truly blank, only then use "null"

Required fields:
- `account_number` - From the account header section
- `source` - Activity section identifier (e.g., 'sec_bot_sold', 'div_int_income', 'trades_pending')
- `settlement_date` or `date` or `post_date` - As labeled in source section
- `amount` - Transaction amount with proper sign
- `description` - Transaction description
- `pending` - Boolean flag (true for trades_pending section, false for all others) 