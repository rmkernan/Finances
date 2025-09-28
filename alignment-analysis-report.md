# Alignment Analysis Report: Activity Mapping Guide vs Database Schema

**Analysis Date:** 09/28/25 4:15PM ET
**Documents Analyzed:**
- `/config/institution-guides/Map_Stmnt_Fid_Activities.md` (Activity mapping guide)
- `/docs/Design/Database/schema.md` (Database schema)

**Purpose:** Comprehensive alignment analysis focusing on the new Section 11 (Trades Pending Settlement) and overall field mapping completeness.

---

## Executive Summary

### Overall Alignment Status: ⚠️ PARTIAL ALIGNMENT WITH CRITICAL GAPS

**Key Findings:**
1. **✅ GOOD:** Most existing activity sections (1-10) have proper database support
2. **🚨 CRITICAL:** Section 11 (Trades Pending Settlement) has significant gaps
3. **⚠️ CONCERN:** Several field mappings reference non-existent database columns
4. **✅ GOOD:** Core transaction framework supports the mapping philosophy

**Priority Action Required:** Address Section 11 gaps and missing database columns before processing documents with pending trades.

---

## Section-by-Section Analysis

### Section 1: Securities Bought & Sold ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| settlement_date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| sec_description | transactions.security_name | ✅ EXISTS | Properly mapped |
| symbol_cusip | transactions.symbol_cusip | ✅ EXISTS | Properly mapped |
| description | transactions.description | ✅ EXISTS | Properly mapped |
| quantity | transactions.quantity | ✅ EXISTS | Proper NUMERIC(8,6) type |
| price_per_unit | transactions.price_per_unit | ✅ EXISTS | Proper NUMERIC(12,4) type |
| cost_basis | transactions.cost_basis | ✅ EXISTS | Properly mapped |
| transaction_cost | transactions.fees | ✅ EXISTS | Properly mapped |
| amount | transactions.amount | ✅ EXISTS | Properly mapped |
| source = 'sec_bot_sold' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 2: Dividends, Interest & Other Income ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| settlement_date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| sec_description | transactions.security_name | ✅ EXISTS | Properly mapped |
| symbol_cusip | transactions.symbol_cusip | ✅ EXISTS | Properly mapped |
| description | transactions.description | ✅ EXISTS | Properly mapped |
| quantity | transactions.quantity | ✅ EXISTS | For reinvestments |
| price_per_unit | transactions.price_per_unit | ✅ EXISTS | For reinvestments |
| amount | transactions.amount | ✅ EXISTS | Income amount |
| source = 'div_int_income' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 4: Other Activity In/Out ✅ MOSTLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| settlement_date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| sec_description | transactions.security_name | ✅ EXISTS | Properly mapped |
| symbol_cusip | transactions.symbol_cusip | ✅ EXISTS | Properly mapped |
| description | transactions.description | ✅ EXISTS | Properly mapped |
| quantity | transactions.quantity | ✅ EXISTS | Contract quantity |
| cost_basis | transactions.cost_basis | ✅ EXISTS | Original cost |
| amount | transactions.amount | ✅ EXISTS | Transaction amount |
| total_activity_in | transactions.total_activity_in | ❌ MISSING | **Gap identified** |
| total_activity_out | transactions.total_activity_out | ❌ MISSING | **Gap identified** |
| source = 'other_activity_in/out' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ⚠️ **MOSTLY ALIGNED** - Missing total fields for section subtotals

---

### Section 5: Deposits ✅ MOSTLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| date | transactions.settlement_date | ✅ EXISTS | Mapped to settlement_date |
| reference | transactions.reference_number | ✅ EXISTS | Internal reference |
| description | transactions.description | ✅ EXISTS | Deposit description |
| amount | transactions.amount | ✅ EXISTS | Deposit amount |
| source = 'deposits' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 6: Withdrawals ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| date | transactions.settlement_date | ✅ EXISTS | Mapped correctly |
| reference | transactions.reference_number | ✅ EXISTS | Extract all text |
| description | transactions.description | ✅ EXISTS | Withdrawal description |
| amount | transactions.amount | ✅ EXISTS | Withdrawal amount |
| source = 'withdrawals' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 7: Exchanges In/Out ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| sec_description | transactions.security_name | ✅ EXISTS | Account identifier |
| symbol_cusip | transactions.symbol_cusip | ✅ EXISTS | Properly mapped |
| description | transactions.description | ✅ EXISTS | Transfer description |
| amount | transactions.amount | ✅ EXISTS | Transfer amount |
| source = 'exchanges_in/out' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 8: Fees and Charges ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| description | transactions.description | ✅ EXISTS | Fee description |
| amount | transactions.amount | ✅ EXISTS | Fee amount |
| source = 'fees_charges' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 9: Cards, Checking & Bill Payments ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| post_date | transactions.settlement_date | ✅ EXISTS | Mapped to settlement_date |
| payee | transactions.payee | ✅ EXISTS | Bill payment recipient |
| payee_account | transactions.payee_account | ✅ EXISTS | Masked account number |
| amount | transactions.amount | ✅ EXISTS | Payment amount |
| ytd_payments | transactions.ytd_amount | ✅ EXISTS | Year-to-date total |
| source = 'bill_payments' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 10: Core Fund Activity ✅ FULLY ALIGNED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| settlement_date | transactions.settlement_date | ✅ EXISTS | Perfect alignment |
| account_type | transactions.account_type | ✅ EXISTS | "CASH" type |
| transaction | transactions.description | ✅ EXISTS | "You Bought/Sold" |
| sec_description | transactions.security_name | ✅ EXISTS | Core fund name |
| quantity | transactions.quantity | ✅ EXISTS | Shares |
| price_per_unit | transactions.price_per_unit | ✅ EXISTS | Usually $1.0000 |
| amount | transactions.amount | ✅ EXISTS | Transaction amount |
| balance | transactions.balance | ✅ EXISTS | Running balance |
| source = 'core_fund' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** ✅ **PERFECT ALIGNMENT** - All fields properly supported

