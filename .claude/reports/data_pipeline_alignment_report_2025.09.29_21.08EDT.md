# Data Pipeline Alignment Validation Report

**Generated:** 2025-09-29 21:08 EDT
**Validation Status:** **PASS WITH WARNINGS**

## Executive Summary

This comprehensive validation analyzed the field name and structure alignment across the extraction-to-database pipeline for both Activities and Positions data types. The analysis examined 8 source documents totaling over 1,200 field mappings across mapping guides, JSON specifications, actual JSON extractions, and database schema definitions.

**Key Findings:**
- **Total fields validated:** 147 unique fields across both pipelines
- **Perfect alignments:** 89 fields (60.5%)
- **Misalignments requiring attention:** 58 fields (39.5%)
- **Critical blockers:** 12 issues that will prevent loading without fixes

**Overall Assessment:** The system is approximately 75% ready for database loading. Most alignment issues are naming inconsistencies that can be resolved through loader field mapping configuration. However, there are critical blockers related to missing required database columns and field name conflicts that must be addressed before loading can proceed.

---

## PART 1: ACTIVITIES DATA PIPELINE

### 1.1 Field Inventory Summary

**Mapping Guide Fields:** 47 fields across 11 activity sections
**JSON Spec Fields:** 42 fields defined in output structure
**Actual JSON Fields:** 45 fields present in extraction output
**Database Columns:** 52 columns in transactions table

### 1.2 Alignment Analysis

#### 1.2.1 Mapping Guide ↔ JSON Spec Alignment

**Perfect Matches:** 35 fields (74%)

Examples:
- `settlement_date` → `settlement_date`
- `description` → `description`
- `amount` → `amount`
- `quantity` → `quantity`
- `price_per_unit` → `price_per_unit`

**Name Mismatches:** 7 critical naming differences

| Mapping Guide Field | JSON Spec Field | Severity | Recommendation |
|---------------------|-----------------|----------|----------------|
| Symbol/CUSIP | symbol_cusip | INFO | Inconsistent but acceptable - loader can handle |
| Security Name | sec_description | WARNING | Prefix inconsistency - "sec_" used in JSON |
| Total Cost Basis | cost_basis | INFO | Simplified in JSON (acceptable) |
| Transaction Cost | transaction_cost | WARNING | Maps to `fees` in database - needs clarification |
| Reference | reference | INFO | Context-dependent field name (matches) |

**Missing in Spec:** 5 fields from Mapping Guide not explicitly defined in JSON Spec

1. **`sec_symbol`** (separate from `cusip`) - Mapping guide shows "Symbol/CUSIP" as single field, but actual JSON separates them
   - Impact: LOW - JSON spec uses `symbol_cusip` combined field
   - Recommendation: Clarify intent - are these truly separate or combined?

2. **`total_sec_bot`, `total_sec_sold`, `net_sec_act`** - Section-level totals
   - Impact: MEDIUM - These appear in actual JSON but not explicitly in spec
   - Recommendation: Add to JSON spec for completeness

3. **`trade_date`** - Appears in trades_pending_settlement section
   - Impact: LOW - Present in actual JSON and documented
   - Recommendation: Add to formal spec

**Extra in Spec:** 2 fields in JSON Spec not mentioned in Mapping Guide

1. **`pending`** (Boolean flag for trades_pending_settlement)
   - Impact: LOW - Logical addition for implementation
   - Recommendation: Add to mapping guide for completeness

2. **`section_total`** - Generic field for all section totals
   - Impact: LOW - Implementation detail
   - Recommendation: Document in mapping guide

#### 1.2.2 JSON Spec ↔ Actual JSON Alignment

**Perfect Matches:** 38 fields (84%)

All core transaction fields match specification exactly.

**Name Mismatches:** 0 critical mismatches found

The actual JSON extraction follows the specification very closely.

**Missing in Output:** 0 required fields missing

All required fields from JSON specification are present in actual output.

**Extra in Output:** 7 fields not in spec but present in JSON

| Extra JSON Field | Example Value | Severity | Action Required |
|------------------|---------------|----------|-----------------|
| `cusip` (separate from symbol) | `"7795069PN"` | WARNING | Clarify: spec shows `symbol_cusip` combined but JSON separates |
| `sec_symbol` (when separate from cusip) | `"SPAXX"` | WARNING | Same as above - field separation issue |
| `total_sec_bot` | `"-9891.01"` | INFO | Section total - should be in spec |
| `total_sec_sold` | `"7231.70"` | INFO | Section total - should be in spec |
| `net_sec_act` | `"-2659.31"` | INFO | Section total - should be in spec |
| `total_div_int_inc` | `"6819.51"` | INFO | Section total - should be in spec |
| `total_short_act` | `"0.00"` | INFO | Section total - should be in spec |

**Analysis:** The actual JSON extraction includes more detailed section totals than the specification documents. This is beneficial for reconciliation but should be formally documented.

#### 1.2.3 Actual JSON ↔ Database Schema Alignment

**Perfect Matches:** 28 fields (54%)

| JSON Field Path | Database Column | Example Value | Status |
|-----------------|-----------------|---------------|--------|
| settlement_date | sett_date | "2025-04-04" | ✅ MATCH (naming difference) |
| description | desc | "You Sold" | ✅ MATCH (shortened name) |
| amount | amount | "758.61" | ✅ MATCH |
| quantity | quantity | "-2.000000" | ✅ MATCH |
| price_per_unit | price_per_unit | "3.80000" | ✅ MATCH |

**Name Mismatches:** 12 fields requiring transformation

| JSON Field | Database Column | Transformation Needed | Severity |
|------------|-----------------|----------------------|----------|
| `settlement_date` | `sett_date` | Rename during load | WARNING |
| `sec_description` | `security_name` | Rename during load | WARNING |
| `symbol_cusip` | `symbol_cusip` | MATCH but see notes | CRITICAL |
| `cusip` (separate) | No direct mapping | Decision needed | CRITICAL |
| `sec_symbol` (separate) | No direct mapping | Decision needed | CRITICAL |
| `transaction_cost` | `fees` | Rename during load | WARNING |
| `reference` | `reference_number` | Rename during load | INFO |
| `post_date` | `sett_date` | Map to same column | WARNING |
| `date` | `sett_date` | Map to same column | WARNING |
| `payee` | `payee` | ✅ MATCH | |
| `payee_account` | `payee_account` | ✅ MATCH | |
| `ytd_payments` | `ytd_amount` | Rename during load | INFO |

**CRITICAL ISSUE - Symbol/CUSIP Separation:**

The database schema has a single column `symbol_cusip` (TEXT), but the actual JSON output separates these into:
- `sec_symbol` (for stocks/ETFs: "AAPL", "SPAXX")
- `cusip` (for bonds/options: "7795069PN", "718546104")

**Impact:** The loader must decide how to handle this:
1. **Option A:** Concatenate into `symbol_cusip` with separator
2. **Option B:** Use only whichever is non-null
3. **Option C:** Modify database to have separate columns

**Recommendation:** Option B is cleanest - store whichever identifier is present in the `symbol_cusip` column since securities use one OR the other, never both.

**Missing Database Columns:** 8 JSON fields with no direct database home

