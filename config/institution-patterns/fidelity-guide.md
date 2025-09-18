# Fidelity Statement Processing Guide

**Created:** 09/18/25 4:00PM ET
**Purpose:** Help Claude extract data from Fidelity statements through intelligent pattern recognition

## Core Philosophy

You're smart. Read this like a human would read a paper statement. Extract what you see. Ask questions when something seems odd.

## Document Structure

Fidelity statements follow this flow:
1. **Portfolio Summary** - Overview of all accounts
2. **Individual Account Sections** - Each account's holdings and activity
3. **Activity Details** - What happened during the period

## Key Patterns

### Holdings Tables
Standard columns: Description | Quantity | Price | Market Value | Cost Basis | Gain/Loss

**Bonds are special:** They show market value with accrued interest underneath in italics. The line below has details including the CUSIP.

### Visual Cues
- **Bold** = Primary identifier
- *Italics* = Usually accrued interest
- Negative numbers = Short positions or obligations
- "unavailable" = Just record it as-is

## Examples of What You'll See

### Stock Entry
```
MICROSOFT CORP (MSFT)    250.000    $423.04    $105,760.00    $95,397.50    $10,362.50
```

### Bond Entry
```
HILLSBORO OHIO CITY SCH B    20,000.000    100.0670    $20,013.40    $19,974.60    $38.80
                                                         $200.00 (italics)
FIXED COUPON MOODYS Aa1 SEMIANNUALLY NEXT CALL DATE 09/30/2025 100.00 CUSIP: 432074EU2
```

### Option Entry
```
PUT (NVDA) NVIDIA CORPORATION    -10.000    0.8500    -$850.00    -$2,943.26    $2,093.26
SEP 19 25 $175 (100 SHS)
```

## What to Extract

Create a JSON structure that mirrors what you see:
- Document metadata (period, institution, accounts)
- For each account: holdings, transactions, income
- Include an extraction_notes field for questions/observations

## When to Ask the User

- "I see a transaction type I don't recognize: [example]. How should I categorize this?"
- "This security shows [unusual thing]. Is this expected?"
- "The numbers don't seem to add up in [section]. Can you clarify?"

## What NOT to Do

- Don't calculate missing values
- Don't interpret tax implications
- Don't skip complex items - ask about them
- Don't worry about perfect field names - capture the data

## Remember

The user knows their finances. This is collaborative. When you're 80% sure, proceed and note your assumptions. When you're less certain, ask. The goal is accurate data capture, not perfection on the first pass.