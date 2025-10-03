# K-1 Import Guide - Dual Verification Workflow

**Spreadsheet ID:** `1LR5lo2CKtYk_Gr27QfaTyOTbD1wzNvZB1p9cTzNNe_0`
**Created:** 2025-01-30
**Updated:** 2025-10-01 9:10PM - Complete revamp for dual-verification approach
**Updated:** 2025-10-01 9:12PM - Added visual-first checklist workflow to prevent box mapping errors
**Updated:** 2025-10-01 9:39PM - Added two-column screenshot requirement and row 64 spacing warning
**Updated:** 2025-10-02 12:47PM - Updated to use custom Google Sheets MCP with read/write/insert capabilities

## 🎯 Take a Deep Breath - This Is Simpler Than It Looks

**What you're really doing:** Going box by box through a tax form, observing what you see, and transcribing that data into a Google Sheet. That's it. Piece of cake.

**The key to success:** Be slow, methodical, and careful. Use BOTH tools together:

1. **Screenshot** → Shows you WHERE each box is located (visual structure)
2. **Extracted text** → Tells you EXACTLY what's in each box (no guessing, no hallucination)

**Core principle:** NEVER trust visual interpretation alone. Always verify values against the extracted text.

## 🔧 MCP Tools for K-1 Import

**Use Custom Google Sheets MCP:** `mcp__google-sheets-custom__*`

**Available tools:**
- `read_cells` - **ALWAYS use first** to check for duplicates and find next column
- `write_cells` - Write K-1 data to sheet
- `insert_rows` / `insert_columns` - Add structure if needed

**Workflow:**
1. Use `read_cells` to read row 5 (check EIN for duplicates)
2. Use `read_cells` to identify next available column
3. Use `write_cells` to populate data
4. Use `read_cells` to verify data was written correctly

**Documentation:** `/Users/richkernan/Projects/mcp-gsheet-custom/CONFIGS.md`

## ⚠️ Critical: Do NOT Read PDF Files

**If asked to process a K-1 PDF directly:** STOP and request:
1. A screenshot of page 1 (for visual layout)
2. Permission to extract text from page 1 using Python (for accurate values)

**Why?** K-1 PDFs are too large and will overwhelm the context window. Reading them directly will fail.

## 🚀 The Workflow (6 Careful Steps)

### Step 1: Get Both Inputs

**User provides:** TWO screenshots (left column + right column) + PDF path

**Why two screenshots?** The K-1 form has two columns. Splitting them reduces visual interference and makes it easier to read each box clearly.

**You do:**
```bash
python3 /Users/richkernan/Projects/Finances/Taxes/Scripts/extract_k1_page1.py '<pdf_path>'
```

**Result:** You now have:
- Left column screenshot (Parts I & II)
- Right column screenshot (Part III)
- Extracted text (accurate values)

### Step 2: Check for Duplicates

1. Find the EIN in the extracted text (search for pattern like "83-3903231")
2. Read row 5 of spreadsheet across all columns
3. If EIN exists → inform user it's already imported
4. If not → identify next available column (F, G, H, etc.)

### Step 3: VISUAL FIRST PASS - Create Box-by-Box Checklist

**Go through the screenshot ONE BOX AT A TIME.** For each box, observe and record:

**Part I & II (Boxes A-N):**
- Box A: [EIN from screenshot]
- Box B: [Partnership name/address]
- Box C: [IRS center]
- Box D: [Is PTP box checked? X or blank]
- Box E: [Partner SSN]
- Box F: [Partner name/address]
- Box G: [Which option is checked? "General partner or LLC member-manager" OR "Limited partner or other LLC member"]
- Box H1: [Which option is checked? "Domestic partner" OR "Foreign partner"]
- Box H2: [Disregarded entity info or blank]
- Box I1: [Entity type]
- Box I2: [Retirement plan checkbox - X or blank]
- Box J: [6 percentage values for profit/loss/capital beginning/ending]
- Box K1: [6 liability values]
- Box K2: [Checkbox - X or blank]
- Box K3: [Checkbox - X or blank]
- Box L: [6 capital account values]
- Box M: [Which box is checked? "Yes" or "No" - look at the actual checkbox, not just the field]
- Box N: [2 values for beginning/ending]

