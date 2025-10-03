# Data Pipeline Alignment Validation Task

**Created:** 09/29/25 8:45PM ET
**Purpose:** Comprehensive validation of field name and structure alignment across the extraction-to-database pipeline for both Activities and Positions data.

## 🎯 Task Objective

Validate that JSON field names produced by extraction agents align with database schema column names, ensuring the loader can successfully map extracted data to database tables without field name mismatches or data loss.

## 📋 Validation Scope

You will validate alignment across 4 stages of the data pipeline for TWO data types:

### Activities Data Pipeline:
1. **Mapping Guide:** `/Users/richkernan/Projects/Finances/config/institution-guides/Map_Stmnt_Fid_Activities.md`
2. **JSON Spec:** `/Users/richkernan/Projects/Finances/config/institution-guides/JSON_Stmnt_Fid_Activities.md`
3. **Actual JSON Output:** `/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_activities_2025.09.29_15.45ET.json`
4. **Database Schema:** `/Users/richkernan/Projects/Finances/docs/Design/Database/schema.md` (focus on `transactions` table)

### Positions Data Pipeline:
1. **Mapping Guide:** `/Users/richkernan/Projects/Finances/config/institution-guides/Map_Stmnt_Fid_Positions.md`
2. **JSON Spec:** `/Users/richkernan/Projects/Finances/config/institution-guides/JSON_Stmnt_Fid_Positions.md`
3. **Actual JSON Output:** `/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_holdings_2025.09.29_15.42ET.json`
4. **Database Schema:** `/Users/richkernan/Projects/Finances/docs/Design/Database/schema.md` (focus on `positions` table)

## 🔍 Validation Methodology

### Step 1: Read All Source Documents

Read all 8 files listed above completely. You need to understand:
- What field names the Mapping Guides specify for extraction
- What field names the JSON Specs define as output structure
- What field names actually appear in the JSON output files
- What column names exist in the database schema tables

### Step 2: Extract Field Inventories

For each data type (Activities and Positions), create comprehensive field inventories:

**A. Mapping Guide Field Inventory**
- List every field name mentioned in the mapping guide
- Note which PDF section each field comes from
- Note any special handling instructions (e.g., "extract exactly as shown", "calculate from X and Y")

**B. JSON Spec Field Inventory**
- List every field name defined in the JSON specification
- Note whether field is required or optional
- Note the data type (string, number, boolean, date, etc.)
- Note any nested structure (e.g., fields within arrays or objects)

**C. Actual JSON Output Field Inventory**
- List every field name present in the actual JSON file
- Note the data type of actual values
- Note any fields that appear in JSON but weren't in the spec
- Note any fields missing from JSON that were in the spec

**D. Database Schema Column Inventory**
- List every column name in the target table
- Note the data type and constraints (NOT NULL, etc.)
- Note any foreign key relationships
- Note any columns that have default values or are auto-generated

### Step 3: Cross-Reference Analysis

For each data type, perform comprehensive cross-referencing:

#### 3A. Mapping Guide → JSON Spec Alignment
Compare field names between Mapping Guide and JSON Spec:
- **Perfect Matches:** Fields with identical names in both documents
- **Name Mismatches:** Fields that exist in both but with different names (e.g., "security_description" vs "sec_description")
- **Missing in Spec:** Fields mentioned in Mapping Guide but not defined in JSON Spec
- **Extra in Spec:** Fields defined in JSON Spec but not mentioned in Mapping Guide

For each mismatch or discrepancy:
- Identify the exact field names in each document
- Quote relevant sections from both documents
- Assess severity: CRITICAL (data loss risk), WARNING (inconsistency), INFO (documentation gap)

#### 3B. JSON Spec → Actual JSON Alignment
Compare field names between JSON Spec and actual JSON output:
- **Perfect Matches:** Fields that appear exactly as specified
- **Name Mismatches:** Fields with different names (e.g., spec says "total_deposits" but JSON has "total_dep")
- **Missing in Output:** Required fields from spec not present in actual JSON
- **Extra in Output:** Fields in JSON that weren't specified
- **Type Mismatches:** Fields where data type differs from spec (e.g., spec says string, JSON has number)

For each issue:
- Show the specific field path in the JSON (e.g., `accounts[0].securities_bought_sold[*].settlement_date`)
- Quote the spec requirement
- Show what the actual JSON contains
- Assess impact on database loading

