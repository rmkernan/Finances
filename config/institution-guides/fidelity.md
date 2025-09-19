# Fidelity Extraction Guide

**Created:** 09/19/25 1:05PM ET
**Updated:** 09/19/25 1:33PM ET - Added pre-processing checks and file management details from process-inbox
**Updated:** 09/19/25 1:38PM ET - Changed to use + instead of & in filenames for shell compatibility
**Updated:** 09/19/25 1:40PM ET - Added validation step to quality checks
**Updated:** 09/19/25 1:46PM ET - Added statement inventory capture for extraction validation
**Purpose:** Comprehensive guide for extracting data from Fidelity statements
**Institution Code:** Fid

## Quick Reference

- **Institution Code:** `Fid`
- **Document Types:** `Stmnt` (statements), `1099` (tax forms)
- **Account Mapping:** See `/config/account-mappings.json`
- **Output Format:** JSON following field mappings below

## Core Philosophy

You're smart. Read this like a human would read a paper statement. Extract what you see. Ask questions when something seems odd. The user knows their finances better than any document - this is collaborative work.

## Field Mappings

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

## Document Structure & Patterns

### Typical Statement Flow
1. **Portfolio Summary** - Overview of all accounts
2. **Account Activity Summary** - Look for transaction counts here!
   - "Securities Bought & Sold: X transactions"
   - "Dividends and Interest: Y payments"
   - Record these numbers for validation
3. **Individual Account Sections** - Each account's holdings and activity
4. **Holdings Section** - Note the total count shown
5. **Activity Details** - The actual transaction listings

### Visual Cues to Notice
- **Bold text** = Primary identifier
- *Italics* = Usually accrued interest for bonds
- Negative numbers = Short positions or obligations
- "unavailable" = Valid value - record as-is

## Pattern Recognition Examples

### Stock Holdings
```
MICROSOFT CORP (MSFT)    250.000    $423.04    $105,760.00    $95,397.50    $10,362.50
```
Extract as: security_description="MICROSOFT CORP", security_identifier="MSFT", quantity=250.000...

### Bond Holdings
```
HILLSBORO OHIO CITY SCH B    20,000.000    100.0670    $20,013.40    $19,974.60    $38.80
                                                         $200.00 (italics)
FIXED COUPON MOODYS Aa1 SEMIANNUALLY NEXT CALL DATE 09/30/2025 100.00 CUSIP: 432074EU2
```
- Market value: $20,013.40
- Accrued interest: $200.00 (the italic number)
- CUSIP: 432074EU2 (from detail line)
- Next call date: 09/30/2025

### Option Holdings
```
PUT (NVDA) NVIDIA CORPORATION    -10.000    0.8500    -$850.00    -$2,943.26    $2,093.26
SEP 19 25 $175 (100 SHS)
```
- Negative quantity indicates short position
- Description contains: TYPE (PUT), SYMBOL (NVDA), EXPIRY, STRIKE

## Transaction Patterns

### Common Transaction Types
| What You See | transaction_type | Notes |
|--------------|-----------------|--------|
| "You Bought" | BUY | Regular purchase |
| "You Sold" | SELL | Regular sale |
| "DIVIDEND RECEIVED" | DIVIDEND | Income payment |
| "ASSIGNED PUTS" | BUY | Options exercised - you bought stock |
| "ASSIGNED CALLS" | SELL | Options exercised - you sold stock |
| "Redeemed" | REDEMPTION | Bond matured/called |
| "Reinvestment" | REINVEST | Dividend reinvested |

### Options Assignments
"TESLA INC COM ASSIGNED PUTS" → BUY transaction (you were assigned stock)
"NVIDIA CORP ASSIGNED CALLS" → SELL transaction (your stock was called away)

## Special Cases

### Multi-Account Statements
- Extract all accounts in a single JSON
- Use document_accounts junction table for linking
- Account names help identify entity ownership

### Amended Documents
- Look for "AMENDED" or "CORRECTED" markers
- Note in extraction_notes
- Will be linked via amends_document_id

### Georgia Municipal Bonds
- Look for "GA" or "GEORGIA" in bond descriptions
- These have special tax treatment (double exempt)
- Include full description for tax categorization

### Money Market Funds
- **FSIXX** = Treasury fund (~97% GA exempt, federal taxable)
- **SPAXX** = Government fund (~55% GA exempt, federal taxable)
- Capture as shown - tax treatment happens during loading

