# Fidelity Activity JSON Output Specification

**Created:** 09/22/25 3:15PM ET
**Updated:** 09/22/25 8:55PM ET - Added doc_md5_hash field to extraction_metadata for duplicate prevention
**Updated:** 09/23/25 2:32PM - Added required account_type field to account-level metadata for loader compatibility
**Updated:** 09/23/25 2:35PM - Aligned data type rules and extraction_type with positions specification for consistency
**Updated:** 09/23/25 4:25PM - Added extraction vs classification philosophy and mapping system guidance
**Purpose:** Formal specification for JSON output from Fidelity statement activity extraction
**Related:** [Map_Stmnt_Fid_Activity.md](./Map_Stmnt_Fid_Activity.md)

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

### Transaction Description Handling
Extract transaction descriptions exactly as shown in the PDF. Do not attempt to standardize or categorize - the mapping system handles:
- "Muni Exempt Int" → interest/muni_exempt classification
- "Dividend Received" → dividend/received classification
- "CLOSING TRANSACTION" → closing_transaction subtype
- "ASSIGNED PUTS" → assignment subtype

## Overview

This document defines the exact JSON structure that must be produced when extracting activity data from Fidelity statements. The extraction process produces a single JSON file containing metadata, document information, and all account activities.

## File Naming Convention

```
{file_hash}_activity_{YYYYMMDD_HHMMSS}.json
```

Example: `a3b5c7d9e1f3_activity_20240922_151500.json`

## Data Type Rules

| Data Type | Format | Example | Notes |
|-----------|--------|---------|-------|
| Dates | `YYYY-MM-DD` | `"2024-08-31"` | ISO 8601 format |
| Currency | String with 2 decimals | `"17525.00"` | Preserve precision, negative for debits |
| Quantities | String with 6 decimals | `"100.000000"` | Preserve all decimal places shown |
| Prices | String with 4 decimals | `"175.2500"` | Preserve all decimal places |
| Percentages | Decimal string | `"0.0525"` | 5.25% = "0.0525" |
| Missing values | `null` | `null` | Not "unavailable" or empty string |
| Account numbers | String | `"X12-123456"` | Preserve format exactly |
| Symbols/CUSIPs | String | `"AAPL"`, `"912828XX5"` | Uppercase as shown |

## Complete JSON Structure for Activity Extraction