**Part III (Boxes 1-23):**
- Box 1: [Value or blank]
- Box 2: [Value or blank]
- Box 3: [Value or blank]
- Box 4a: [Value or blank]
- Box 4b: [Value or blank]
- Box 4c: [Value or blank]
- Box 5: [Value or blank]
- Box 6a: [Value or blank]
- Box 6b: [Value or blank]
- Box 6c: [Value or blank]
- Box 7: [Value or blank]
- Box 8: [Value or blank]
- Box 9a: [Value or blank]
- Box 9b: [Value or blank]
- Box 9c: [Value or blank]
- Box 10: [Value or blank]
- Box 11: [Value or blank]
- Box 12: [Value or blank]
- Box 13: [How many lines? What's on each line?]
- Box 14: [How many lines? What's on each line?]
- Box 15: [How many lines? What's on each line?]
- Box 16: [Checkbox - X or blank]
- Box 17: [How many lines? What's on each line?]
- Box 18: [How many lines? What's on each line?]
- Box 19: [How many lines? What's on each line?]
- Box 20: [How many lines? What's on each line?]
- Box 21: [Value or blank]
- Box 22: [Checkbox - X or blank]
- Box 23: [Checkbox - X or blank]

**Present this checklist to the user for review before proceeding.**

### Step 4: MAP TO EXTRACTED TEXT

Now match your visual observations to the extracted text to get EXACT values:

1. The extracted text is a stream of values without labels
2. Go through your visual checklist in order
3. For each non-blank box, the next value in the extracted text should match
4. **If something doesn't match or seems ambiguous** → STOP and ask the user

**Example:**
- Visual: Box 1 shows a negative number
- Extracted text shows: "(8,984)"
- Match! ✓

- Visual: Box 9a shows "65"
- But wait, extracted text after Box 8 shows: "65" then "9" then "24"
- Which is 9a, 9b, 9c? STOP and ask user.

### Step 5: RESOLVE AMBIGUITIES

**When unclear, ask the user specific questions:**
- "I see values 65, 9, and 24 after Box 8. Which boxes are these for: 9a, 9b, 9c, or 10?"
- "Box M shows two checkboxes. Which one has an X inside: Yes or No?"
- "Box 16 - is the checkbox marked X or blank?"

### Step 6: BUILD ARRAY AND POPULATE

1. Build 84-row array using confirmed values from extracted text
2. Update spreadsheet column
3. Read back multi-line boxes to verify
4. Fix any errors immediately

## 📋 Row Mapping Reference

**Only consult this when you need to know which row a specific box goes in.**

### Part I - Partnership Info (Rows 5-8)
- Row 5: Box A - EIN
- Row 6: Box B - Partnership name/address (multi-line)
- Row 7: Box C - IRS center (usually "E-FILE")
- Row 8: Box D - PTP checkbox ("X" or blank)

### Part II - Partner Info (Rows 11-17)
- Row 11: Box E - Partner SSN
- Row 12: Box F - Partner name/address (multi-line)
- Row 13: Box G - Partner type text (not just "X")
- Row 14: Box H1 - Domestic/Foreign text (not just "X")
- Row 15: Box H2 - Disregarded entity (usually blank)
- Row 16: Box I1 - Entity type (usually "INDIVIDUAL")
- Row 17: Box I2 - Retirement plan checkbox

### Box J - Profit/Loss/Capital (Rows 19-24)
- Rows 19-20: Profit Beginning/Ending %
- Rows 21-22: Loss Beginning/Ending %
- Rows 23-24: Capital Beginning/Ending %

### Box K1 - Liabilities (Rows 26-31)
- Rows 26-27: Nonrecourse Beginning/Ending
- Rows 28-29: Qualified nonrecourse Beginning/Ending
- Rows 30-31: Recourse Beginning/Ending

### Box K2-K3 (Rows 32-33)
- Row 32: Lower-tier partnerships checkbox
- Row 33: Guarantees checkbox

### Box L - Capital Account (Rows 35-40)
- Row 35: Beginning
- Row 36: Contributed
- Row 37: Net income/loss
- Row 38: Other increase/decrease
- Row 39: Withdrawals
- Row 40: Ending

### Box M-N (Rows 41, 43-44)
- Row 41: Built-in gain/loss (Yes/No/X No/X Yes)
- Row 43: Box N Beginning
- Row 44: Box N Ending

### Part III - Income Items (Rows 47-88)

**⚠️ CRITICAL: Row 64 is a blank spacing row - DO NOT populate it. Use batch update to skip it.**

**Single-line boxes:**
- Rows 47-63: Boxes 1-11 (NOTE: Box 11 has 2 rows: 63 is line 1, row 64 is SPACING)
- Row 65: Box 12
- Row 73: Box 16 (checkbox)
- Rows 86-88: Boxes 21-23

**Multi-line boxes (each line = one discrete value per row):**
- Box 11 (row 63 only): Other income (loss) - 1 line (row 64 is spacing, not part of Box 11)
- Box 13 (rows 66-68): Other deductions, 3 lines
- Box 14 (rows 69-70): Self-employment, 2 lines
- Box 15 (rows 71-72): Credits, 2 lines
- Box 17 (rows 74-76): AMT items, 3 lines
- Box 18 (rows 77-79): Tax-exempt income, 3 lines
- Box 19 (rows 80-81): Distributions, 2 lines
- Box 20 (rows 82-85): Other information, 4 lines

**For multi-line boxes:** Find the box in extracted text, then record each discrete value on its own row. Some codes appear without amounts (just "A" not "A: 123") - record exactly as shown.

## 🎯 Key Success Factors

1. **Always use extracted text for values** - Never rely on visual interpretation alone
2. **Use screenshot for structure only** - It tells you where boxes are, not what's in them
3. **Multi-line boxes get one value per row** - Don't combine multiple lines in one cell
4. **Blank rows stay blank** - Don't populate headers, spacing rows, or section dividers
5. **Record exactly as shown** - "A" is different from "A: 0" is different from blank

## 📊 Current K-1s in Spreadsheet

| Column | Partnership | EIN | Status |
|--------|------------|-----|--------|
| C | Steel Partners Holdings L.P. | 13-3727655 | Complete ✓ |
| D | Energy Transfer LP | 30-0108820 | Complete ✓ |
| E | MPLX LP | 27-0005456 | Complete ✓ |
| F | (Partner name here) | 30-0924031 | Complete ✓ |
| G | (Available) | - | Empty |

---

**Remember:** Screenshot = WHERE. Extracted text = WHAT. Use both, trust the text.
