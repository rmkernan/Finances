# 1099 Import Map & Instructions

**Created:** 2025-01-02
**Updated:** 2025-10-01 6:52PM - Added Claude orientation section with key rules and navigation guidance
**Updated:** 2025-10-01 7:10PM - Added PyPDF2 text extraction workflow for simple 1099 PDFs to save tokens
**Updated:** 2025-10-02 12:45PM - Updated to use custom Google Sheets MCP with expanded capabilities
**Updated:** 2025-10-02 1:43PM - Fixed pre-import validation to read full row 14 (A14:Z14) to see all existing accounts
**Updated:** 2025-10-02 1:46PM - Enhanced validation to read both row 3 (headers/Total column) and row 14 (accounts), insert new column before Total
**Updated:** 2025-10-02 2:26PM - Fixed 1099-B structure map: rows 17-18 headers, then category header + 6 data rows for each section (20-25, 27-32, 34-39, 41-46, 48-53, 55-60)

## 🎯 FOR CLAUDE: READ THIS FIRST

**Purpose:** This document guides importing 1099 tax forms into a consolidated Google Sheets worksheet.

**MCP Tool to Use:** Custom Google Sheets MCP (`mcp__google-sheets-custom__*`)
- **Available tools:** `read_cells`, `write_cells`, `insert_rows`, `insert_columns`
- **Documentation:** `/Users/richkernan/Projects/mcp-gsheet-custom/CONFIGS.md`
- **Important:** ALWAYS use `read_cells` to verify sheet state before and after operations

**Before you begin:**
1. **Read the entire "Import Workflow" section** (below) to understand the process
2. **Use `read_cells` to inspect the sheet** - see current data and find next available column
3. **Review the row structure** to know where data goes (rows 6-17 = payer/recipient, row 18+ = form data)
4. **Check the box mappings** for the specific form type you're importing
5. **Important rules:**
   - Account numbers are truncated to **9 characters** when written to the sheet
   - All four tabs (INT, DIV, MISC, B) must use the **same column** for consistency
   - Forms not applicable should have data boxes marked as **"N/A"**
   - Data starts at **row 18** for INT/DIV/MISC, **row 20** for 1099-B
   - Use **Python script** for Fidelity CSVs, **MCP tools** for simple PDFs

**For simple 1099 PDFs (recommended approach):**

Use **text extraction** instead of multimodal PDF reading to save tokens:

```python
import PyPDF2

pdf_path = '/path/to/1099.pdf'
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    print(text)  # Extract all text from PDF
```

Then manually populate using Custom Google Sheets MCP:
1. Extract key fields from text (payer, recipient, account number, box values)
2. Ask user for account name
3. Use `read_cells` to find next available column (C-G)
4. Use `write_cells` to populate all 4 tabs (can write multiple cells at once)
5. Use `read_cells` again to verify data was written correctly
6. Remember to truncate account number to 9 characters and mark N/A tabs appropriately

**MCP Tool Reference:**
- `mcp__google-sheets-custom__read_cells(spreadsheet_id, range_name)` - Read data from range
- `mcp__google-sheets-custom__write_cells(spreadsheet_id, range_name, values)` - Write 2D array to range
- `mcp__google-sheets-custom__insert_rows(spreadsheet_id, sheet_id, start_index, end_index)` - Insert rows
- `mcp__google-sheets-custom__insert_columns(spreadsheet_id, sheet_id, start_index, end_index)` - Insert columns

## Purpose
This document provides context and instructions for importing 1099 tax forms into the consolidated Google Sheets worksheet.

## Spreadsheet Information

### Location
- **Google Sheet ID**: `1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0`
- **URL**: https://docs.google.com/spreadsheets/d/1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0/edit
- **Title**: K-1 Consolidation Worksheet 2024

### Tab Structure
The worksheet contains the following tabs for 1099 forms:

1. **1099-INT** (Sheet ID: 371297715)
   - Interest Income
   - Columns: Box, Description, 1099-INT #1 through #5, Total

2. **1099-DIV** (Sheet ID: 477886708)
   - Dividends and Distributions
   - Columns: Box, Description, 1099-DIV #1 through #5, Total