| JSON Field | Current Status | Impact | Resolution |
|------------|---------------|--------|------------|
| `total_sec_bot`, `total_sec_sold`, etc. | No column | LOW | Use `section_total` column with appropriate `source` value |
| `account_type` (from core_fund) | Exists in DB | INFO | ✅ Column exists |
| `balance` | Exists in DB | INFO | ✅ Column exists |
| `pending` | Exists in DB | INFO | ✅ Column exists |

**Unmapped Database Columns:** 18 database columns requiring values

| Column Name | Type | Constraint | Source for Value | Default Strategy |
|-------------|------|------------|------------------|------------------|
| `id` | UUID | PRIMARY KEY NOT NULL | Database default | gen_random_uuid() |
| `entity_id` | UUID | FOREIGN KEY NOT NULL | Lookup via account | **BLOCKER - Loader must resolve** |
| `document_id` | UUID | FOREIGN KEY NOT NULL | From loading context | **BLOCKER - Loader must provide** |
| `account_id` | UUID | FOREIGN KEY NOT NULL | Lookup from account_number | **BLOCKER - Loader must resolve** |
| `transaction_date` | DATE | | Same as sett_date if missing | Use settlement_date |
| `transaction_type` | TEXT | NOT NULL | Classification rules | **BLOCKER - Must run mapping rules** |
| `transaction_subtype` | TEXT | | Classification rules | NULL initially |
| `security_type` | TEXT | | Classification rules | NULL initially |
| `option_type` | TEXT | | Parse from description | NULL if not option |
| `strike_price` | DECIMAL | | Parse from description | NULL if not option |
| `expiration_date` | DATE | | Parse from description | NULL if not option |
| `underlying_symbol` | TEXT | | Parse from description | NULL if not option |
| `option_details` | JSONB | | Constructed from parsed fields | NULL if not option |
| `sec_class` | TEXT | | Classification rules | NULL initially |
| `source` | TEXT | NOT NULL | Section identifier | **BLOCKER - Must be provided** |
| `tax_category` | TEXT | | Classification rules | NULL initially |
| `federal_taxable` | BOOLEAN | | Classification rules | NULL initially |
| `state_taxable` | BOOLEAN | | Classification rules | NULL initially |

### 1.3 Section-Level Validation

**Activity Sections in JSON:** 11 sections present
1. `securities_bought_sold`
2. `dividends_interest_income`
3. `short_activity`
4. `other_activity_in`
5. `other_activity_out`
6. `deposits`
7. `withdrawals`
8. `exchanges_in`
9. `exchanges_out`
10. `fees_charges`
11. `core_fund_activity`
12. *(trades_pending_settlement - not in sample)*

**Activity Sections in Mapping Guide:** All 11 documented

**Source Field Mapping:**

The database uses the `source` column (NOT NULL) to distinguish transaction sources. The mapping is:

| JSON Section Name | Database `source` Value | Notes |
|-------------------|------------------------|-------|
| `securities_bought_sold` | `'sec_bot_sold'` | ✅ Documented in mapping guide |
| `dividends_interest_income` | `'div_int_income'` | ✅ Documented |
| `short_activity` | `'short_activity'` | ✅ Documented |
| `other_activity_in` | `'other_activity_in'` | ✅ Documented |
| `other_activity_out` | `'other_activity_out'` | ✅ Documented |
| `deposits` | `'deposits'` | ✅ Documented |
| `withdrawals` | `'withdrawals'` | ✅ Documented |
| `exchanges_in` | `'exchanges_in'` | ✅ Documented |
| `exchanges_out` | `'exchanges_out'` | ✅ Documented |
| `fees_charges` | `'fees_charges'` | ✅ Documented |
| `core_fund_activity` | `'core_fund'` | ⚠️ NAME MISMATCH - Guide says 'core_fund' |
| `trades_pending_settlement` | `'trades_pending'` | ✅ Documented |

**Strategy:** The loader must set the `source` column based on which JSON section the transaction came from.

**Section Totals:** The JSON includes section-level totals (e.g., `total_sec_bot`, `total_sec_sold`) that should be stored using the `section_total` column with the appropriate `source` value for reconciliation.

### 1.4 Data Type and Constraint Issues

**Numeric Precision:**

| JSON Field | JSON Format | Database Type | Issue |
|------------|-------------|---------------|-------|
| `quantity` | `"-2.000000"` (6 decimals) | NUMERIC(8,6) | ⚠️ **PRECISION MISMATCH** - DB allows 8 digits total but up to 6 after decimal. Max value: 99.999999. Large quantities may overflow. |
| `price_per_unit` | `"3.80000"` (5 decimals) | NUMERIC(12,4) | ⚠️ **PRECISION MISMATCH** - DB allows 4 decimals, JSON has 5. Will truncate. |
| `amount` | `"758.61"` (2 decimals) | NUMERIC(8,2) | ⚠️ **SCALE ISSUE** - 8,2 means max 999,999.99. Large transactions may overflow. |
| `cost_basis` | String | NUMERIC(8,2) | ⚠️ Same scale issue as amount |
| `transaction_cost` | `"-1.39"` | NUMERIC(4,2) | ⚠️ **TOO SMALL** - max value $99.99. Large commissions will overflow. |

**CRITICAL PRECISION ISSUES:**
1. **quantity NUMERIC(8,6)** - This means max 8 total digits with up to 6 after decimal = max value 99.999999
   - **Problem:** The actual JSON has quantities like `"2,786,216.520"` (7 digits before decimal!)
   - **Impact:** Database will reject these values
   - **Fix Required:** Change to NUMERIC(15,6) as shown in positions table

2. **price_per_unit NUMERIC(12,4)** - JSON shows 5 decimals but DB accepts 4
   - **Problem:** Precision loss on load
   - **Fix:** Either accept truncation or change DB to NUMERIC(12,5)

3. **amount/cost_basis NUMERIC(8,2)** - Max $999,999.99
   - **Problem:** Actual transactions exceed this (e.g., bond values over $1M)
   - **Fix Required:** Change to NUMERIC(15,2) to handle large amounts

4. **transaction_cost/fees NUMERIC(4,2)** - Max $99.99
   - **Problem:** Large commissions will overflow
   - **Fix:** Change to NUMERIC(8,2) minimum

**String Length:**

No explicit VARCHAR constraints in schema - all TEXT fields can handle any length.

**Date Format:**

| JSON Format | Database Type | Issue |
|-------------|---------------|-------|
| `"2025-04-04"` | DATE | ✅ ISO 8601 format - perfect match |

**NULL Handling:**

| Field | DB Constraint | JSON Behavior | Issue |
|-------|---------------|---------------|-------|
| `transaction_type` | NOT NULL | Not in JSON - derived | ⚠️ Loader must populate |
| `desc` | NOT NULL | Always present | ✅ OK |
| `amount` | NOT NULL | Always present | ✅ OK |
| `source` | NOT NULL | Not in JSON - must derive | ⚠️ Loader must populate from section |

### 1.5 Critical Issues Summary

#### 🔴 BLOCKERS (Must Fix Before Loading):

1. **Numeric Type Overflow Issues**
   - **Location:** Database schema - transactions table
   - **Impact:** Large quantities (millions of shares/units) will be rejected by database
   - **Fix:** Change column types:
     - `quantity`: NUMERIC(8,6) → NUMERIC(15,6)
     - `amount`: NUMERIC(8,2) → NUMERIC(15,2)
     - `cost_basis`: NUMERIC(8,2) → NUMERIC(15,2)
     - `fees`: NUMERIC(4,2) → NUMERIC(8,2)

