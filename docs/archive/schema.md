# Financial Data Schema

This document describes the database schema for the financial data management application.

## Overview

The schema is designed to handle financial data from multiple sources (Fidelity statements, 1099 forms, QuickBooks exports) with proper tax categorization and cross-platform accessibility.

## Core Tables

### accounts
Master registry of all financial accounts.

- **id** - Unique identifier
- **account_number** - Account identifier (e.g., "Z40-394067")
- **institution** - Financial institution name (e.g., "Fidelity")
- **account_name** - Account holder name (e.g., "Milton Preschool Inc")
- **account_type** - Type of account (e.g., "Corporation", "Individual")
- **tax_id** - Tax identification number (e.g., "**-***3140")
- **status** - Account status (active/inactive)
- **created_at** - Record creation timestamp

### documents
Tracks all imported source documents to maintain audit trail.

- **id** - Unique identifier
- **account_id** - Links to accounts table
- **document_type** - Primary document category (e.g., "statement", "1099_official", "1099_info", "quickbooks")
- **document_subtype** - Specific form type (e.g., "1099-DIV", "1099-INT", "1099-B", "monthly_statement")
- **period_start** - Start date of period covered by document
- **period_end** - End date of period covered by document
- **file_path** - Path to original PDF/CSV file
- **file_hash** - Hash of file contents to detect duplicates
- **processed_at** - When document data was imported
- **created_at** - Record creation timestamp

### transactions
All financial transactions from all sources.

- **id** - Unique identifier
- **document_id** - Links to source document
- **account_id** - Links to account
- **transaction_date** - Date transaction occurred
- **settlement_date** - Date transaction settled
- **transaction_type** - Type (e.g., "dividend", "interest", "redemption", "sale", "withdrawal")
- **security_cusip** - Security identifier (e.g., "04780MWW5")
- **security_name** - Full security name
- **security_symbol** - Trading symbol (e.g., "FSIXX", "SPAXX")
- **quantity** - Number of shares/bonds
- **price** - Price per unit
- **amount** - Total dollar amount
- **description** - Transaction description/memo

#### Tax Treatment Fields
- **federal_taxable** - Whether taxable at federal level (yes/no)
- **state_taxable** - Whether taxable at state level (yes/no)
- **issuer_state_code** - State where security was issued (e.g., "GA", "CA")
- **taxpayer_state_code** - Taxpayer's state of residence
- **tax_category** - Specific tax category (e.g., "ordinary_dividend", "qualified_dividend", "municipal_interest", "private_activity_bond")
- **is_amt_preference** - Alternative Minimum Tax preference item (yes/no)
- **section_199a_eligible** - Eligible for Section 199A QBI deduction (yes/no)
- **created_at** - Record creation timestamp

### tax_reports
Summary data from 1099 forms for tax reporting.

- **id** - Unique identifier
- **account_id** - Links to account
- **document_id** - Links to source 1099 document
- **tax_year** - Tax year (e.g., 2024)
- **form_type** - Form type (e.g., "1099-DIV", "1099-INT", "1099-B")
- **is_official** - Whether reported to IRS (true) or informational only (false)

#### 1099-DIV Fields
- **ordinary_dividends** - Box 1a total ordinary dividends
- **qualified_dividends** - Box 1b qualified dividends  
- **capital_gain_distributions** - Box 2a capital gain distributions
- **exempt_interest_dividends** - Box 12 exempt interest dividends

#### 1099-INT Fields
- **interest_income** - Box 1 interest income
- **tax_exempt_interest** - Box 8 tax-exempt interest

#### 1099-B Fields
- **proceeds** - Total proceeds from sales
- **cost_basis** - Total cost basis
- **realized_gain_loss** - Net realized gain/loss
- **created_at** - Record creation timestamp

### securities
Master data for all securities (bonds, stocks, funds).

- **cusip** - Primary key, security identifier
- **symbol** - Trading symbol
- **name** - Full security name
- **security_type** - Type (e.g., "municipal_bond", "corporate_bond", "money_market")
- **issuer** - Issuing entity
- **maturity_date** - Maturity date for bonds
- **coupon_rate** - Interest rate for bonds

#### Municipal Bond Specific Fields
- **state_code** - Issuing state
- **is_tax_exempt** - Federal tax exempt status
- **is_private_activity** - Private activity bond designation
- **created_at** - Record creation timestamp

## Tax Treatment Examples

### Federal Taxable, State Exempt
- Georgia municipal bond held by Georgia resident
- `federal_taxable = true, state_taxable = false`

### Federal Exempt, State Taxable  
- California municipal bond held by Georgia resident
- `federal_taxable = false, state_taxable = true`

### Both Exempt
- In-state municipal bond
- `federal_taxable = false, state_taxable = false`

### Both Taxable
- Corporate dividends, most interest income
- `federal_taxable = true, state_taxable = true`

### Special Cases
- Private activity bonds: Federal exempt but AMT preference
- REIT dividends: Section 199A eligible
- Money market dividends: Ordinary income treatment

## Data Sources Handled

1. **Fidelity Monthly Statements** - Transaction details, holdings
2. **Fidelity 1099 Official Forms** - IRS-reported tax data
3. **Fidelity 1099 Informational** - Additional tax data not reported to IRS
4. **QuickBooks Exports** - Cash flow and income tracking
5. **Additional broker statements** - Extensible for other institutions

## Notes

- All monetary amounts stored as precise decimals (no floating point)
- Comprehensive audit trail through document linkage
- Designed for multi-state tax complexity
- Supports both individual and corporate tax treatments
- Extensible for additional document types and tax scenarios