3. **1099-B** (Sheet ID: 1830090953)
   - Broker Transactions
   - Columns: Box, Description, 1099-B #1 through #5, Total

4. **1099-MISC** (Sheet ID: 960633198)
   - Miscellaneous Income
   - Columns: Box, Description, 1099-MISC #1 through #5, Total

### Row Structure (Common to All Tabs)
- **Row 1**: Title
- **Row 3**: Headers (Box, Description, columns for each 1099, Total)
- **Row 6**: Payer's name
- **Row 7**: Payer's TIN/EIN
- **Row 8**: Payer's address
- **Row 11**: Recipient's name
- **Row 12**: Recipient's TIN
- **Row 13**: Recipient's address
- **Row 14**: Account number
- **Row 15**: Account name (friendly name derived from CSV filename)
- **Row 16**: (blank row)
- **Row 17**: Section header (empty)
- **Row 18+**: Form-specific box data

## Import Workflow

### Step 1: Pre-Import Validation
Before importing any 1099:

1. **Read sheet structure to understand layout**
   - Read row 3 (headers): `read_cells(spreadsheet_id, "1099-INT!A3:Z3")`
   - Read row 14 (account numbers): `read_cells(spreadsheet_id, "1099-INT!A14:Z14")`
   - Row 3 shows where the "Total" column is located
   - Row 14 shows which columns have existing account numbers

2. **Check for duplicates** by account number
   - Compare new account number against all existing accounts in row 14
   - If account number already exists, skip or confirm overwrite

3. **Identify where to insert new column**
   - New column must be inserted BEFORE the "Total" column
   - Use `insert_columns` to add a column at the Total column position (shifts Total to the right)
   - This becomes your target column for the new account data

### Step 2: Extract Data from CSV

#### Fidelity CSV Format
Fidelity provides CSVs with the following row types:

- **"1099 Summary"**: Aggregate totals row (use this for summary forms)
- **"1099-B-Detail"**: Individual transaction details
- **"1099-B-Subtotal-by-CUSIP"**: Subtotals by security
- **"1099-B-Total-by-section"**: Section totals
- **"1099-1256 Options Contracts"**: Options contract details

**Key Fields in CSV:**
- Column 2: Account number (e.g., "Z27375656", "Z24527872")
- Column 3: Customer Name
- Column 4: SSN/TIN
- Columns 8+: All box amounts for each form type

**Extraction Rules:**
1. Find the row where Column 1 = "1099 Summary"
2. Extract account number, customer name, SSN/TIN
3. Extract all 1099-DIV, 1099-INT, 1099-MISC, 1099-B, 1099-OID columns
4. Convert values to floats (strip leading zeros)
5. For 1099-B, use summary totals only (not individual transaction details)

### Step 3: Populate Spreadsheet

**For each form type (INT, DIV, MISC, B):**

1. **Determine target column**
   - Check existing account numbers in row 14
   - If account exists: update existing column
   - If new account: use next available column (C, D, E, F, or G)

2. **Write payer information** (rows 6-8):
   - Payer name
   - Payer TIN/EIN
   - Payer address

3. **Write recipient information** (rows 11-15):
   - Recipient name (from CSV)
   - Recipient TIN (from CSV)
   - Recipient address (from CSV or default)
   - Account number (from CSV)
   - Account name (derived from CSV filename: e.g., "2024_1099_Joint-CMA-5656.csv" → "Joint-CMA-5656")

4. **Write form amounts** (row 18+):
   - Map CSV column names to box numbers
   - Write only numeric values (leave text fields like foreign country)
   - Write $0 for boxes that are $0 (to show completeness)

5. **Preserve formatting**
   - Use `sheets_update_values` which updates values only
   - Never modify formatting, borders, colors, etc.

## Known Payers

### Fidelity Investments
- **Name**: Fidelity Investments
- **EIN**: 77-0196742
- **Address**: 100 Salem Street, Smithfield, RI 02917
- **CSV Location Pattern**: `/Users/richkernan/Library/CloudStorage/GoogleDrive-Rich@krkmilton.com/My Drive/Kernan Personal/Kernan Financials/Kernan Taxes/2024 Taxes/2024 Forms/Fidelity/`
- **File Pattern**: `2024_1099_Joint-*.csv`
- **Account Format**: Z########