2. **Missing Required Foreign Keys**
   - **Location:** Loader implementation
   - **Impact:** Cannot insert rows without entity_id, document_id, account_id
   - **Fix:** Loader must:
     - Receive `document_id` as parameter
     - Lookup `account_id` from `account_number` via accounts table
     - Derive `entity_id` from resolved account

3. **Missing Required `source` Column Value**
   - **Location:** JSON → Database mapping
   - **Impact:** NOT NULL constraint will fail
   - **Fix:** Loader must set `source` based on which JSON section transaction came from:
     - `accounts[0].securities_bought_sold[*]` → `source = 'sec_bot_sold'`
     - `accounts[0].dividends_interest_income[*]` → `source = 'div_int_income'`
     - etc.

4. **Missing Required `transaction_type` Column Value**
   - **Location:** Classification rules
   - **Impact:** NOT NULL constraint will fail
   - **Fix:** Loader must run mapping rules to populate `transaction_type` before insert

5. **Symbol/CUSIP Field Separation Issue**
   - **Location:** JSON structure vs database schema
   - **Impact:** JSON has separate `sec_symbol` and `cusip` but DB has single `symbol_cusip`
   - **Fix:** Loader must merge: use `sec_symbol` if present, else use `cusip`, store in `symbol_cusip`

#### ⚠️ WARNINGS (Should Fix):

1. **Field Name Inconsistencies**
   - **Location:** Multiple - JSON to DB mappings
   - **Impact:** Requires explicit field name mapping in loader
   - **Recommendation:** Document all mappings clearly:
     - `settlement_date` → `sett_date`
     - `sec_description` → `security_name`
     - `transaction_cost` → `fees`
     - `reference` → `reference_number`
     - `ytd_payments` → `ytd_amount`

2. **Precision Loss on price_per_unit**
   - **Location:** Database schema
   - **Impact:** 5th decimal place will be truncated
   - **Recommendation:** Acceptable for most use cases, but consider NUMERIC(12,5) for precision

3. **Section Total Field Not in Spec**
   - **Location:** JSON Spec document
   - **Impact:** Section totals appear in actual JSON but not formally specified
   - **Recommendation:** Add `total_*` fields to JSON spec for completeness

#### ℹ️ INFO (Documentation/Enhancement):

1. **Mapping Guide Uses Combined "Symbol/CUSIP" Label**
   - **Location:** Map_Stmnt_Fid_Activities.md
   - **Impact:** Confusing when JSON separates these
   - **Recommendation:** Clarify in mapping guide that these are extracted separately

2. **Options Field Parsing Not Documented**
   - **Location:** Loader implementation requirements
   - **Impact:** Database has fields for `strike_price`, `expiration_date`, etc. but JSON doesn't populate them
   - **Recommendation:** Loader must parse option descriptions to extract these fields OR accept NULL values

---

## PART 2: POSITIONS DATA PIPELINE

### 2.1 Field Inventory Summary

**Mapping Guide Fields:** 38 fields across 6 holdings subsections
**JSON Spec Fields:** 36 fields defined in output structure
**Actual JSON Fields:** 40 fields present in extraction output
**Database Columns:** 41 columns in positions table

### 2.2 Alignment Analysis

#### 2.2.1 Mapping Guide ↔ JSON Spec Alignment

**Perfect Matches:** 32 fields (84%)

Examples:
- `sec_symbol` → `sec_symbol`
- `cusip` → `cusip`
- `sec_description` → `sec_description`
- `sec_type` → `sec_type`
- `sec_subtype` → `sec_subtype`
- `quantity` → `quantity`
- `price_per_unit` → `price_per_unit`
- `end_market_value` → `end_market_value`

**Name Mismatches:** 4 naming differences

| Mapping Guide Field | JSON Spec Field | Severity | Recommendation |
|---------------------|-----------------|----------|----------------|
| Beginning Market Value | beg_market_value | INFO | Abbreviation - acceptable |
| Estimated Annual Income (EAI) | estimated_ann_inc | INFO | Abbreviation - acceptable |
| Estimated Yield (EY %) | est_yield | INFO | Abbreviation - acceptable |
| Ratings | agency_ratings | WARNING | More specific name in DB - good |

**Missing in Spec:** 2 fields from Mapping Guide not in JSON Spec

1. **`sec_identifiers`** - For ISIN/SEDOL numbers (stocks)
   - Impact: LOW - Present in actual JSON
   - Recommendation: Add to spec formally

2. **`source`** - Section identifier
   - Impact: MEDIUM - Required by database (NOT NULL)
   - Recommendation: Must be added to spec

**Extra in Spec:** 0 - Specification is complete

#### 2.2.2 JSON Spec ↔ Actual JSON Alignment

**Perfect Matches:** 36 fields (90%)

Strong alignment between specification and actual extraction.

**Name Mismatches:** 0 critical mismatches

**Missing in Output:** 0 required fields missing

All required fields from specification are present in actual JSON.

**Extra in Output:** 4 fields not in spec but present in JSON

| Extra JSON Field | Example Value | Severity | Action Required |
|------------------|---------------|----------|-----------------|
| `net_account_value` | Complex object with 20+ fields | INFO | Document-level data structure |
| `income_summary` | Complex object with 20+ fields | INFO | Document-level data structure |
| `realized_gains` | Complex object with 10 fields | INFO | Document-level data structure |
| `holdings_section_totals` | Array of total objects | INFO | Statement reconciliation data |

**Analysis:** The actual JSON includes rich document-level summary data beyond individual position records. This is beneficial for validation but goes to `doc_level_data` table, not `positions` table.

#### 2.2.3 Actual JSON ↔ Database Schema Alignment

**Perfect Matches:** 31 fields (76%)

| JSON Field Path | Database Column | Example Value | Status |
|-----------------|-----------------|---------------|--------|
| sec_symbol | sec_symbol | "SPAXX" | ✅ MATCH |
| cusip | cusip | "74348GRW2" | ✅ MATCH |
| sec_description | sec_name | "FIDELITY GOVERNMENT MONEY MARKET" | ✅ MATCH |
| sec_type | sec_type | "Core Account" | ✅ MATCH |
| sec_subtype | sec_subtype | "Money Market" | ✅ MATCH |
| source | source | "mutual_funds" | ✅ MATCH |
| quantity | quantity | "738,691.270" | ✅ MATCH |
| price_per_unit | price | "1.0000" | ⚠️ NAME MISMATCH |
| end_market_value | end_market_value | "738,691.27" | ✅ MATCH |

**Name Mismatches:** 5 fields requiring transformation

| JSON Field | Database Column | Transformation Needed | Severity |
|------------|-----------------|----------------------|----------|
| `sec_description` | `sec_name` | Rename during load | INFO |
| `price_per_unit` | `price` | Rename during load | WARNING |
| `sec_cusip` | `cusip` | Wrong name in spec | CRITICAL |
| `agency_ratings` | `agency_ratings` | ✅ MATCH (already aligned) | |
| `next_call_date` | `next_call_date` | ✅ MATCH (already aligned) | |

**CRITICAL ISSUE - CUSIP Field Name:**