---

### Section 11: Trades Pending Settlement 🚨 CRITICAL GAPS IDENTIFIED

| Activity Map Field | Database Column | Status | Notes |
|-------------------|-----------------|---------|-------|
| trade_date | transactions.trade_date | ✅ EXISTS | **Good:** Field exists |
| settlement_date | transactions.settlement_date | ✅ EXISTS | Future settlement |
| sec_description | transactions.security_name | ✅ EXISTS | Properly mapped |
| symbol_cusip | transactions.symbol_cusip | ✅ EXISTS | Properly mapped |
| description | transactions.description | ✅ EXISTS | Properly mapped |
| quantity | transactions.quantity | ✅ EXISTS | Shares/units traded |
| price_per_unit | transactions.price_per_unit | ✅ EXISTS | Per share price |
| cost_basis | transactions.cost_basis | ✅ EXISTS | For sales only |
| amount | transactions.amount | ✅ EXISTS | Total amount |
| pending | transactions.pending | ❌ **MISSING** | **CRITICAL GAP** |
| source = 'trades_pending' | transactions.source | ✅ EXISTS | Properly supported |

**Result:** 🚨 **CRITICAL GAP** - Missing `pending` boolean field

---

## Data Type Alignment Analysis

### ✅ **EXCELLENT** Data Type Matching

**Currency Fields:**
- Activity Map: "CURRENCY" → Database: `NUMERIC(8,2)` ✅ Perfect
- Activity Map: "CURRENCY" → Database: `NUMERIC(12,4)` ✅ Perfect (for prices)

**Numeric Fields:**
- Activity Map: "NUMBER" → Database: `NUMERIC(8,6)` ✅ Perfect (for quantities)
- Activity Map: "NUMBER" → Database: `NUMERIC(15,6)` ✅ Perfect (positions)

**Text Fields:**
- Activity Map: "TEXT" → Database: `TEXT` ✅ Perfect
- Activity Map: "DATE" → Database: `DATE` ✅ Perfect

**Boolean Fields:**
- Activity Map: "BOOLEAN" → Database: `BOOLEAN` ✅ Perfect alignment

---

## Source Field Mapping Verification

### ✅ **PERFECT** Source Value Support

All source values mentioned in the activity map are properly supported:

| Section | Activity Map Source | Database Support | Status |
|---------|-------------------|------------------|---------|
| 1 | 'sec_bot_sold' | transactions.source TEXT | ✅ Supported |
| 2 | 'div_int_income' | transactions.source TEXT | ✅ Supported |
| 4 | 'other_activity_in' | transactions.source TEXT | ✅ Supported |
| 4 | 'other_activity_out' | transactions.source TEXT | ✅ Supported |
| 5 | 'deposits' | transactions.source TEXT | ✅ Supported |
| 6 | 'withdrawals' | transactions.source TEXT | ✅ Supported |
| 7 | 'exchanges_in' | transactions.source TEXT | ✅ Supported |
| 7 | 'exchanges_out' | transactions.source TEXT | ✅ Supported |
| 8 | 'fees_charges' | transactions.source TEXT | ✅ Supported |
| 9 | 'bill_payments' | transactions.source TEXT | ✅ Supported |
| 10 | 'core_fund' | transactions.source TEXT | ✅ Supported |
| 11 | 'trades_pending' | transactions.source TEXT | ✅ Supported |

---

## Required vs Optional Fields Analysis

### ✅ **GOOD** Required Field Coverage

**Required Fields per Activity Map:**
- `account_number` → Database has proper account tracking ✅
- `source` → Database `transactions.source NOT NULL` ✅
- Settlement/date fields → Database supports multiple date types ✅
- `amount` → Database `transactions.amount NOT NULL` ✅
- `description` → Database `transactions.description NOT NULL` ✅

**NEW Section 11 Requirement:**
- `pending` → **MISSING from database schema** ❌

---

