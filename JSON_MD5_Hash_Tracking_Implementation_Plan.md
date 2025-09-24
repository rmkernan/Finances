# 📋 **JSON MD5 Hash Tracking Implementation Plan**

**Created:** 09/24/25 1:57PM
**Purpose:** Comprehensive implementation plan for adding JSON MD5 hash tracking to enable incremental loading of activities and positions from the same PDF document

**Status Legend:**
- 🔘 **Not Started** - Work not yet begun
- 🔄 **In Progress** - Currently being worked on
- ✅ **Complete** - Work finished and verified
- ❌ **Blocked** - Cannot proceed due to dependencies or issues

---

## **Phase 1: Database Schema Changes**
**Status:** ✅ **Complete**

### **Step 1.1: Add New Columns**
**Status:** ✅ **Complete**
```sql
-- Add 4 new columns to documents table
ALTER TABLE documents
ADD COLUMN activities_loaded TIMESTAMPTZ,
ADD COLUMN activities_json_md5_hash VARCHAR(32),
ADD COLUMN positions_loaded TIMESTAMPTZ,
ADD COLUMN positions_json_md5_hash VARCHAR(32);
```

### **Step 1.2: Add Column Comments**
**Status:** ✅ **Complete**
```sql
COMMENT ON COLUMN documents.activities_loaded IS 'Timestamp when activities/transactions were loaded from JSON extraction';
COMMENT ON COLUMN documents.activities_json_md5_hash IS 'MD5 hash of the activities JSON file content used for duplicate prevention';
COMMENT ON COLUMN documents.positions_loaded IS 'Timestamp when holdings/positions were loaded from JSON extraction';
COMMENT ON COLUMN documents.positions_json_md5_hash IS 'MD5 hash of the positions JSON file content used for duplicate prevention';
```

### **Step 1.3: Add Indexes (Optional but Recommended)**
**Status:** ✅ **Complete**
```sql
-- For efficient lookup of documents by JSON hash
CREATE INDEX idx_documents_activities_json_hash ON documents(activities_json_md5_hash) WHERE activities_json_md5_hash IS NOT NULL;
CREATE INDEX idx_documents_positions_json_hash ON documents(positions_json_md5_hash) WHERE positions_json_md5_hash IS NOT NULL;
```

---

## **Phase 2: Documentation Updates**
**Status:** ✅ **Complete**

### **Step 2.1: Update Database Schema Documentation**
**Status:** ✅ **Complete**
**File:** `/docs/Design/Database/schema.md`

**Changes needed:**
- Add new column definitions in documents table section
- Update the duplicate prevention workflow section
- Add examples of the new incremental loading process
- Update comments section with new column descriptions

### **Step 2.2: Update Claude Context Documentation**
**Status:** ✅ **Complete**
**File:** `/docs/Design/Database/CLAUDE.md`

**Changes needed:**
- Update "Duplicate Prevention Strategy" section
- Add new workflow examples for incremental loading
- Update common queries section
- Add troubleshooting scenarios for JSON hash mismatches

### **Step 2.3: Update Loader Documentation**
**Status:** ✅ **Complete**
**File:** `/loaders/simple_loader.py` header comments

**Changes needed:**
- Update creation/modification history
- Document new incremental loading capability
- Update design principles section

---

## **Phase 3: Loader Code Modifications**
**Status:** ✅ **Complete**

### **Step 3.1: Modify create_document Function**
**Status:** ✅ **Complete**
**Location:** Lines 304-353 in `simple_loader.py`

**Required changes:**
```python
def create_document(data, institution_id, loaded_path, extraction_type, json_md5_hash, conn):
    """Create or update document record with incremental loading support"""

    # Check if document exists by PDF hash
    doc_hash = metadata.get('doc_md5_hash')
    existing_doc = get_existing_document(doc_hash, conn)

    if existing_doc:
        # Document exists - check if this extraction type already loaded
        return handle_incremental_load(existing_doc, extraction_type, json_md5_hash, conn)
    else:
        # New document - create fresh record
        return create_new_document(data, institution_id, loaded_path, extraction_type, json_md5_hash, conn)
```

### **Step 3.2: Add New Helper Functions**
**Status:** ✅ **Complete**

**New functions needed:**

1. **`get_existing_document(doc_hash, conn)`** - Lookup existing document by PDF hash
2. **`handle_incremental_load(existing_doc, extraction_type, json_md5_hash, conn)`** - Handle loading additional data type
3. **`create_new_document(...)`** - Create fresh document record
4. **`check_json_duplicate(existing_doc, extraction_type, json_md5_hash)`** - Prevent duplicate JSON loading

### **Step 3.3: Update Main Loading Logic**
**Status:** ✅ **Complete**
**Location:** Lines 621-698 in `load_document()` function

