# Fidelity Statement Comprehensive Attribute List

**Created:** 09/18/25 12:49PM ET
**Purpose:** Complete catalog of extractable attributes from Fidelity investment statements
**Based On:** Statement8312025.pdf analysis and extraction feedback

## Document-Level Attributes

### Header Information
- `statement_period_start` - First day of statement period
- `statement_period_end` - Last day of statement period
- `statement_date` - Date statement was generated
- `document_pages` - Total page count
- `institution_name` - "Fidelity Investments" or specific division
- `statement_type` - "Investment Report" / "Account Statement" / etc.

### Account Summary (Per Account)
- `account_number` - Full account number (e.g., Z24-527872)
- `account_type` - Investment, Retirement, Cash Management, etc.
- `account_holder_name` - Exact name as shown
- `account_holder_type` - Individual, Joint, Trust, etc.
- `beginning_balance` - Balance at period start
- `ending_balance` - Balance at period end
- `total_contributions` - Sum of deposits/contributions
- `total_withdrawals` - Sum of withdrawals/distributions
- `total_change_in_value` - Market appreciation/depreciation

## Transaction-Level Attributes

### Core Transaction Fields (REQUIRED)
- `transaction_date` - Trade/settlement date (MM/DD format)
- `settlement_date` - When funds/securities settled
- `account_number` - Which account this belongs to
- `transaction_type` - Categorization (see types below)
- `description` - Full transaction description
- `amount` - Dollar amount (positive or negative)
- `page_number` - Source page in PDF

### Securities Transaction Fields (CONDITIONAL - when applicable)
- `action` - "BOUGHT" / "SOLD" / "REINVESTED" / etc.
- `security_name` - Full name of security
- `ticker_symbol` - Stock/fund ticker if available
- `cusip` - CUSIP identifier
- `quantity` - Number of shares/units
- `price_per_share` - Execution price
- `commission` - Trading commission if any
- `fees` - Other fees if itemized
- `transaction_id` - Unique transaction identifier if provided

### Options Transaction Fields (CONDITIONAL - for options)
- `option_type` - "PUT" / "CALL"
- `underlying_symbol` - Underlying security ticker
- `strike_price` - Option strike price
- `expiration_date` - Option expiration
- `contracts` - Number of contracts (x100 for shares)
- `option_action` - "OPENING" / "CLOSING" / "ASSIGNED" / "EXPIRED"
- `premium` - Option premium paid/received

### Dividend/Interest Fields (CONDITIONAL)
- `dividend_type` - "ORDINARY" / "QUALIFIED" / "CAPITAL GAIN" / etc.
- `payment_type` - "CASH" / "REINVESTED"
- `rate_per_share` - Dividend rate if shown
- `ex_dividend_date` - Ex-dividend date if shown
- `record_date` - Record date if shown
- `payable_date` - Payment date if shown
- `tax_withholding` - Foreign/domestic tax withheld

### Transfer/Wire Fields (CONDITIONAL)
- `transfer_direction` - "IN" / "OUT"
- `transfer_type` - "WIRE" / "EFT" / "CHECK" / etc.
- `counterparty` - Other institution/account involved
- `reference_number` - Wire/transfer reference
- `memo` - Transfer memo/notes

## Transaction Type Classification

### Standard Types to Identify
1. **TRADE_BUY** - Purchase of securities
2. **TRADE_SELL** - Sale of securities
3. **DIVIDEND** - Dividend payment
4. **INTEREST** - Interest payment
5. **REINVESTMENT** - Automatic reinvestment
6. **TRANSFER_IN** - Money/securities received
7. **TRANSFER_OUT** - Money/securities sent
8. **WIRE_IN** - Wire transfer received
9. **WIRE_OUT** - Wire transfer sent
10. **FEE** - Account/transaction fees
11. **TAX_WITHHOLDING** - Tax withheld
12. **OPTION_BUY** - Option purchase
13. **OPTION_SELL** - Option sale
14. **OPTION_ASSIGNMENT** - Option assigned
15. **OPTION_EXPIRATION** - Option expired
16. **MARGIN_INTEREST** - Margin interest charged
17. **SHORT_SALE** - Short sale transaction
18. **SHORT_COVER** - Short position covered

## Position/Holdings Attributes (if included)

### Per Position
- `position_date` - As-of date for holdings
- `security_name` - Full security name
- `ticker_symbol` - Ticker symbol
- `cusip` - CUSIP number
- `quantity` - Shares/units held
- `price` - Current market price
- `market_value` - Total position value
- `cost_basis` - Purchase cost basis
- `unrealized_gain_loss` - Paper profit/loss
- `position_type` - "LONG" / "SHORT" / "OPTION"

