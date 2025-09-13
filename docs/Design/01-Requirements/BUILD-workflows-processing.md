# BUILD: Document Processing & Loading Implementation Guide

**Created:** 09/12/25 8:15PM ET  
**Updated:** 09/12/25 8:54PM ET - Removed validation step (these are official docs, already validated by institutions)
**Purpose:** Complete technical specification for Claude-assisted document processing and database loading  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement Claude-side document processing pipeline that extracts financial data from PDFs/CSVs and loads into database  
**Prerequisites:** Claude Code environment, PDF parsing capability, database schema deployed, file system access  
**Key Decisions Made:** Manual Claude processing (not automated), simple ask-or-flag decision making, transaction-safe loading  
**Output Expected:** Processed documents in database with extracted transactions linked to source PDFs

## Quick Reference

**Core Workflows:**
- **Workflow 1:** Document Intake & Classification (detecting document type and structure)
- **Workflow 2:** Data Extraction (parsing transactions with ask-or-flag logic)
- **Workflow 3:** Database Loading (transaction-safe insertion with duplicate detection)
- **Workflow 4:** File Management (moving through processing states)
- **Workflow 5:** Error Recovery (handling failures and retries)

**Key Components:** DocumentProcessor, PDFExtractor, CSVParser, DatabaseLoader, FileManager

**Processing States:** inbox → processing → processed → archived (or → failed)

## System Architecture

### Processing Pipeline Overview
```
┌────────────────────────────────────────────────────┐
│           Document Processing Pipeline             │
├────────────────────────────────────────────────────┤
│                                                    │
│  /documents/inbox/                                 │
│       ↓                                            │
│  1. DOCUMENT DISCOVERY                             │
│     • List new files                               │
│     • Calculate MD5 hash                           │
│     • Check for duplicates                         │
│       ↓                                            │
│  2. CLASSIFICATION                                 │
│     • Detect document type                         │
│     • Extract metadata                             │
│     • Identify account/entity                      │
│       ↓                                            │
│  3. EXTRACTION                                     │
│     • Parse PDF/CSV content                        │
│     • Extract transactions                         │
│     • Apply tax categories (FSIXX, SPAXX, etc.)   │
│     • Flag anything unclear                        │
│       ↓                                            │
│  4. DATABASE LOADING                               │
│     • Begin transaction                            │
│     • Insert documents record                      │
│     • Insert transactions                          │
│     • Commit or rollback                           │
│       ↓                                            │
│  /documents/processed/                             │
│                                                    │
└────────────────────────────────────────────────────┘
```

### File System Structure
```
/documents/
├── inbox/              # New documents to process
├── processing/         # Temporarily during processing
├── processed/          # Successfully processed
│   ├── 2024/
│   │   ├── statements/
│   │   ├── tax-forms/
│   │   └── other/
├── failed/            # Failed processing
└── archived/          # Old documents (manual cleanup)
```

## Workflow 1: Document Intake & Classification

### File Discovery Process
```python
# Pseudocode for document discovery
def discover_documents():
    files = list_files("/documents/inbox/")
    
    for file in files:
        # Calculate MD5 hash for duplicate detection (fast and sufficient)
        file_hash = calculate_md5(file.path)
        
        # Check if already processed (single indexed query)
        existing = db.query(
            "SELECT id FROM documents WHERE file_hash = ?", 
            file_hash
        )
        
        if existing:
            log("Duplicate detected: " + file.name)
            move_to("/documents/failed/duplicates/", file)
            continue
            
        # Move to processing folder
        move_to("/documents/processing/", file)
        
        # Begin classification
        classify_document(file)
```

