# Financial Data Management Application - Product Requirements Document

## Executive Summary

This application is designed to process, organize, and analyze financial data from multiple sources (primarily Fidelity statements and 1099 forms) to provide comprehensive insights into yearly and monthly financial pictures, including transactions, realized and unrealized gains, taxable and non-taxable income, with proper handling of federal vs state tax implications.

## Background & Context

### Problem Statement
Current financial data management challenges include:
- **Data Fragmentation**: Financial information scattered across multiple document types (monthly statements, various 1099 forms, QuickBooks exports)
- **Tax Complexity**: Income has varying tax treatments (federal taxable/state exempt, federal exempt/state taxable, both exempt, both taxable)
- **Reconciliation Gaps**: Discovered significant discrepancies between official 1099 forms and actual account activity (e.g., $58,535 total income vs $0 reported on official 1099)
- **Manual Processing**: Time-consuming manual analysis of PDF statements and tax forms
- **Multi-State Complexity**: Municipal bonds from multiple states require different tax treatment based on taxpayer residence

### Key Discoveries from Analysis
1. **Multiple 1099 Types**: Official IRS-reported forms vs "Info Only" forms for corporate exemptions
2. **Missing Data**: Official 1099 showed $0 dividend income while statements showed $29,515 in dividends
3. **Corporate Tax Status**: Milton Preschool Inc marked as "exempt recipient for 1099 reporting purposes"
4. **Cross-Source Validation**: Need to reconcile data between Fidelity statements, 1099s, and QuickBooks

## Technical Architecture

### Infrastructure
- **Database**: PostgreSQL via Supabase Docker hosted on Mac Mini M4
- **Host Platform**: Mac Mini M4 (silent, low-power, always-on reliability)
- **Remote Access**: Accessible from PC and laptop via local network and remote connections
- **Storage**: Built-in SSD on Mac Mini for reliability and performance

### Cross-Platform Access
- **Local Network**: `http://mac-mini.local:3000` for same-network access
- **Remote Access**: Tailscale VPN for secure remote connectivity
- **File Sharing**: SMB/AFP for document upload from PC to Mac

## Core Features

### 1. Document Ingestion & Processing

#### PDF Processing Pipeline
- **Folder-Based Import**: Drop PDFs into designated folders for automatic processing
- **AI-Powered Extraction**: Use Claude's native PDF reading capabilities to extract structured data
- **Document Classification**: Auto-detect document types (monthly statements, 1099-DIV, 1099-INT, 1099-B, etc.)
- **Original Preservation**: Maintain original PDFs for human verification and reference
- **Duplicate Detection**: File hash-based detection to prevent duplicate imports

#### Supported Document Types
1. **Fidelity Monthly Statements**
   - Transaction details
   - Holdings information
   - Cash flow data
   - Account summaries

2. **Fidelity 1099 Forms**
   - Official IRS-reported forms (1099-DIV, 1099-INT, 1099-B)
   - Informational forms for tax-exempt entities
   - Consolidated forms vs individual security forms

3. **QuickBooks Exports** 
   - CSV format cash flow data
   - Income categorization
   - Cross-reference validation

4. **Future Extensions**
   - Other broker statements
   - Bank statements
   - Tax preparation documents

#### CSV Processing
- **Fidelity CSV Parser**: Handle complex consolidated 1099 CSV format
- **QuickBooks Integration**: Process QB export format
- **Data Validation**: Cross-check CSV data against PDF sources

### 2. Data Extraction & Structuring

#### Transaction Processing
- **Comprehensive Categorization**: Dividends, interest, capital gains, redemptions, withdrawals
- **Security Identification**: CUSIP, symbol, full name extraction
- **Quantity & Pricing**: Precise decimal handling for shares and prices
- **Tax Classification**: Automatic categorization based on security type and source

