# Sample Documents Directory

**Purpose:** Store sample documents from each institution for reference during processing

## Directory Structure

```
samples/
├── fidelity/
│   ├── statement-sample.pdf     # Monthly statement example
│   ├── 1099-div-sample.pdf      # Dividend tax form
│   ├── 1099-int-sample.pdf      # Interest tax form
│   └── 1099-b-sample.pdf        # Brokerage proceeds form
├── bank-of-america/
│   └── (future samples)
└── charles-schwab/
    └── (future samples)
```

## Usage

These samples help Claude:
1. Recognize document layouts and patterns
2. Understand institution-specific formats
3. Learn from examples when processing new documents
4. Verify extraction accuracy

## Adding New Samples

When adding samples:
1. **Redact sensitive information** (SSN, full account numbers)
2. **Keep formatting intact** (layout helps with recognition)
3. **Include variety** (different transaction types, edge cases)
4. **Name descriptively** (institution-doctype-sample.pdf)

## Security Note

Sample documents should be:
- Redacted of personal information
- Not contain real account numbers (use XXX-XXXXXX format)
- Safe to commit to repository if needed

## Corresponding Pattern Guides

Each institution folder here should have a matching guide in:
`/config/institution-patterns/[institution-name].md`