### Hierarchical Document Classification
```python
def classify_document(pdf_file):
    """
    Hierarchical classification - identify context before content
    Classification order: Entity → Institution → Account → Document Type
    """
    
    # Step 1: Claude reads first 1-2 pages (sufficient for classification)
    # Using multimodal capability to see logos, formatting, structure
    first_page = claude.read_pdf(pdf_file, pages=[1])
    
    # Initial classification attempt from page 1
    classification = {
        # LEVEL 1: Entity identification (WHO owns this?)
        "entity_id": None,
        "entity_name": detect_entity_name(first_page),  # "Milton Preschool Inc"
        
        # LEVEL 2: Institution identification (WHERE is it from?)
        "institution_id": None,
        "institution_name": detect_institution(first_page),  # "Fidelity"
        
        # LEVEL 3: Account identification (WHICH account?)
        "account_number": detect_account_number(first_page),  # "Z40-394067"
        "account_type": detect_account_type(first_page),  # "brokerage"
        
        # LEVEL 4: Document type (WHAT is it?)
        "document_type": detect_document_type(first_page),  # "statement"
        "document_subtype": detect_subtype(first_page),  # "monthly_statement"
        
        # LEVEL 5: Period covered
        "period_start": extract_period_start(first_page),
        "period_end": extract_period_end(first_page),
        
        # Metadata
        "file_name": pdf_file.name,
        "file_hash": pdf_file.hash,
        "file_size": pdf_file.size,
        "pages_total": pdf_file.page_count,
        "classification_complete": False
    }
    
    # If critical fields missing from page 1, read page 2
    if not all([classification["entity_name"], 
                classification["institution_name"], 
                classification["account_number"]]):
        second_page = claude.read_pdf(pdf_file, pages=[2])
        update_classification(classification, second_page)
    
    # Match against known entities/institutions/accounts
    classification = match_to_database(classification)
    
    # Check if we have everything we need
    if not all([classification.get("entity_id"), 
                classification.get("institution_id"), 
                classification.get("account_number")]):
        classification["needs_review"] = True
        classification["review_reason"] = "Missing entity, institution, or account"
    
    classification["classification_complete"] = True
    
    return classification

def match_to_database(classification):
    """
    Match detected values to existing database records
    """
    
    # Match entity name to entity_id
    if classification["entity_name"]:
        entity = db.query("""
            SELECT id, name, entity_type 
            FROM entities 
            WHERE name ILIKE %s OR alternate_names @> %s
        """, classification["entity_name"], [classification["entity_name"]])
        
        if entity:
            classification["entity_id"] = entity.id
        else:
            classification["needs_review"] = True
            classification["review_reason"] = "Unknown entity"
    
    # Match institution
    if classification["institution_name"]:
        institution = db.query("""
            SELECT id, name 
            FROM institutions 
            WHERE name ILIKE %s
        """, classification["institution_name"])
        
        if institution:
            classification["institution_id"] = institution.id
    
    # Match account (must match entity + institution + account number)
    if all([classification["entity_id"], 
            classification["institution_id"], 
            classification["account_number"]]):
        account = db.query("""
            SELECT id, account_name, account_type 
            FROM accounts 
            WHERE entity_id = %s 
            AND institution_id = %s 
            AND account_number_masked = mask_account(%s)
        """, classification["entity_id"], 
             classification["institution_id"],
             classification["account_number"])
        
        if account:
            classification["account_id"] = account.id
        else:
            classification["needs_review"] = True
            classification["review_reason"] = "Unknown account"
    
    return classification
```