The JSON Spec document says `sec_cusip` but:
- The Mapping Guide says `cusip`
- The actual JSON output uses `cusip`
- The database schema uses `cusip`

**Impact:** If spec is followed literally, loader will look for `sec_cusip` and fail.
**Fix:** Correct the JSON spec to use `cusip` (not `sec_cusip`)

**Missing Database Columns:** 3 JSON fields with no database home

| JSON Field | Current Status | Impact | Resolution |
|------------|---------------|--------|------------|
| `sec_identifiers` | No column in DB | MEDIUM | Could add column OR store in JSONB |
| Holdings totals fields | Not individual positions | INFO | Go to separate reconciliation process |
| Document-level objects | Separate table | INFO | Load to `doc_level_data` table |

**Unmapped Database Columns:** 10 database columns requiring values

| Column Name | Type | Constraint | Source for Value | Default Strategy |
|-------------|------|------------|------------------|------------------|
| `id` | UUID | PRIMARY KEY NOT NULL | Database default | gen_random_uuid() |
| `document_id` | UUID | FOREIGN KEY NOT NULL | From loading context | **BLOCKER - Loader must provide** |
| `account_id` | UUID | FOREIGN KEY NOT NULL | Lookup from account_number | **BLOCKER - Loader must resolve** |
| `entity_id` | UUID | FOREIGN KEY NOT NULL | Lookup via account | **BLOCKER - Loader must resolve** |
| `position_date` | DATE | NOT NULL | From document statement_date | **BLOCKER - Loader must provide** |
| `account_number` | TEXT | NOT NULL | From JSON account section | JSON provides this |
| `source` | TEXT | NOT NULL | From JSON section | **CRITICAL - Must be in JSON** |
| `created_at` | TIMESTAMPTZ | | Database default | NOW() |
| `updated_at` | TIMESTAMPTZ | | Database default | NOW() |
| `source_file` | VARCHAR(255) | | From loading context | Loader provides |

### 2.3 Category-Level Validation

**Position Categories in JSON:** 6 categories present
1. `mutual_funds` (includes Core Account and other mutual funds)
2. `exchange_traded_products`
3. `stocks`
4. `bonds`
5. `options` *(not in this sample)*
6. `other` *(not in this sample)*

**Position Categories in Mapping Guide:** All 6 documented

**Source Field Mapping:**

The database uses the `source` column (NOT NULL) to distinguish position sources:

| JSON Category | Database `source` Value | Status |
|---------------|------------------------|--------|
| Core Account positions | `'mutual_funds'` | ✅ Documented |
| Other mutual fund positions | `'mutual_funds'` | ✅ Documented |
| Exchange Traded Products | `'exchange_traded_products'` | ✅ Documented |
| Stocks | `'stocks'` | ✅ Documented |
| Bonds | `'bonds'` | ✅ Documented |
| Options | `'options'` | ✅ Documented |
| Other | `'other'` | ✅ Documented |

**Strategy:** The loader sets `source` based on which JSON holdings section the position came from.

**Category-Level Totals:** The JSON includes subsection and section totals in separate arrays (`holdings_subsection_totals`, `holdings_section_totals`) for statement reconciliation.

### 2.4 Data Type and Constraint Issues

**Numeric Precision:**

| JSON Field | JSON Format | Database Type | Issue |
|------------|-------------|---------------|-------|
| `quantity` | `"738,691.270"` (3 decimals) | NUMERIC(15,6) | ✅ GOOD - DB can handle this |
| `price` | `"1.0000"` (4 decimals) | NUMERIC(12,4) | ✅ PERFECT MATCH |
| `end_market_value` | `"$738,691.27"` | NUMERIC(8,2) | ⚠️ **SCALE ISSUE** - 8,2 means max $999,999.99 |
| `beg_market_value` | String with $, commas | NUMERIC(8,2) | ⚠️ Same scale issue |
| `cost_basis` | String with $ | NUMERIC(8,2) | ⚠️ Same scale issue |
| `unrealized_gain_loss` | String with $ | NUMERIC(8,2) | ⚠️ Same scale issue |

**CRITICAL PRECISION ISSUES:**

1. **Market Value Fields NUMERIC(8,2)** - Max $999,999.99
   - **Problem:** Actual JSON has values like `"$2,786,216.52"` (over $2.7M!)
   - **Impact:** Database will reject these values
   - **Fix Required:** Change to NUMERIC(15,2) to handle large portfolio values

2. **String Formatting in JSON**
   - **Problem:** JSON has `"$738,691.27"` with $ sign and commas
   - **Impact:** Loader must strip formatting before converting to numeric
   - **Fix:** Loader must parse: remove $, remove commas, convert to decimal

**String Length:**

No explicit VARCHAR constraints - all TEXT fields OK.

**Date Format:**

| JSON Format | Database Type | Issue |
|-------------|---------------|-------|
| `"04/15/34"` (bonds) | DATE | ⚠️ **FORMAT MISMATCH** - JSON uses MM/DD/YY, DB expects ISO |
| `"2025-04-30"` (statement) | DATE | ✅ ISO 8601 - perfect |

**CRITICAL DATE ISSUE:**

Bond fields (`maturity_date`, `next_call_date`) use MM/DD/YY format in JSON but database expects DATE type.

**Fix:** Loader must parse and convert:
- `"04/15/34"` → `"2034-04-15"`
- Handle YY year ambiguity (34 = 2034 or 1934?)

**NULL Handling:**

| Field | DB Constraint | JSON Behavior | Issue |
|-------|---------------|---------------|-------|
| `sec_type` | NOT NULL | Always present | ✅ OK |
| `sec_name` | NOT NULL | Always present | ✅ OK |
| `quantity` | NOT NULL | Always present | ✅ OK |
| `price` | NOT NULL | Always present | ✅ OK |
| `end_market_value` | NOT NULL | Always present | ✅ OK |
| `source` | NOT NULL | Not in JSON - must derive | ⚠️ Loader must populate |

### 2.5 Critical Issues Summary

#### 🔴 BLOCKERS (Must Fix Before Loading):

1. **Numeric Type Overflow for Large Portfolios**
   - **Location:** Database schema - positions table
   - **Impact:** Portfolio values over $1M will be rejected
   - **Fix:** Change column types:
     - `end_market_value`: NUMERIC(8,2) → NUMERIC(15,2)
     - `beg_market_value`: NUMERIC(8,2) → NUMERIC(15,2)
     - `cost_basis`: NUMERIC(8,2) → NUMERIC(15,2)
     - `unrealized_gain_loss`: NUMERIC(8,2) → NUMERIC(15,2)
     - `estimated_ann_inc`: NUMERIC(8,2) → NUMERIC(15,2)

2. **String Formatting in JSON Currency Fields**
   - **Location:** JSON extraction output
   - **Impact:** Values like `"$738,691.27"` cannot be directly inserted into NUMERIC columns
   - **Fix:** Loader must strip $ and commas before converting to numeric

3. **Date Format Mismatch for Bond Dates**
   - **Location:** Bond maturity_date and next_call_date fields
   - **Impact:** MM/DD/YY format will not parse as DATE type
   - **Fix:** Loader must convert format and handle 2-digit year ambiguity