#### Tax Intelligence Engine
- **Multi-Level Tax Treatment**:
  - Federal taxable/exempt status
  - State taxable/exempt status  
  - Issuer state vs taxpayer state
  - Special categories (AMT preference, Section 199A eligibility)

- **Municipal Bond Expertise**:
  - State-specific exemptions
  - Private activity bond identification
  - Cross-state tax implications

- **Corporate vs Individual Rules**:
  - Different reporting requirements
  - Qualified vs ordinary dividend treatment
  - Section 199A deduction eligibility

### 3. Data Reconciliation & Validation

#### Cross-Source Verification
- **Statement vs 1099 Matching**: Identify discrepancies between monthly statements and tax forms
- **Official vs Informational**: Compare IRS-reported vs informational-only data
- **QuickBooks Reconciliation**: Validate cash flow data against brokerage records

#### Data Quality Assurance
- **Missing Data Detection**: Flag incomplete or missing information
- **Anomaly Identification**: Highlight unusual patterns or discrepancies
- **Audit Trail**: Complete lineage from source document to processed transaction

### 4. Financial Analysis & Reporting

#### Dashboard Views
1. **Annual Tax Summary**
   - Federal vs state tax obligations
   - Ordinary vs qualified dividend breakdown
   - Tax-exempt interest summary
   - Capital gains/losses analysis

2. **Monthly Cash Flow Analysis**
   - Income trend visualization
   - Seasonal pattern identification
   - Source-by-source breakdown

3. **Investment Performance Tracking**
   - Realized gains/losses over time
   - Security-specific performance
   - Tax-efficiency metrics

4. **Tax Planning Tools**
   - Tax-loss harvesting opportunities
   - Municipal bond ladder analysis
   - Income timing optimization

#### Export Capabilities
- **Tax Preparation Reports**: Formatted summaries for tax professionals
- **CSV Exports**: Raw data for further analysis
- **PDF Reports**: Comprehensive annual summaries

### 5. User Interface & Experience

#### Web-Based Dashboard
- **Responsive Design**: Accessible from desktop and mobile
- **Intuitive Navigation**: Clear separation of import, analysis, and reporting functions
- **Real-Time Updates**: Live data refresh as documents are processed

#### Document Management
- **PDF Viewer Integration**: View original documents within application
- **Search & Filter**: Find specific transactions or documents
- **Annotation Support**: Add notes and tags to transactions

## Detailed Workflows

### Document Import Workflow
1. **File Drop**: User places PDFs in designated import folder
2. **Auto-Detection**: System identifies document type and account
3. **AI Extraction**: Claude processes PDF and extracts structured data
4. **Data Validation**: System validates extracted data and flags anomalies
5. **Database Storage**: Processed data written to PostgreSQL with audit trail
6. **User Review**: Dashboard shows newly imported data for verification
7. **Archive**: Original PDF moved to processed folder with metadata

### Monthly Reconciliation Workflow
1. **Import Current Month**: Process all statements and tax documents
2. **Cross-Reference**: Compare data across multiple sources
3. **Discrepancy Report**: Generate list of mismatches or missing data
4. **Manual Review**: User verifies and corrects flagged items
5. **Final Processing**: Confirmed data integrated into master database
6. **Report Generation**: Monthly summary and analysis reports

### Tax Season Workflow
1. **Annual Compilation**: Aggregate all tax-relevant transactions
2. **Form Generation**: Create summaries matching 1099 categories
3. **State Analysis**: Multi-state tax impact calculation
4. **Discrepancy Resolution**: Reconcile any remaining data gaps
5. **Export for Tax Prep**: Generate formatted reports for tax professional

## Technical Specifications

### Database Schema
(Reference: schema.md for complete details)
- **accounts**: Master account registry
- **documents**: Source document tracking
- **transactions**: All financial transactions with comprehensive tax attributes
- **tax_reports**: 1099 form summaries
- **securities**: Master security data with municipal bond specifics