**Known Fidelity Accounts:**
- Z27375656 (CMA-5656) - Cash Management Account
- Z24527872 (Brokerage-7872) - Brokerage Account

## Box Number Mappings

### 1099-INT (Interest Income)
| Row | Box | Description                                             | CSV Column                                                       |
|-----|-----|---------------------------------------------------------|------------------------------------------------------------------|
| 17  |     | FORM 1099-INT AMOUNTS (section header)                  | (structural row - no data)                                       |
| 18  | 1   | Interest income                                         | 1099-INT-1 Interest Income                                       |
| 19  | 2   | Early withdrawal penalty                                | 1099-INT-2 Early Withdrawal Penalty                              |
| 20  | 3   | Interest on U.S. Savings Bonds and Treasury obligations | 1099-INT-3 Interest on U.S. Savings Bonds and Treas. Obligations |
| 21  | 4   | Federal income tax withheld                             | 1099-INT-4 Federal Income Tax Withheld                           |
| 22  | 5   | Investment expenses                                     | 1099-INT-5 Investment Expenses                                   |
| 23  | 6   | Foreign tax paid                                        | 1099-INT-6 Foreign Tax Paid                                      |
| 24  | 7   | Foreign country or U.S. possession                      | 1099-INT-7 Foreign Country or U.S. Possession                    |
| 25  | 8   | Tax-exempt interest                                     | 1099-INT-8 Tax-Exempt Interest                                   |
| 26  | 9   | Specified private activity bond interest                | 1099-INT-9 Specified Private Activity Bond Interest              |
| 27  | 10  | Market discount                                         | 1099-INT-10 Market Discount                                      |
| 28  | 11  | Bond premium                                            | 1099-INT-11 Bond Premium                                         |
| 29  | 12  | Bond premium on Treasury obligations                    | 1099-INT-12 Bond premium on U.S. Treasury Obligations            |
| 30  | 13  | Bond premium on tax-exempt bond                         | 1099-INT-13 Bond Premium on Tax-Exempt Bond                      |
| 31  | 14  | Tax-exempt and tax credit bond CUSIP no.                | 1099-INT-14 Tax-Exempt Bond CUSIP No.                            |
| 32  |     | (blank separator row)                                   | (structural row - no data)                                       |
| 33  |     | STATE TAX INFORMATION (section header)                  | (structural row - no data)                                       |
| 34  | 15  | State                                                   | 1099-INT-15 State (shows "-" when empty)                         |
| 35  | 16  | State identification no.                                | 1099-INT-16 State Identification No. (shows "-" when empty)      |
| 36  | 17  | State tax withheld                                      | 1099-INT-17 State Tax Withheld (shows "0" when empty)            |
| 37  |     | (blank separator row)                                   | (structural row - no data)                                       |
| 38  |     | (blank separator row)                                   | (structural row - no data)                                       |
| 39  |     | (blank separator row)                                   | (structural row - no data)                                       |
| 40  |     | (blank separator row)                                   | (structural row - no data)                                       |

