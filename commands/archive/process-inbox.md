# Process Inbox Command

**Created:** 09/18/25 11:15AM ET
**Updated:** 09/19/25 12:35PM ET - Added intuitive filename format with account mappings and source file renaming
**Purpose:** Guide Claude through intelligent document processing from inbox to structured JSON
**Usage:** User runs this command when new documents are ready for processing

## Command: `/process-inbox`

### Step 1: Discovery Phase
```bash
# Check what documents are waiting to be processed
ls -la /Users/richkernan/Projects/Finances/documents/inbox/
```

### Step 2: Initial Assessment

For each document found, I will:
1. **Identify the document type** by reading the first few pages
2. **Determine the institution** (Fidelity, Bank of America, etc.)
3. **Check for existing patterns** in our institution guides
4. **Report what I found** before proceeding

### Step 3: Pre-Processing Checks

Before extracting data, I will verify:
- **Duplicate Check:** Calculate MD5 hash and check against database
- **Amendment Check:** Look for "AMENDED", "CORRECTED", or version indicators
- **Multi-Account Check:** Determine if this is a combined statement
- **Confidence Assessment:** Flag any concerns before proceeding

### Step 4: Data Extraction (Collaborative Process)

**APPROACH:** Reference `/config/institution-patterns/fidelity-guide.md` for patterns and principles.
**REMEMBER:** You're intelligent - use your judgment. When uncertain, ASK THE USER for clarification.

Based on document type, I will:

#### For Financial Statements:
- Extract EXACT entity/account holder names as shown in the document
- Extract account numbers exactly as displayed
- **IMPORTANT:** Look for and parse structured tables:
  - "Securities Bought & Sold" sections with full trade details
  - "Activity" tables with transaction information
  - "Dividends and Interest" sections
  - "Options Activity" with contract details
- Parse all transactions with:
  - Date as shown (transaction AND settlement dates)
  - Action indicators ("You Bought" / "You Sold" / etc.)
  - Description EXACTLY as written (no interpretation)
  - Amount with proper sign
  - Quantity (number of shares/units)
  - Price per share (execution price)
  - Security symbols/CUSIPs from detail tables
  - Commission and fees if itemized
- Note page numbers for audit trail
- DO NOT apply any tax rules or categorization
- DO NOT interpret what type of income it is
- Just extract the raw data

#### For Tax Forms (1099s):
- Distinguish between Official vs Informational versions
- Extract all box values with their labels
- Link to appropriate entity/account
- Flag corporate exemption patterns (Official = $0)

#### For Bank Statements:
- Extract account details and period
- Parse transaction listings
- Identify check numbers and wire references
- Categorize by transaction type

### Step 5: Structured Output Generation

I will create a JSON file using field names from the Fidelity document map:
```json
{
  "extraction_session": {
    "timestamp": "ISO-8601 timestamp",
    "source_file": "original filename",
    "file_hash": "MD5 hash",
    "document_pages": "total pages",
    "extractor": "claude"
  },
  "document_info": {
    "institution": "as shown on document",
    "document_type": "statement/1099/etc",
    "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
    "portfolio_total_value": 1234567.89,
    "portfolio_change_period": 12345.67
  },
  "accounts": [
    {
      "account_number": "EXACTLY as shown",
      "account_holder_name": "EXACT name from document",
      "account_type": "as described in document",
      "net_account_value": 1234567.89,
      "transactions": [
        {
          "settlement_date": "YYYY-MM-DD",
          "security_name": "EXACT text from document",
          "security_identifier": "symbol or CUSIP",
          "transaction_description": "You Bought/You Sold/etc",
          "quantity": 123.456,
          "price_per_unit": 12.34,
          "cost_basis": 1234.56,
          "fees": 0.00,
          "amount": 1234.56,
          "transaction_type": "BUY/SELL/DIVIDEND/etc"
        }
      ],
      "positions": [
        {
          "security_description": "Full security name",
          "quantity": 123.456,
          "price_per_unit": 12.34,
          "market_value": 1234.56,
          "cost_basis": 1000.00,
          "unrealized_gain_loss": 234.56
        }
      ],
      "income_summary": {
        "taxable_income_period": 123.45,
        "taxable_income_ytd": 1234.56,
        "tax_exempt_income_period": 0.00,
        "tax_exempt_income_ytd": 0.00
      }
    }
  ],
  "extraction_notes": "Any observations or issues encountered during extraction"
}
```

### Step 6: Decision Points

I will **ASK THE USER** when:
- **Duplicate suspected:** "Found similar document [name] from [date]. Process anyway?"
- **Unknown pattern:** "This transaction type is new: [description]. How should I categorize?"
- **Entity unclear:** "Cannot determine which entity owns account [number]. Please specify."
- **Tax ambiguous:** "Cannot determine if [security] is GA municipal. Is it tax-exempt for GA?"