### Entity and Institution Detection Patterns
```python
# Entity detection - look for account holder names
ENTITY_PATTERNS = {
    "Milton Preschool Inc": ["MILTON PRESCHOOL INC", "Milton Preschool, Inc."],
    "Entity A Corp": ["ENTITY A CORP", "Entity A Corporation"],
    "Personal": ["RICHARD KERNAN", "JANE KERNAN", "KERNAN FAMILY"],
}

# Institution detection - look for logos, headers, unique formatting
INSTITUTION_PATTERNS = {
    "Fidelity": {
        "text_markers": ["Fidelity Investments", "Fidelity Brokerage Services"],
        "account_format": r"[A-Z]\d{2}-\d{6}",  # Z40-394067
        "visual_cues": "Green header, pyramid logo"
    },
    "Bank of America": {
        "text_markers": ["Bank of America", "BofA"],
        "account_format": r"\d{4} \d{4} \d{4}",  # 1234 5678 9012
        "visual_cues": "Red and blue flag logo"
    },
    "Charles Schwab": {
        "text_markers": ["Charles Schwab", "Schwab Bank"],
        "account_format": r"\d{4}-\d{4}",  # 1234-5678
        "visual_cues": "Blue text, modern layout"
    }
}

# Document type detection patterns
DOCUMENT_PATTERNS = {
    "statement": {
        "markers": ["Statement Period", "Account Summary", "Transaction Details"],
        "regex": r"Statement Period:\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})"
    },
    "1099-DIV": {
        "markers": ["Form 1099-DIV", "Dividends and Distributions"],
        "regex": r"Box 1a.*?\$([0-9,]+\.\d{2})"
    },
    "1099-INT": {
        "markers": ["Form 1099-INT", "Interest Income"],
        "regex": r"Box 1.*?\$([0-9,]+\.\d{2})"
    },
    "1099-B": {
        "markers": ["Form 1099-B", "Proceeds From Broker"],
        "regex": r"Proceeds.*?\$([0-9,]+\.\d{2})"
    }
}
```

## Workflow 2: Data Extraction & Validation

### Simple Transaction Extraction
```python
def extract_transactions(pdf_file, classification):
    """
    Extract all transactions from the document
    No coordinate tracking needed - just get the data
    """
    
    # Read the full document now (we only read 1-2 pages during classification)
    full_document = claude.read_pdf(pdf_file, all_pages=True)
    
    extracted_data = {
        "document_id": generate_uuid(),
        "entity_id": classification["entity_id"],
        "institution_id": classification["institution_id"],
        "account_id": classification["account_id"],
        "transactions": [],
        "summary": {},
        "extraction_metadata": {}
    }
    
    # Extract based on document type
    if classification["document_type"] == "statement":
        transactions = extract_statement_transactions(full_document)
    elif classification["document_type"] in ["1099-DIV", "1099-INT"]:
        transactions = extract_tax_form_data(full_document)
    else:
        transactions = extract_generic_transactions(full_document)
    
    # Add entity/institution/account context to each transaction
    for transaction in transactions:
        transaction["entity_id"] = classification["entity_id"]
        transaction["institution_id"] = classification["institution_id"]
        transaction["account_id"] = classification["account_id"]
        transaction["source_document_id"] = extracted_data["document_id"]
        
    extracted_data["transactions"] = transactions
    extracted_data["transaction_count"] = len(transactions)
    
    return extracted_data
```

### Transaction Parsing
```python
def parse_transaction(text_line, institution_type):
    """
    Parse a transaction line from PDF text - simple extraction
    Example: "01/31/24  FSIXX DIVIDEND  CASH DIV     $4,327.68"
    """
    
    # Institution-specific patterns for better accuracy
    if institution_type == "fidelity":
        pattern = r"(\d{2}/\d{2}/\d{2})\s+(.*?)\s+\$([0-9,]+\.\d{2})"
    elif institution_type == "bofa":
        pattern = r"(\d{2}/\d{2})\s+(.*?)\s+([0-9,]+\.\d{2})"
    elif institution_type == "schwab":
        pattern = r"(\d{2}/\d{2}/\d{4})\s+(.*?)\s+\$([0-9,]+\.\d{2})"
    else:
        # Generic pattern
        pattern = r"(\d{1,2}/\d{1,2}/\d{2,4})\s+(.*?)\s+\$?([0-9,]+\.\d{2})"
    
    match = re.match(pattern, text_line)
    if match:
        transaction = {
            "transaction_date": parse_date(match.group(1)),
            "description": match.group(2).strip(),
            "amount": parse_amount(match.group(3)),
            "transaction_type": classify_transaction_type(match.group(2)),
            "raw_text": text_line  # Keep original for reference
        }
        
        # Extract additional fields based on transaction type
        if "DIVIDEND" in transaction["description"].upper():
            transaction["security_symbol"] = extract_symbol(transaction["description"])
            transaction["transaction_type"] = "dividend"
        elif "INTEREST" in transaction["description"].upper():
            transaction["transaction_type"] = "interest"
        elif "BUY" in transaction["description"].upper() or "BOUGHT" in transaction["description"].upper():
            transaction["transaction_type"] = "buy"
            transaction["security_symbol"] = extract_symbol(transaction["description"])
        elif "SELL" in transaction["description"].upper() or "SOLD" in transaction["description"].upper():
            transaction["transaction_type"] = "sell"
            transaction["security_symbol"] = extract_symbol(transaction["description"])
            
        return transaction
    
    return None  # Could not parse
```

