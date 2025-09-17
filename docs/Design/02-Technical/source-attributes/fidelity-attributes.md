# Fidelity Source Document Attributes

**Institution:** Fidelity Investments
**Analysis Date:** 09/17/25
**Sample Document:** Statement8312025.pdf (August 2024 Combined Statement)
**Purpose:** Catalog all extractable data attributes from Fidelity documents

---

## Document Types and Attributes

### Combined Monthly Statements

**Document Metadata:**
- `statement_period` (text): "August 1-31, 2024"
- `statement_type` (text): "Combined Statement"
- `total_pages` (integer): 36
- `account_count` (integer): 2
- `entity_name` (text): "MILTON PRESCHOOL INC"

**Account-Level Attributes:**
- `account_number` (text): "Z24-527872", "Z27-375656"
- `account_type` (text): "Cash Management Account", "Brokerage Account"
- `beginning_balance` (currency): Account value at start of period
- `ending_balance` (currency): Account value at end of period
- `net_change` (currency): Change during period

**Transaction Attributes:**
- `transaction_date` (date): Format "MM/DD" (e.g., "08/31", "08/13")
- `description` (text):
  - "REINVESTMENT FIDELITY TREASURY MONEY MKT (FSIXX)"
  - "ELECTRONIC TRANSFER MILTON PRESCHOOL"
  - "BROKERAGE FEE FSIXX"
- `amount` (currency): Right-aligned, includes negatives for fees
- `transaction_type` (inferred): dividend, transfer, fee

**Security/Holdings Attributes:**
- `security_symbol` (text): "FSIXX"
- `security_name` (text): "FIDELITY TREASURY MONEY MKT"
- `share_quantity` (decimal): Number of shares held
- `share_price` (currency): Price per share (typically $1.00 for money market)
- `total_value` (currency): Quantity × Price

**Summary Totals:**
- `total_account_value` (currency): Sum across all accounts
- `period_income` (currency): Total dividends/interest for period
- `period_fees` (currency): Total fees charged
- `net_deposits_withdrawals` (currency): Net external transfers

---

## 1099-DIV Tax Forms (Expected)

**Note:** Not present in August statement sample, but expected annually.

**Recipient Information:**
- `recipient_name` (text): Entity name as appears on tax form
- `recipient_tin` (text): Tax ID number
- `recipient_address` (text): Mailing address

**Payer Information:**
- `payer_name` (text): "Fidelity Investments"
- `payer_tin` (text): Fidelity's tax ID
- `payer_address` (text): Fidelity's address

**Tax Amounts:**
- `ordinary_dividends` (currency): Box 1a
- `qualified_dividends` (currency): Box 1b
- `capital_gain_distributions` (currency): Box 2a
- `exempt_interest_dividends` (currency): Box 11
- `foreign_tax_paid` (currency): Box 6
- `federal_income_tax_withheld` (currency): Box 4

**Form Metadata:**
- `tax_year` (integer): Tax year (e.g., 2024)
- `form_type` (text): "1099-DIV"
- `is_corrected` (boolean): Whether this is a corrected form
- `is_informational` (boolean): True if "INFORMATIONAL COPY - NOT FILED WITH IRS"

---

## 1099-INT Tax Forms (Expected)

**Interest Income:**
- `interest_income` (currency): Box 1
- `early_withdrawal_penalty` (currency): Box 2
- `us_savings_bonds_interest` (currency): Box 3
- `federal_income_tax_withheld` (currency): Box 4
- `investment_expenses` (currency): Box 5
- `foreign_tax_paid` (currency): Box 6
- `foreign_country` (text): Box 7
- `tax_exempt_interest` (currency): Box 8
- `specified_private_activity_bond_interest` (currency): Box 9

---

## Trade Confirmations (Expected)

**Note:** Not present in statement sample, but expected for stock trades.

**Trade Details:**
- `trade_date` (date): When trade was executed
- `settlement_date` (date): When trade settles
- `action` (text): "Buy", "Sell", "Exchange"
- `quantity` (decimal): Number of shares
- `security_symbol` (text): Stock/fund symbol
- `security_description` (text): Full security name
- `price` (currency): Price per share
- `principal_amount` (currency): Shares × Price
- `commission` (currency): Brokerage commission
- `fees` (currency): Additional fees
- `net_amount` (currency): Total amount with fees

**Account Information:**
- `account_number` (text): Account where trade occurred
- `confirmation_number` (text): Unique trade identifier

---

## Data Quality Notes

**High Confidence Attributes:**
- Account numbers (clearly displayed)
- Transaction amounts (formatted consistently)
- Dates (standard MM/DD format)
- Security symbols (standardized)

**Medium Confidence Attributes:**
- Transaction descriptions (some variation in format)
- Security names (may have abbreviations)

**Requires Validation:**
- Transaction type classification (must be inferred from description)
- Tax treatment (not explicitly stated in statements)

**Missing from Sample:**
- Check images/details
- Wire transfer details beyond basic description
- International transaction attributes
- Margin account information
- Options trading data

---

## Extraction Patterns by Attribute

**Account Numbers:**
- Pattern: Letter + 2 digits + hyphen + 6 digits
- Location: Multiple places throughout document
- Reliability: Very High

**Transaction Amounts:**
- Pattern: Dollar sign + formatted number with commas
- Location: Right column of activity sections
- Reliability: Very High
- Note: Negative amounts show with minus sign

**Dates:**
- Pattern: MM/DD (two digits each)
- Location: Left column of activity sections
- Reliability: Very High
- Note: Year inferred from statement period

**Security Information:**
- Pattern: Symbol in parentheses after security name
- Location: Transaction descriptions, holdings sections
- Reliability: High
- Note: FSIXX consistently appears this way

---

## Schema Mapping Preview

**Primary Extractions → Database Fields:**
- `account_number` → `accounts.account_number`
- `transaction_date` + period → `transactions.transaction_date`
- `amount` → `transactions.amount`
- `description` → `transactions.description`
- `security_symbol` → `transactions.security_info->>'symbol'`
- `security_name` → `transactions.security_info->>'name'`

**Document Metadata → Database Fields:**
- `statement_period` → `documents.period_start`, `documents.period_end`
- `entity_name` → Lookup to `entities.entity_name`
- Statement file → `documents.file_path`, `documents.file_name`

---

## Future Considerations

**Additional Document Types to Analyze:**
- Year-end 1099 forms (January delivery)
- Trade confirmations for stock purchases
- Check deposit confirmations
- Wire transfer confirmations
- Quarterly statements with different formatting

**Potential New Attributes:**
- International holdings data
- Tax lot information for sales
- Dividend reinvestment details
- Account fee breakdowns
- Performance benchmarking data

---

*This attribute catalog serves as the definitive reference for what data can be extracted from Fidelity documents. It should be updated as new document types are encountered and analyzed.*