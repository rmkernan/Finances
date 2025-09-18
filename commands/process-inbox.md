# Process Inbox Command

**Created:** 09/18/25 11:15AM ET
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

### Step 4: Pure Data Extraction (NO INTERPRETATION)

Based on document type, I will:

#### For Financial Statements:
- Extract EXACT entity/account holder names as shown in the document
- Extract account numbers exactly as displayed
- Parse all transactions with:
  - Date as shown
  - Description EXACTLY as written (no interpretation)
  - Amount with proper sign
  - Security symbols/CUSIPs if present
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

I will create a JSON file with this structure:
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
    "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
  },
  "accounts": [
    {
      "account_number": "EXACTLY as shown",
      "account_holder": "EXACT name from document",
      "account_type": "as described in document",
      "transactions": [
        {
          "date": "YYYY-MM-DD",
          "description": "EXACT text from document",
          "amount": 1234.56,
          "symbol": "if shown",
          "cusip": "if shown",
          "page": "source page number"
        }
      ]
    }
  ],
  "extraction_feedback": {
    "confidence": "high/medium/low",
    "ambiguities": ["things that were unclear"],
    "assumptions": ["any decisions I had to make"],
    "questions": ["things I need clarification on"]
  }
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

After successful extraction:
```bash
# Save extraction to timestamped JSON
/documents/extractions/extraction_YYYYMMDD_HHMMSS_[filename].json

# Move original to processing folder (not processed yet - awaiting load confirmation)
mv /documents/inbox/[file] /documents/processing/[file]
```

## Institution-Specific Guides Referenced

Based on the institution identified, I will use:
- **Fidelity:** `/config/institution-patterns/fidelity.md`
- **Bank of America:** `/config/institution-patterns/boa.md` (to be created)
- **SunTrust:** `/config/institution-patterns/suntrust.md` (to be created)
- **Generic patterns:** `/config/doctrine.md`

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
- [ ] All transactions are extracted with tax categories
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