#### 3C. Actual JSON → Database Schema Alignment
Compare field names in JSON output to database column names:
- **Perfect Matches:** JSON fields that map directly to columns with same name
- **Name Mismatches:** JSON fields that must be renamed to match database columns
- **Missing Mappings:** Database columns with no corresponding JSON field (may need defaults or derivation)
- **Unmapped JSON Fields:** JSON fields with no corresponding database column (may be metadata only)
- **Type Mismatches:** JSON fields with incompatible types for target columns

For each alignment issue:
- Show the JSON field path and example value
- Show the database column name and type
- Identify whether this is a naming issue, missing field, or type conversion issue
- Specify what transformation the loader needs to perform
- Flag if this will cause loading failures

### Step 4: Section-Level Structure Validation

For Activities data specifically, validate that all activity section types align:

**JSON Sections** (from actual output):
- `securities_bought_sold`
- `dividends_interest_income`
- `short_activity`
- `other_activity_in`
- `other_activity_out`
- `deposits`
- `withdrawals`
- `exchanges_in`
- `exchanges_out`
- `fees_charges`
- `core_fund_activity`
- `trades_pending_settlement`

Validate:
1. Does the JSON spec define all these section types?
2. Does the database have a way to distinguish between section types? (e.g., a `source` column or `transaction_type` column)
3. If sections map to a single `transactions` table, how does the loader know which section each transaction came from?
4. Are there section-level totals that need validation? (e.g., `total_sec_bot`, `total_sec_sold`)

For Positions data specifically, validate that all position categories align:

**JSON Categories** (from actual output):
- Core accounts
- Mutual funds
- Stocks
- Bonds
- Options
- ETFs/ETPs

Validate:
1. Does the database schema support categorization?
2. How are security types distinguished in the database?
3. Are there category-level totals or aggregations that need special handling?

### Step 5: Data Type and Constraint Validation

For each field-to-column mapping, validate:

**Numeric Fields:**
- Precision requirements (e.g., 6 decimals for quantities, 5 for prices)
- Range constraints (e.g., amounts can be negative for debits)
- Whether NULLs are allowed

**String Fields:**
- Maximum length constraints
- Special characters handling (e.g., security descriptions with parentheses, dashes)
- Encoding issues (e.g., unicode characters in names)

**Date Fields:**
- Format in JSON (e.g., "2025-04-30", "04/30/2025")
- Expected format in database (DATE type, TIMESTAMP type)
- Timezone handling

**Boolean Fields:**
- Representation in JSON (true/false, 1/0, "yes"/"no")
- Database column type (BOOLEAN, INTEGER, etc.)

### Step 6: Identify Critical Loading Blockers

Flag issues that will prevent database loading:

**BLOCKER Priority Issues:**
- Required database columns with no corresponding JSON field
- JSON field names that don't match any database column (and can't be automatically mapped)
- Data type incompatibilities that can't be automatically converted
- Foreign key references that can't be resolved (e.g., account_id lookup)

**WARNING Priority Issues:**
- Optional database columns with no JSON field (may need defaults)
- Field name inconsistencies that require explicit mapping configuration
- Precision mismatches that might cause rounding errors
- Missing section identifiers that make transaction classification ambiguous

**INFO Priority Issues:**
- Documentation inconsistencies (field described differently in different docs)
- Extra JSON fields that won't be loaded but aren't harmful
- Metadata fields that are extraction-only (not meant for database)

## 📊 Required Report Format

Generate a comprehensive report with the following structure:

```markdown
# Data Pipeline Alignment Validation Report

**Generated:** [timestamp]
**Validation Status:** [PASS / PASS WITH WARNINGS / FAIL]

## Executive Summary

[2-3 paragraph summary of overall findings]
- Total fields validated: [count]
- Perfect alignments: [count]
- Misalignments requiring action: [count]
- Critical blockers: [count]

---

## PART 1: ACTIVITIES DATA PIPELINE

### 1.1 Field Inventory Summary

**Mapping Guide Fields:** [count] fields across [X] sections
**JSON Spec Fields:** [count] fields
**Actual JSON Fields:** [count] fields
**Database Columns:** [count] columns in transactions table

### 1.2 Alignment Analysis

#### 1.2.1 Mapping Guide ↔ JSON Spec Alignment

**Perfect Matches:** [count]
[List with examples]

**Name Mismatches:** [count]
| Mapping Guide | JSON Spec | Severity | Recommendation |
|---------------|-----------|----------|----------------|
| [field_name]  | [field_name] | [CRITICAL/WARNING/INFO] | [action needed] |

**Missing in Spec:** [count]
[List with impact assessment]

**Extra in Spec:** [count]
[List with explanation]

#### 1.2.2 JSON Spec ↔ Actual JSON Alignment

**Perfect Matches:** [count]
[Examples]

**Name Mismatches:** [count]
| JSON Spec | Actual JSON | Example Value | Severity | Action Required |
|-----------|-------------|---------------|----------|-----------------|
| [field]   | [field]     | [value]       | [level]  | [action]       |

**Missing in Output:** [count]
[List with impact - will this cause loading failures?]

**Extra in Output:** [count]
[List - are these harmful or just extra metadata?]

#### 1.2.3 Actual JSON ↔ Database Schema Alignment

**Perfect Matches:** [count]
| JSON Field Path | Database Column | Example Value | Status |
|-----------------|-----------------|---------------|--------|
| accounts[*].securities_bought_sold[*].settlement_date | settlement_date | "2025-04-04" | ✅ MATCH |

**Name Mismatches:** [count]
| JSON Field | Database Column | Transformation Needed | Severity |
|------------|-----------------|----------------------|----------|
| [field]    | [column]        | [rename/convert]     | [level]  |

**Missing Database Columns:** [count]
[JSON fields with no database home - will these cause errors?]

**Unmapped Database Columns:** [count]
| Column Name | Type | Constraint | Source for Value | Default Strategy |
|-------------|------|------------|------------------|------------------|
| transaction_id | UUID | PRIMARY KEY NOT NULL | Auto-generated | Database default |
| account_id | UUID | FOREIGN KEY NOT NULL | Lookup from account_number | Loader must resolve |

### 1.3 Section-Level Validation

**Activity Sections in JSON:** [list all present]
**Activity Sections in Spec:** [list all defined]
**Source Field Mapping:**
- How does database distinguish transaction sources?
- Column used: [column_name]
- Mapping strategy: [describe]

### 1.4 Data Type and Constraint Issues

**Numeric Precision:**
[List any precision mismatches]

**String Length:**
[List any potential truncation issues]

**Date Format:**
[Describe format conversions needed]

**NULL Handling:**
[List columns that require NOT NULL but might receive NULL from JSON]

### 1.5 Critical Issues Summary

**🔴 BLOCKERS (Must Fix Before Loading):**
1. [Issue description]
   - Location: [file/field]
   - Impact: [what will break]
   - Recommendation: [specific fix]

**⚠️ WARNINGS (Should Fix):**
1. [Issue description]
   - Location: [file/field]
   - Impact: [potential problems]
   - Recommendation: [specific fix]

**ℹ️ INFO (Documentation/Enhancement):**
1. [Issue description]
   - Location: [file/field]
   - Impact: [minor inconsistency]
   - Recommendation: [optional improvement]

---

## PART 2: POSITIONS DATA PIPELINE

[Repeat entire structure from Part 1 for Positions/Holdings data]

### 2.1 Field Inventory Summary
[Same structure as 1.1]

### 2.2 Alignment Analysis
[Same structure as 1.2]

### 2.3 Category-Level Validation
[Same structure as 1.3 but for position categories]

### 2.4 Data Type and Constraint Issues
[Same structure as 1.4]

### 2.5 Critical Issues Summary
[Same structure as 1.5]

---

## PART 3: CROSS-CUTTING ANALYSIS

### 3.1 Common Patterns
[Identify naming patterns that appear in both Activities and Positions]
- Do both use `sec_description` or do they differ?
- Do both use same date format?
- Do both use same approach for CUSIPs, symbols, etc.?

### 3.2 Loader Requirements

Based on all misalignments found, the loader must:

**Field Name Mappings:**
```
JSON_FIELD_NAME → DATABASE_COLUMN_NAME
[list all renames needed]
```

**Data Type Conversions:**
```
JSON_TYPE → DATABASE_TYPE (conversion method)
[list all transformations]
```

**Foreign Key Resolutions:**
```
JSON_FIELD → DATABASE_FK (lookup strategy)
[list all FK resolutions]
```

**Derived Fields:**
```
DATABASE_COLUMN ← COMPUTED_FROM (calculation)
[list all fields that must be derived]
```

**Default Values:**
```
DATABASE_COLUMN ← DEFAULT_VALUE (when JSON field absent)
[list all defaults needed]
```

### 3.3 Documentation Updates Needed

**Files Requiring Updates:**
1. [filename] - [what needs to change and why]
2. [filename] - [what needs to change and why]

---

## PART 4: RECOMMENDATIONS

### 4.1 Immediate Actions (Before Next Load)

Priority 1 (Critical):
- [ ] [Specific action with file and line numbers]
- [ ] [Specific action with file and line numbers]

Priority 2 (Important):
- [ ] [Specific action with file and line numbers]
- [ ] [Specific action with file and line numbers]

### 4.2 Process Improvements

1. **Field Naming Standardization:**
   [Recommend consistent naming pattern across all docs]

2. **Validation Automation:**
   [Suggest automated validation checks]

3. **Documentation Synchronization:**
   [Recommend process to keep docs in sync]

### 4.3 Loader Implementation Guidance

Based on findings, the loader implementation should:
1. [Specific guidance based on discovered misalignments]
2. [Specific guidance based on discovered misalignments]
3. [Specific guidance based on discovered misalignments]

---

## APPENDICES

### Appendix A: Complete Field Mappings

**Activities Data - Complete Field-to-Column Map:**
```
[Complete exhaustive list of every JSON field and its database column]
```

**Positions Data - Complete Field-to-Column Map:**
```
[Complete exhaustive list of every JSON field and its database column]
```

### Appendix B: Sample Data Validation

Show 2-3 example records from actual JSON and how they would map to database rows:

**Activities Example:**
```json
[actual JSON record]
```
Maps to database row:
```sql
[SQL INSERT statement showing mapped values]
```

**Positions Example:**
```json
[actual JSON record]
```
Maps to database row:
```sql
[SQL INSERT statement showing mapped values]
```

### Appendix C: Files Analyzed

- Mapping Guide Activities: [path] (last modified: [date])
- JSON Spec Activities: [path] (last modified: [date])
- Actual JSON Activities: [path] (created: [timestamp])
- Mapping Guide Positions: [path] (last modified: [date])
- JSON Spec Positions: [path] (last modified: [date])
- Actual JSON Positions: [path] (created: [timestamp])
- Database Schema: [path] (last modified: [date])

---

## VALIDATION CONCLUSION

**Overall Status:** [PASS / PASS WITH WARNINGS / FAIL]

**Can data be loaded to database?** [YES / YES WITH MODIFICATIONS / NO]

**If modifications needed:**
[Summarize minimum changes required before loading can succeed]

**Confidence Level:** [HIGH / MEDIUM / LOW]
[Explain confidence level]
```

