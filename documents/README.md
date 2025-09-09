# Documents - Financial Document Management

**Created:** 09/09/25 5:56PM ET  
**Updated:** 09/09/25 5:56PM ET  
**Purpose:** Guide for organizing and managing financial documents in the processing pipeline

## Directory Structure

### Document Lifecycle Management

```
/documents/
├── /inbox/           # New documents awaiting processing
├── /processed/       # Successfully processed documents  
├── /archived/        # Year-end and long-term storage
└── README.md         # This file - document handling guide
```

## Document Flow Workflow

### 1. Document Arrival → `/inbox/`

#### Supported Document Types
- **Fidelity Monthly Statements** (PDF) - Complete transaction and holdings data
- **Fidelity 1099 Tax Forms** (PDF) - Official and informational tax summaries
- **Fidelity CSV Exports** (CSV) - Structured tax form data
- **QuickBooks Exports** (CSV) - Cash flow and income tracking data
- **Other Broker Statements** (PDF) - Extensible for additional institutions

#### File Naming Conventions
```
Recommended naming pattern for clarity:
YYYY-MM-DD_Source_DocumentType_AccountRef

Examples:
2024-01-31_Fidelity_Statement_Z40394067.pdf
2024-12-31_Fidelity_1099DIV_Official_Z40394067.pdf  
2024-12-31_Fidelity_1099DIV_Info_Z40394067.pdf
2024-12-31_QuickBooks_Export_MiltonPreschool.csv
```

#### Upload Process
```bash
# From PC via network share:
Copy files to: \\Mac-mini\richkernan\Projects\Finances\documents\inbox\

# From Mac directly:
Copy files to: /Users/richkernan/Projects/Finances/documents/inbox/

# Automatic monitoring will detect new files for processing
```

### 2. Processing → Database Extraction

#### Automated Processing Pipeline
1. **File Detection:** System monitors inbox for new files
2. **Document Classification:** Auto-identify document type and structure  
3. **Data Extraction:** Claude AI processes PDF/CSV content
4. **Validation:** Cross-check extracted data for accuracy
5. **Database Storage:** Insert structured data with audit trail
6. **File Movement:** Move to processed folder with timestamp

#### Processing Verification
```sql
-- Check processing status for recent documents
SELECT 
    d.file_path,
    d.document_type,
    d.processed_at,
    COUNT(t.id) as transactions_extracted
FROM documents d
LEFT JOIN transactions t ON d.id = t.document_id
WHERE d.processed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY d.id, d.file_path, d.document_type, d.processed_at
ORDER BY d.processed_at DESC;
```

### 3. Archive Management → `/processed/` and `/archived/`

#### Processed Documents (`/processed/`)
- **Purpose:** Recently processed documents with active data
- **Retention:** Current and prior year for operational access
- **Organization:** Flat structure with descriptive filenames
- **Backup:** Included in regular system backups

#### Archived Documents (`/archived/`)  
- **Purpose:** Long-term storage for historical documents
- **Organization:** Year-based folder structure
- **Retention:** Permanent retention for audit and tax purposes
- **Access:** Reference only, not actively processed

```
/archived/
├── /2022/
├── /2023/
├── /2024/
│   ├── /statements/
│   ├── /1099-forms/  
│   └── /other/
└── /2025/
```

## Document Types and Processing

### Fidelity Monthly Statements

#### Key Data Elements
- **Account Information:** Holder name, account number, statement period
- **Transaction Details:** Date, type, security, quantity, amount
- **Holdings Summary:** Positions, market values, asset allocation
- **Cash Flow:** Deposits, withdrawals, dividends, interest

#### Processing Focus Areas
```markdown
Critical Extractions:
- All dividend and interest transactions with precise amounts
- Security identification (symbol, CUSIP, full name)
- Tax treatment indicators (municipal bonds, tax-exempt interest)
- Cash flow events (deposits, withdrawals, transfers)
- Settlement dates for proper tax year assignment
```

#### Common Patterns
```markdown
January Statement (Example):
- FSIXX dividends: ~$4,327 (Treasury fund, fully taxable)
- SPAXX dividends: ~$2 (Money market, fully taxable)
- Large withdrawals: $200k wire transfers to other accounts
- Municipal bond interest: Various amounts by issuer state
```

### Fidelity 1099 Tax Forms

#### Document Variations
1. **Official 1099 Forms** - IRS-reported amounts
2. **Informational 1099 Forms** - Complete income picture for corporate exemption

#### Corporate Exemption Pattern (Milton Preschool Inc)
```markdown
Expected Pattern for Corporate Exemption:
Official Form: All income boxes = $0.00 + "exempt recipient" notation
Informational Form: Actual amounts + "not furnished to IRS" disclaimer

Example 2024:
- Official 1099-DIV: $0 dividends (reported to IRS)
- Informational 1099-DIV: $29,515 dividends (actual income)
- Both show same bond redemption proceeds: $240,000
```

#### Key Form Types
- **1099-DIV:** Dividend and capital gain distributions
- **1099-INT:** Interest income (taxable and tax-exempt)
- **1099-B:** Proceeds from broker transactions (bond sales/redemptions)

### CSV Data Files