### Claude's Decision Making (No Confidence Scores Needed)
```python
def process_transaction(transaction_text):
    """
    Claude processes each transaction with simple decision logic
    No confidence scores - just process, ask, or flag
    """
    
    # Try to parse the transaction
    parsed = parse_transaction(transaction_text)
    
    if not parsed:
        # Can't parse it at all
        return {
            "needs_review": True,
            "review_reason": "Could not parse transaction format",
            "raw_text": transaction_text
        }
    
    # Check if we have all required fields
    if not parsed.get("date"):
        return {
            **parsed,
            "needs_review": True,
            "review_reason": "Missing transaction date"
        }
    
    if not parsed.get("amount"):
        return {
            **parsed,
            "needs_review": True,
            "review_reason": "Could not determine amount"
        }
    
    # Check if entity/account mapping is clear
    if not parsed.get("account_id"):
        # If processing single document, ask user
        if is_interactive_mode():
            account = ask_user(f"Which account is this for? {parsed['description']}")
            parsed["account_id"] = account
        else:
            # In batch mode, flag for review
            parsed["needs_review"] = True
            parsed["review_reason"] = "Could not determine account"
    
    # Transaction looks good
    return parsed

def ask_user(question):
    """
    Simple user interaction when Claude needs help
    """
    print(f"\n❓ {question}")
    return input("> ")
```

### Tax Classification Logic
```python
def apply_tax_classification(transaction, account_info):
    """
    Apply tax rules based on transaction type and security
    """
    
    tax_data = {
        "federal_taxable": True,
        "state_taxable": True,
        "tax_category": "ordinary_income",
        "tax_details": {}
    }
    
    # Money market funds (FSIXX, SPAXX)
    if transaction["security"] in ["FSIXX", "SPAXX"]:
        tax_data["tax_category"] = "ordinary_dividend"
        
        # FSIXX - ~97% Georgia exempt
        if transaction["security"] == "FSIXX":
            tax_data["tax_details"]["ga_exempt_pct"] = 0.97
            
        # SPAXX - ~55% Georgia exempt  
        elif transaction["security"] == "SPAXX":
            tax_data["tax_details"]["ga_exempt_pct"] = 0.55
    
    # Municipal bonds
    elif "MUNI" in transaction["description"] or "MUNICIPAL" in transaction["description"]:
        tax_data["federal_taxable"] = False
        tax_data["tax_category"] = "municipal_interest"
        
        # Detect issuer state
        issuer_state = extract_issuer_state(transaction["description"])
        tax_data["tax_details"]["issuer_state"] = issuer_state
        
        # Georgia bonds are state tax exempt for GA residents
        if issuer_state == "GA":
            tax_data["state_taxable"] = False
        else:
            tax_data["state_taxable"] = True
    
    # Corporate exemption handling
    if account_info["entity_type"] == "S-Corp" and account_info["tax_exempt"]:
        tax_data["tax_details"]["corporate_exemption"] = True
        tax_data["tax_details"]["reports_to_irs"] = False
    
    return tax_data
```

## Workflow 3: Database Loading