### 1099-DIV (Dividends and Distributions)
| Row | Box | Description                                        | CSV Column                                                     |
|-----|-----|----------------------------------------------------|----------------------------------------------------------------|
| 17  |     | FORM 1099-DIV AMOUNTS (section header)             | (structural row - no data)                                     |
| 18  | 1a  | Total ordinary dividends                           | 1099-DIV-1A Total Ordinary Dividends                           |
| 19  | 1b  | Qualified dividends                                | 1099-DIV-1B Qualified Dividends                                |
| 20  | 2a  | Total capital gain distributions                   | 1099-DIV-2A Total Capital Gain Distributions                   |
| 21  | 2b  | Unrecaptured Section 1250 gain                     | 1099-DIV-2B Unrecap. Sec 1250 Gain                             |
| 22  | 2c  | Section 1202 gain                                  | 1099-DIV-2C Section 1202 Gain                                  |
| 23  | 2d  | Collectibles (28%) gain                            | 1099-DIV-2D Collectibles (28%) Gain                            |
| 24  | 2e  | Section 897 ordinary dividends                     | 1099-DIV-2E SECTION 897 ORDINARY DIVIDENDS                     |
| 25  | 2f  | Section 897 capital gain                           | 1099-DIV-2F SECTION 897 CAPITAL GAIN                           |
| 26  | 3   | Nondividend distributions                          | 1099-DIV-3 Nondividend Distributions                           |
| 27  | 4   | Federal income tax withheld                        | 1099-DIV-4 Federal Income Tax Withheld                         |
| 28  | 5   | Section 199A dividends                             | 1099-DIV-5 Section 199A Dividends                              |
| 29  | 6   | Investment expenses                                | 1099-DIV-6 Investment Expenses                                 |
| 30  | 7   | Foreign tax paid                                   | 1099-DIV-7 Foreign Tax Paid                                    |
| 31  | 8   | Foreign country or U.S. possession                 | 1099-DIV-8 Foreign Country or U.S. Possession                  |
| 32  | 9   | Cash liquidation distributions                     | 1099-DIV-9 Cash Liquidation Distributions                      |
| 33  | 10  | Noncash liquidation distributions                  | 1099-DIV-10 Non-Cash Liquidation Distributions                 |
| 34  | 11  | FATCA filing requirement                           | 1099-DIV-11 FATCA filing requirement                           |
| 35  | 12  | Exempt-interest dividends                          | 1099-DIV-12 Exempt Interest Dividends                          |
| 36  | 13  | Specified private activity bond interest dividends | 1099-DIV-13 Specified Private Activity Bond Interest Dividends |
| 37  |     | (blank separator row)                              | (structural row - no data)                                     |
| 38  |     | STATE TAX INFORMATION (section header)             | (structural row - no data)                                     |
| 39  | 14  | State                                              | 1099-DIV-14 State (shows "-" when empty)                       |
| 40  | 15  | State identification no.                           | 1099-DIV-15 State Identification No. (shows "-" when empty)    |
| 41  | 16  | State tax withheld                                 | 1099-DIV-16 State Tax Withheld (shows "0" when empty)          |
| 42  |     | (blank separator row)                              | (structural row - no data)                                     |
| 43  |     | (blank separator row)                              | (structural row - no data)                                     |
| 44  |     | (blank separator row)                              | (structural row - no data)                                     |
| 45  |     | (blank separator row)                              | (structural row - no data)                                     |

### 1099-MISC (Miscellaneous Income)
| Row | Box | Description                                          | CSV Column                                                        |
|-----|-----|------------------------------------------------------|-------------------------------------------------------------------|
| 17  |     | FORM 1099-MISC AMOUNTS (section header)              | (structural row - no data)                                        |
| 18  | 1   | Rents                                                | 1099-MISC-1 Rents                                                 |
| 19  | 2   | Royalties                                            | 1099-MISC-2 Royalties                                             |
| 20  | 3   | Other income                                         | 1099-MISC-3 Other Income                                          |
| 21  | 4   | Federal income tax withheld                          | 1099-MISC-4 Federal Income Tax Withheld                           |
| 22  | 5   | Fishing boat proceeds                                | 1099-MISC-5 Fishing boat proceeds                                 |
| 23  | 6   | Medical and health care payments                     | 1099-MISC-6 Medical and health care payments                      |
| 24  | 7   | Direct sales of $5,000 or more                       | 1099-MISC-7 Direct sales of $5,000 or more                        |
| 25  | 8   | Substitute payments in lieu of dividends or interest | 1099-MISC-8 Substitute Payments In Lieu of Dividends and Interest |
| 26  | 9   | Crop insurance proceeds                              | 1099-MISC-9 Crop insurance proceeds                               |
| 27  | 10  | Gross proceeds paid to an attorney                   | 1099-MISC-10 Gross proceeds paid to an attorney                   |
| 28  | 11  | Fish purchased for resale                            | 1099-MISC-11 Fish purchased for resale                            |
| 29  | 12  | Section 409A deferrals                               | 1099-MISC-12 Section 409A deferrals                               |
| 30  | 13  | Excess golden parachute payments                     | 1099-MISC-13 Excess golden parachute payments                     |
| 31  | 14  | Nonqualified deferred compensation                   | 1099-MISC-14 Nonqualified deferred compensation                   |
| 32  |     | (blank separator row)                                | (structural row - no data)                                        |
| 33  |     | STATE TAX INFORMATION (section header)               | (structural row - no data)                                        |
| 34  | 15  | State tax withheld                                   | 1099-MISC-16 State Tax Withheld (shows "0" when empty)            |
| 35  | 16  | State/Payer's state no.                              | 1099-MISC-17 State/Payer's State No. (shows "-" when empty)       |
| 36  | 17  | State income                                         | 1099-MISC-18 State Income (shows "-" when empty)                  |
| 37  |     | (blank separator row)                                | (structural row - no data)                                        |
| 38  |     | (blank separator row)                                | (structural row - no data)                                        |
| 39  |     | (blank separator row)                                | (structural row - no data)                                        |
| 40  |     | (blank separator row)                                | (structural row - no data)                                        |