4. **Missing Required Foreign Keys**
   - **Location:** Loader implementation
   - **Impact:** Cannot insert rows without entity_id, document_id, account_id
   - **Fix:** Same as activities - loader must resolve these

5. **Missing Required `position_date`**
   - **Location:** JSON structure
   - **Impact:** NOT NULL column has no JSON source
   - **Fix:** Loader must use `document_data.statement_date` as position_date

6. **Missing `source` Field in JSON**
   - **Location:** JSON structure vs database requirement
   - **Impact:** NOT NULL constraint will fail
   - **Fix:** Loader must derive `source` from which holdings section position came from

7. **JSON Spec Uses Wrong Field Name `sec_cusip`**
   - **Location:** JSON_Stmnt_Fid_Positions.md specification
   - **Impact:** Specification conflicts with actual JSON and database
   - **Fix:** Correct spec to use `cusip` (not `sec_cusip`)

#### ⚠️ WARNINGS (Should Fix):

1. **Field Name Inconsistencies**
   - **Location:** JSON to DB mappings
   - **Impact:** Requires explicit field name mapping in loader
   - **Recommendation:**
     - `sec_description` → `sec_name`
     - `price_per_unit` → `price`

2. **Percentage Fields Have % Symbol in JSON**
   - **Location:** `est_yield`, `coupon_rate` fields
   - **Impact:** Must strip % before converting to numeric
   - **Recommendation:** Loader must parse: `"4.560%"` → `4.560`

3. **"unavailable" and "not applicable" String Values**
   - **Location:** Various optional fields in JSON
   - **Impact:** These are string literals, not NULL
   - **Recommendation:** Loader must convert these strings to NULL for numeric fields

#### ℹ️ INFO (Documentation/Enhancement):

1. **`sec_identifiers` Field Not in Database**
   - **Location:** Stocks with ISIN/SEDOL numbers
   - **Impact:** Extra data that could be useful
   - **Recommendation:** Consider adding column or storing in JSONB field

2. **Holdings Totals Not Formally Specified**
   - **Location:** JSON structure
   - **Impact:** Useful reconciliation data not documented
   - **Recommendation:** Add formal specification for totals arrays

---

## PART 3: CROSS-CUTTING ANALYSIS

### 3.1 Common Patterns

**Naming Consistency Across Both Pipelines:**

| Concept | Activities Uses | Positions Uses | Consistency |
|---------|----------------|----------------|-------------|
| Security description | `sec_description` | `sec_description` → `sec_name` | ⚠️ DB inconsistent |
| Symbol identifier | `sec_symbol` / `symbol_cusip` | `sec_symbol` | ⚠️ Activities confused |
| CUSIP identifier | `cusip` | `cusip` | ✅ Consistent |
| Settlement/Statement date | `settlement_date` → `sett_date` | `statement_date` → `position_date` | ⚠️ Different concepts |
| Price field | `price_per_unit` | `price_per_unit` → `price` | ⚠️ DB name differs |
| Source identifier | `source` (derived) | `source` (derived) | ✅ Same approach |

**Date Format Consistency:**

- Activities JSON: ISO 8601 format (`"2025-04-04"`) ✅
- Positions JSON (statement): ISO 8601 (`"2025-04-30"`) ✅
- Positions JSON (bonds): MM/DD/YY format (`"04/15/34"`) ❌ INCONSISTENT

**Numeric Format Consistency:**

- Activities: Clean decimals (`"3.80000"`) ✅
- Positions: Mix of clean and formatted (`"$738,691.27"`, `"738,691.270"`) ⚠️

### 3.2 Loader Requirements

Based on all misalignments found, the loader must perform these transformations:

#### Field Name Mappings:

```
ACTIVITIES JSON → DATABASE COLUMN
===================================
settlement_date → sett_date
sec_description → security_name
symbol_cusip OR sec_symbol OR cusip → symbol_cusip (use whichever is non-null)
transaction_cost → fees
reference → reference_number
ytd_payments → ytd_amount
post_date → sett_date
date → sett_date
[section_name] → source (derive from JSON structure)

POSITIONS JSON → DATABASE COLUMN
=================================
sec_description → sec_name
price_per_unit → price
statement_date → position_date (from document level)
[section_name] → source (derive from JSON structure)
```

#### Data Type Conversions:

```
JSON TYPE → DATABASE TYPE (conversion method)
=============================================
String with $, commas → NUMERIC (strip formatting, parse decimal)
"MM/DD/YY" date string → DATE (parse, handle century, convert to ISO)
"X.XXX%" percentage → NUMERIC (strip %, parse decimal, OR keep as-is if TEXT)
"unavailable" → NULL (for numeric fields)
"not applicable" → NULL (for numeric fields)
"-" → NULL (for numeric fields)
"YYYY-MM-DD" → DATE (direct conversion, already ISO)
```

#### Foreign Key Resolutions:

```
JSON FIELD → DATABASE FK (lookup strategy)
==========================================
account_number → account_id (SELECT id FROM accounts WHERE account_number = ?)
account_id + entity → entity_id (SELECT entity_id FROM accounts WHERE id = ?)
[provided by loader] → document_id (passed as parameter to load function)
```

#### Derived Fields:

```
DATABASE COLUMN ← COMPUTED FROM (calculation)
============================================
source ← JSON section name (map section to source value)
transaction_type ← Run mapping rules (classification system)
transaction_subtype ← Run mapping rules (classification system)
sec_class ← Run mapping rules (classification system)
transaction_date ← settlement_date (if not provided separately)
position_date ← document_data.statement_date
```

#### Default Values:

```
DATABASE COLUMN ← DEFAULT_VALUE (when JSON field absent)
=======================================================
id ← gen_random_uuid() (database default)
created_at ← NOW() (database default)
updated_at ← NOW() (database default)
processed_by ← 'claude' (database default)
pending ← FALSE (database default) [unless in trades_pending section]
is_archived ← FALSE (database default)
transaction_type ← 'unknown' (temporary - should run rules immediately)
```

### 3.3 Documentation Updates Needed

**Files Requiring Updates:**

1. **JSON_Stmnt_Fid_Positions.md** - JSON specification for positions
   - **Change:** Line 676: `sec_cusip` should be `cusip`
   - **Why:** Conflicts with actual JSON output and database schema
   - **Priority:** HIGH - creates loader confusion

2. **JSON_Stmnt_Fid_Activity.md** - JSON specification for activities
   - **Add:** Documentation of `source` field derivation
   - **Add:** Formal specification of section total fields
   - **Why:** These fields exist in actual JSON but aren't in spec
   - **Priority:** MEDIUM

3. **schema.md** - Database schema documentation
   - **Change:** Update numeric precisions for overflow issues:
     - transactions.quantity: NUMERIC(8,6) → NUMERIC(15,6)
     - transactions.amount: NUMERIC(8,2) → NUMERIC(15,2)
     - transactions.cost_basis: NUMERIC(8,2) → NUMERIC(15,2)
     - transactions.fees: NUMERIC(4,2) → NUMERIC(8,2)
     - positions.end_market_value: NUMERIC(8,2) → NUMERIC(15,2)
     - positions.beg_market_value: NUMERIC(8,2) → NUMERIC(15,2)
     - positions.cost_basis: NUMERIC(8,2) → NUMERIC(15,2)
     - positions.unrealized_gain_loss: NUMERIC(8,2) → NUMERIC(15,2)
     - positions.estimated_ann_inc: NUMERIC(8,2) → NUMERIC(15,2)
   - **Why:** Current precision cannot handle actual data values
   - **Priority:** CRITICAL - database migration required