### Transaction-Safe Database Loading
```python
def load_to_database(classification, extraction_result):
    """
    Load extracted data into database with full transaction safety
    """
    
    try:
        # Begin database transaction
        db.begin_transaction()
        
        # 1. Insert document record
        document_id = insert_document(classification, extraction_result)
        
        # 2. Insert transactions
        transaction_ids = insert_transactions(document_id, extraction_result["transactions"])
        
        # 3. Store coordinate data for highlighting
        store_coordinates(document_id, extraction_result["coordinates"])
        
        # 4. Update account balances if needed
        update_account_balances(extraction_result)
        
        # 5. Create data quality flags if needed
        create_quality_flags(document_id, extraction_result)
        
        # Commit transaction
        db.commit()
        
        return {
            "success": True,
            "document_id": document_id,
            "transaction_count": len(transaction_ids)
        }
        
    except Exception as e:
        # Rollback on any error
        db.rollback()
        
        return {
            "success": False,
            "error": str(e),
            "recovery_action": determine_recovery_action(e)
        }
```

### Document Insertion
```sql
-- Insert document with all metadata
INSERT INTO documents (
    id,
    entity_id,
    institution_id,
    document_type,
    document_subtype,
    file_name,
    file_path,
    file_hash,
    file_size,
    period_start,
    period_end,
    extraction_notes,
    raw_extraction,
    needs_review,
    review_priority,
    processed_at,
    processed_by
) VALUES (
    $1,  -- UUID
    $2,  -- entity_id from classification
    $3,  -- institution_id from classification
    $4,  -- 'statement', '1099', etc.
    $5,  -- '1099-DIV', '1099-INT', etc.
    $6,  -- Original filename
    $7,  -- Path in processed folder
    $8,  -- MD5 hash
    $9,  -- File size in bytes
    $10, -- Period start date
    $11, -- Period end date
    $12, -- JSON notes about extraction
    $13, -- Complete extraction result as JSONB
    $14, -- Boolean flag for needs_review
    $15, -- Review priority ('high', 'medium', 'low')
    NOW(),
    'Claude Code'
)
RETURNING id;
```

### Transaction Insertion (Simple)
```sql
-- Insert transactions with link to source document
INSERT INTO transactions (
    id,
    entity_id,
    institution_id,
    account_id,
    source_document_id,
    transaction_date,
    transaction_type,
    description,
    amount,
    security_symbol,
    tax_category,
    federal_taxable,
    state_taxable,
    needs_review,
    raw_text
) VALUES (
    $1,  -- UUID
    $2,  -- entity_id from classification
    $3,  -- institution_id from classification
    $4,  -- account_id from classification
    $5,  -- document_id for "View Source" feature
    $6,  -- transaction_date
    $7,  -- 'dividend', 'interest', 'buy', 'sell', etc.
    $8,  -- Full description from statement
    $9,  -- Amount as NUMERIC
    $10, -- Security symbol if applicable (FSIXX, GOOG, etc.)
    $11, -- Tax category
    $12, -- Federal taxable boolean
    $13, -- State taxable boolean
    $14, -- Needs review flag
    $15  -- Original text line for debugging
);

-- Simple query to view transactions with filters
SELECT 
    t.*,
    e.name as entity_name,
    i.name as institution_name,
    a.account_name,
    d.file_path as source_document_path
FROM transactions t
JOIN entities e ON t.entity_id = e.id
JOIN institutions i ON t.institution_id = i.id
JOIN accounts a ON t.account_id = a.id
JOIN documents d ON t.source_document_id = d.id
WHERE 
    ($entity_id IS NULL OR t.entity_id = $entity_id)
    AND ($date_start IS NULL OR t.transaction_date >= $date_start)
    AND ($date_end IS NULL OR t.transaction_date <= $date_end)
    AND ($institution_id IS NULL OR t.institution_id = $institution_id)
ORDER BY t.transaction_date DESC;
```