```json
{
  "extraction_metadata": {
    "document_id": "generated_uuid",
    "file_path": "/path/to/statement.pdf",
    "file_hash": "sha256_hash_of_file",
    "doc_md5_hash": "md5_hash_of_file",
    "extraction_type": "activities",
    "extraction_timestamp": "2024-09-22T15:15:00Z",
    "extractor_version": "1.0",
    "pages_processed": 27,
    "extraction_notes": []
  },

  "document_data": {
    "institution": "Fidelity",
    "statement_date": "2024-08-31",
    "period_start": "2024-08-01",
    "period_end": "2024-08-31"
  },

  "accounts": [
    {
      "account_number": "X12-123456",
      "account_name": "INDIVIDUAL - TOD",
      "account_holder_name": "JOHN DOE",
      "account_type": "brokerage",

      "securities_bought_sold": [
        {
          "settlement_date": "2024-08-15",
          "sec_description": "APPLE INC COM",
          "sec_symbol": "AAPL",
          "cusip": null,
          "description": "You Bought",
          "quantity": "10.000000",
          "price_per_unit": "175.2500",
          "cost_basis": null,
          "transaction_cost": "0.00",
          "amount": "-1752.50"
        },
        {
          "settlement_date": "2024-08-20",
          "sec_description": "US TREASURY BILL DUE 09/15/24",
          "sec_symbol": null,
          "cusip": "912797HT6",
          "description": "You Sold",
          "quantity": "100000.000000",
          "price_per_unit": "99.9850",
          "cost_basis": "99950.00",
          "transaction_cost": "0.00",
          "amount": "99985.00"
        },
        {
          "settlement_date": "2024-08-25",
          "sec_description": "PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION",
          "sec_symbol": null,
          "cusip": null,
          "description": "You Bought - OPENING TRANSACTION",
          "quantity": "1.000000",
          "price_per_unit": "1500.0000",
          "cost_basis": null,
          "transaction_cost": "0.65",
          "amount": "-1500.65"
        }
      ],

      "dividends_interest_income": [
        {
          "settlement_date": "2024-08-01",
          "sec_description": "VANGUARD TOTAL STOCK MKT INDEX ADM",
          "sec_symbol": "VTSAX",
          "cusip": null,
          "description": "Dividend Received",
          "quantity": null,
          "price_per_unit": null,
          "amount": "125.50"
        },
        {
          "settlement_date": "2024-08-15",
          "sec_description": "GEORGIA ST ATLANTA ARPT REV BDS REF-BD",
          "sec_symbol": null,
          "cusip": "373384KR9",
          "description": "Muni Exempt Int",
          "quantity": null,
          "price_per_unit": null,
          "amount": "437.50"
        },
        {
          "settlement_date": "2024-08-20",
          "sec_description": "FIDELITY GOVERNMENT MONEY MARKET FUND",
          "sec_symbol": "SPAXX",
          "cusip": null,
          "description": "Interest Earned",
          "quantity": null,
          "price_per_unit": null,
          "amount": "35.25"
        },
        {
          "settlement_date": "2024-08-25",
          "sec_description": "APPLE INC COM",
          "sec_symbol": "AAPL",
          "cusip": null,
          "description": "Reinvestment",
          "quantity": "0.500000",
          "price_per_unit": "176.0000",
          "amount": "-88.00"
        }
      ],

      "other_activity_in": [
        {
          "settlement_date": "2024-08-18",
          "sec_description": "PUT (SPY) SPDR S&P 500 AUG 16 24 $450 (100 SHS)",
          "sec_symbol": null,
          "cusip": null,
          "description": "Expired",
          "quantity": "1.000000",
          "cost_basis": "500.00",
          "amount": "0.00"
        },
        {
          "settlement_date": "2024-08-30",
          "sec_description": "ANNALY CAPITAL MANAGEMENT INC COM NEW",
          "sec_symbol": "NLY",
          "cusip": null,
          "description": "Return Of Capital",
          "quantity": null,
          "cost_basis": null,
          "amount": "125.00"
        }
      ],

      "other_activity_out": [
        {
          "settlement_date": "2024-08-22",
          "sec_description": "CALL (AAPL) APPLE INC AUG 23 24 $175 (100 SHS)",
          "sec_symbol": null,
          "cusip": null,
          "description": "Assigned",
          "quantity": "1.000000"
        }
      ],

      "deposits": [
        {
          "date": "2024-08-05",
          "reference": "ACH123456789",
          "description": "Direct Deposit From EMPLOYER NAME",
          "amount": "5000.00"
        }
      ],

      "withdrawals": [
        {
          "date": "2024-08-10",
          "reference": "WIRE987654321",
          "description": "Wire Tfr To Bank WIRE987654321 CHASE BANK Account ending in 4567",
          "amount": "-3000.00"
        }
      ],

      "exchanges_in": [
        {
          "date": "2024-08-12",
          "sec_description": "FROM Z98-765432 ROTH IRA",
          "sec_symbol": null,
          "cusip": null,
          "description": "Transferred From",
          "amount": "10000.00"
        }
      ],

      "exchanges_out": [
        {
          "date": "2024-08-28",
          "sec_description": "TO Y87-654321 TRADITIONAL IRA",
          "sec_symbol": null,
          "cusip": null,
          "description": "Transferred To",
          "amount": "-5000.00"
        }
      ],

      "fees_charges": [
        {
          "date": "2024-08-31",
          "description": "Account Service Fee",
          "amount": "-25.00"
        }
      ],

      "billpay": [
        {
          "post_date": "2024-08-15",
          "payee": "MORTGAGE COMPANY",
          "payee_account": "****1234",
          "amount": "-2500.00",
          "ytd_payments": "20000.00"
        }
      ],

      "core_fund_activity": [
        {
          "settlement_date": "2024-08-01",
          "account_type": "CASH",
          "transaction": "You Bought",
          "sec_description": "FIDELITY GOVERNMENT MONEY MARKET FUND",
          "sec_symbol": "SPAXX",
          "quantity": "1500.000000",
          "price_per_unit": "1.0000",
          "amount": "-1500.00",
          "balance": "8500.00"
        },
        {
          "settlement_date": "2024-08-31",
          "account_type": "CASH",
          "transaction": "You Sold",
          "sec_description": "FIDELITY GOVERNMENT MONEY MARKET FUND",
          "sec_symbol": "SPAXX",
          "quantity": "2000.000000",
          "price_per_unit": "1.0000",
          "amount": "2000.00",
          "balance": "6500.00"
        }
      ],

      "trades_pending_settlement": [
        {
          "trade_date": "2024-08-30",
          "settlement_date": "2024-09-03",
          "sec_description": "MICROSOFT CORP COM",
          "sec_symbol": "MSFT",
          "cusip": null,
          "description": "You Bought",
          "quantity": "5.000000",
          "price_per_unit": "420.5000",
          "amount": "-2102.50"
        }
      ]
    }
  ]
}
```

