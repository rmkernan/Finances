# Fidelity Statement Activity Document Map

**Created:** 09/22/25 3:45PM ET
**Updated:** 09/22/25 2:08PM ET - Aligned database column names with actual schema (security_identifier, price_per_unit)
**Updated:** 09/22/25 2:17PM ET - Aligned with positions map: separated ticker/CUSIP, added sec_ prefix to JSON fields, standardized naming conventions
**Updated:** 09/22/25 5:21PM ET - Added multi-line description parsing guidance and Bill Payments section details
**Updated:** 09/22/25 6:13PM ET - Clarified bond redemption pricing, dividend reinvestment dual-entry, and null handling based on agent feedback
**Updated:** 09/22/25 8:02PM ET - Enhanced bond redemption section with specific examples and clarified normal null price behavior
**Purpose:** Navigation guide for locating and extracting account activity data from Fidelity statements

## Claude's Role as Financial Activity Transcriber

You are extracting transaction and activity data from Fidelity statements to create a comprehensive record of all financial activities.

**Your Task:** Identify and extract all transaction activities, cash flows, and account events from Fidelity statements into structured JSON format.

**The Goal:** Convert all account activity from PDF statements into a structured format for transaction analysis and reconciliation.

**Document Structure Note:** A single Fidelity statement PDF contains activity for MULTIPLE accounts. You must extract activity data for ALL accounts listed in the document.

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

## 1. Securities Bought & Sold

**Target Table:** `transactions` with `transaction_type = 'TRADE'`
**Location:** First subsection under Activity for each account

| Source Label     | JSON Field       | Database Column              | Type     | Notes                      |
|------------------|------------------|------------------------------|----------|----------------------------|
| Settlement Date  | settlement_date  | transactions.settlement_date | DATE     | MM/DD format               |
| Security Name    | sec_description  | transactions.security_name   | TEXT     | Full security description  |
| Symbol           | sec_symbol       | transactions.security_identifier | TEXT     | Trading symbol (stocks/ETFs/funds) |
| CUSIP            | cusip            | transactions.cusip           | TEXT     | CUSIP (bonds)              |
| Description      | description      | transactions.description     | TEXT     | "You Bought" or "You Sold" |
| Quantity         | quantity         | transactions.quantity        | NUMBER   | Shares/units traded        |
| Price            | price_per_unit   | transactions.price_per_unit  | CURRENCY | Per share price            |
| Total Cost Basis | cost_basis       | transactions.cost_basis      | CURRENCY | For sales only             |
| Transaction Cost | transaction_cost | transactions.fees            | CURRENCY | Commission/fees            |
| Amount           | amount           | transactions.amount          | CURRENCY | Total transaction amount   |

**Parsing Notes:**
- "You Bought" = BUY transaction (amount is negative)
- "You Sold" = SELL transaction (amount is positive)
- Options transactions include details like "OPENING TRANSACTION" or "CLOSING TRANSACTION"
- Some entries show gain/loss information (e.g., "Short-term gain: $10,683.02")

## 2. Dividends, Interest & Other Income

**Target Table:** `transactions` with `transaction_type = 'INCOME'`
**Location:** After Securities Bought & Sold

| Source Label    | JSON Field       | Database Column              | Type     | Notes               |
|-----------------|------------------|------------------------------|----------|---------------------|
| Settlement Date | settlement_date  | transactions.settlement_date | DATE     | MM/DD format        |
| Security Name   | sec_description  | transactions.security_name   | TEXT     | Full security name  |
| Symbol          | sec_symbol       | transactions.security_identifier | TEXT     | Trading symbol      |
| CUSIP           | cusip            | transactions.cusip           | TEXT     | CUSIP if bond       |
| Description     | description      | transactions.description     | TEXT     | Type of income      |
| Quantity        | quantity         | transactions.quantity        | NUMBER   | For reinvestments   |
| Price           | price_per_unit   | transactions.price_per_unit  | CURRENCY | For reinvestments   |
| Amount          | amount           | transactions.amount          | CURRENCY | Income amount       |

