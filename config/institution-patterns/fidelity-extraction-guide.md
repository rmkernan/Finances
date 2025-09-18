# Fidelity Statement Extraction Guide

**Created:** 09/18/25 3:45PM ET
**Updated:** 01/18/25 2:45PM ET - Simplified to leverage Claude's intelligence
**Purpose:** Guide for extracting data from Fidelity Investment statements

## Core Principle

**This is a collaborative process.** When you encounter something unclear or unusual, ASK THE USER. They know their finances better than any documentation could capture.

## Reading Fidelity Statements

Think of this like reading a paper statement that arrived in the mail. Extract what you see at face value:
- If it says "unavailable" - record "unavailable"
- If quantities are negative - record them as negative
- If something looks unusual - ask about it

## Key Patterns to Recognize

### Holdings Section
Each holding type follows a similar table structure. The data is what it is - record it faithfully.

**Bonds are slightly special:**
- The market value has two numbers stacked vertically
- Top number (regular text) = market value
- Bottom number (italics) = accrued interest
- The details line below contains notes and the CUSIP

### Common Holding Types
- **Stocks**: May have M (margin) or S (short) prefixes
- **Bonds**: Include maturity dates and detailed notes
- **Options**: Can have negative quantities and "unavailable" values
- **Mutual Funds**: Often show yields instead of some values

### Transaction Activity
"Securities Bought & Sold" section shows what happened during the period:
- "You Bought" / "You Sold" = regular trades
- "Assigned" = options exercised
- "Redeemed" = bonds matured or called

## JSON Output Structure

Use this basic structure, adapting as needed:
```json
{
  "extraction_session": {...},
  "document_info": {...},
  "accounts": [
    {
      "account_number": "as shown",
      "transactions": [...],
      "positions": [...],
      "income_summary": {...}
    }
  ],
  "extraction_notes": "Any questions or uncertainties"
}
```

## When to Ask Questions

**Always ask when:**
- You see a transaction type you don't recognize
- Account ownership is unclear
- Numbers don't seem to reconcile
- You encounter a new document format

**Examples of good questions:**
- "I see a transaction labeled 'ASSIGNED PUTS' - should this be categorized as a buy?"
- "This bond shows 'PRE-REFUNDED' - do you want me to note the redemption date?"
- "There's a negative position in NVDA - is this a short sale you're tracking?"

## What NOT to Do

- Don't try to calculate missing values
- Don't make assumptions about tax treatment
- Don't skip something because it looks complicated - ask instead
- Don't worry about perfect categorization - capture the data first

## Remember

You're as intelligent as the person who wrote this guide. Use your judgment, recognize patterns, and ask questions when something doesn't make sense. The goal is accurate data extraction through human-AI collaboration, not automated perfection.

When in doubt, include questionable items in your extraction_notes field and discuss them with the user.