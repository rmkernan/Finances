# Commands - Claude Code Operation Templates

**Created:** 09/09/25 5:52PM ET  
**Updated:** 09/09/25 5:52PM ET  
**Purpose:** Guide for using Claude Code command templates in financial data processing

## Command Overview

This directory contains Claude Code command templates for common financial data operations. These templates provide structured workflows for consistent, accurate processing of financial documents and data.

## Available Commands

### Core Processing Commands

#### [process-document.md](./process-document.md)
**Purpose:** Process new financial documents (PDFs, CSVs) and extract structured data  
**Use When:** New documents arrive in `/documents/inbox/`  
**Key Features:**
- Automatic document type classification
- AI-powered PDF data extraction  
- Tax treatment classification
- Data validation and quality checks
- File management and archiving

**Quick Usage:**
```bash
# Place documents in inbox, then use this template to:
# 1. Identify document type and structure
# 2. Extract all transaction and tax data
# 3. Apply proper tax classifications
# 4. Validate and store in database
# 5. Move processed files to archive
```

#### [reconcile-income.md](./reconcile-income.md)
**Purpose:** Cross-source income reconciliation and discrepancy identification  
**Use When:** Monthly reconciliation or investigating data mismatches  
**Key Features:**
- Multi-source data comparison (Fidelity vs 1099 vs QuickBooks)
- Variance detection and flagging
- Corporate exemption handling
- Missing transaction identification
- Automated reconciliation reporting

**Quick Usage:**
```bash
# Run monthly or after processing multiple document sources:
# 1. Compare dividend totals across sources
# 2. Validate tax-exempt interest amounts
# 3. Identify QuickBooks-only transactions (PPR Interest)
# 4. Flag discrepancies requiring investigation
# 5. Generate comprehensive reconciliation report
```

#### [generate-qbo.md](./generate-qbo.md)
**Purpose:** Generate QuickBooks QBO import files for brokerage cash flows  
**Use When:** Monthly bookkeeping integration or QuickBooks import needed  
**Key Features:**
- Cash flow focus (excludes internal security transactions)
- Proper OFX formatting for QuickBooks compatibility
- Account mapping to chart of accounts
- Duplicate prevention through unique transaction IDs
- Tax treatment preservation in categorization

**Quick Usage:**
```bash
# Generate monthly QBO files for QuickBooks import:
# 1. Select date range for export
# 2. Filter to cash flow transactions only
# 3. Apply account mappings from configuration
# 4. Generate OFX-formatted QBO file
# 5. Validate before QuickBooks import
```

## Command Usage Patterns

### Typical Monthly Workflow
```bash
1. Process new documents:
   - Use process-document.md for each new PDF/CSV in inbox
   - Validate extraction accuracy and completeness

2. Reconcile data sources:  
   - Use reconcile-income.md to identify discrepancies
   - Investigate and resolve significant variances

3. Generate QuickBooks integration:
   - Use generate-qbo.md to create monthly QBO file
   - Import to QuickBooks for bookkeeping integration
```

### Ad-Hoc Operations
```bash
Document Processing:
- Process individual documents as they arrive
- Handle special document types or edge cases
- Reprocess documents if extraction rules improve

Data Investigation:
- Reconcile specific time periods or transactions
- Research discrepancies flagged by automated processes
- Validate tax classifications for complex securities

Report Generation:
- Generate custom QBO exports for specific periods
- Create tax preparation summaries
- Export data for external analysis
```

## Command Structure and Customization

### Template Components
Each command template includes:
- **Overview:** Purpose and usage context
- **Workflow:** Step-by-step processing instructions
- **SQL Queries:** Database operations and validations
- **Error Handling:** Common issues and resolution approaches
- **Success Criteria:** How to verify successful completion

### Customization Guidelines
```markdown
Adapting Commands for Specific Situations:
1. **Copy the template** - Don't modify the original
2. **Customize parameters** - Dates, accounts, filters as needed
3. **Add specific validation** - Additional checks for your use case
4. **Document changes** - Note modifications for future reference
5. **Test thoroughly** - Validate results before relying on output
```

## Best Practices

### Before Running Commands

#### Data Preparation
- [ ] Ensure all source documents are available and accessible
- [ ] Verify database connectivity and permissions
- [ ] Check for any pending manual review items
- [ ] Backup critical data if making significant changes

