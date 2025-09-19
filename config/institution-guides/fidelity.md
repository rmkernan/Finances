# Fidelity Extraction Guide

**Created:** 09/19/25 1:05PM ET
**Updated:** 09/19/25 1:33PM ET - Added pre-processing checks and file management details from process-inbox
**Updated:** 09/19/25 1:38PM ET - Changed to use + instead of & in filenames for shell compatibility
**Updated:** 09/19/25 1:40PM ET - Added validation step to quality checks
**Updated:** 09/19/25 1:46PM ET - Added statement inventory capture for extraction validation
**Updated:** 09/19/25 2:50PM ET - Added Fidelity-specific scale assessment and extraction strategies based on 36-page statement testing
**Updated:** 09/19/25 2:57PM ET - Added Task tool integration guidelines and flexible inventory approach
**Updated:** 09/19/25 3:27PM ET - Added comprehensive navigation map and systematic extraction workflow based on 36-page statement processing experience
**Purpose:** Comprehensive guide for extracting data from Fidelity statements
**Institution Code:** Fid

## Quick Reference

- **Institution Code:** `Fid`
- **Document Types:** `Stmnt` (statements), `1099` (tax forms)
- **Account Mapping:** See `/config/account-mappings.json`
- **Output Format:** JSON following field mappings below

## Core Philosophy

You're smart. Read this like a human would read a paper statement. Extract what you see. Ask questions when something seems odd. The user knows their finances better than any document - this is collaborative work.

## Fidelity Statement Scale Assessment

**Before starting extraction, assess the Fidelity statement scope:**
- Count pages (shown on each page footer)
- Scan holdings sections for volume (Mutual Funds, Stocks, Bonds, Options sections)
- Scan activity sections for transaction density
- Note account complexity (single vs. multi-account statements)

### **Small Fidelity Statements (1-10 pages)**
- **Typical:** Single account, basic holdings, minimal activity
- **Approach:** Direct section-by-section file editing
- **Method:** Build JSON incrementally with Edit tool
- **Characteristics:** <20 holdings, <30 transactions, mostly stocks/funds

### **Medium Fidelity Statements (10-25 pages)**
- **Typical:** Single active account or dual account with moderate complexity
- **Approach:** Section-in-memory + checkpoint writes
- **Method:** Build complete sections in memory, write after major sections
- **Characteristics:** 20-50 holdings, 30-80 transactions, some options/bonds

### **Large Fidelity Statements (25+ pages)**
- **Typical:** Multi-account, active trading, complex instruments
- **Approach:** Memory-first with strategic Task tool delegation
- **Method:** Create skeleton, use Task tool for bulk repetitive sections, checkpoint writes
- **Characteristics:** 50+ holdings, 80+ transactions, extensive options/bonds/activity
- **Fidelity-specific:** Heavy options activity, municipal bonds with complex details, extensive transaction categories

## Systematic Extraction Workflow

**Recommended Approach: Direct Section-by-Section File Editing**

Based on processing experience, **avoid Task tool for bulk extraction** - direct editing is 10x faster and more accurate.

### Phase 1: Document Initialization
1. **Create extraction JSON skeleton** with document metadata
2. **Load account mappings** to translate account numbers to friendly names
3. **Capture basic portfolio totals** from Portfolio Summary section
4. **Initialize accounts array** with account numbers and basic values

### Phase 2: Holdings Extraction (Account by Account)
For each account, process holdings **in document order:**

**2.1 Mutual Funds** (typically first)
- Build JSON entries for each fund
- Include share class and yields where shown
- **Checkpoint**: Write file after completing all mutual funds

**2.2 Exchange Traded Products** (ETFs, ETNs)
- Usually small section, process sequentially
- **Checkpoint**: Write file after completing ETPs

**2.3 Stocks** (largest section typically)
- Process Common Stock, then Preferred Stock
- Handle short positions (negative quantities)
- Include dividend yields where shown
- **Checkpoint**: Write file after every 15-20 positions to avoid memory issues

**2.4 Bonds** (most complex section)
- Corporate bonds first, then Municipal bonds
- Extract full bond details: CUSIP, ratings, call features, maturity
- Capture accrued interest as separate field
- **Critical**: Georgia municipal bonds need special attention for tax treatment
- **Checkpoint**: Write file after each bond subsection (Corporate, then Municipal)