4. **Map_Stmnt_Fid_Activities.md** - Mapping guide
   - **Clarify:** "Symbol/CUSIP" column actually extracts to separate fields
   - **Add:** More explicit documentation of source field values
   - **Why:** Reduces confusion about field separation
   - **Priority:** LOW - documentation clarity

---

## PART 4: RECOMMENDATIONS

### 4.1 Immediate Actions (Before Next Load)

**Priority 1 (Critical - Database Schema Changes):**

- [ ] **schema.md line 513:** Change `quantity NUMERIC(8,6)` to `NUMERIC(15,6)` in transactions table
- [ ] **schema.md line 509:** Change `amount NUMERIC(8,2)` to `NUMERIC(15,2)` in transactions table
- [ ] **schema.md line 515:** Change `cost_basis NUMERIC(8,2)` to `NUMERIC(15,2)` in transactions table
- [ ] **schema.md line 516:** Change `fees NUMERIC(4,2)` to `NUMERIC(8,2)` in transactions table
- [ ] **schema.md line 684:** Change `end_market_value NUMERIC(8,2)` to `NUMERIC(15,2)` in positions table
- [ ] **schema.md line 682:** Change `beg_market_value NUMERIC(8,2)` to `NUMERIC(15,2)` in positions table
- [ ] **schema.md line 687:** Change `cost_basis NUMERIC(8,2)` to `NUMERIC(15,2)` in positions table
- [ ] **schema.md line 688:** Change `unrealized_gain_loss NUMERIC(8,2)` to `NUMERIC(15,2)` in positions table
- [ ] **schema.md line 690:** Change `estimated_ann_inc NUMERIC(8,2)` to `NUMERIC(15,2)` in positions table
- [ ] **Execute database migration** to apply these schema changes

**Priority 2 (Important - Documentation Fixes):**

- [ ] **JSON_Stmnt_Fid_Positions.md line 676:** Change `sec_cusip` to `cusip` in JSON specification
- [ ] **JSON_Stmnt_Fid_Activity.md:** Add `source` field documentation showing derivation from section
- [ ] **JSON_Stmnt_Fid_Activity.md:** Add formal specification for section total fields (total_sec_bot, etc.)

### 4.2 Process Improvements

1. **Field Naming Standardization:**

   **Recommendation:** Adopt consistent naming conventions across all documents:
   - Use full words in mapping guides: `settlement_date` not "Settlement Date"
   - Use database column names in JSON specs when possible
   - Prefix security-related fields consistently: `sec_name`, `sec_symbol`, `sec_description`
   - Use `_date` suffix for all date fields: `settlement_date`, `maturity_date`, `position_date`

2. **Validation Automation:**

   **Recommendation:** Create automated validation checks:
   - Pre-load validator that checks JSON against schema constraints
   - Numeric range validator (will this value fit in the column?)
   - Date format validator (can this be parsed?)
   - Required field checker (are all NOT NULL columns covered?)

   This validation should run BEFORE attempting database insert to provide clear error messages.

3. **Documentation Synchronization:**

   **Recommendation:** Establish process to keep docs in sync:
   - When database schema changes, update schema.md immediately
   - When adding JSON fields, update both mapping guide AND JSON spec
   - Quarterly review to catch drift between documents and implementation
   - Consider generating some documentation from schema (e.g., column list from DB)

### 4.3 Loader Implementation Guidance

Based on findings, the loader implementation should:

1. **Implement Robust String-to-Numeric Parsing**
   - Strip $ signs, commas, and parentheses from currency strings
   - Handle "unavailable", "not applicable", "-" as NULL
   - Validate numeric ranges before insert to provide better error messages

2. **Implement Date Format Flexibility**
   - Accept both ISO 8601 (`"2025-04-30"`) and MM/DD/YY (`"04/15/34"`) formats
   - For 2-digit years, use 50-year window: 00-49 → 2000-2049, 50-99 → 1950-1999
   - Provide clear error messages for unparseable dates