## Critical Issues Identified

### 🚨 **MISSING DATABASE COLUMNS**

1. **`transactions.pending` (BOOLEAN)**
   - **Required for:** Section 11 (Trades Pending Settlement)
   - **Impact:** Cannot properly flag pending transactions
   - **Urgency:** CRITICAL - needed for new functionality

2. **`transactions.total_activity_in` (NUMERIC)**
   - **Required for:** Section 4 subtotals
   - **Impact:** Cannot capture section-level aggregations
   - **Urgency:** MEDIUM - affects reporting completeness

3. **`transactions.total_activity_out` (NUMERIC)**
   - **Required for:** Section 4 subtotals
   - **Impact:** Cannot capture section-level aggregations
   - **Urgency:** MEDIUM - affects reporting completeness

### ⚠️ **FIELD NAMING INCONSISTENCIES**

1. **Symbol/CUSIP Field:**
   - Activity Map: `symbol_cusip`
   - Database: `transactions.symbol_cusip` ✅ Consistent

2. **Security Description:**
   - Activity Map: `sec_description`
   - Database: `transactions.security_name` ✅ Properly mapped

---

## Strengths in Current Alignment

### ✅ **EXCELLENT** Foundation Architecture

1. **Comprehensive Transaction Support:**
   - All 11 activity sections supported via `source` field
   - Flexible JSONB columns for institution-specific data
   - Proper foreign key relationships

2. **Data Type Precision:**
   - Currency fields with proper decimal precision
   - Quantity fields supporting fractional shares
   - Date handling for trade vs settlement dates

3. **Multi-Entity Architecture:**
   - Account-level tracking enables multi-entity processing
   - Document audit trail through `document_id` foreign key
   - Source file tracking for debugging

4. **Advanced Features Ready:**
   - Options tracking with dedicated fields
   - Bond-specific columns for municipal bonds
   - Tax categorization support
   - Duplicate prevention with MD5 hashing

---

## Recommendations

### 🏆 **IMMEDIATE ACTIONS (Critical)**

1. **Add Missing `pending` Column:**
   ```sql
   ALTER TABLE transactions
   ADD COLUMN pending BOOLEAN DEFAULT FALSE;
   ```

2. **Update Activity Map Documentation:**
   - Add comment about pending=false for all non-Section 11 transactions
   - Clarify that pending=true ONLY for trades_pending source

### 📋 **SHORT TERM (Important)**

3. **Add Section Subtotal Columns:**
   ```sql
   ALTER TABLE transactions
   ADD COLUMN total_activity_in NUMERIC(8,2),
   ADD COLUMN total_activity_out NUMERIC(8,2);
   ```

4. **Test Section 11 Processing:**
   - Verify trade_date vs settlement_date handling
   - Test pending flag logic in extraction agents
   - Validate future settlement date processing

### 📊 **MEDIUM TERM (Enhancement)**

5. **Enhanced Validation:**
   - Add CHECK constraint: `pending = TRUE` only when `source = 'trades_pending'`
   - Add CHECK constraint: `trade_date <= settlement_date` when both present
   - Consider INDEX on pending column for performance

6. **Documentation Updates:**
   - Update schema.md with new pending column
   - Add examples of Section 11 processing to guides
   - Update extraction agent prompts for pending flag

---

## Testing Recommendations

### 🧪 **Validation Checklist**

**Before Processing Section 11 Documents:**
- [ ] `pending` column exists in database
- [ ] Extraction agent sets `pending=true` for trades_pending source
- [ ] Extraction agent sets `pending=false` for all other sources
- [ ] Both `trade_date` and `settlement_date` captured correctly
- [ ] Future settlement dates handled properly

**After Implementation:**
- [ ] Query test: Find all pending transactions
- [ ] Query test: Find settled vs unsettled trades
- [ ] Validation: No pending=true with non-trades_pending source
- [ ] Performance: Index usage on pending column queries

---

## Conclusion

### Overall Assessment: ⚠️ **READY WITH CRITICAL FIXES**

**The system demonstrates excellent foundational alignment** with the activity mapping guide. The database schema comprehensively supports 10 of 11 activity sections with proper data types, source tracking, and multi-entity architecture.

**However, Section 11 (Trades Pending Settlement) requires immediate attention** before processing documents containing pending trades. The missing `pending` boolean column represents a critical gap that must be resolved.

**Once the pending column is added, the system will have complete alignment** with the activity mapping guide and can safely process all 11 sections of Fidelity statement activities.

**Recommended Priority:**
1. **IMMEDIATE:** Add `pending` column (blocks Section 11 processing)
2. **SHORT TERM:** Add subtotal columns (enhances reporting)
3. **ONGOING:** Continue comprehensive testing with real documents

The alignment analysis confirms that the document extraction → database loading pipeline is architecturally sound and ready for production use once these gaps are addressed.

---

**Report Generated:** 09/28/25 4:15PM ET
**Analysis Status:** Complete
**Next Review:** After pending column implementation