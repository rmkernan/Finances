# Development Context & Getting Started Guide

## Overview
This document provides essential context for developers picking up this financial data management application project. It summarizes key discoveries, sample data insights, and implementation guidance.

## Project Status
- **Database Schema**: Defined in `schema.md`
- **Requirements**: Detailed in `prd.md` 
- **Sample Data**: Available in current directory for analysis
- **Next Phase**: Ready for development on Mac Mini M4

## Critical Discoveries Made During Analysis

### Major Data Discrepancy Found
**Problem**: Fidelity official 1099 shows $0 income vs actual $58,535+ in dividends/interest
- **Official 1099**: `2024-Milton-Preschool-Inc-4067-Consolidated-Form-1099.csv` shows zeros for all income categories
- **Informational 1099**: `2024-Milton-Preschool-Inc-4067-Consolidated-Form-1099-Info-Only.pdf` shows $29,515 in dividends + $8,900 tax-exempt interest
- **QuickBooks**: `QB MPS.CSV` shows $58,535 total income including $23k in PPR interest payments
- **Monthly Statement**: `Statement1312024.pdf` shows $4,329 in dividends for January alone

**Implication**: Multiple 1099 forms exist, corporate tax exemption creates "info only" reporting, significant reconciliation challenges.

### Corporate Tax Status Complexity
Milton Preschool Inc is marked as "exempt recipient for 1099 reporting purposes" meaning:
- Income exists but may not be automatically reported to IRS
- Requires manual tracking and proper corporate tax reporting
- Different rules than individual tax returns

### Multi-State Municipal Bond Taxation
Found bonds from 7 different states with complex tax implications:
- **Georgia bonds**: Tax-exempt for Georgia residents both federal and state
- **California bonds**: Federal exempt, but state taxable for Georgia residents  
- **Other states**: Various combinations of federal/state treatment
- **Private Activity Bonds**: Special AMT considerations

### Data Source Reconciliation Needs
Three primary data sources with different perspectives:
1. **Fidelity Statements**: Transaction-level detail, complete cash flows
2. **Fidelity 1099s**: Tax reporting summaries (both official and informational)
3. **QuickBooks**: Cash flow categorization and income tracking

## Sample Files to Analyze First

### 1. Fidelity 1099 CSV (Official)
**File**: `fidelity/2024-Milton-Preschool-Inc-4067-Consolidated-Form-1099.csv`
**Key Insights**: 
- Shows only bond redemptions ($240,000 total proceeds)
- All income categories show $0 (major red flag)
- Bond transactions: 6 municipal bonds redeemed at par (no gains/losses)
- Securities: Atlanta GA Airport, Auburn ME, California Muni, Cobb County GA, Coopersville MI, West Clermont OH

### 2. Fidelity 1099 PDF (Informational)
**File**: `fidelity/Milton/2024-Milton-Preschool-Inc-4067-Consolidated-Form-1099-Info-Only.pdf`
**Key Insights**:
- $29,515.27 in ordinary dividends (FSIXX: $29,063, SPAXX: $452)
- $8,900 in tax-exempt municipal interest  
- Same $240,000 in bond proceeds as official form
- Corporate exemption notice: "not furnished to the IRS"

### 3. Monthly Statement Example  
**File**: `Statement1312024.pdf`
**Key Insights**:
- January 2024: $4,329.68 in taxable dividends
- $200,000 withdrawal to "Reliant Income Fund" 
- Holdings: FSIXX (Treasury fund) and SPAXX (Money market)
- Demonstrates monthly transaction detail level

### 4. QuickBooks Export
**File**: `QB MPS.CSV`
**Key Insights**:
- $58,535.44 total investment income for 2024
- Includes $23k+ in "PPR Interest" (missing from Fidelity forms)
- Municipal bond interest payments that correspond to bonds later redeemed
- Monthly dividend payments from FSIXX/SPAXX matching statement data

## Network & File Structure

### File Paths
- **Mac Directory**: `/Users/richkernan/Projects/Finances/`
- **Network Access**: `//Mac-mini/richkernan/Projects/Finances/`
- **Sample Data**: Available in current directory and `fidelity/` subdirectory

### Cross-Platform Setup
- **Database Host**: Mac Mini M4 (primary development machine)
- **Network Access**: SMB sharing enabled for PC file transfers
- **Remote Access**: Plan for Tailscale VPN for remote development

## Technology Stack Decisions & Rationale

### Database: PostgreSQL via Supabase Docker
**Why chosen**:
- NUMERIC type for precise financial calculations (no floating point errors)
- JSON support for complex document structures
- ACID compliance for financial data integrity
- Superior date/time handling for tax periods
- Real-time features via Supabase

### Host Platform: Mac Mini M4  
**Why chosen**:
- Silent operation (no fans under normal load)
- Low power consumption (10W idle)
- Always-on reliability compared to Windows sleep issues  
- M4 performance for PDF processing and database queries
- Unix-based for easier Docker deployment

### PDF Processing Strategy
**Approach**: Use Claude's native PDF reading capabilities
**Why**: Modern LLMs excel at structured data extraction from complex documents, handles varying formats automatically, no need for brittle PDF parsing libraries

## Implementation Priority

### Phase 1: Core Data Pipeline
1. **Set up Supabase Docker** on Mac Mini
2. **Implement schema** from `schema.md`
3. **Create PDF ingestion** using Claude API for extraction
4. **Test with sample files** to validate extraction accuracy