## Field Completeness Rules

### Required Fields (Never null)
- All metadata fields (including `doc_md5_hash`)
- `account_number`
- `settlement_date` or `date` or `post_date` (depending on activity type)
- `description`
- `amount`

### Activity-Specific Required Fields

#### Securities Bought & Sold
- `sec_description`
- `quantity`
- `price_per_unit`
- Either `sec_symbol` OR `cusip` (bonds have CUSIP, stocks have symbol)

#### Dividends & Interest
- `sec_description`
- Either `sec_symbol` OR `cusip`

#### Deposits & Withdrawals
- `date`
- `description`

#### Bill Payments
- `post_date`
- `payee`
- `payee_account`

#### Core Fund Activity
- `settlement_date`
- `account_type`
- `transaction`
- `sec_description`
- `quantity`
- `price_per_unit`
- `balance`

### Optional Fields (Can be null)
- `cost_basis`: Present for sales, null for purchases
- `transaction_cost`: May be zero
- `reference`: May not be present for all deposits/withdrawals
- `ytd_payments`: Only for recurring bill payments
- Options fields when not an option transaction

## Activity Section Mapping

Each account should have these activity sections (if present in statement):

1. `securities_bought_sold` - Trading transactions
2. `dividends_interest_income` - Income transactions
3. `other_activity_in` - Options expirations, returns of capital
4. `other_activity_out` - Options assignments
5. `deposits` - Cash deposits
6. `withdrawals` - Cash withdrawals
7. `exchanges_in` - Transfers from other accounts
8. `exchanges_out` - Transfers to other accounts
9. `fees_charges` - Account fees
10. `billpay` - Card and bill payments
11. `core_fund_activity` - Money market transactions
12. `trades_pending_settlement` - Unsettled trades

## Extraction Instructions for Claude

1. **One JSON file per document** containing all accounts and their activities
2. **Preserve exact values** - Copy numbers exactly as shown
3. **Include all activities** - Even zero-amount transactions (like expired options)
4. **Maintain chronological order** - Within each section
5. **Parse option descriptions** - Extract underlying symbol, strike, expiration from text
6. **Handle signs correctly**:
   - Purchases/debits: negative amounts
   - Sales/credits: positive amounts
   - Income: positive amounts
   - Fees: negative amounts
7. **Ask if uncertain** - If data unclear, ask for guidance

## Validation Rules

The Python loader will validate:
1. Required fields are not null
2. Numeric strings can be parsed as decimals
3. Dates are valid ISO 8601 format
4. Account numbers match expected patterns
5. Amount signs are consistent with transaction types

## Example: Special Cases

### Option Description Parsing
Statement shows: "PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION"
JSON outputs:
- `"sec_description"`: Full text as shown
- `"sec_symbol"`: `null` (options don't have simple symbols)
- `"description"`: `"You Bought - OPENING TRANSACTION"`

### Bond Redemption
Statement shows: "REDEMPTION PAYOUT #REOR R123456"
JSON outputs:
- `"description"`: `"REDEMPTION PAYOUT"`
- `"reference"`: `"#REOR R123456"`

### Wire Transfer
Statement shows: "Wire Tfr To Bank WIRE123 CHASE BANK Account ending in 4567"
JSON outputs:
- `"reference"`: `"WIRE123"`
- `"description"`: Full text as shown

---

*This specification ensures consistent, complete JSON output for all activity data that can be reliably processed by the Python database loader.*