## 🎯 Success Criteria

Your validation is complete when:
1. ✅ All 8 source files have been read completely
2. ✅ Every field in every JSON file has been cross-referenced against specs and schema
3. ✅ Every database column has been checked for a JSON source
4. ✅ All misalignments are documented with severity and recommendations
5. ✅ The report clearly states whether loading can proceed
6. ✅ Specific actionable recommendations are provided for any blockers
7. ✅ Complete field mapping tables are provided for loader implementation

## ⚠️ Important Guidance

**Be Extremely Thorough:**
- Don't just check top-level fields - check nested fields in arrays and objects
- Don't just check one example - check multiple records to find inconsistencies
- Don't assume fields with similar names are the same - verify exact matches
- Don't skip optional fields - they may still have alignment issues

**Be Specific in Recommendations:**
- Bad: "Field names don't match"
- Good: "JSON field `sec_description` must be mapped to database column `security_description` in transactions table"

**Quote Evidence:**
- When you find a mismatch, quote the relevant text from both documents
- Show actual JSON examples that demonstrate the issue
- Reference specific line numbers or section headings in documents

**Assess Real Impact:**
- Don't just list differences - explain what will happen if not fixed
- Distinguish between "will cause loading failure" vs "might cause data quality issues" vs "just documentation inconsistency"

## 🚀 Execution Instructions

1. Read this entire task document carefully
2. Read all 8 source files completely
3. Take detailed notes as you build field inventories
4. Systematically cross-reference as described
5. Generate the comprehensive report
6. Save the report to: `/Users/richkernan/Projects/Finances/.claude/reports/data_pipeline_alignment_report_[timestamp].md`
7. Return a summary of findings focusing on critical blockers

**Estimated Time:** This is a thorough analysis task. Take the time needed to be comprehensive and accurate. The user needs confidence that database loading will succeed or clear guidance on what must be fixed first.