### Phase 2: Reconciliation Engine
1. **Cross-source data matching** (statements vs 1099s vs QuickBooks)
2. **Discrepancy detection** and flagging
3. **Tax categorization** engine for municipal bonds
4. **Data validation** rules and error handling

### Phase 3: User Interface
1. **Document upload** and processing interface
2. **Reconciliation dashboard** showing discrepancies
3. **Tax analysis** views (federal vs state treatment)
4. **Report generation** for tax preparation

## Key Validation Tests

### Data Integrity Tests
- Import January 2024 statement and verify $4,329.68 dividend extraction
- Process informational 1099 and confirm $29,515 dividend total
- Cross-reference municipal bond interest payments with redemption dates

### Tax Logic Tests
- Georgia municipal bond: should be federal exempt, state exempt for Georgia resident
- California municipal bond: should be federal exempt, state taxable for Georgia resident
- FSIXX/SPAXX dividends: should be ordinary income, fully taxable

### Reconciliation Tests
- QuickBooks $58k total vs Fidelity sources should identify $23k PPR gap
- Monthly statement dividends should aggregate to informational 1099 totals
- Bond redemption proceeds should match between CSV and PDF sources

## Critical Business Rules

### Corporate Tax Treatment
- Income may exist without automatic IRS reporting
- Qualified vs ordinary dividend rules differ for corporations
- Section 199A deduction eligibility varies by source

### Municipal Bond Taxation
- Issuer state vs taxpayer state determines treatment
- Private activity bonds have special AMT implications
- Bond premium amortization affects tax calculations

### Multi-Source Data Handling
- Official 1099s take precedence for IRS reporting
- Informational forms provide complete income picture
- Monthly statements provide transaction-level detail
- QuickBooks provides cash flow perspective

## Common Pitfalls to Avoid

1. **Floating Point Math**: Use NUMERIC/DECIMAL for all currency calculations
2. **Single Source Assumption**: Always cross-reference multiple documents
3. **Tax Oversimplification**: Municipal bonds have complex multi-state rules
4. **Date Handling**: Pay attention to settlement vs transaction dates
5. **Corporate vs Individual**: Different tax rules apply to corporate entities

## Next Steps for Mac Development

1. **Review all sample files** to understand data patterns
2. **Set up development environment** (Supabase Docker, Python, etc.)
3. **Implement basic PDF extraction** for one document type
4. **Create reconciliation logic** for known discrepancies
5. **Build iteratively** with frequent validation against sample data

## QuickBooks Integration via QBO Export

### CRITICAL FEATURE: Brokerage Account Reconciliation
**Key Discovery**: The application should generate .qbo (QuickBooks Bank Connect) files for seamless QuickBooks integration. This is a HIGH PRIORITY feature for practical usability.

#### QBO Export Strategy - Cash Flow Focus
For brokerage accounts, treat like **bank account reconciliation**, NOT security trading:

**INCLUDE in QBO Export** (Cash Flow Items):
- **Interest/Dividend payments** (FSIXX dividends, SPAXX dividends, bond interest)
- **Deposits** (cash contributions to brokerage account)
- **Withdrawals** (like $200k to Reliant Income Fund from Jan statement)
- **Account fees** (management fees, advisory fees)
- **Bond redemptions** (principal payments received - the $240k from 2024)
- **Dividend distributions** (actual cash received)

**EXCLUDE from QBO Export** (Internal Transactions):
- ~~Security purchases/sales~~ (only care about cash impact)
- ~~Reinvestment transactions~~ (wash transactions that don't affect cash)
- ~~Position changes~~ (share quantity changes)
- ~~Internal transfers between fund positions~~

#### Sample QBO Transaction Structure
From January 2024 statement:
```
Date: 01/31/2024, Type: DEPOSIT, Amount: +$4,327.65, Memo: "FSIXX Dividend"
Date: 01/31/2024, Type: DEPOSIT, Amount: +$2.03, Memo: "SPAXX Dividend"  
Date: 01/30/2024, Type: WITHDRAWAL, Amount: -$200,000.00, Memo: "Wire to Reliant Income Fund"
```

#### Technical Implementation Notes
- **QBO Format**: Based on OFX (Open Financial Exchange) XML standard
- **Transaction Types**: Use standard banking codes (DEPOSIT, WITHDRAWAL, FEE, etc.)
- **Account Mapping**: Fidelity account Z40-394067 → QuickBooks bank account
- **Duplicate Prevention**: Use unique transaction IDs from source documents
- **Date Handling**: Use settlement dates, not transaction dates

#### Business Value
- **Seamless QuickBooks reconciliation** - No manual entry of brokerage cash flows
- **Tax preparation efficiency** - Income automatically categorized in QuickBooks
- **Audit trail maintenance** - Complete cash flow documentation
- **Multi-entity support** - Handle corporate vs personal account differences

#### Implementation Priority
This QBO export functionality should be implemented in **Phase 2** alongside the reconciliation engine, as it provides immediate practical value for ongoing bookkeeping activities.

## Contact & Handoff Notes

This project represents a real-world financial data challenge with genuine complexity around:
- Corporate tax exemption status
- Multi-state municipal bond portfolios  
- Cross-source data reconciliation
- Precision financial calculations
- **QuickBooks integration for practical usability**

The sample data provides excellent test cases for validation and the schema is designed to handle the discovered complexity. Focus on data accuracy and audit trails - this is financial data that needs to be bulletproof. **The QBO export feature is critical for day-to-day utility and should be prioritized highly.**