### 1099-B (Broker Transactions)
**Note**: 1099-B has a unique structure with breakdown by reporting category

#### Summary by Reporting Category (Rows 17-61)
Each category section has: category header + 6 data rows + blank separator row (except TOTAL which is last)

| Row   | Category/Metric                                     | Source                                                      |
|-------|-----------------------------------------------------|-------------------------------------------------------------|
| 17    | FORM 1099-B SUMMARY OF PROCEEDS (section header)    | (structural row - no data)                                  |
| 18    | (blank structural row)                              | (structural row - no data)                                  |
| 19    | Short-term, basis reported to IRS (category header) | (structural row - no data)                                  |
| 20    | - Total Proceeds                                    | 1099-B-Total-by-section row (SHORT TERM/COVERED) column 13  |
| 21    | - Total Cost Basis                                  | 1099-B-Total-by-section row (SHORT TERM/COVERED) column 14  |
| 22    | - Total Market Discount                             | 1099-B-Total-by-section row (SHORT TERM/COVERED) column 15  |
| 23    | - Total Wash Sales                                  | 1099-B-Total-by-section row (SHORT TERM/COVERED) column 16  |
| 24    | - Realized Gain/Loss                                | 1099-B-Total-by-section row (SHORT TERM/COVERED) calculated |
| 25    | - Fed Income Tax Withheld                           | 1099-B-Total-by-section row (SHORT TERM/COVERED) column 19  |
| 26    | Short-term, basis NOT reported (category header)    | (structural row - no data)                                  |
| 27    | - Total Proceeds                                    | Section totals: SHORT TERM / NONCOVERED                     |
| 28    | - Total Cost Basis                                  | Section totals: SHORT TERM / NONCOVERED                     |
| 29    | - Total Market Discount                             | Section totals: SHORT TERM / NONCOVERED                     |
| 30    | - Total Wash Sales                                  | Section totals: SHORT TERM / NONCOVERED                     |
| 31    | - Realized Gain/Loss                                | Section totals: SHORT TERM / NONCOVERED                     |
| 32    | - Fed Income Tax Withheld                           | Section totals: SHORT TERM / NONCOVERED                     |
| 33    | Long-term, basis reported to IRS (category header)  | (structural row - no data)                                  |
| 34    | - Total Proceeds                                    | Section totals: LONG TERM / COVERED                         |
| 35    | - Total Cost Basis                                  | Section totals: LONG TERM / COVERED                         |
| 36    | - Total Market Discount                             | Section totals: LONG TERM / COVERED                         |
| 37    | - Total Wash Sales                                  | Section totals: LONG TERM / COVERED                         |
| 38    | - Realized Gain/Loss                                | Section totals: LONG TERM / COVERED                         |
| 39    | - Fed Income Tax Withheld                           | Section totals: LONG TERM / COVERED                         |
| 40    | Long-term, basis NOT reported (category header)     | (structural row - no data)                                  |
| 41    | - Total Proceeds                                    | Section totals: LONG TERM / NONCOVERED                      |
| 42    | - Total Cost Basis                                  | Section totals: LONG TERM / NONCOVERED                      |
| 43    | - Total Market Discount                             | Section totals: LONG TERM / NONCOVERED                      |
| 44    | - Total Wash Sales                                  | Section totals: LONG TERM / NONCOVERED                      |
| 45    | - Realized Gain/Loss                                | Section totals: LONG TERM / NONCOVERED                      |
| 46    | - Fed Income Tax Withheld                           | Section totals: LONG TERM / NONCOVERED                      |
| 47    | Basis not reported, term unknown (category header)  | (structural row - no data)                                  |
| 48    | - Total Proceeds                                    | Section totals: (if exists)                                 |
| 49    | - Total Cost Basis                                  | Section totals: (if exists)                                 |
| 50    | - Total Market Discount                             | Section totals: (if exists)                                 |
| 51    | - Total Wash Sales                                  | Section totals: (if exists)                                 |
| 52    | - Realized Gain/Loss                                | Section totals: (if exists)                                 |
| 53    | - Fed Income Tax Withheld                           | Section totals: (if exists)                                 |
| 54    | TOTAL (category header)                             | (structural row - no data)                                  |
| 55    | - Total Proceeds                                    | 1099-B-Total Proceeds                                       |
| 56    | - Total Cost Basis                                  | 1099-B-Total Cost Basis                                     |
| 57    | - Total Market Discount                             | 1099-B-Total Market Discount                                |
| 58    | - Total Wash Sales                                  | 1099-B-Total Wash Sales                                     |
| 59    | - Realized Gain/Loss                                | 1099-B-Realized Gain/Loss                                   |
| 60    | - Fed Income Tax Withheld                           | 1099-B-Federal Income Tax Withheld                          |
| 61    | TRANSACTION DETAILS (footer note)                   | (structural row - no data)                                  |