## Extraction Rules & Guidelines

### Data Formatting
- **Dates:** Extract as MM/DD, add year from statement period
- **Amounts:** Include negative sign for debits, no currency symbols
- **Account Numbers:** Full account number including prefix
- **Names:** Exact text including special characters and punctuation
- **Page Numbers:** Actual PDF page number, not printed page number

### Quality Checks
- **Completeness:** Every visible transaction must be extracted
- **Accuracy:** Numbers must match exactly (no rounding)
- **Consistency:** Same security should have same name/CUSIP throughout
- **Validation:** Buy + Sell quantities should reconcile with position changes

### Structured Sections to Target
1. **"Activity" Section** - Main transaction list
2. **"Securities Bought & Sold" Tables** - Detailed trade information
3. **"Dividends and Interest" Section** - Income transactions
4. **"Account Summary" Box** - High-level metrics
5. **"Holdings" or "Positions" Section** - Current portfolio

### Critical Missing Elements from Current Extraction
Based on the feedback report, these are NOT being captured but SHOULD be:

1. **Buy/Sell Indicators** - "You Bought" vs "You Sold" designations
2. **Quantities** - Number of shares per transaction
3. **Prices Per Share** - Execution prices for trades
4. **Settlement Dates** - Separate from transaction dates
5. **CUSIP Numbers** - Security identifiers
6. **Commission/Fees** - Separated from principal amounts
7. **Option Details** - Strike prices, expirations, contract counts
8. **Transaction IDs** - Unique identifiers when provided
9. **Short Position Markers** - "SHT" designations
10. **Substitute Payments** - Special dividend types

## JSON Output Structure

```json
{
  "extraction_metadata": {
    "extracted_at": "ISO-8601 timestamp",
    "source_file": "filename.pdf",
    "pages_processed": 36,
    "extractor_version": "1.0",
    "confidence_score": 0.95
  },
  "document": {
    "statement_period_start": "2025-08-01",
    "statement_period_end": "2025-08-31",
    "institution": "Fidelity Investments",
    "document_type": "Investment Report",
    "total_pages": 36
  },
  "accounts": [
    {
      "account_number": "Z24-527872",
      "account_holder": "RICHARD MICHAEL KERNAN - JOINT WROS - TOD",
      "beginning_balance": 1250000.00,
      "ending_balance": 1275000.00,
      "total_activity": 25000.00
    }
  ],
  "transactions": [
    {
      "transaction_date": "08/15",
      "settlement_date": "08/17",
      "account_number": "Z24-527872",
      "transaction_type": "TRADE_BUY",
      "action": "BOUGHT",
      "security_name": "NVIDIA CORP",
      "ticker_symbol": "NVDA",
      "cusip": "67066G104",
      "quantity": 100,
      "price_per_share": 125.50,
      "amount": -12550.00,
      "commission": 0,
      "description": "YOU BOUGHT NVIDIA CORP",
      "page_number": 17
    }
  ],
  "extraction_stats": {
    "total_transactions": 129,
    "transactions_by_type": {
      "TRADE_BUY": 45,
      "TRADE_SELL": 38,
      "DIVIDEND": 15,
      "OPTION_BUY": 12,
      "TRANSFER_IN": 10,
      "REINVESTMENT": 9
    },
    "accounts_processed": 2,
    "earliest_date": "08/01",
    "latest_date": "08/31"
  }
}
```

## Implementation Priority

### Phase 1 - Core Extraction (MUST HAVE)
- All Document-Level Attributes
- Core Transaction Fields
- Basic transaction_type classification
- Page number references

### Phase 2 - Enhanced Detail (SHOULD HAVE)
- Securities Transaction Fields
- Options Transaction Fields
- Dividend/Interest Fields
- Structured table parsing

### Phase 3 - Advanced Features (NICE TO HAVE)
- Position/Holdings tracking
- Cross-transaction validation
- Confidence scoring per field
- Automated reconciliation checks

## Notes for Extraction Agent

1. **ALWAYS check structured tables** - Don't just scan narrative text
2. **Look for "Securities Bought & Sold" sections** - These have complete trade details
3. **Parse activity tables carefully** - Column headers indicate data types
4. **Extract EVERYTHING visible** - Don't make assumptions about relevance
5. **Maintain field relationships** - A buy transaction's quantity must match its securities detail
6. **Flag uncertainties** - Use extraction_notes field for ambiguous items
7. **Preserve original text** - Keep exact descriptions for audit trail

This attribute list should be referenced by the extraction agent to ensure complete and accurate data capture from Fidelity statements.