**Income Types:**
- "Dividend Received" - Regular dividend
- "Muni Exempt Int" - Tax-exempt municipal interest
- "Interest Earned" - Taxable interest
- "Reinvestment" - Dividend reinvestment (appears as dual entry:
  1. Negative amount for the reinvestment purchase
  2. Positive amount for the dividend received)
- "Return Of Capital" - ROC distribution

## 3. Short Activity
OUT OF SCOPE


## 4. Other Activity In/Out

**Target Table:** `transactions` with `transaction_type = 'OTHER'`
**Location:** Separate sections for options/assignments

### Other Activity In
| Source Label    | JSON Field       | Database Column              | Type     | Notes                          |
|-----------------|------------------|------------------------------|----------|--------------------------------|
| Settlement Date | settlement_date  | transactions.settlement_date | DATE     | MM/DD format                   |
| Security Name   | sec_description  | transactions.security_name   | TEXT     | Option/security description    |
| Symbol          | sec_symbol       | transactions.security_identifier | TEXT     | Trading symbol                 |
| CUSIP           | cusip            | transactions.cusip           | TEXT     | CUSIP if applicable            |
| Description     | description      | transactions.description     | TEXT     | "Expired", "Return Of Capital" |
| Quantity        | quantity         | transactions.quantity        | NUMBER   | Contract quantity              |
| Cost Basis      | cost_basis       | transactions.cost_basis      | CURRENCY | Original cost                  |
| Amount          | amount           | transactions.amount          | CURRENCY | Transaction amount             |

### Other Activity Out
| Source Label    | JSON Field       | Database Column              | Type   | Notes              |
|-----------------|------------------|------------------------------|--------|--------------------|
| Settlement Date | settlement_date  | transactions.settlement_date | DATE   | MM/DD format       |
| Security Name   | sec_description  | transactions.security_name   | TEXT   | Option description |
| Symbol          | sec_symbol       | transactions.security_identifier | TEXT   | Option symbol      |
| CUSIP           | cusip            | transactions.cusip           | TEXT   | CUSIP if applicable|
| Description     | description      | transactions.description     | TEXT   | "Assigned"         |
| Quantity        | quantity         | transactions.quantity        | NUMBER | Contracts assigned |

## 5. Deposits

**Target Table:** `transactions` with `transaction_type = 'DEPOSIT'`
**Location:** Separate section

| Source Label | JSON Field  | Database Column               | Type     | Notes                     |
|--------------|-------------|-------------------------------|----------|---------------------------|
| Date         | date        | transactions.settlement_date  | DATE     | MM/DD format              |
| Reference    | reference   | transactions.reference_number | TEXT     | Internal reference        |
| Description  | description | transactions.description      | TEXT     | Deposit description       |
| Amount       | amount      | transactions.amount           | CURRENCY | Deposit amount (positive) |

## 6. Withdrawals

**Target Table:** `transactions` with `transaction_type = 'WITHDRAWAL'`
**Location:** Separate section

| Source Label | JSON Field  | Database Column               | Type     | Notes                        |
|--------------|-------------|-------------------------------|----------|------------------------------|
| Date         | date        | transactions.settlement_date  | DATE     | MM/DD format                 |
| Reference    | reference   | transactions.reference_number | TEXT     | Wire reference number        |
| Description  | description | transactions.description      | TEXT     | Withdrawal description       |
| Amount       | amount      | transactions.amount           | CURRENCY | Withdrawal amount (negative) |

**Common Patterns:**
- Wire transfers show destination bank details
- Format: "Wire Tfr To Bank [Reference] [Bank Name] [Account ending]"

## 7. Exchanges In/Out

**Target Table:** `transactions` with `transaction_type = 'TRANSFER'`
**Location:** Separate sections

