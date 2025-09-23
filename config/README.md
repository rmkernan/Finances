# Configuration Directory Documentation

**Created:** 09/23/25 7:16PM ET
**Purpose:** Comprehensive guide to configuration files and mapping system maintenance

## Overview

This directory contains all configuration files for the financial data management system. The configuration-driven approach allows updates to transaction classification, security patterns, and reference data without code changes. The system uses a cascading priority structure to classify transactions with precision while providing fallback mechanisms.

## Configuration Files

### `data-mappings.json` - Primary Mapping System
**Purpose:** Central configuration for all transaction classification rules

**Structure:**
```json
{
  "transaction_descriptions": {},  // Precise transaction categorization
  "security_types": {},           // Security type identification
  "security_patterns": {},        // Options lifecycle and special transactions
  "security_classification": {},  // Security name pattern matching
  "activity_sections": {}         // Fallback section-based classification
}
```

**Example Patterns:**
```json
// Transaction Description Mapping
"Dividend Received": {
  "type": "dividend",
  "subtype": "received",
  "notes": "Standard dividend payment"
}

// Security Pattern Overrides (Highest Priority)
"CLOSING TRANSACTION": {
  "type": "override_subtype",
  "subtype": "closing_transaction",
  "notes": "Options closing transaction - override subtype regardless of other mappings"
}

// Security Classification by Name
"CALL (": {
  "type": "sec_class",
  "subtype": "call",
  "notes": "Call options - security name starts with CALL ("
}
```

### `account-mappings.json` - Complete Reference Data
**Purpose:** Master reference for entities, institutions, and accounts used by process-inbox command

**Contains:**
- **Entities:** Business and individual entity definitions with tax details
- **Institutions:** Financial institution metadata and types
- **Accounts:** Complete account metadata including friendly names and tax attributes
- **Usage Examples:** Filename generation patterns and database creation guidance

**Key Features:**
```json
"entities": {
  "kernan_family": {
    "entity_name": "Kernan Family",
    "entity_type": "individual",
    "tax_id": "2222",
    "georgia_resident": true
  }
}
```

### `database-account-mappings.json` - Loader Configuration
**Purpose:** Simplified mappings for database loading with lazy creation strategy

**Strategy:**
- **Lazy Creation:** Entities and institutions created when first encountered
- **Auto-inference:** Entity details derived from account holder names
- **Placeholder Tax IDs:** Generated automatically, edited later in UI
- **Focus:** Get data loaded quickly, cleanup happens in application

**Configuration:**
```json
"loader_settings": {
  "auto_create_entities": true,
  "auto_create_institutions": true,
  "match_on_last_four": true,
  "use_owner_name_for_entity": true
}
```

### `institution-guides/` - Extraction Templates
**Purpose:** Institution-specific document processing guides

**Files:**
- `JSON_Stmnt_Fid_Activity.md` - Activity transaction extraction patterns
- `JSON_Stmnt_Fid_Positions.md` - Holdings/positions extraction patterns
- `Map_Stmnt_Fid_Activities.md` - Activity classification mappings
- `Map_Stmnt_Fid_Positions.md` - Position classification mappings

### `tax-rules.md` & `doctrine.md`
**Purpose:** Tax treatment rules and business logic documentation

## Classification Logic

### Priority Order (Highest to Lowest)

1. **Security Patterns** (`security_patterns`)
   - OPENING TRANSACTION, CLOSING TRANSACTION, ASSIGNED PUTS/CALLS
   - **Type:** `override_subtype` - Forces specific subtype regardless of other rules
   - **Use Case:** Options lifecycle events that need special handling

2. **Transaction Descriptions** (`transaction_descriptions`)
   - Exact description matches: "Dividend Received", "Muni Exempt Int"
   - **Most specific and reliable classification**

3. **Security Classification** (`security_classification`)
   - Security name pattern matching: "CALL (", "PUT ("
   - **Identifies options and complex securities**

4. **Security Types** (`security_types`)
   - Basic security type classification: "PUT", "CALL"

5. **Activity Sections** (`activity_sections`)
   - **Fallback mechanism** when specific patterns don't match
   - Broad categories: "securities_bought_sold", "dividends_interest_income"

### Security Pattern Examples

**Options Lifecycle Management:**
```json
// Opening new positions
"OPENING TRANSACTION": {
  "subtype": "opening_transaction"  // Override any other classification
}

// Closing existing positions
"CLOSING TRANSACTION": {
  "subtype": "closing_transaction"  // Override any other classification
}

// Options assignment events
"ASSIGNED PUTS": {
  "subtype": "assignment"  // Critical for tax treatment
}
```

**Tax-Sensitive Classifications:**
```json
// Municipal bond interest (tax-exempt)
"Muni Exempt Int": {
  "type": "interest",
  "subtype": "muni_exempt"  // Georgia tax-exempt treatment
}

// Standard dividend income
"Dividend Received": {
  "type": "dividend",
  "subtype": "received"  // Taxable dividend income
}
```

## Adding New Patterns

### Step 1: Identify Classification Need
```bash
# Search for unclassified transactions
grep -r "needs_classification" /Users/richkernan/Projects/Finances/documents/4extractions/
```

### Step 2: Choose Appropriate Section
- **Exact match needed?** → `transaction_descriptions`
- **Options lifecycle?** → `security_patterns`
- **Security name pattern?** → `security_classification`
- **Broad category fallback?** → `activity_sections`

### Step 3: Add Pattern
```json
// Example: Adding new dividend type
"transaction_descriptions": {
  "Capital Gain Short Term": {
    "type": "capital_gain",
    "subtype": "short_term",
    "notes": "Short-term capital gains distribution"
  }
}
```