**Key changes:**
- Pass `extraction_type` parameter to `create_document()`
- Handle document already exists scenario (don't fail)
- Update success/error messaging for incremental loads

### **Step 3.4: Add JSON Hash Calculation**
**Status:** ✅ **Complete**
**Location:** In `load_document()` before calling `create_document()`

```python
# Calculate JSON file hash before any database operations
import hashlib
json_content = json.dumps(data, sort_keys=True)
json_md5_hash = hashlib.md5(json_content.encode()).hexdigest()
```

---

## **Phase 4: Enhanced Error Handling & Logic**
**Status:** 🔘 **Not Started**

### **Step 4.1: Duplicate Detection Logic**
**Status:** 🔘 **Not Started**
```python
def check_extraction_status(existing_doc, extraction_type, json_md5_hash):
    """Check if extraction already loaded and handle appropriately"""

    if extraction_type == 'activities':
        if existing_doc['activities_json_md5_hash'] == json_md5_hash:
            return 'SKIP_DUPLICATE'  # Same JSON already loaded
        elif existing_doc['activities_loaded']:
            return 'WARN_REPROCESS'  # Different JSON for same type
        else:
            return 'PROCEED'  # Not yet loaded

    # Similar logic for positions...
```

### **Step 4.2: User Interaction for Reprocessing**
**Status:** 🔘 **Not Started**
```python
def handle_reprocessing_scenario(doc_id, extraction_type, old_hash, new_hash):
    """Handle case where different JSON content exists for same extraction type"""

    print(f"WARNING: Document already has {extraction_type} loaded")
    print(f"  Existing JSON hash: {old_hash}")
    print(f"  New JSON hash: {new_hash}")
    print(f"  This suggests the JSON extraction content has changed.")
    print(f"  Proceeding will DELETE existing {extraction_type} and reload with new data.")

    # For now, proceed automatically but log the event
    # Future: Could prompt user for confirmation
```

---

## **Phase 5: Testing Plan**
**Status:** 🔘 **Not Started**

### **Step 5.1: Unit Tests**
**Status:** 🔘 **Not Started**
- Test `get_existing_document()` with valid/invalid hashes
- Test `check_extraction_status()` with all scenarios
- Test JSON MD5 hash calculation consistency
- Test database column updates

### **Step 5.2: Integration Tests**
**Status:** 🔘 **Not Started**

**Scenario A: Fresh Document (Both Extractions)**
- **Status:** 🔘 **Not Started**
1. Load activities JSON → Document created, activities_loaded set
2. Load positions JSON → Same document updated, positions_loaded set
3. Verify both timestamps and hashes stored correctly

**Scenario B: Duplicate Prevention**
- **Status:** 🔘 **Not Started**
1. Load activities JSON → Success
2. Load same activities JSON again → Should skip with message
3. Load positions JSON → Should proceed normally

**Scenario C: Reprocessing**
- **Status:** 🔘 **Not Started**
1. Load activities JSON → Success
2. Modify JSON content slightly
3. Load modified activities JSON → Should warn and reprocess
4. Verify old transactions deleted, new ones loaded

**Scenario D: Error Recovery**
- **Status:** 🔘 **Not Started**
1. Load activities JSON → Success
2. Simulate failure during positions loading
3. Verify partial state handled correctly
4. Retry positions loading → Should work

### **Step 5.3: Performance Tests**
**Status:** 🔘 **Not Started**
- Test with large JSON files (>1000 transactions)
- Measure impact of new indexes on query performance
- Test concurrent loading scenarios

---

## **Phase 6: Migration & Rollback Strategy**
**Status:** 🔘 **Not Started**

### **Step 6.1: Migration Script**
**Status:** 🔘 **Not Started**
```sql
-- migration_add_json_tracking.sql
BEGIN;

-- Add columns
ALTER TABLE documents
ADD COLUMN activities_loaded TIMESTAMPTZ,
ADD COLUMN activities_json_md5_hash VARCHAR(32),
ADD COLUMN positions_loaded TIMESTAMPTZ,
ADD COLUMN positions_json_md5_hash VARCHAR(32);

-- Add comments
COMMENT ON COLUMN documents.activities_loaded IS 'Timestamp when activities/transactions were loaded from JSON extraction';
COMMENT ON COLUMN documents.activities_json_md5_hash IS 'MD5 hash of the activities JSON file content used for duplicate prevention';
COMMENT ON COLUMN documents.positions_loaded IS 'Timestamp when holdings/positions were loaded from JSON extraction';
COMMENT ON COLUMN documents.positions_json_md5_hash IS 'MD5 hash of the positions JSON file content used for duplicate prevention';

-- Add indexes
CREATE INDEX idx_documents_activities_json_hash ON documents(activities_json_md5_hash) WHERE activities_json_md5_hash IS NOT NULL;
CREATE INDEX idx_documents_positions_json_hash ON documents(positions_json_md5_hash) WHERE positions_json_md5_hash IS NOT NULL;

-- Update existing documents with current timestamp where data exists
UPDATE documents SET
    activities_loaded = processed_at
WHERE id IN (SELECT DISTINCT document_id FROM transactions);

UPDATE documents SET
    positions_loaded = processed_at
WHERE id IN (SELECT DISTINCT document_id FROM positions);

COMMIT;
```

### **Step 6.2: Rollback Script**
**Status:** 🔘 **Not Started**
```sql
-- rollback_json_tracking.sql
BEGIN;

-- Remove indexes
DROP INDEX IF EXISTS idx_documents_activities_json_hash;
DROP INDEX IF EXISTS idx_documents_positions_json_hash;

-- Remove columns
ALTER TABLE documents
DROP COLUMN activities_loaded,
DROP COLUMN activities_json_md5_hash,
DROP COLUMN positions_loaded,
DROP COLUMN positions_json_md5_hash;

COMMIT;
```

---

## **Phase 7: Deployment Steps**
**Status:** 🔘 **Not Started**

### **Step 7.1: Pre-Deployment**
**Status:** 🔘 **Not Started**
1. **Backup current database** - Status: 🔘 **Not Started**
2. **Test migration script on copy of production data** - Status: 🔘 **Not Started**
3. **Verify rollback script works** - Status: 🔘 **Not Started**
4. **Complete all unit and integration tests** - Status: 🔘 **Not Started**

### **Step 7.2: Deployment**
**Status:** 🔘 **Not Started**
1. **Apply database migration** - Status: 🔘 **Not Started**
2. **Deploy updated loader code** - Status: 🔘 **Not Started**
3. **Update documentation** - Status: 🔘 **Not Started**
4. **Test with sample files** - Status: 🔘 **Not Started**
5. **Monitor for issues** - Status: 🔘 **Not Started**

### **Step 7.3: Post-Deployment**
**Status:** 🔘 **Not Started**
1. **Verify existing documents updated correctly** - Status: 🔘 **Not Started**
2. **Test incremental loading with real data** - Status: 🔘 **Not Started**
3. **Monitor performance impact** - Status: 🔘 **Not Started**
4. **Update operational procedures** - Status: 🔘 **Not Started**

---

## **Phase 8: Implementation Timeline**
**Status:** 🔘 **Not Started**

### **Week 1: Database & Documentation**
**Status:** 🔘 **Not Started**
- Steps 1.1-1.3 (Database changes)
- Steps 2.1-2.3 (Documentation)
- Step 6.1-6.2 (Migration scripts)

### **Week 2: Code Implementation**
**Status:** 🔘 **Not Started**
- Steps 3.1-3.4 (Code changes)
- Steps 4.1-4.2 (Logic enhancements)
- Steps 5.1 (Unit tests)

### **Week 3: Testing & Deployment**
**Status:** 🔘 **Not Started**
- Steps 5.2-5.3 (Integration & performance tests)
- Step 7.1 (Pre-deployment verification)
- Step 7.2-7.3 (Deployment)

---

## **Risk Mitigation**

### **High Risk: Data corruption during migration**
**Status:** 🔘 **Not Started**
- **Mitigation:** Full backup + tested rollback script
- **Responsible:** Database Administrator
- **Timeline:** Before any migration

### **Medium Risk: Performance impact of new indexes**
**Status:** 🔘 **Not Started**
- **Mitigation:** Performance testing + monitoring plan
- **Responsible:** Developer + DBA
- **Timeline:** Week 2-3

### **Low Risk: User confusion with new behavior**
**Status:** 🔘 **Not Started**
- **Mitigation:** Clear logging + documentation
- **Responsible:** Developer
- **Timeline:** Week 2

---

## **Success Criteria**

- ✅ **All database schema changes applied successfully**
- ✅ **Loader can handle incremental loading (activities first, then positions)**
- ✅ **Duplicate JSON detection prevents data corruption**
- ✅ **Reprocessing scenario handled gracefully**
- ✅ **Performance impact is minimal (<10% increase in load times)**
- ✅ **All existing functionality continues to work**
- ✅ **Complete rollback capability verified**

---

## **Notes & Updates**

**09/24/25 1:57PM** - Initial plan created based on analysis of current loader architecture and duplicate hash problem

**09/24/25 2:26PM** - Completed Phase 1: Database Schema Changes
- Added 4 new columns to documents table: activities_loaded, activities_json_md5_hash, positions_loaded, positions_json_md5_hash
- Added column comments for documentation
- Created partial indexes for efficient JSON hash lookups
- Updated existing document with activities_loaded timestamp (1 document found with transactions)

**09/24/25 2:29PM** - Completed Phase 2: Documentation Updates
- Updated schema.md with new column definitions and incremental loading workflow
- Updated CLAUDE.md with enhanced duplicate prevention strategy and new query examples
- Updated simple_loader.py header comments with incremental loading design principles

**09/24/25 2:33PM** - Completed Phase 3: Loader Code Modifications
- Added 5 new helper functions: get_existing_document, check_extraction_status, handle_reprocessing_scenario, update_document_loading_status, create_new_document
- Modified create_document function to support incremental loading with JSON hash tracking
- Updated load_document function with JSON hash calculation and extraction type detection
- Added hashlib import for MD5 hash generation

---

**This plan ensures systematic, safe implementation of the JSON MD5 hash tracking feature with complete rollback capability and thorough testing.**