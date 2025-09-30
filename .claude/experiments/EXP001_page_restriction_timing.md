# Experiment 001: Explicit Page Restriction Impact on Extraction Speed

**Created:** 2025-09-29 8:07PM ET
**Purpose:** Test whether explicit "DO NOT READ" instructions improve extraction speed
**Status:** Ready to Execute
**Estimated Duration:** 30-40 minutes total
**Priority:** HIGH - Critical performance optimization

## 🎯 Objective

Test whether explicit "DO NOT READ" page restrictions significantly improve extraction speed compared to implicit page guidance.

## 📋 Hypothesis

**Current Problem:** The fidelity-statement-extractor agent may be reading ALL pages of the PDF even when told which pages contain holdings data. This wastes tokens and time.

**Hypothesis:** Adding explicit "DO NOT READ pages X-Y" instructions will prevent the agent from scanning irrelevant pages, reducing extraction time by 20-30% with no loss in accuracy.

## 🧪 Experimental Design

### Test Setup

**Control Group (Agent A):**
- Uses current prompt style: "Holdings are on pages 1-12 and 19-21"
- Tells agent WHERE holdings are located
- Does NOT explicitly tell agent to skip other pages

**Treatment Group (Agent B):**
- Uses explicit restriction style: "READ ONLY pages 1-12 and 19-21. DO NOT READ pages 13-18, 22."
- Tells agent WHERE to read AND where NOT to read
- Uses directive language: "STOP READING after page 21"

**Test Document:**
- File: `/Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf`
- Pages: 22 total (trimmed statement)
- Holdings pages: 1-12 (Account 1), 19-21 (Account 2)
- Non-holdings pages: 13-18, 22 (activities sections)
- Expected positions: ~102 holdings across 2 accounts

### Measurements

1. **Primary Metric:** Wall-clock extraction time (start to finish)
2. **Validation Metrics:**
   - Number of positions extracted (should be identical: ~102)
   - Accuracy spot-check (compare 10 random positions)
3. **Qualitative:** Agent behavior observations

### Success Criteria

✅ **Experiment succeeds if:**
- Treatment group is ≥20% faster than control group
- Both groups extract same number of positions (±2 tolerance)
- Spot-check shows identical data quality

## 📝 Execution Instructions

### Phase 1: Run Control Group (Agent A)

**Step 1.1 - Record Start Time**
```bash
echo "CONTROL START: $(date '+%Y-%m-%d %H:%M:%S')" > /tmp/exp001_control.log
```

**Step 1.2 - Launch Control Agent**

Use the Task tool with `fidelity-statement-extractor` subagent:

```
EXTRACTION MODE: Holdings
DOC_MD5_HASH: e4feb9724c684f281d4fb6a1cda17180
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf

PAGE MAP FOR THIS STATEMENT (trimmed PDF page numbers):
- Account Z24-527872 (KernBrok): pages 1-12
- Account Z27-375656 (KernCMA): pages 19-21

Please extract HOLDINGS data for ALL ACCOUNTS in this statement.

CRITICAL: Extract all accounts found in the statement into a single JSON file. Use the page map above to locate each account's holdings section.

- EXTRACT holdings/positions for ALL accounts using the page map
- CREATE complete JSON from scratch using Map_Stmnt_Fid_Positions.md
- FOLLOW the mapping document to locate and extract ALL fields
- INCLUDE doc_md5_hash in output
- SAVE as new JSON file: /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_CONTROL_exp001.json

Expected output:
- New JSON extraction file in /documents/4extractions/ containing all accounts
- Report on extraction success/issues
```

**Step 1.3 - Record End Time**
```bash
echo "CONTROL END: $(date '+%Y-%m-%d %H:%M:%S')" >> /tmp/exp001_control.log
```

**Step 1.4 - Record Results**
```bash
# Count positions in output
CONTROL_POSITIONS=$(jq '[.accounts[].holdings | length] | add' /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_CONTROL_exp001.json)
echo "CONTROL POSITIONS: $CONTROL_POSITIONS" >> /tmp/exp001_control.log
```

---

### Phase 2: Run Treatment Group (Agent B)

**Step 2.1 - Record Start Time**
```bash
echo "TREATMENT START: $(date '+%Y-%m-%d %H:%M:%S')" > /tmp/exp001_treatment.log
```

**Step 2.2 - Launch Treatment Agent**

Use the Task tool with `fidelity-statement-extractor` subagent:

```
EXTRACTION MODE: Holdings
DOC_MD5_HASH: e4feb9724c684f281d4fb6a1cda17180
SOURCE_PDF: /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf

READ ONLY THESE PAGES:
- Pages 1-12: Account Z24-527872 (KernBrok) Holdings
- Pages 19-21: Account Z27-375656 (KernCMA) Holdings

DO NOT READ:
- Pages 13-18: Activities sections (not needed for holdings extraction)
- Page 22: Activities section (not needed for holdings extraction)

STOP READING after page 21. You have all required holdings data.

Please extract HOLDINGS data for ALL ACCOUNTS in this statement.

CRITICAL: Extract all accounts found in the statement into a single JSON file. Focus ONLY on the pages specified above (1-12, 19-21).

- EXTRACT holdings/positions for ALL accounts from pages 1-12 and 19-21 ONLY
- CREATE complete JSON from scratch using Map_Stmnt_Fid_Positions.md
- FOLLOW the mapping document to locate and extract ALL fields
- INCLUDE doc_md5_hash in output
- SAVE as new JSON file: /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_TREATMENT_exp001.json

Expected output:
- New JSON extraction file in /documents/4extractions/ containing all accounts
- Report on extraction success/issues
```

**Step 2.3 - Record End Time**
```bash
echo "TREATMENT END: $(date '+%Y-%m-%d %H:%M:%S')" >> /tmp/exp001_treatment.log
```

**Step 2.4 - Record Results**
```bash
# Count positions in output
TREATMENT_POSITIONS=$(jq '[.accounts[].holdings | length] | add' /Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_TREATMENT_exp001.json)
echo "TREATMENT POSITIONS: $TREATMENT_POSITIONS" >> /tmp/exp001_treatment.log
```

---

### Phase 3: Calculate Results

**Step 3.1 - Calculate Time Differences**

Run this Python script to calculate timing:

```python
from datetime import datetime

# Read log files
with open('/tmp/exp001_control.log', 'r') as f:
    control_lines = f.readlines()
with open('/tmp/exp001_treatment.log', 'r') as f:
    treatment_lines = f.readlines()

# Parse timestamps
def parse_log(lines):
    start = None
    end = None
    positions = None
    for line in lines:
        if 'START:' in line:
            start = datetime.strptime(line.split('START: ')[1].strip(), '%Y-%m-%d %H:%M:%S')
        elif 'END:' in line:
            end = datetime.strptime(line.split('END: ')[1].strip(), '%Y-%m-%d %H:%M:%S')
        elif 'POSITIONS:' in line:
            positions = int(line.split('POSITIONS: ')[1].strip())
    return start, end, positions

control_start, control_end, control_positions = parse_log(control_lines)
treatment_start, treatment_end, treatment_positions = parse_log(treatment_lines)

# Calculate durations
control_duration = (control_end - control_start).total_seconds()
treatment_duration = (treatment_end - treatment_start).total_seconds()

# Calculate improvement
time_saved = control_duration - treatment_duration
percent_improvement = (time_saved / control_duration) * 100

print("\n" + "="*60)
print("EXPERIMENT 001 RESULTS")
print("="*60)
print(f"\nCONTROL GROUP (Current Prompt Style):")
print(f"  Duration: {control_duration:.1f} seconds ({control_duration/60:.1f} minutes)")
print(f"  Positions: {control_positions}")

print(f"\nTREATMENT GROUP (Explicit Restrictions):")
print(f"  Duration: {treatment_duration:.1f} seconds ({treatment_duration/60:.1f} minutes)")
print(f"  Positions: {treatment_positions}")

print(f"\nRESULTS:")
print(f"  Time Saved: {time_saved:.1f} seconds ({time_saved/60:.1f} minutes)")
print(f"  Improvement: {percent_improvement:.1f}%")
print(f"  Position Match: {'✅ PASS' if abs(control_positions - treatment_positions) <= 2 else '❌ FAIL'}")

print(f"\nHYPOTHESIS TEST:")
if percent_improvement >= 20 and abs(control_positions - treatment_positions) <= 2:
    print("  ✅ HYPOTHESIS CONFIRMED")
    print("  Explicit page restrictions improve speed by ≥20% with no accuracy loss.")
    print("\n  RECOMMENDATION: Update process-inbox.md to use explicit restrictions.")
elif percent_improvement >= 10:
    print("  ⚠️  PARTIAL SUCCESS")
    print(f"  Improvement of {percent_improvement:.1f}% is meaningful but below 20% threshold.")
    print("\n  RECOMMENDATION: Consider implementing, monitor results.")
else:
    print("  ❌ HYPOTHESIS REJECTED")
    print("  No significant improvement detected.")
    print("\n  RECOMMENDATION: Do not implement. Investigate other optimizations.")

print("="*60 + "\n")
```

Save this as `/tmp/exp001_analyze.py` and run:
```bash
python3 /tmp/exp001_analyze.py
```

---

### Phase 4: Accuracy Spot Check

**Step 4.1 - Compare 10 Random Positions**

Run this validation script:

```python
import json
import random

# Load both JSON files
with open('/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_CONTROL_exp001.json', 'r') as f:
    control = json.load(f)
with open('/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_TREATMENT_exp001.json', 'r') as f:
    treatment = json.load(f)

# Extract all positions from both
control_positions = []
for account in control['accounts']:
    control_positions.extend(account['holdings'])

treatment_positions = []
for account in treatment['accounts']:
    treatment_positions.extend(account['holdings'])

# Create lookup by symbol
control_by_symbol = {p.get('symbol', p.get('description', 'UNKNOWN')): p for p in control_positions}
treatment_by_symbol = {p.get('symbol', p.get('description', 'UNKNOWN')): p for p in treatment_positions}

# Random sample 10 positions
sample_keys = random.sample(list(control_by_symbol.keys()), min(10, len(control_by_symbol)))

print("\n" + "="*60)
print("ACCURACY SPOT CHECK - 10 RANDOM POSITIONS")
print("="*60)

mismatches = 0
for key in sample_keys:
    control_pos = control_by_symbol.get(key)
    treatment_pos = treatment_by_symbol.get(key)

    if not treatment_pos:
        print(f"\n❌ {key}: Missing in treatment")
        mismatches += 1
        continue

    # Compare key fields
    fields_to_check = ['quantity', 'end_market_value', 'price_per_unit']
    match = True
    for field in fields_to_check:
        if control_pos.get(field) != treatment_pos.get(field):
            print(f"\n❌ {key}: Mismatch in {field}")
            print(f"   Control: {control_pos.get(field)}")
            print(f"   Treatment: {treatment_pos.get(field)}")
            match = False
            mismatches += 1
            break

    if match:
        print(f"✅ {key}: Match")

print(f"\nACCURACY RESULT: {10-mismatches}/10 positions match")
if mismatches == 0:
    print("✅ ACCURACY TEST PASSED")
else:
    print(f"⚠️  {mismatches} mismatches detected - investigate")

print("="*60 + "\n")
```

Save as `/tmp/exp001_accuracy.py` and run:
```bash
python3 /tmp/exp001_accuracy.py
```

---

## 📊 Expected Outcomes

### Scenario 1: Hypothesis Confirmed (Most Likely)
- Treatment is 20-30% faster
- Position counts match
- Accuracy spot check passes
- **Action:** Implement explicit restrictions in process-inbox.md

### Scenario 2: Marginal Improvement (10-19%)
- Some improvement but below threshold
- Position counts match
- **Action:** Consider implementing, but look for additional optimizations

### Scenario 3: No Improvement (<10%)
- Minimal or no time difference
- **Action:** Do not implement. Agent is already reading efficiently. Test other hypotheses.

### Scenario 4: Treatment Slower
- Unexpected result - explicit instructions add overhead
- **Action:** Keep current approach. Investigate why explicit instructions slow processing.

## 🔍 Observation Notes

While running the experiment, note:

1. **Agent behavior during extraction:**
   - Does treatment agent mention "skipping pages"?
   - Does control agent mention reading activities pages?

2. **Quality observations:**
   - Are there any warnings or errors in either extraction?
   - Does one agent seem more "confident" in its output?

3. **Token usage (if available):**
   - Does treatment use fewer tokens?

## 📋 Final Report Format

After completing all phases, create a summary:

```
EXPERIMENT 001 FINAL REPORT
Date: [execution date]

RESULTS:
- Control Duration: X minutes
- Treatment Duration: Y minutes
- Improvement: Z%
- Position Count Match: YES/NO
- Accuracy Check: PASS/FAIL

HYPOTHESIS: CONFIRMED / REJECTED / PARTIAL

RECOMMENDATION:
[Your recommendation based on results]

NEXT STEPS:
[What should be done with these findings]
```

Save this to: `/Users/richkernan/Projects/Finances/.claude/experiments/EXP001_results.md`

---

## 🚨 Troubleshooting

**If extraction fails:**
- Check that PDF path is correct: `ls -la /Users/richkernan/Projects/Finances/documents/2staged/Fid_Stmnt_2025-04_KernBrok+KernCMA.pdf`
- Verify mapping doc exists: `ls -la /Users/richkernan/Projects/Finances/config/institution-guides/Map_Stmnt_Fid_Positions.md`
- Check agent logs for specific errors

**If timing seems off:**
- Verify system time is correct: `date`
- Check if other processes are using CPU
- Consider running experiment twice to rule out system variance

**If position counts don't match:**
- This might indicate the treatment agent is actually skipping holdings data
- Investigate which positions are missing
- This would be a critical failure - do not implement

---

## ✅ Experiment Checklist

- [ ] Phase 1: Control group extraction complete
- [ ] Phase 2: Treatment group extraction complete
- [ ] Phase 3: Timing analysis complete
- [ ] Phase 4: Accuracy spot check complete
- [ ] Final report written
- [ ] Results communicated to user

**Good luck! This experiment will definitively answer whether explicit page restrictions improve extraction performance.**