### Performance Requirements
- **Import Speed**: Process typical monthly statement (10-20 pages) within 30 seconds
- **Query Response**: Dashboard loads within 2 seconds
- **Concurrent Access**: Support simultaneous access from PC and laptop
- **Data Integrity**: ACID compliance for all financial transactions

### Security & Privacy
- **Local Data Storage**: All financial data remains on local network
- **Encrypted Backups**: Time Machine integration for automated backups
- **Access Control**: User authentication for remote access
- **Audit Logging**: Complete access and modification history

## Integration Points

### Supabase Features Utilized
- **PostgreSQL Database**: Core data storage with financial precision
- **Real-Time Subscriptions**: Live dashboard updates
- **Authentication**: User access control
- **REST API**: Programmatic access for extensions
- **Admin Dashboard**: Database administration and monitoring

### External Integrations
- **File System**: Automated folder monitoring for new documents
- **Time Machine**: Backup integration
- **Tailscale**: Secure remote access
- **Future**: Tax software integration, additional broker APIs

## Success Metrics

### Functional Success
- **Import Accuracy**: >99% successful extraction of transaction data
- **Reconciliation Rate**: <1% unresolved discrepancies per month
- **Processing Time**: <2 minutes per document on average
- **User Adoption**: Daily use during active periods

### Business Value
- **Time Savings**: 80% reduction in manual financial data processing
- **Tax Accuracy**: Complete elimination of missed income reporting
- **Insight Generation**: Monthly trend analysis and tax optimization recommendations
- **Audit Readiness**: Complete documentation trail for all financial activity

## Development Phases

### Phase 1: Core Infrastructure (Weeks 1-2)
- Set up Supabase Docker on Mac Mini
- Implement database schema
- Create basic document import pipeline
- Build PDF processing foundation

### Phase 2: Data Processing (Weeks 3-4)  
- Implement AI-powered PDF extraction
- Build tax categorization engine
- Create reconciliation algorithms
- Develop data validation rules

### Phase 3: User Interface (Weeks 5-6)
- Build responsive web dashboard
- Implement document management features
- Create basic reporting views
- Add user authentication

### Phase 4: Advanced Features (Weeks 7-8)
- Advanced tax analysis tools
- Comprehensive reporting system
- Multi-state tax calculations
- Performance optimization

### Phase 5: Polish & Extension (Weeks 9-10)
- User experience refinements
- Additional document type support
- Backup and recovery features
- Documentation and deployment guides

## Risk Mitigation

### Technical Risks
- **PDF Parsing Accuracy**: Implement validation and manual review workflows
- **Database Performance**: Index optimization and query tuning
- **Network Reliability**: Offline mode support for critical functions

### Data Risks  
- **Backup Failures**: Multiple backup strategies (Time Machine + manual exports)
- **Hardware Failure**: Mac Mini replacement procedures and data recovery
- **Corruption**: Database integrity checks and point-in-time recovery

### Operational Risks
- **User Error**: Comprehensive audit trail and undo capabilities
- **Tax Rule Changes**: Modular tax engine for easy updates
- **Scale Limitations**: Performance monitoring and optimization plans

## Future Enhancements

### Short-Term (6 months)
- **Additional Brokers**: Schwab, Vanguard statement processing
- **Mobile App**: iOS/Android companion for viewing reports
- **Advanced Analytics**: Predictive modeling for tax planning

### Long-Term (12+ months)
- **Multi-Entity Support**: Handle multiple legal entities and accounts
- **Tax Software Integration**: Direct export to TurboTax, TaxAct
- **Investment Analysis**: Portfolio optimization and rebalancing recommendations
- **Collaborative Features**: Multi-user access with role-based permissions

## Conclusion

This comprehensive financial data management application addresses the critical need for automated, accurate processing of complex financial documents with sophisticated tax treatment analysis. By leveraging modern AI capabilities for document processing and robust database design for financial data integrity, the system will provide significant time savings and improved accuracy for financial analysis and tax preparation activities.