| Source Label  | JSON Field       | Database Column              | Type     | Notes                 |
|---------------|------------------|------------------------------|----------|-----------------------|
| Date          | date             | transactions.settlement_date | DATE     | MM/DD format          |
| Security Name | sec_description  | transactions.security_name   | TEXT     | Account identifier    |
| Symbol        | sec_symbol       | transactions.security_identifier | TEXT     | Usually blank → null  |
| CUSIP         | cusip            | transactions.cusip           | TEXT     | Usually blank → null  |
| Description   | description      | transactions.description     | TEXT     | "Transferred From/To" |
| Amount        | amount           | transactions.amount          | CURRENCY | Transfer amount       |

## 8. Fees and Charges

**Target Table:** `transactions` with `transaction_type = 'FEE'`
**Location:** Separate section

| Source Label | JSON Field  | Database Column              | Type     | Notes                 |
|--------------|-------------|------------------------------|----------|-----------------------|
| Date         | date        | transactions.settlement_date | DATE     | MM/DD format          |
| Description  | description | transactions.description     | TEXT     | Fee description       |
| Amount       | amount      | transactions.amount          | CURRENCY | Fee amount (negative) |

## 9. Cards, Checking & Bill Payments

**Target Table:** `transactions` with `transaction_type = 'BILLPAY'`
**Location:** Separate section in cash management accounts

| Source Label  | JSON Field    | Database Column              | Type     | Notes                     |
|---------------|---------------|------------------------------|----------|---------------------------|
| Post Date     | post_date     | transactions.settlement_date | DATE     | MM/DD format              |
| Payee         | payee         | transactions.payee           | TEXT     | Bill payment recipient    |
| Payee Account | payee_account | transactions.payee_account   | TEXT     | Masked account number     |
| Amount        | amount        | transactions.amount          | CURRENCY | Payment amount (negative) |
| YTD Payments  | ytd_payments  | transactions.ytd_amount      | CURRENCY | Year-to-date total        |

**Example from statement:**
```
Post Date  Payee                   Payee Account      Amount        YTD Payments
08/29      CHASE CARD SERVICES     ************5793   -$18,132.00   $61,534.00
```

## 10. Core Fund Activity

**Target Table:** `transactions` with `transaction_type = 'CORE_FUND'`
**Location:** Detailed money market fund transactions

| Source Label    | JSON Field       | Database Column              | Type     | Notes                      |
|-----------------|------------------|------------------------------|----------|----------------------------|
| Settlement Date | settlement_date  | transactions.settlement_date | DATE     | MM/DD format               |
| Account Type    | account_type     | transactions.account_type    | TEXT     | "CASH"                     |
| Transaction     | transaction      | transactions.description     | TEXT     | "You Bought" or "You Sold" |
| Description     | sec_description  | transactions.security_name   | TEXT     | Core fund name             |
| Symbol          | sec_symbol       | transactions.security_identifier | TEXT     | Fund ticker if available   |
| Quantity        | quantity         | transactions.quantity        | NUMBER   | Shares                     |
| Price           | price_per_unit   | transactions.price_per_unit  | CURRENCY | Usually $1.0000            |
| Amount          | amount           | transactions.amount          | CURRENCY | Transaction amount         |
| Balance         | balance          | transactions.balance         | CURRENCY | Running balance            |


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
- **Price handling**: When price shows "-" for redemptions, use null (this is normal)
- **Cost basis**: Usually null for redemptions (this is normal)
- **Transaction cost**: Use null for blank/missing costs (not "0.00")
- Amount reflects redemption proceeds
- Reference numbers (#REOR, etc.) are part of the description

**This is normal bond redemption behavior - not a parsing challenge**

### Transaction Signs
- **Purchases/Debits:** Negative amounts
- **Sales/Credits:** Positive amounts
- **Income:** Positive amounts
- **Fees:** Negative amounts
- **Deposits:** Positive amounts
- **Withdrawals:** Negative amounts

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
11. Note any Trades Pending Settlement

## Required Fields for All Transactions

Every transaction record should include:
- `account_number` - From the account header
- `transaction_date` - Trade or post date
- `settlement_date` - Settlement date
- `transaction_type` - Category of transaction
- `amount` - Transaction amount with proper sign
- `description` - Transaction description