### Duplicate Detection Strategy
```python
def calculate_md5(file_path):
    """
    Calculate MD5 hash of file - fast and sufficient for duplicate detection
    """
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_for_duplicates(file_hash, period_start, period_end, account_id):
    """
    Multi-level duplicate detection
    """
    
    # Level 1: Exact file hash match (MD5 - indexed for fast lookup)
    exact_match = db.query("""
        SELECT id, file_name, processed_at 
        FROM documents 
        WHERE file_hash = %s
    """, file_hash)
    
    if exact_match:
        return {
            "is_duplicate": True,
            "duplicate_type": "exact_file",
            "existing_document": exact_match
        }
    
    # Level 2: Same period and account
    period_match = db.query("""
        SELECT id, file_name, processed_at
        FROM documents d
        JOIN document_accounts da ON d.id = da.document_id
        WHERE da.account_id = %s
        AND d.period_start = %s
        AND d.period_end = %s
        AND d.document_type = 'statement'
    """, account_id, period_start, period_end)
    
    if period_match:
        return {
            "is_duplicate": True,
            "duplicate_type": "same_period",
            "existing_document": period_match,
            "action": "check_if_amendment"
        }
    
    return {"is_duplicate": False}
```

### Amendment Handling
```python
def handle_amendment(new_document, existing_document):
    """
    Handle corrected/amended documents
    """
    
    # Check for amendment markers
    is_amendment = any([
        "AMENDED" in new_document["file_name"].upper(),
        "CORRECTED" in new_document["file_name"].upper(),
        "REVISED" in new_document["file_name"].upper()
    ])
    
    if is_amendment:
        # Link to original document
        db.execute("""
            UPDATE documents 
            SET amends_document_id = %s,
                amendment_notes = %s
            WHERE id = %s
        """, existing_document["id"], "Amended version available", new_document["id"])
        
        # Mark original as superseded
        db.execute("""
            UPDATE documents
            SET is_superseded = true,
                superseded_by = %s
            WHERE id = %s
        """, new_document["id"], existing_document["id"])
        
        return {
            "action": "amendment_linked",
            "original_id": existing_document["id"],
            "amended_id": new_document["id"]
        }
```

## Workflow 4: File Management

### File State Transitions
```python
def manage_file_states(file, processing_result):
    """
    Move files through processing states
    """
    
    source_path = f"/documents/processing/{file.name}"
    
    if processing_result["success"]:
        # Organize by year and type
        year = processing_result["period_end"].year
        doc_type = processing_result["document_type"]
        
        # Create destination path
        dest_folder = f"/documents/processed/{year}/{doc_type}/"
        ensure_directory_exists(dest_folder)
        
        # Add timestamp to filename to prevent overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = file.name.rsplit('.', 1)[0]
        extension = file.name.rsplit('.', 1)[1]
        dest_name = f"{base_name}_{timestamp}.{extension}"
        dest_path = f"{dest_folder}{dest_name}"
        
        # Move file
        move_file(source_path, dest_path)
        
        # Update database with final path
        db.execute("""
            UPDATE documents 
            SET file_path = %s 
            WHERE id = %s
        """, dest_path, processing_result["document_id"])
        
    else:
        # Move to failed folder with error info
        error_folder = f"/documents/failed/{datetime.now().strftime('%Y%m%d')}/"
        ensure_directory_exists(error_folder)
        
        error_path = f"{error_folder}{file.name}"
        move_file(source_path, error_path)
        
        # Write error log
        error_log = f"{error_path}.error.json"
        write_json(error_log, {
            "file": file.name,
            "error": processing_result["error"],
            "timestamp": datetime.now().isoformat(),
            "recovery_action": processing_result.get("recovery_action")
        })
```

### Cleanup and Archival
```python
def cleanup_old_documents():
    """
    Archive old processed documents
    """
    
    cutoff_date = datetime.now() - timedelta(days=365)
    
    old_documents = db.query("""
        SELECT file_path 
        FROM documents 
        WHERE processed_at < %s
        AND archived = false
    """, cutoff_date)
    
    for doc in old_documents:
        source = doc["file_path"]
        archive_path = source.replace("/processed/", "/archived/")
        
        ensure_directory_exists(os.path.dirname(archive_path))
        move_file(source, archive_path)
        
        db.execute("""
            UPDATE documents 
            SET file_path = %s, archived = true 
            WHERE file_path = %s
        """, archive_path, source)
```

## Workflow 5: Error Recovery

