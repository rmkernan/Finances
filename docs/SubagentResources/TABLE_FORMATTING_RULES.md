# Markdown Table Formatting Rules - Programmatic Approach

**Created:** 09/10/25 10:35AM ET  
**Updated:** 09/10/25 11:42AM ET - Added automatic table detection and Claude workflow instructions  
**Purpose:** Token-efficient, programmatic markdown table formatting with multi-line cell support  

---

## 🚨 Critical: Never Count Separator Lines

**IMPORTANT:** When calculating column widths, **exclude separator lines** (|---|---|):
- Separator lines are OUTPUT, not INPUT
- They are generated AFTER calculating content widths
- Including them causes over-padding and misalignment

**Only count actual content rows (headers and data).**

---

## Core Principle: Use Python, Not Manual Counting

Manual character counting is unreliable and inefficient. The Python script below handles everything automatically with 100% accuracy.

---

## The Solution: Python Script

### Quick Usage

```bash
# Fix a table from lines 100-150
sed -n '100,150p' file.md | python3 -c "[paste script below]" > fixed_table.txt

# Then replace in file
(head -n 99 file.md; cat fixed_table.txt; tail -n +151 file.md) > file.md.new
mv file.md.new file.md
```

### The Script

```python
import sys
import textwrap

MAX_COL_WIDTH = 75  # Adjust if needed
MIN_PADDING = 2

def split_cell_content(content, max_width):
    if len(content) <= max_width - MIN_PADDING:
        return [content]
    wrapper = textwrap.TextWrapper(width=max_width - MIN_PADDING, 
                                 break_long_words=False,
                                 break_on_hyphens=True)
    return wrapper.wrap(content)

def process_table():
    lines = [line.rstrip() for line in sys.stdin]
    raw_rows = []
    
    # CRITICAL: Skip separator lines (|---|)
    for line in lines:
        if line.strip() and not line.startswith('|--'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                raw_rows.append(cells)
    
    if not raw_rows:
        return
    
    processed_rows = []
    for row in raw_rows:
        split_cells = []
        max_lines = 1
        
        for cell in row:
            cell_lines = split_cell_content(cell, MAX_COL_WIDTH)
            split_cells.append(cell_lines)
            max_lines = max(max_lines, len(cell_lines))
        
        for line_idx in range(max_lines):
            new_row = []
            for cell_lines in split_cells:
                if line_idx < len(cell_lines):
                    new_row.append(cell_lines[line_idx])
                else:
                    new_row.append('')
            processed_rows.append(new_row)
    
    # Calculate column widths from content only
    num_cols = len(processed_rows[0]) if processed_rows else 0
    col_widths = [0] * num_cols
    
    for row in processed_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    col_widths = [w + MIN_PADDING for w in col_widths]
    
    # Output formatted table
    for i, row in enumerate(processed_rows):
        line = '|'
        for j, cell in enumerate(row):
            padding = col_widths[j] - len(cell) - 1
            line += ' ' + cell + ' ' * padding + '|'
        print(line)
        
        if i == 0:  # Add separator after header
            separator = '|' + '|'.join(['-' * w for w in col_widths]) + '|'
            print(separator)

process_table()
```

---

## How to Verify Your Results

```bash
# Quick verification - all columns should show same width
cat fixed_table.txt | grep -v "^|--" | head -5 | while read line; do
  echo "$line" | awk -F'|' '{for(i=2;i<NF;i++) printf "%d ", length($i)} END {print ""}'
done
```

If all rows show identical numbers, the table is correctly formatted.

---

## Automatic Table Detection and Formatting

### Step 1: Find All Tables in File
```bash
# Find all table separators (each indicates a table)
grep -n "^\|---" file.md
# Output example: 73:|----|  144:|----|  235:|----|
```

### Step 2: Calculate Table Boundaries for Each Separator
For separator at line N:
- **Header**: Line N-1 (immediately before separator)
- **Table start**: Search backwards from N-1 to find first table row
- **Table end**: Search forwards from N+1 until first non-table line