**2.5 Options** (if present)
- Handle puts and calls separately
- Include full option details: underlying, strike, expiration
- Negative quantities for short option positions
- **Checkpoint**: Write file after completing options

**2.6 Other Holdings** (REITs, warrants, etc.)
- Usually small section at end
- **Final Holdings Checkpoint**: Write complete holdings section

### Phase 3: Activity Extraction
Process transaction sections **in document order:**

**3.1 Securities Bought & Sold** (largest activity section)
- Extract systematically: settlement date, security, type, quantity, price, amount
- Handle option assignments and special transaction types
- **Checkpoint**: Write after every 20-25 transactions

**3.2 Income Activities**
- Dividends, interest, other income
- Usually shorter section, process completely
- **Checkpoint**: Write after completing income section

**3.3 Other Activities**
- Deposits, withdrawals, fees, core fund activity
- Process remaining activity sections
- **Final Activity Checkpoint**: Write complete activity section

### Phase 4: Validation & Completion
1. **Cross-check totals** against statement summaries
2. **Update extraction_verification** with actual counts vs. expected
3. **Add extraction_notes** for any questions or unusual items
4. **Final write** with validation results

### Key Lessons from Experience:
- **Section-by-section editing** beats memory-first approaches
- **Regular checkpoints** prevent data loss and manage context
- **Direct file editing** is faster than Task tool delegation
- **Follow document order** rather than trying to optimize sequence

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

## Fidelity Statement Navigation Map

### Document Structure (Section Order)
Fidelity statements follow a predictable structure regardless of length:

**1. Portfolio Summary (2-3 sections)**
- Your Net Portfolio Value - Extract overall totals
- Accounts Included in This Report - Account numbers and values
- Income Summary - Period and YTD breakdowns
- Top Holdings - Major positions across all accounts
- Asset Allocation - Portfolio percentages

**2. Account Summary Sections (1 section per account)**
- Net Account Value and change information
- Account Holdings pie chart breakdown
- Top Holdings for this specific account
- Income Summary for this account
- **Navigation tip:** Look for "Account # Z##-######" headers

**3. Holdings Sections (5-12 sections per account)**
Each account's holdings broken down by security type **in this order:**
- Mutual Funds (Short-Term, Bond, Stock funds)
- Exchange Traded Products (ETFs, ETNs)
- Stocks (Common Stock, then Preferred Stock)
- Bonds (Corporate, then Municipal - longest section)
- Options (if any active positions)
- Other (REITs, warrants, misc. holdings)
- **Navigation tip:** Each subsection shows "X% of account holdings"

**4. Activity Sections (8-12 sections per account)**
Transaction details in **this order:**
- Securities Bought & Sold (longest activity section)
- Dividends, Interest & Other Income
- Short Activity (if applicable)
- Other Activity In/Out (options expirations, assignments)
- Deposits/Exchanges In/Withdrawals
- Fees and Charges
- Core Fund Activity (money market movements)
- Trades Pending Settlement (if any)

**5. Estimated Cash Flow (1 section at end)**
- Monthly projections for next 12 months

### Section Length Expectations
- **Small statements:** Holdings 3-8 sections, Activity 5-10 sections
- **Medium statements:** Holdings 8-15 sections, Activity 10-20 sections
- **Large statements:** Holdings 15-25 sections, Activity 20-35 sections

### Navigation Cues
- **Bold section headers** clearly mark each major section
- **Account transitions** always start with account summary
- **Subsection percentages** help confirm you're in holdings vs. activity
- **Date columns** indicate you've reached activity sections
- **"Total" rows** mark the end of each holdings subsection

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
- **Activity Summary:** Record transaction counts if standard summary sections exist
- **Holdings Count:** Note "X holdings" or "X positions" from holdings header
- **Transaction Categories:** Capture counts by type if shown (buys, sells, dividends)
- **Page References:** Note which pages contain what sections for audit trail
- **Flexible Approach:** If standard summary sections are missing, scan holdings/activity sections for volume and note in extraction_notes

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