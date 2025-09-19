# Fidelity Statement Document Map

**Created:** 09/18/25 1:20PM ET
**Updated:** 01/18/25 3:00PM ET - Simplified extraction guidance while maintaining field mappings
**Purpose:** Field mappings from Fidelity statements to database columns

## How to Use This Document

This document defines WHERE data should go (the field mappings). For HOW to extract it, use your intelligence and ask questions when uncertain.

## Core Field Mappings

### Portfolio Level
| Source Label | JSON Field | Database Column | Type | Notes |
|--------------|------------|-----------------|------|--------|
| Ending Net Portfolio Value | portfolio_total_value | documents.portfolio_value | CURRENCY | Main portfolio total |
| Portfolio Change from Last Period | portfolio_change_period | null | CURRENCY | Context only |
| Period dates | period_start, period_end | documents.period_start/end | DATE | From statement header |

### Account Level
| Source Label | JSON Field | Database Column | Type | Notes |
|--------------|------------|-----------------|------|--------|
| Account Number | account_number | accounts.account_number | TEXT | Exact as shown |
| Account holder name | account_holder_name | accounts.account_holder_name | TEXT | From account header |
| Net Account Value | net_account_value | null | CURRENCY | Account total |
| Beginning Net Account Value | beginning_value | null | CURRENCY | Period start value |

### Holdings/Positions
| Source Label | JSON Field | Database Column | Type | Notes |
|--------------|------------|-----------------|------|--------|
| Description | security_description | positions.security_name | TEXT | Full security name |
| Symbol/CUSIP | security_identifier | positions.security_identifier | TEXT | From description or details |
| Quantity | quantity | positions.quantity | NUMBER | Can be negative |
| Price Per Unit | price_per_unit | positions.price | CURRENCY | Current price |
| Market Value | market_value | positions.market_value | CURRENCY | Current value |
| Cost Basis | cost_basis | positions.cost_basis | CURRENCY | Original cost |
| Unrealized Gain/Loss | unrealized_gain_loss | positions.unrealized_gain_loss | CURRENCY | Calculated field |

### Transactions
| Source Label | JSON Field | Database Column | Type | Notes |
|--------------|------------|-----------------|------|--------|
| Settlement Date | settlement_date | transactions.settlement_date | DATE | Add year from period |
| Security Name | security_name | transactions.security_name | TEXT | From description |
| Description | transaction_description | transactions.description | TEXT | "You Bought", "You Sold", etc. |
| Quantity | quantity | transactions.quantity | NUMBER | Shares/units |
| Price | price_per_unit | transactions.price_per_unit | CURRENCY | Execution price |
| Amount | amount | transactions.amount | CURRENCY | Total with sign |
| Transaction Type | transaction_type | transactions.transaction_type | TEXT | BUY/SELL/DIVIDEND/etc. |

### Income Summary
| Source Label | JSON Field | Database Column | Type | Notes |
|--------------|------------|-----------------|------|--------|
| Taxable (period) | taxable_income_period | income_summaries.taxable_income | CURRENCY | This period's taxable |
| Taxable (YTD) | taxable_income_ytd | null | CURRENCY | Year to date |
| Tax-exempt (period) | tax_exempt_income_period | income_summaries.tax_exempt_income | CURRENCY | This period's exempt |

## Pattern Recognition Tips

### Finding Data in the Statement

**Holdings Section**
- Table with columns: Description | Quantity | Price | Market Value | Cost Basis | Gain/Loss
- Bonds: Market value on top, accrued interest in italics below
- Options: May show "unavailable" for some values

**Transaction Section**
- Look for "Securities Bought & Sold" heading
- Each row has settlement date, description, quantity, price, amount
- Transaction type from description: "You Bought" → BUY, "You Sold" → SELL

**Income Summary**
- Usually near account summary
- Split between Taxable and Tax-exempt
- Shows both period and YTD amounts

## Special Cases

### Bonds
- Extract CUSIP from the detail line below description
- Accrued interest is the italic number under market value
- Next call date: Look for "NEXT CALL DATE MM/DD/YYYY" in details
- If no call date found, use "undetermined"

### Options
- Negative quantities indicate short positions
- Description contains: TYPE SYMBOL COMPANY EXPIRY STRIKE
- "unavailable" is a valid value - don't calculate

### Short Positions
- Marked with "S" or "SHT"
- Show negative quantities and values
- This is normal - record as shown

## Common Transaction Patterns

| What You See | transaction_type | Notes |
|--------------|-----------------|--------|
| "You Bought" | BUY | Regular purchase |
| "You Sold" | SELL | Regular sale |
| "DIVIDEND RECEIVED" | DIVIDEND | Income payment |
| "ASSIGNED PUTS/CALLS" | BUY/SELL | Options exercised |
| "Redeemed" | REDEMPTION | Bond matured/called |
| "Reinvestment" | REINVEST | Dividend reinvested |

## Handling Complex Items

### For Options Assignments
"TESLA INC COM ASSIGNED PUTS" → This is a BUY transaction (you were assigned stock)

### For Income Already Categorized
The statement shows "Taxable" and "Tax-exempt" - capture these AS SHOWN. Don't recategorize.

### For Security Identifiers
- Use CUSIP when available (bonds always have them)
- Use ticker symbol for stocks
- Include the full description regardless

### For Dates in Activity Section
Add the year from the statement period (August 2025 → dates are in 2025)

## When in Doubt

If you can't find a mapped field or aren't sure about categorization:
1. Include what you found in extraction_notes
2. Ask the user for clarification
3. Record the raw data rather than skipping it

Remember: This should feel like reading a paper statement. The goal is accurate data capture. The user knows their finances better than any document.