#### Fidelity CSV Exports
```markdown
Structure: Consolidated 1099 data in structured format
Key Fields: Account number, form type, box amounts, security details
Usage: Validation and cross-reference with PDF forms
Common Issue: May show $0 for corporate exemption (same as official PDFs)
```

#### QuickBooks Export Data
```markdown
Structure: Transaction-level cash flow data
Key Fields: Date, account, transaction type, amount, description
Usage: Identify transactions missing from Fidelity sources
Known Gap: "PPR Interest" payments often present in QB but not Fidelity
```

## File Management Best Practices

### Security and Privacy

#### Local Storage Policy
- **No Cloud Storage:** All financial documents remain on local network
- **Encrypted Backups:** Time Machine with encrypted volumes  
- **Access Control:** Network shares with authentication
- **Audit Trail:** Complete processing history maintained

#### File Integrity
```bash
# Verify file integrity using checksums
shasum -a 256 /path/to/document.pdf > document.pdf.sha256

# Check for file corruption before processing
shasum -a 256 -c document.pdf.sha256
```

### Organization Standards

#### File Naming Consistency
```markdown
Benefits of Standard Naming:
- Easy sorting and chronological organization
- Clear identification of source and content
- Prevents processing of duplicate files
- Supports automated file management
```

#### Folder Structure Maintenance
```bash
# Weekly cleanup - move old processed files to archive
find /processed/ -name "*.pdf" -mtime +365 -exec mv {} /archived/$(date +%Y)/ \;

# Monthly organization - verify folder structure
ls -la /documents/inbox/     # Should be empty or contain only new files
ls -la /documents/processed/ # Should contain current year documents  
ls -la /documents/archived/  # Should have year-based organization
```

## Document Processing Commands

### Manual Processing Workflow

#### Process New Document
```bash
# 1. Verify document in inbox
ls -la /Users/richkernan/Projects/Finances/documents/inbox/

# 2. Use processing command template
# See: /commands/process-document.md

# 3. Verify extraction results
SELECT * FROM transactions WHERE document_id = [new_document_id];

# 4. Check file moved to processed
ls -la /Users/richkernan/Projects/Finances/documents/processed/
```

#### Batch Processing Multiple Documents
```bash
# Process all documents in inbox sequentially
for file in /documents/inbox/*.{pdf,csv}; do
    echo "Processing: $file"
    # Apply process-document.md template
    # Verify results before proceeding to next
done
```

### Quality Assurance Checks

#### Post-Processing Validation
```sql
-- Verify all documents have extracted data
SELECT 
    d.file_path,
    d.document_type,
    COUNT(t.id) as transaction_count,
    SUM(t.amount) as total_amount
FROM documents d
LEFT JOIN transactions t ON d.id = t.document_id
WHERE d.processed_at >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY d.id, d.file_path, d.document_type;
```

#### Missing Document Detection
```sql
-- Check for expected monthly statements
WITH expected_statements AS (
    SELECT generate_series(
        date_trunc('month', CURRENT_DATE - INTERVAL '12 months'),
        date_trunc('month', CURRENT_DATE),
        '1 month'::interval
    )::date as expected_month
)
SELECT 
    e.expected_month,
    COUNT(d.id) as statements_found
FROM expected_statements e
LEFT JOIN documents d ON date_trunc('month', d.period_start) = e.expected_month
    AND d.document_type = 'statement'
GROUP BY e.expected_month
HAVING COUNT(d.id) = 0  -- Missing statements
ORDER BY e.expected_month;
```

## Troubleshooting Common Issues

### Processing Failures

#### PDF Reading Issues
```markdown
Symptoms: Extraction errors, incomplete data, formatting problems
Solutions:
- Verify PDF is not password-protected or corrupted
- Check file size and page count for completeness
- Try alternative PDF processing if Claude has difficulties
- Consider manual extraction for critical documents
```

#### Document Classification Errors
```markdown
Symptoms: Wrong document type assigned, incorrect processing workflow
Solutions:  
- Review document header and content structure
- Check for non-standard formats or layouts
- Update classification rules for new document variations
- Process manually with correct document type specified
```

### File Management Issues

#### Duplicate File Detection
```sql
-- Find potential duplicate documents by file hash
SELECT file_hash, COUNT(*), STRING_AGG(file_path, '; ') as file_paths
FROM documents 
GROUP BY file_hash
HAVING COUNT(*) > 1;
```

#### Missing File Recovery
```bash
# Check Time Machine for accidentally deleted files
sudo tmutil listbackups
sudo tmutil restore /path/to/missing/file

# Verify network share connectivity for remote access
ping mac-mini.local
smbclient -L //mac-mini.local -U richkernan
```

## Related Documentation

### Processing Workflows
- **[/commands/process-document.md](../commands/process-document.md)** - Document processing command template
- **[/docs/technical/processing-rules.md](../docs/technical/processing-rules.md)** - Extraction guidelines

### Configuration
- **[/config/doctrine.md](../config/doctrine.md)** - Core processing decisions
- **[/docs/technical/database-schema.md](../docs/technical/database-schema.md)** - Data structure

### Historical Examples
- **[/docs/archive/context.md](../docs/archive/context.md)** - Sample document analysis and patterns

---

*Proper document management ensures complete audit trails and reliable data processing. Maintain organization and security throughout the document lifecycle.*