### Error Classification and Recovery
```python
ERROR_RECOVERY_STRATEGIES = {
    "pdf_corrupted": {
        "retry": False,
        "action": "manual_review",
        "message": "PDF file is corrupted or password protected"
    },
    "duplicate_detected": {
        "retry": False,
        "action": "check_amendment",
        "message": "Document already processed, checking if amendment"
    },
    "extraction_failed": {
        "retry": True,
        "max_retries": 3,
        "action": "retry_with_different_parser",
        "message": "Extraction failed, will retry with alternative method"
    },
    "database_connection": {
        "retry": True,
        "max_retries": 5,
        "backoff": "exponential",
        "action": "wait_and_retry",
        "message": "Database connection failed, will retry"
    },
    "validation_failed": {
        "retry": False,
        "action": "flag_for_review",
        "message": "Data validation failed, needs manual review"
    }
}

def handle_processing_error(error, context):
    """
    Determine recovery strategy based on error type
    """
    
    error_type = classify_error(error)
    strategy = ERROR_RECOVERY_STRATEGIES.get(error_type, {
        "retry": False,
        "action": "manual_review",
        "message": "Unknown error, needs manual review"
    })
    
    if strategy["retry"]:
        if context["retry_count"] < strategy.get("max_retries", 3):
            # Calculate backoff
            if strategy.get("backoff") == "exponential":
                wait_time = 2 ** context["retry_count"]
            else:
                wait_time = 5  # Fixed 5 second wait
            
            time.sleep(wait_time)
            
            # Retry with incremented count
            return process_document(
                context["file"], 
                retry_count=context["retry_count"] + 1
            )
    
    # If not retrying, handle based on action
    return execute_recovery_action(strategy["action"], context)
```

### Manual Review Queue
```sql
-- Create manual review entry
INSERT INTO manual_review_queue (
    id,
    document_id,
    file_path,
    error_type,
    error_details,
    priority,
    status,
    created_at
) VALUES (
    gen_random_uuid(),
    $1,  -- document_id (may be NULL if processing failed early)
    $2,  -- file_path
    $3,  -- error_type
    $4,  -- error_details as JSONB
    $5,  -- priority ('high', 'medium', 'low')
    'pending',
    NOW()
);

-- Query for pending reviews
SELECT 
    q.*,
    d.file_name,
    d.document_type,
    d.extraction_confidence
FROM manual_review_queue q
LEFT JOIN documents d ON q.document_id = d.id
WHERE q.status = 'pending'
ORDER BY 
    CASE q.priority 
        WHEN 'high' THEN 1 
        WHEN 'medium' THEN 2 
        ELSE 3 
    END,
    q.created_at ASC;
```

## Implementation Guidelines

### View Source Document Feature
```python
def view_source_document(transaction_id):
    """
    Simple implementation to open the source PDF for a transaction
    """
    
    # Get the source document path
    result = db.query("""
        SELECT d.file_path, d.file_name
        FROM transactions t
        JOIN documents d ON t.source_document_id = d.id
        WHERE t.id = %s
    """, transaction_id)
    
    if result:
        file_path = result["file_path"]
        print(f"Opening source document: {result['file_name']}")
        
        # Open PDF in default viewer (Mac/Linux/Windows)
        import subprocess
        import platform
        
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', file_path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(file_path)
        else:                                   # Linux
            subprocess.call(('xdg-open', file_path))
    else:
        print("Source document not found")
```