## When to Ask the User

**Ask about:**
- Unknown transaction types: "I see [description]. How should I categorize this?"
- New securities: "VMFXX appears to be new. Is this a money market fund?"
- Entity mapping: "Wire to 'ABC Corp' - which entity does this relate to?"
- Missing data: "Cost basis shows 'unavailable' - should I leave blank or note this?"

**Proceed automatically for:**
- Standard buy/sell transactions
- Known money market dividends (FSIXX/SPAXX)
- Clear option exercises
- Holdings with all data present

## Pre-Processing Checks

Before extraction:
- **Duplicate Check:** Calculate MD5 hash of source file and check against database
- **Amendment Check:** Look for "AMENDED" or "CORRECTED" markers
- **Multi-Account Check:** Determine if this is a combined statement

During extraction - CAPTURE INVENTORY:
- **Activity Summary:** Record transaction counts shown in summary sections
- **Holdings Count:** Note "X holdings" or "X positions" from holdings header
- **Transaction Categories:** Capture counts by type if shown (buys, sells, dividends)
- **Page References:** Note which pages contain what sections for audit trail

## Extraction Output & File Management

### File Naming Convention

1. **Load account mappings** from `/config/account-mappings.json`
2. **Generate intuitive filenames:**
   - Institution code: `Fid`
   - Document type: `Stmnt` or `1099`
   - Statement period: `YYYY-MM` format
   - Account labels: From mappings (Brok, CMA) or last 4 digits if unmapped
   - Extraction timestamp: `YYYY.MM.DD_HH.MMET`

### Output Files

**Extraction JSON:**
`/documents/extractions/Fid_Stmnt_2025-08_Brok+CMA_2025.09.19_13.15ET.json`

**Renamed Source PDF:**
`/documents/processed/Fid_Stmnt_2025-08_Brok+CMA.pdf`

Move original from inbox to processed with new name after successful extraction.

### JSON Structure
```json
{
  "extraction_session": {
    "timestamp": "ISO-8601",
    "source_file": "original filename",
    "file_hash": "MD5 hash",
    "document_pages": "total pages",
    "extractor": "claude"
  },
  "document_info": {
    "institution": "Fidelity",
    "document_type": "statement",
    "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
    "portfolio_total_value": 0.00,
    "portfolio_change_period": 0.00
  },
  "accounts": [...],
  "statement_inventory": {
    "description": "Counts/totals as shown in statement summary sections",
    "activity_summary": {
      "securities_bought_sold": "15 transactions (from Activity Summary)",
      "dividends_interest": "8 payments (from Activity Summary)",
      "other_activity": "3 transactions (from Activity Summary)"
    },
    "holdings_summary": {
      "total_positions": "12 (from Holdings section header)",
      "stocks": "5",
      "bonds": "3",
      "mutual_funds": "4"
    },
    "page_references": {
      "activity_summary": "Page 3",
      "holdings_section": "Pages 8-10",
      "transaction_details": "Pages 15-18"
    }
  },
  "extraction_verification": {
    "extracted_counts": {
      "total_transactions": 13,
      "total_positions": 7,
      "buy_transactions": 7,
      "sell_transactions": 4
    },
    "discrepancies": [
      "Statement claims 15 transactions, extracted 13 - may be missing 2",
      "Check pages 17-18 for additional transactions"
    ]
  },
  "extraction_notes": "Any questions or observations"
}
```

## What NOT to Do

- Don't calculate missing values - leave blank or note as unavailable
- Don't interpret tax implications during extraction - just capture what's shown
- Don't skip complex items - ask about them or note in extraction_notes
- Don't apply business rules - raw extraction only

## Quality Checks

Before finalizing extraction:
- [ ] All pages reviewed
- [ ] Account numbers match throughout
- [ ] Dates include proper year (from period)
- [ ] Transaction signs correct (buys negative, sells positive)
- [ ] Special securities (bonds/options) have detail fields
- [ ] Questions documented in extraction_notes

After extraction complete:
- [ ] Run `/validate [extraction_file]` to check database compatibility
- [ ] Fix any errors identified by validation
- [ ] Only proceed to loading after validation passes

## Remember

This is collaborative intelligence. When you're 80% sure, proceed and note assumptions. When less certain, ask. The goal is accurate data capture with the user's knowledge filling gaps.