```bash
# Get table boundaries for separator at line 73
N=73
# Find table start (search backwards)
awk -v n=$((N-1)) 'NR <= n && /^\|[^-]/ {start=NR} END {print start}' file.md
# Find table end (search forwards)  
awk -v n=$((N+1)) 'NR >= n && (!/^\|/ || /^\|---/) {print NR-1; exit}' file.md
```

### Step 3: Claude Workflow
1. **Run detection**: Get all separator line numbers
2. **Calculate ranges**: Use algorithm to find start/end for each table
3. **Verify ranges**: Visually confirm each range captures complete table
4. **Apply formatter**: Use Python script on each confirmed range
5. **Replace in file**: Update original file with formatted tables

### Complete Example with Auto-Detection

```bash
# 1. Find all tables automatically
grep -n "^\|---" file.md
# Output: 73:|----|  144:|----|  235:|----|

# 2. For each separator, calculate boundaries and format
for sep_line in 73 144 235; do
  # Calculate table boundaries
  start=$(awk -v n=$((sep_line-1)) 'NR <= n && /^\|[^-]/ {s=NR} END {print s}' file.md)
  end=$(awk -v n=$((sep_line+1)) 'NR >= n && (!/^\|/ || /^\|---/) {print NR-1; exit} END {if(!found) print NR}' file.md)
  
  echo "Table found: lines $start-$end"
  
  # Format the table
  sed -n "${start},${end}p" file.md | python3 -c "[paste script]" > table_${start}.txt
done

# 3. Replace tables in file (manual verification recommended)
```

## Single Command Pattern for Claude
**Usage**: "Apply table formatting rules from TABLE_FORMATTING_RULES_V2.md to [target_file]"

**Claude should**:
1. Find all table separators using grep
2. Calculate boundaries algorithmically 
3. Verify each range by reading those lines
4. Apply Python formatter to each table
5. Update the target file

---

## Summary for Quick Reference

1. **Never include separator lines** (|---|) when calculating widths
2. **Use the Python script** - it handles everything automatically
3. **Verify with simple bash commands** - don't trust visual alignment
4. **Multi-line cells are handled automatically** by the script


---

## Full Script (Copy This)

For easy copying, here's the complete formatting script:

```python
import sys
import textwrap

MAX_COL_WIDTH = 75
MIN_PADDING = 2

def split_cell_content(content, max_width):
    if len(content) <= max_width - MIN_PADDING:
        return [content]
    wrapper = textwrap.TextWrapper(width=max_width - MIN_PADDING, 
                                 break_long_words=False,
                                 break_on_hyphens=True)
    return wrapper.wrap(content)

def process_table():
    lines = [line.rstrip() for line in sys.stdin]
    raw_rows = []
    
    for line in lines:
        if line.strip() and not line.startswith('|--'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                raw_rows.append(cells)
    
    if not raw_rows:
        return
    
    processed_rows = []
    
    for row in raw_rows:
        split_cells = []
        max_lines = 1
        
        for cell in row:
            cell_lines = split_cell_content(cell, MAX_COL_WIDTH)
            split_cells.append(cell_lines)
            max_lines = max(max_lines, len(cell_lines))
        
        for line_idx in range(max_lines):
            new_row = []
            for cell_lines in split_cells:
                if line_idx < len(cell_lines):
                    new_row.append(cell_lines[line_idx])
                else:
                    new_row.append('')
            processed_rows.append(new_row)
    
    num_cols = len(processed_rows[0]) if processed_rows else 0
    col_widths = [0] * num_cols
    
    for row in processed_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    col_widths = [w + MIN_PADDING for w in col_widths]
    
    for i, row in enumerate(processed_rows):
        line = '|'
        for j, cell in enumerate(row):
            padding = col_widths[j] - len(cell) - 1
            line += ' ' + cell + ' ' * padding + '|'
        print(line)
        
        if i == 0:
            separator = '|' + '|'.join(['-' * w for w in col_widths]) + '|'
            print(separator)

process_table()
```

Save this as `format_table.py` and use: `sed -n 'X,Yp' file.md | python3 format_table.py`