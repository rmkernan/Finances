# Fidelity Document Processing Guide

**Institution:** Fidelity Investments
**Updated:** 09/17/25
**Purpose:** Guide for Claude to extract data from Fidelity documents

## Account Number Patterns

### Format
- Pattern: `[A-Z]\d{2}-\d{6}` (Letter + 2 digits + hyphen + 6 digits)
- Examples: `Z24-527872`, `Z27-375656`
- Location: Each account shown on separate page sections
- Label: "Account Number" (no colon)
- Note: Combined statements show multiple accounts with separate summaries

### Special Cases
- Joint accounts may show both account holders' names
- Corporate accounts show company name with officer names below
- Trust accounts show trustee names

## Document Recognition Patterns

### Monthly Statements

**Visual Identifiers:**
- Green Fidelity header with green shield/pyramid logo
- "Fidelity Account" as main header
- "Combined Statement" subtitle for multi-account statements
- Statement period format: "August 1-31, 2024"
- Account name shown prominently (e.g., "MILTON PRESCHOOL INC")

**Structure:**
- Combined statements show multiple accounts in one document
- Each account gets its own section with summary, activity, and holdings
- Account numbers clearly marked throughout

**Common Transaction Formats:**
```
Dividends:
08/31  REINVESTMENT FIDELITY TREASURY MONEY MKT (FSIXX)    $X,XXX.XX

Electronic Transfers:
08/13  ELECTRONIC TRANSFER MILTON PRESCHOOL (Note)        $XXX,XXX.XX

Fees:
08/31  BROKERAGE FEE FSIXX                                   -$X.XX

Format: Date (MM/DD) | Description | Amount (right-aligned)
```

### 1099-DIV Forms

**Critical: Two Versions May Exist**
1. **Official 1099-DIV** (Filed with IRS)
   - May show $0.00 for corporate exempt entities
   - Has "Copy B - For Recipient" notation
   - Filed by January 31

2. **Informational 1099-DIV** (NOT filed with IRS)
   - Shows actual dividend amounts
   - Marked "INFORMATIONAL COPY - NOT FILED WITH IRS"
   - Provided for record-keeping

**Key Fields:**
- Box 1a: Total ordinary dividends
- Box 1b: Qualified dividends (subset of 1a)
- Box 5: Section 199A dividends
- Box 6: Foreign tax paid
- Box 11: Exempt-interest dividends (for mutual funds)

### 1099-INT Forms
- Box 1: Interest income
- Box 3: Interest on U.S. Savings Bonds
- Box 8: Tax-exempt interest (municipal bonds)
- Box 9: Specified private activity bond interest

### 1099-B Forms
- Shows proceeds from sales
- Includes cost basis information
- Categories: Short-term vs Long-term
- Covered vs Non-covered securities

## Money Market Fund Patterns

### FSIXX (Fidelity Treasury Money Market)
- **Full Name:** "FIDELITY TREASURY MONEY MKT"
- **Dividend Pattern:** Posts on last business day of month
- **Transaction Description:** "REINVESTMENT FIDELITY TREASURY MONEY MKT (FSIXX)"
- **Fee Pattern:** "BROKERAGE FEE FSIXX" (small monthly fee)
- **Extract:** Symbol (FSIXX), amount, date, type (dividend vs fee)

### SPAXX (Fidelity Government Money Market)
- **Dividend Pattern:** Posts on last business day of month
- **Transaction Description:** "SPAXX DIVIDEND CASH DIV"
- **Extract:** Symbol (SPAXX), amount, date

## Municipal Bond Interest

### Recognition Patterns
- Shows as "INTEREST" with CUSIP number
- May include state abbreviation in description
- Examples:
  - "INTEREST 123456789 GA MUNI"
  - "INTEREST 987654321 CA MUNI"
- **Extract:** CUSIP, state (if shown), amount

## Data Extraction Guidelines

### Transaction Date Formats
- Statements: `MM/DD/YY` (01/31/24)
- Tax forms: `MM/DD/YYYY` (01/31/2024)
- Trade confirmations: `MM/DD/YYYY`

### Amount Formats
- Positive: Deposits, dividends, interest
- Negative (with minus): Purchases, withdrawals, fees
- May include parentheses for negatives: `($1,234.56)`
- Always includes cents: `$1,234.00`

### Security Symbols
- Money markets: FSIXX, SPAXX, FCASH
- Extract from transaction description
- May be followed by quantity: "100 SH GOOG"

## Common Issues & Solutions

### Combined Statements
- Shows "Combined Statement" at top
- Each account's transactions are clearly separated
- Account number appears with each section

### Issue: Pending Transactions
- **Pattern:** Marked as "PENDING" or dated in future
- **Solution:** Ignore pending transactions

### Issue: Corporate Actions
- **Pattern:** Stock splits, mergers, spin-offs
- **Solution:** May show $0 amount but affect share count

### Issue: Year-End Adjustments
- **Pattern:** December statements may have corrections
- **Solution:** Look for "ADJUSTMENT" or "CORRECTION"

### Issue: Check Images
- **Pattern:** Check images attached to statement
- **Solution:** Note check number but don't process image

## Extraction Confidence Indicators

### High Confidence
- Standard dividend/interest transactions
- Wire transfers with clear descriptions
- Buy/sell transactions with standard format

### Ask User
- Unusual transaction descriptions
- Transactions that don't match known patterns
- Multiple possible account mappings

### Flag for Review
- Missing or corrupted data
- Amounts that don't reconcile
- Duplicate-looking transactions

## Monthly Reconciliation Checks

1. **Beginning Balance + Activity = Ending Balance**
2. **Sum of transactions = Net change in account value**
3. **Dividend dates match last business day for money market funds**

## Sample Extraction Output

```json
{
  "entity": "Milton Preschool Inc",
  "institution": "Fidelity",
  "account": "Z40-394067",
  "document_type": "statement",
  "period": "2024-01-01 to 2024-01-31",
  "transactions": [
    {
      "date": "2024-01-31",
      "description": "FSIXX DIVIDEND CASH DIV",
      "type": "dividend",
      "amount": 4327.68,
      "security": "FSIXX"
    }
  ]
}
```

## Questions to Ask User

When processing Fidelity documents, ask about:
1. "Is this the official or informational 1099?" (if both might exist)
2. "Should I use the amended version?" (if amendment detected)
3. "Which entity owns account [number]?" (if not clear from document)

## Additional Patterns from Analysis

### Holdings Summary Format
- Shows each position with quantity and current value
- Format: `Quantity | Symbol | Description | Price | Value`
- Money market funds show as "Core Position"
- Includes total account value at bottom

### Account Types
- **Cash Management Account:** Primary transaction account
- **Brokerage Account:** Investment holdings
- Combined statements alternate between account types

### Missing from Current Documents
- No municipal bond transactions in sample (all FSIXX)
- No stock trades in sample period
- No check deposits or wire transfers shown

## Notes for Future Updates

- Fidelity may change format slightly each year
- New money market funds may be added
- International transactions need special handling
- Combined statements require careful account separation