## Deduplication Strategy

### Check Before Import
1. Read all account numbers from row 14 across columns C-G for each tab
2. Match against CSV account number
3. If found:
   - Prompt: "Account {account} already exists in column {col}. Overwrite? (y/n)"
   - If yes: overwrite that column
   - If no: skip import
4. If not found: use next available column

## Python Script Location

**Script**: `/Users/richkernan/Projects/Finances/Taxes/Scripts/import_1099.py`

### Usage
```bash
python3 /Users/richkernan/Projects/Finances/Taxes/Scripts/import_1099.py \
  --csv "/path/to/fidelity_1099.csv" \
  --check-duplicates
```

## Quick Reference Commands

### List all imported accounts
```python
# Check 1099-INT accounts
sheets_get_values(range="1099-INT!C14:G14", spreadsheetId="1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0")

# Check 1099-DIV accounts  
sheets_get_values(range="1099-DIV!C14:G14", spreadsheetId="1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0")
```

### Import new 1099
```python
# 1. Extract from CSV
# 2. Check for duplicates (row 14)
# 3. Find next available column
# 4. Populate payer info (rows 6-8)
# 5. Populate recipient info (rows 11-14)
# 6. Populate amounts (rows 16+)
```

## Common Issues & Solutions

### Issue: Account number already exists
- **Solution**: Check if this is an update or duplicate. Compare dates/amounts.

### Issue: CSV format different from expected
- **Solution**: Fidelity format may vary. Check column headers match expected names.

### Issue: Missing box values
- **Solution**: Write $0 for numeric boxes, leave text boxes empty if not provided.

### Issue: Formatting lost after import
- **Solution**: Only use `sheets_update_values`, never `sheets_batch_update` with formatting. Values-only updates preserve all formatting.

## Import Checklist

- [ ] Locate CSV file
- [ ] Open Python/script environment
- [ ] Run extraction script
- [ ] Review extracted data for accuracy
- [ ] Check for duplicate account numbers
- [ ] Determine target column(s)
- [ ] Import to spreadsheet (values only)
- [ ] Verify totals column calculates correctly
- [ ] Cross-check one or two boxes against PDF/paper form
- [ ] Mark CSV as imported (rename or move to /imported folder)

## Notes

- Always preserve user formatting in spreadsheet
- Account numbers are the primary key for deduplication
- For Fidelity, use only "1099 Summary" row, not detail rows
- The "Total" column (H) auto-calculates via formulas
- Each form type can hold up to 5 separate 1099s (columns C-G)

## Last Updated
2025-01-02