### Claude Code Integration
```python
# Main processing command for Claude
def process_document_command(file_path):
    """
    Main entry point for Claude Code document processing
    Simplified flow without coordinate tracking
    """
    
    print(f"Processing document: {file_path}")
    
    # Step 1: Check for duplicates
    file_hash = calculate_md5(file_path)
    if is_duplicate(file_hash):
        print("❌ Duplicate document detected")
        return
    
    # Step 2: Classification (WHO, WHERE, WHICH, WHAT)
    print("Classifying document...")
    classification = classify_document(file_path)
    print(f"Entity: {classification['entity_name']}")
    print(f"Institution: {classification['institution_name']}")
    print(f"Account: {classification['account_number']}")
    print(f"Type: {classification['document_type']}")
    
    # Step 3: Extract transactions
    print("Extracting transactions...")
    extraction = extract_transactions(file_path, classification)
    print(f"Found {len(extraction['transactions'])} transactions")
    
    # Step 4: Apply tax rules
    for transaction in extraction['transactions']:
        apply_tax_classification(transaction)
    
    # Step 5: Handle any flagged items
    flagged = [t for t in extraction['transactions'] if t.get('needs_review')]
    if flagged:
        print(f"\n⚠️ {len(flagged)} transactions need review:")
        for t in flagged[:5]:  # Show first 5
            print(f"  {t.get('raw_text', 'Unknown')} - Reason: {t.get('review_reason')}")
        response = input("\nProceed anyway? (y/n): ")
        if response.lower() != 'y':
            return handle_user_rejection(file_path, extraction)
    
    # Step 6: Load to database
    print("Loading to database...")
    result = load_to_database(classification, extraction)
    
    if result["success"]:
        print(f"✅ Successfully processed!")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Loaded {result['transaction_count']} transactions")
        
        # Move file to processed folder
        move_to_processed(file_path, classification)
    else:
        print(f"❌ Processing failed: {result['error']}")
        move_to_failed(file_path)
    
    return result
```


### Performance Targets
- **Single PDF (< 20 pages):** Process in < 30 seconds
- **CSV file (any size):** Process in < 10 seconds
- **Database loading:** Complete transaction in < 5 seconds
- **Duplicate detection:** Check in < 1 second (MD5 hash)

### Testing Strategy
```python
# Test cases for document processing
def test_document_processing():
    test_cases = [
        {
            "name": "Standard monthly statement",
            "file": "test_data/fidelity_statement_202401.pdf",
            "expected_transactions": 15,
            "expected_needs_review": False
        },
        {
            "name": "1099-DIV with corporate exemption",
            "file": "test_data/1099_div_corporate.pdf",
            "expected_official_amount": 0.00,
            "expected_info_amount": 29515.27
        },
        {
            "name": "Duplicate document detection",
            "file": "test_data/duplicate_statement.pdf",
            "expected_result": "duplicate_detected"
        },
        {
            "name": "Amended document handling",
            "file": "test_data/amended_1099.pdf",
            "expected_link": "original_doc_id"
        }
    ]
    
    for test in test_cases:
        result = process_document(test["file"])
        assert_test_expectations(result, test)
```

## Acceptance Criteria

- [ ] **GIVEN** a PDF in inbox, **WHEN** processed, **THEN** transactions appear in database within 30 seconds
- [ ] **GIVEN** a duplicate file, **WHEN** processed, **THEN** system detects and prevents duplicate insertion
- [ ] **GIVEN** unclear transaction data, **WHEN** processing, **THEN** Claude asks user or flags for review
- [ ] **GIVEN** a transaction in UI, **WHEN** "View Source" clicked, **THEN** opens original PDF document
- [ ] **GIVEN** an amended document, **WHEN** processed, **THEN** links to original via amends_document_id
- [ ] **GIVEN** a processing failure, **WHEN** retried, **THEN** system attempts recovery based on error type
- [ ] **GIVEN** successful processing, **WHEN** complete, **THEN** file moves from inbox to processed folder

## Error Handling Matrix

| Error Type | Retry | Max Attempts | Recovery Action | User Notification |
|------------|-------|--------------|-----------------|-------------------|
| PDF Corrupted | No | - | Move to failed folder | "PDF cannot be read" |
| Duplicate File | No | - | Check if amendment | "Duplicate detected" |
| Network Error | Yes | 5 | Exponential backoff | "Retrying connection" |
| Database Error | Yes | 3 | Wait 5 seconds | "Database temporarily unavailable" |
| Extraction Failed | Yes | 2 | Try alternative parser | "Trying alternative method" |
| Validation Error | No | - | Flag for review | "Data validation failed" |
| Unknown Error | No | - | Manual review queue | "Needs manual review" |

---

*This implementation guide provides complete technical specifications for building the document processing pipeline. All workflows, algorithms, and data structures are defined for autonomous development.*