### Step 4: Test Classification
```bash
# Re-run extraction to test new pattern
/.claude/commands/process-inbox.md
```

## Maintenance Procedures

### Updating Mappings

1. **Backup Current Configuration**
   ```bash
   cp /Users/richkernan/Projects/Finances/config/data-mappings.json \
      /Users/richkernan/Projects/Finances/config/data-mappings.json.backup
   ```

2. **Edit Configuration File**
   ```bash
   # Use your preferred editor
   code /Users/richkernan/Projects/Finances/config/data-mappings.json
   ```

3. **Validate JSON Syntax**
   ```bash
   python -m json.tool /Users/richkernan/Projects/Finances/config/data-mappings.json
   ```

4. **Test with Recent Extractions**
   ```bash
   # Re-process recent documents to verify mappings
   /.claude/commands/process-inbox.md
   ```

### Reloading Configuration Changes

**For Document Processing:**
- Configuration is read fresh for each extraction
- Changes take effect immediately on next document processing

**For Database Loading:**
- Restart loader process to pick up changes
- Clear any cached mapping data

### Backup and Recovery

**Recommended Backup Strategy:**
```bash
# Daily backup of all config files
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  /Users/richkernan/Projects/Finances/config/
```

**Recovery Process:**
1. Restore from backup: `tar -xzf config-backup-YYYYMMDD.tar.gz`
2. Validate restored files with JSON syntax check
3. Test with known good document extractions

## Common Use Cases

### Options Trading Support

**Challenge:** Options have complex lifecycle events requiring precise classification

**Solution:** Multi-layer classification system
```json
// 1. Pattern Override (Highest Priority)
"CLOSING TRANSACTION": {
  "type": "override_subtype",
  "subtype": "closing_transaction"
}

// 2. Security Name Classification
"CALL (AAPL": {
  "type": "sec_class",
  "subtype": "call"
}

// 3. Fallback Section
"securities_bought_sold": {
  "type": "trade",
  "subtype": "security"
}
```

### Tax Category Management

**Municipal Bonds vs Regular Interest:**
```json
// Tax-exempt municipal bond interest
"Muni Exempt Int": {
  "type": "interest",
  "subtype": "muni_exempt"  // Georgia tax-free
}

// Taxable bank interest
"Interest Earned": {
  "type": "interest",
  "subtype": "deposit"  // Fully taxable
}
```

### Multi-Entity Handling

**Entity-Specific Processing:**
- Use `account-mappings.json` for complete entity metadata
- `database-account-mappings.json` for lazy creation during loading
- Entity context drives tax treatment and reporting requirements

## Troubleshooting

### Common Issues and Solutions

**1. Unclassified Transactions**
```bash
# Symptom: Transactions falling to activity_sections fallback
# Solution: Add specific transaction_descriptions pattern

# Find unclassified patterns
grep -r "investment" /Users/richkernan/Projects/Finances/documents/4extractions/ | \
  grep -v "subtype"
```

**2. Options Misclassification**
```bash
# Symptom: OPENING/CLOSING not properly identified
# Solution: Check security_patterns section

# Verify pattern exists
grep -A3 "OPENING TRANSACTION" /Users/richkernan/Projects/Finances/config/data-mappings.json
```

**3. Account Mapping Errors**
```bash
# Symptom: Unknown account numbers in extractions
# Solution: Add to account-mappings.json

# Find missing accounts
grep -r "account_number" /Users/richkernan/Projects/Finances/documents/4extractions/ | \
  cut -d'"' -f4 | sort -u
```

**4. JSON Syntax Errors**
```bash
# Validate JSON syntax
python -m json.tool /Users/richkernan/Projects/Finances/config/data-mappings.json

# Fix common issues: trailing commas, unescaped quotes
```

### Validation Tools

**Configuration Syntax Check:**
```bash
# Validate all JSON config files
for file in /Users/richkernan/Projects/Finances/config/*.json; do
  echo "Checking $file..."
  python -m json.tool "$file" > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
done
```

**Mapping Coverage Analysis:**
```bash
# Find unmapped transaction descriptions
grep -r '"description"' /Users/richkernan/Projects/Finances/documents/4extractions/ | \
  cut -d'"' -f4 | sort | uniq -c | sort -nr
```

**Test Extraction Pipeline:**
```bash
# Re-run extraction on known document
/.claude/commands/process-inbox.md
# Select a previously processed document to verify mapping changes
```

## File Paths Quick Reference

**Primary Configuration:**
- `/Users/richkernan/Projects/Finances/config/data-mappings.json`
- `/Users/richkernan/Projects/Finances/config/account-mappings.json`
- `/Users/richkernan/Projects/Finances/config/database-account-mappings.json`

**Institution Guides:**
- `/Users/richkernan/Projects/Finances/config/institution-guides/`

**Processing Commands:**
- `/.claude/commands/process-inbox.md`

**Extraction Results:**
- `/Users/richkernan/Projects/Finances/documents/4extractions/`

---

## Quick Start Examples

**Add New Transaction Type:**
1. Edit `data-mappings.json` → `transaction_descriptions`
2. Add pattern: `"New Description": {"type": "X", "subtype": "Y"}`
3. Test with recent extraction

**Add New Account:**
1. Edit `account-mappings.json` → `accounts`
2. Add complete metadata
3. Re-run process-inbox command

**Debug Classification:**
1. Check extraction JSON for unclassified items
2. Trace through priority order (patterns → descriptions → classification → sections)
3. Add most specific pattern that matches the need

This configuration system balances precision with maintainability, allowing rapid updates to classification rules without code changes while maintaining strict tax compliance and audit trails.