I will **FLAG FOR REVIEW** when:
- Confidence is below 80% on any transaction
- Corporate exemption pattern detected (expected but needs confirmation)
- Cross-source validation will be needed
- Manual verification recommended

I will **PROCEED AUTOMATICALLY** when:
- Standard FSIXX/SPAXX dividends with clear patterns
- Transactions match known patterns exactly
- All account numbers map to known entities
- Confidence is high across all extractions

### Step 7: File Management

After successful extraction, I will:

1. **Load account mappings** from `/config/account-mappings.json`
2. **Generate intuitive filenames** based on:
   - Institution (Fid, BoA, etc.)
   - Document type (Stmnt, 1099, etc.)
   - Statement period (YYYY-MM format)
   - Account labels from mapping (Brok, CMA, or last 4 digits if unmapped)
   - Extraction timestamp (YYYY.MM.DD_HH.MMET)

3. **Save files with meaningful names:**
```bash
# Example extraction filename for August 2025 Fidelity statement with accounts 7872 & 5656:
# Fid_Stmnt_2025-08_Brok&CMA_2025.09.18_15.48ET.json
/documents/extractions/[Institution]_[Type]_[Period]_[Accounts]_[YYYY.MM.DD]_[HH.MM]ET.json

# Rename and move source document with matching convention (without timestamp):
# Fid_Stmnt_2025-08_Brok&CMA.pdf
mv /documents/inbox/[genericname].pdf /documents/processed/[Institution]_[Type]_[Period]_[Accounts].pdf
```

4. **Update account mappings** if new accounts discovered:
   - Prompt user: "Found new account ending in 1234. What label should I use? (e.g., 'Checking', 'IRA', 'Brok')"
   - Add to `/config/account-mappings.json` for future use

## Institution-Specific Guides Referenced

Based on the institution identified, I will use:
- **Fidelity Document Map:** `/config/institution-patterns/fidelity-document-map.md` (PRIMARY REFERENCE)
- **Fidelity Patterns:** `/config/institution-patterns/fidelity.md` (tax treatment details)
- **Generic patterns:** `/config/doctrine.md`
- **Bank of America:** `/config/institution-patterns/boa.md` (to be created)
- **SunTrust:** `/config/institution-patterns/suntrust.md` (to be created)

## Tax Classification Rules (NOT APPLIED DURING EXTRACTION)

Tax categorization happens AFTER extraction during database loading.
During extraction, we only capture the RAW DATA from the document.
The description field tells us what it is (e.g., "Municipal Exempt Interest").
We do NOT interpret or categorize during extraction.

## Output Files Created

1. **JSON Extraction:** `/documents/extractions/extraction_[timestamp]_[docname].json`
2. **Processing Log:** Append to `/documents/logs/processing_[date].log`
3. **Review Items:** List in JSON under `needs_review` array

## Error Handling

If extraction fails:
- Save partial extraction with `"status": "failed"`
- Document specific failure reason
- Keep document in inbox for retry
- Alert user to the issue

## Success Criteria

Extraction is complete when:
- [ ] All pages have been reviewed
- [ ] All accounts are identified and mapped
- [ ] All transactions are extracted with complete details (including buy/sell, quantities, prices)
- [ ] JSON file is valid and complete
- [ ] Original document is moved to processing folder
- [ ] User has been notified of any items needing review

## Notes for Future Enhancement

As we process more document types, we should:
1. Create institution-specific extraction patterns
2. Build a library of transaction description mappings
3. Develop confidence scoring algorithms
4. Add support for OCR of scanned documents
5. Handle multi-currency transactions

---

## Example Usage

**User:** `/process-inbox`

**Claude:**
```
I found 2 documents in the inbox:
1. Statement8312025.pdf (Fidelity, 36 pages)
2. 1099DIV_2024.pdf (Fidelity, 2 pages)

Starting with Statement8312025.pdf...

This appears to be a Fidelity Combined Statement for August 2024.
I've identified 2 accounts:
- Z24-527872 (Milton Preschool Inc)
- Z27-375656 (Milton Preschool Inc)

Extracting transactions... [shows progress]

✓ Extracted 15 transactions with high confidence
! 2 items flagged for review:
  - Wire transfer on 08/13 has unclear destination
  - New security "VMFXX" not in our database

Creating extraction file: extraction_20250918_111530_Statement8312025.json

Shall I proceed with the 1099DIV document? (y/n)
```

---

*This command provides Claude with context and structure while maintaining the flexibility to handle various document types intelligently.*