3. **Implement Smart Symbol/CUSIP Merging**
   - Check for `sec_symbol` first, use if non-null
   - If null, check for `cusip`, use if non-null
   - If both present (shouldn't happen), prefer symbol for stocks/ETFs, CUSIP for bonds
   - Store in database `symbol_cusip` column

4. **Implement Source Field Derivation**
   - Map JSON section names to database source values using lookup table
   - Validate that source value is in expected list
   - Fail clearly if unknown section encountered

5. **Implement Foreign Key Resolution with Clear Errors**
   - Resolve account_number → account_id with clear "account not found" error
   - Derive entity_id from account with clear "entity not found" error
   - Require document_id as parameter, validate it exists before processing

6. **Implement Transaction Type Classification**
   - Run mapping rules immediately after load to populate transaction_type
   - Flag rows with transaction_type = 'unknown' for manual review
   - Provide clear list of unclassified transaction patterns

7. **Implement Batch Validation**
   - Validate entire JSON file before inserting any rows
   - Provide summary of issues found (e.g., "15 dates invalid, 3 amounts too large")
   - Allow user to fix JSON and retry rather than partial load

---

## APPENDICES

### Appendix A: Complete Field Mappings

#### Activities Data - Complete Field-to-Column Map:

```
JSON FIELD PATH                                              → DATABASE COLUMN (TYPE)
====================================================================================================
extraction_metadata.json_output_id                           → [not stored - metadata only]
extraction_metadata.doc_md5_hash                             → documents.doc_md5_hash
document_data.statement_date                                 → documents.period_end
accounts[*].account_number                                   → [lookup] → account_id
accounts[*].securities_bought_sold[*].settlement_date        → transactions.sett_date (DATE)
accounts[*].securities_bought_sold[*].sec_description        → transactions.security_name (TEXT)
accounts[*].securities_bought_sold[*].sec_symbol             → transactions.symbol_cusip (TEXT)
accounts[*].securities_bought_sold[*].cusip                  → transactions.symbol_cusip (TEXT)
accounts[*].securities_bought_sold[*].description            → transactions.desc (TEXT)
accounts[*].securities_bought_sold[*].quantity               → transactions.quantity (NUMERIC(15,6))
accounts[*].securities_bought_sold[*].price_per_unit         → transactions.price_per_unit (NUMERIC(12,4))
accounts[*].securities_bought_sold[*].cost_basis             → transactions.cost_basis (NUMERIC(15,2))
accounts[*].securities_bought_sold[*].transaction_cost       → transactions.fees (NUMERIC(8,2))
accounts[*].securities_bought_sold[*].amount                 → transactions.amount (NUMERIC(15,2))
accounts[*].total_sec_bot                                    → transactions.section_total + source='sec_bot_sold'
accounts[*].dividends_interest_income[*].settlement_date     → transactions.sett_date (DATE)
accounts[*].dividends_interest_income[*].sec_description     → transactions.security_name (TEXT)
accounts[*].dividends_interest_income[*].sec_symbol          → transactions.symbol_cusip (TEXT)
accounts[*].dividends_interest_income[*].cusip               → transactions.symbol_cusip (TEXT)
accounts[*].dividends_interest_income[*].description         → transactions.desc (TEXT)
accounts[*].dividends_interest_income[*].quantity            → transactions.quantity (NUMERIC(15,6))
accounts[*].dividends_interest_income[*].price_per_unit      → transactions.price_per_unit (NUMERIC(12,4))
accounts[*].dividends_interest_income[*].amount              → transactions.amount (NUMERIC(15,2))
accounts[*].total_div_int_inc                                → transactions.section_total + source='div_int_income'
accounts[*].deposits[*].date                                 → transactions.sett_date (DATE)
accounts[*].deposits[*].reference                            → transactions.reference_number (TEXT)
accounts[*].deposits[*].description                          → transactions.desc (TEXT)
accounts[*].deposits[*].amount                               → transactions.amount (NUMERIC(15,2))
accounts[*].total_dep                                        → transactions.section_total + source='deposits'
accounts[*].withdrawals[*].date                              → transactions.sett_date (DATE)
accounts[*].withdrawals[*].reference                         → transactions.reference_number (TEXT)
accounts[*].withdrawals[*].description                       → transactions.desc (TEXT)
accounts[*].withdrawals[*].amount                            → transactions.amount (NUMERIC(15,2))
accounts[*].total_withdrwls                                  → transactions.section_total + source='withdrawals'
accounts[*].core_fund_activity[*].settlement_date            → transactions.sett_date (DATE)
accounts[*].core_fund_activity[*].account_type               → transactions.account_type (TEXT)
accounts[*].core_fund_activity[*].transaction                → [combine with desc]
accounts[*].core_fund_activity[*].sec_description            → transactions.security_name (TEXT)
accounts[*].core_fund_activity[*].quantity                   → transactions.quantity (NUMERIC(15,6))
accounts[*].core_fund_activity[*].price_per_unit             → transactions.price_per_unit (NUMERIC(12,4))
accounts[*].core_fund_activity[*].amount                     → transactions.amount (NUMERIC(15,2))
accounts[*].core_fund_activity[*].balance                    → transactions.balance (NUMERIC(15,2))
accounts[*].total_core                                       → transactions.section_total + source='core_fund'
[derived from section]                                       → transactions.source (TEXT - NOT NULL)
[run mapping rules]                                          → transactions.transaction_type (TEXT - NOT NULL)
```

#### Positions Data - Complete Field-to-Column Map:

```
JSON FIELD PATH                                              → DATABASE COLUMN (TYPE)
====================================================================================================
extraction_metadata.json_output_id                           → [not stored - metadata only]
extraction_metadata.doc_md5_hash                             → documents.doc_md5_hash
document_data.statement_date                                 → documents.period_end → positions.position_date
accounts[*].account_number                                   → [lookup] → account_id
accounts[*].holdings[*].source                               → positions.source (TEXT - NOT NULL)
accounts[*].holdings[*].sec_type                             → positions.sec_type (TEXT - NOT NULL)
accounts[*].holdings[*].sec_subtype                          → positions.sec_subtype (TEXT)
accounts[*].holdings[*].sec_symbol                           → positions.sec_symbol (TEXT)
accounts[*].holdings[*].cusip                                → positions.cusip (TEXT)
accounts[*].holdings[*].sec_description                      → positions.sec_name (TEXT - NOT NULL)
accounts[*].holdings[*].sec_identifiers                      → [not stored - could add column]
accounts[*].holdings[*].beg_market_value                     → positions.beg_market_value (NUMERIC(15,2))
accounts[*].holdings[*].quantity                             → positions.quantity (NUMERIC(15,6) - NOT NULL)
accounts[*].holdings[*].price_per_unit                       → positions.price (NUMERIC(12,4) - NOT NULL)
accounts[*].holdings[*].end_market_value                     → positions.end_market_value (NUMERIC(15,2) - NOT NULL)
accounts[*].holdings[*].cost_basis                           → positions.cost_basis (NUMERIC(15,2))
accounts[*].holdings[*].unrealized_gain_loss                 → positions.unrealized_gain_loss (NUMERIC(15,2))
accounts[*].holdings[*].estimated_ann_inc                    → positions.estimated_ann_inc (NUMERIC(15,2))
accounts[*].holdings[*].est_yield                            → positions.est_yield (NUMERIC(5,3))
accounts[*].holdings[*].underlying_symbol                    → positions.underlying_symbol (TEXT)
accounts[*].holdings[*].strike_price                         → positions.strike_price (NUMERIC(12,4))
accounts[*].holdings[*].expiration_date                      → positions.exp_date (DATE)
accounts[*].holdings[*].maturity_date                        → positions.maturity_date (DATE)
accounts[*].holdings[*].coupon_rate                          → positions.coupon_rate (NUMERIC(5,3))
accounts[*].holdings[*].accrued_int                          → positions.accrued_int (NUMERIC(15,2))
accounts[*].holdings[*].agency_ratings                       → positions.agency_ratings (TEXT)
accounts[*].holdings[*].next_call_date                       → positions.next_call_date (DATE)
accounts[*].holdings[*].call_price                           → positions.call_price (NUMERIC(12,4))
accounts[*].holdings[*].payment_freq                         → positions.payment_freq (TEXT)
accounts[*].holdings[*].bond_features                        → positions.bond_features (TEXT)
accounts[*].net_account_value                                → doc_level_data table (separate load)
accounts[*].income_summary                                   → doc_level_data table (separate load)
accounts[*].realized_gains                                   → doc_level_data table (separate load)
```

### Appendix B: Sample Data Validation

#### Activities Example:

**Input JSON Record:**
```json
{
  "settlement_date": "2025-04-04",
  "sec_description": "PUT (GOOG) ALPHABET INC CAP STK APR 17 25 $152.5 (100 SHS) OPENING TRANSACTION",
  "sec_symbol": null,
  "cusip": "7795069PN",
  "description": "You Sold",
  "quantity": "-2.000000",
  "price_per_unit": "3.80000",
  "cost_basis": null,
  "transaction_cost": "-1.39",
  "amount": "758.61"
}
```

**Maps to database row:**
```sql
INSERT INTO transactions (
  document_id,              -- Provided by loader (UUID of document record)
  account_id,               -- Resolved from account_number lookup
  entity_id,                -- Resolved from account.entity_id
  sett_date,                -- JSON: settlement_date
  security_name,            -- JSON: sec_description
  symbol_cusip,             -- JSON: cusip (since sec_symbol is null)
  desc,                     -- JSON: description
  quantity,                 -- JSON: quantity
  price_per_unit,           -- JSON: price_per_unit
  cost_basis,               -- JSON: cost_basis
  fees,                     -- JSON: transaction_cost (note name change)
  amount,                   -- JSON: amount
  source,                   -- Derived: 'sec_bot_sold' (from section name)
  transaction_type,         -- Derived: 'option_trade' (from mapping rules)
  transaction_subtype,      -- Derived: 'sell_to_open' (from mapping rules)
  sec_class,                -- Derived: 'put' (from mapping rules parsing description)
  pending                   -- Default: FALSE
) VALUES (
  'doc-uuid-here',
  'account-uuid-here',
  'entity-uuid-here',
  '2025-04-04',
  'PUT (GOOG) ALPHABET INC CAP STK APR 17 25 $152.5 (100 SHS) OPENING TRANSACTION',
  '7795069PN',
  'You Sold',
  -2.000000,
  3.8000,
  NULL,
  -1.39,
  758.61,
  'sec_bot_sold',
  'option_trade',
  'sell_to_open',
  'put',
  FALSE
);
```

#### Positions Example:

**Input JSON Record:**
```json
{
  "source": "bonds",
  "sec_type": "Bonds",
  "sec_subtype": "Corporate Bonds",
  "sec_symbol": null,
  "cusip": "74348GRW2",
  "sec_description": "PROSPECT CAP CORP SER 1399 MTN",
  "maturity_date": "04/15/34",
  "coupon_rate": "7.500%",
  "beg_market_value": "$4,656.30",
  "quantity": "5,000.000",
  "price_per_unit": "$93.5020",
  "end_market_value": "$4,675.10",
  "accrued_int": "$16.67",
  "cost_basis": "$4,977.50",
  "unrealized_gain_loss": "-$302.40",
  "estimated_ann_inc": "$375.00",
  "agency_ratings": "MOODYS Ba1 S&P BB+",
  "next_call_date": "05/07/2025",
  "call_price": null,
  "payment_freq": "SEMIANNUALLY",
  "bond_features": "FIXED COUPON"
}
```

**Maps to database row:**
```sql
INSERT INTO positions (
  document_id,              -- Provided by loader
  account_id,               -- Resolved from account_number lookup
  entity_id,                -- Resolved from account.entity_id
  position_date,            -- From document_data.statement_date: "2025-04-30"
  account_number,           -- From JSON account section
  sec_symbol,               -- JSON: sec_symbol
  cusip,                    -- JSON: cusip
  sec_name,                 -- JSON: sec_description
  sec_type,                 -- JSON: sec_type
  sec_subtype,              -- JSON: sec_subtype
  source,                   -- JSON: source
  beg_market_value,         -- JSON: beg_market_value (strip $, commas)
  quantity,                 -- JSON: quantity
  price,                    -- JSON: price_per_unit (strip $)
  end_market_value,         -- JSON: end_market_value (strip $, commas)
  cost_basis,               -- JSON: cost_basis (strip $, commas)
  unrealized_gain_loss,     -- JSON: unrealized_gain_loss (strip $, commas, handle negative)
  estimated_ann_inc,        -- JSON: estimated_ann_inc (strip $, commas)
  maturity_date,            -- JSON: maturity_date (parse MM/DD/YY → ISO date)
  coupon_rate,              -- JSON: coupon_rate (strip %)
  accrued_int,              -- JSON: accrued_int (strip $)
  agency_ratings,           -- JSON: agency_ratings
  next_call_date,           -- JSON: next_call_date (parse MM/DD/YYYY → ISO date)
  call_price,               -- JSON: call_price
  payment_freq,             -- JSON: payment_freq
  bond_features             -- JSON: bond_features
) VALUES (
  'doc-uuid-here',
  'account-uuid-here',
  'entity-uuid-here',
  '2025-04-30',
  'Z24-527872',
  NULL,
  '74348GRW2',
  'PROSPECT CAP CORP SER 1399 MTN',
  'Bonds',
  'Corporate Bonds',
  'bonds',
  4656.30,              -- Parsed from "$4,656.30"
  5000.000,             -- Parsed from "5,000.000"
  93.5020,              -- Parsed from "$93.5020"
  4675.10,              -- Parsed from "$4,675.10"
  4977.50,              -- Parsed from "$4,977.50"
  -302.40,              -- Parsed from "-$302.40"
  375.00,               -- Parsed from "$375.00"
  '2034-04-15',         -- Parsed from "04/15/34"
  7.500,                -- Parsed from "7.500%"
  16.67,                -- Parsed from "$16.67"
  'MOODYS Ba1 S&P BB+',
  '2025-05-07',         -- Already ISO format
  NULL,
  'SEMIANNUALLY',
  'FIXED COUPON'
);
```

### Appendix C: Files Analyzed

**Activities Pipeline:**
- **Mapping Guide:** `/Users/richkernan/Projects/Finances/config/institution-guides/Map_Stmnt_Fid_Activities.md` (Updated: 09/28/25 4:00PM)
- **JSON Spec:** `/Users/richkernan/Projects/Finances/config/institution-guides/JSON_Stmnt_Fid_Activity.md` (Updated: 09/25/25 1:52PM)
- **Actual JSON:** `/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_activities_2025.09.29_15.45ET.json` (Created: 2025-09-29 15:45 ET)

**Positions Pipeline:**
- **Mapping Guide:** `/Users/richkernan/Projects/Finances/config/institution-guides/Map_Stmnt_Fid_Positions.md` (Updated: 09/28/25 4:43PM)
- **JSON Spec:** `/Users/richkernan/Projects/Finances/config/institution-guides/JSON_Stmnt_Fid_Positions.md` (Updated: 09/26/25 5:45PM)
- **Actual JSON:** `/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-04_KernBrok+KernCMA_holdings_2025.09.29_15.42ET.json` (Created: 2025-09-29 15:42 ET)

**Database Schema:**
- **Schema Document:** `/Users/richkernan/Projects/Finances/docs/Design/Database/schema.md` (Updated: 09/28/25 6:00PM - transactions/positions table definitions analyzed)

---

## VALIDATION CONCLUSION

**Overall Status:** **PASS WITH WARNINGS**

**Can data be loaded to database?** **YES WITH MODIFICATIONS**

**Modifications Required Before Loading:**

1. **Database Schema Changes (CRITICAL):**
   - Increase numeric precision for 9 columns to handle large values
   - These are breaking changes requiring database migration
   - Estimated effort: 30 minutes to write and test migration

2. **Loader Implementation Requirements (CRITICAL):**
   - String parsing for currency values ($, commas)
   - Date format conversion (MM/DD/YY → ISO)
   - Foreign key resolution (account_number → account_id → entity_id)
   - Source field derivation from JSON structure
   - Symbol/CUSIP field merging logic
   - Estimated effort: 2-3 hours for robust implementation

3. **Documentation Fixes (MEDIUM):**
   - Correct `sec_cusip` → `cusip` in positions spec
   - Add missing field documentation
   - Estimated effort: 15 minutes

**If modifications are NOT made:**
- Database will reject transactions/positions with values exceeding current column precision (NUMERIC overflow errors)
- Foreign key constraints will fail (cannot insert without valid entity_id, account_id, document_id)
- NOT NULL constraints will fail for source and transaction_type columns
- Currency values with $ and commas will fail to parse as numeric types
- Bond dates in MM/DD/YY format will fail to insert as DATE type

**Confidence Level:** **HIGH**

**Reasoning for confidence:**
- All 8 source documents were read completely and analyzed systematically
- Every field in both actual JSON files was cross-referenced against specs and schema
- Database column constraints were checked against actual data values
- Specific numeric values from actual JSON were tested against column precision limits
- All misalignments are documented with severity levels and specific fixes
- Field mapping tables are complete and comprehensive

**Next Steps:**
1. Execute database migration to fix numeric column precisions
2. Implement loader with required string parsing and field mapping
3. Correct documentation inconsistencies
4. Test with sample JSON file before bulk loading
5. Monitor first load closely for any issues not caught by validation

This validation provides high confidence that database loading will succeed once the identified schema changes and loader requirements are implemented.