#### Environment Validation
- [ ] Confirm working directory is `/Users/richkernan/Projects/Finances/`
- [ ] Verify access to documents directories
- [ ] Test database connection and schema availability
- [ ] Review any recent configuration changes

### During Command Execution

#### Process Monitoring
- [ ] Review extraction results for accuracy and completeness
- [ ] Monitor data quality flags and validation errors
- [ ] Verify transaction amounts and tax classifications
- [ ] Check cross-source reconciliation results

#### Error Response
- [ ] Stop processing if critical errors encountered
- [ ] Document and investigate any anomalies
- [ ] Flag uncertainties for manual review
- [ ] Preserve audit trail of all decisions and modifications

### After Command Completion

#### Validation and Documentation
- [ ] Verify all expected data was processed correctly
- [ ] Review and resolve any data quality flags
- [ ] Document any manual adjustments or decisions
- [ ] Update processing records and file organization

#### Follow-up Actions
- [ ] Move processed documents to appropriate folders
- [ ] Update configuration if new patterns identified
- [ ] Schedule any required follow-up processing
- [ ] Communicate results to stakeholders if needed

## Common Scenarios and Command Selection

### New Document Arrives
**Use:** [process-document.md](./process-document.md)
**Focus:** Complete extraction and validation
**Next Steps:** File archiving and cross-reference validation

### Month-End Reconciliation
**Use:** [reconcile-income.md](./reconcile-income.md)
**Focus:** Cross-source validation and discrepancy identification
**Next Steps:** Investigation of flagged variances

### QuickBooks Integration
**Use:** [generate-qbo.md](./generate-qbo.md)  
**Focus:** Cash flow export and account mapping
**Next Steps:** QBO file import and reconciliation in QuickBooks

### Data Quality Investigation
**Use:** Combination of reconcile-income.md and custom queries
**Focus:** Research specific discrepancies or patterns
**Next Steps:** Update processing rules or flag for manual resolution

## Error Recovery and Troubleshooting

### Common Issues

#### Document Processing Failures
```markdown
Symptoms: Incomplete extraction, formatting errors, validation failures
Solutions:
- Review document quality and format consistency
- Check Claude AI processing for accuracy
- Validate database schema and constraints
- Consider manual extraction for complex cases
```

#### Reconciliation Discrepancies  
```markdown
Symptoms: Cross-source variances, missing transactions, timing differences
Solutions:
- Investigate settlement vs transaction date differences
- Check for corporate exemption patterns (expected discrepancies)
- Research transaction types and categorization rules
- Review source document completeness
```

#### QBO Generation Problems
```markdown
Symptoms: Invalid OFX format, QuickBooks import failures, account mapping errors
Solutions:
- Validate OFX XML structure and required elements
- Check account mapping configuration and QuickBooks chart of accounts
- Verify transaction type conversions and amount precision
- Test with small transaction sets before full export
```

## Command Development and Maintenance

### Adding New Commands
```markdown
When creating new command templates:
1. Follow the established template structure
2. Include comprehensive workflow steps
3. Provide specific SQL queries and validations  
4. Document error handling and edge cases
5. Test with real data before committing
6. Update this README with new command description
```

### Maintaining Existing Commands
```markdown
Regular maintenance tasks:
- Update SQL queries as database schema evolves
- Incorporate new tax rules and business logic changes
- Enhance error handling based on operational experience
- Add new validation steps as edge cases are discovered
- Keep documentation current with actual processing workflows
```

## Related Resources

### Configuration Files
- **[/config/doctrine.md](../config/doctrine.md)** - Core processing decisions and patterns
- **[/config/tax-rules.md](../config/tax-rules.md)** - Tax classification logic
- **[/config/accounts-map.md](../config/accounts-map.md)** - QuickBooks integration mappings

### Technical Documentation  
- **[/docs/technical/processing-rules.md](../docs/technical/processing-rules.md)** - Detailed extraction guidelines
- **[/docs/technical/database-schema.md](../docs/technical/database-schema.md)** - Data structure and relationships
- **[/docs/requirements/current-requirements.md](../docs/requirements/current-requirements.md)** - Active development priorities

### Historical Context
- **[/docs/archive/context.md](../docs/archive/context.md)** - Original analysis and discoveries
- **[/docs/archive/prd.md](../docs/archive/prd.md)** - Complete product requirements
- **[/docs/archive/schema.md](../docs/archive/schema.md)** - Full database schema design

---

*These command templates embody best practices learned from real financial data processing. Use them as guides for consistent, accurate operations.*