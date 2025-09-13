# BUILD: Document Workflows Implementation Guide

**Created:** 09/12/25 5:53PM ET  
**Purpose:** Complete context for document viewing and search workflows - UI patterns, data flow, interactions  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement document viewing and search workflows with PDF integration and data extraction display  
**Prerequisites:** PDF.js or react-pdf, document database schema, file storage system, search indexing  
**Key Decisions Made:** Split-screen PDF + data view, confidence indicators, source highlighting, full-text search  
**Output Expected:** Document viewer with PDF rendering, extracted data display, search functionality, document management

## Quick Reference

**Core Workflows:**
- **Workflow 1:** Viewing Processed Documents (PDF + extracted data side-by-side)
- **Workflow 7:** Document Search & Discovery (full-text search with advanced filters)

**Key Components:** DocumentViewer, PDFRenderer, ExtractedDataPanel, DocumentSearch, DocumentList, ConfidenceIndicator

**Data Models:** Document has processing_status, confidence_score, extraction_data (JSONB), source highlighting coordinates

## Navigation Architecture (For Context)

### Context Hierarchy
```
Global (All Entities)
    ↓
Entity Context (e.g., Milton Preschool Inc)
    ↓  
Institution Context (e.g., Fidelity at Milton)
    ↓
Account Context (e.g., Brokerage ***4567)
```

### Document-Account Relationship Model
- Documents belong to one institution
- Documents can be linked to multiple accounts (e.g., consolidated statements)
- Transactions extracted from documents are attributed to specific accounts
- When viewing a document through an account context, only see transactions for that account
- "View Document" always shows the complete PDF

### URL Patterns for Documents
```
/documents                                          → Global document list
/entities/{entity}/documents                        → Entity's documents
/entities/{entity}/institutions/{institution}/documents → Institution's documents for entity
/entities/{entity}/accounts/{account}/documents     → Account's documents
/documents/{document_id}                           → Document viewer (full context)
/documents/{document_id}?account={account_id}      → Document viewer (account context)
```

---

## Workflow 1: Viewing Processed Documents

**User Story:** "I want to see what Claude extracted from my statements"

### Navigation Path
1. Select entity/account in left panel or navigate via URL
2. Click "Documents" tab in main content area
3. See list of processed documents with status indicators
4. Click document to view PDF + extracted data side-by-side

### Core Components

#### 1. Document List Component
```typescript
interface DocumentListProps {
  entityId?: string
  accountId?: string
  institutionId?: string
  filters?: DocumentFilters
}

interface Document {
  id: string
  file_name: string
  document_type: 'statement' | 'tax_form' | 'confirmation' | 'correspondence'
  period_start: string
  period_end: string
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  confidence_score: number
  created_at: string
  institution_name: string
  entity_name: string
  extraction_notes?: string
}
```

**Layout:**
- Table with sortable columns: Date | Type | Institution | Status | Confidence | Actions
- Status indicators: Processing (spinner), Completed (green check), Failed (red X), Pending (clock)
- Confidence indicators: >90% (green), 70-90% (yellow), <70% (red)
- Quick filters: Document type, Date range, Status, Institution

**Data Source:**
```sql
SELECT d.*, 
       i.name as institution_name,
       e.name as entity_name,
       COUNT(t.id) as transaction_count
FROM documents d
JOIN institutions i ON d.institution_id = i.id
LEFT JOIN entities e ON d.entity_id = e.id
LEFT JOIN transactions t ON d.id = t.source_document_id
WHERE ($entity_id IS NULL OR d.entity_id = $entity_id)
  AND ($account_id IS NULL OR EXISTS (
    SELECT 1 FROM transactions t2 WHERE t2.source_document_id = d.id AND t2.account_id = $account_id
  ))
  AND ($institution_id IS NULL OR d.institution_id = $institution_id)
  AND ($document_type IS NULL OR d.document_type = $document_type)
  AND d.created_at >= $date_start AND d.created_at <= $date_end
GROUP BY d.id, i.name, e.name
ORDER BY d.period_end DESC, d.created_at DESC
```

#### 2. Document Viewer Component
```typescript
interface DocumentViewerProps {
  documentId: string
  accountContext?: string // Filter to show only this account's data
}

interface ExtractedData {
  transactions: Transaction[]
  summary: {
    total_deposits: number
    total_withdrawals: number
    ending_balance: number
    period: { start: string; end: string }
  }
  confidence_scores: {
    overall: number
    transactions: number
    balances: number
  }
  processing_notes: string[]
  highlights: Array<{
    page: number
    coordinates: { x: number; y: number; width: number; height: number }
    data_reference: string // Links to specific transaction/data point
  }>
}
```

**Layout - Split Screen:**
```
┌─────────────────────────────┬─────────────────────────────┐
│                             │ Document: Jan 2024 Statement│
│                             ├─────────────────────────────┤
│                             │                             │
│        PDF VIEWER           │  📊 Extraction Summary      │
│                             │  Confidence: 94% ✅         │
│                             │                             │
│   [PDF content with         │  💰 Transactions (23)       │
│    highlighting on          │  ┌─────────────────────────┐ │
│    click from right]        │  │ Date  | Description  | $│ │
│                             │  │ 1/31  | FSIXX Div  +4327│ │
│                             │  │ 1/31  | Wire Out  -200k │ │
│                             │  │ 1/15  | Bond Int   +1250│ │
│                             │  └─────────────────────────┘ │
│                             │                             │
│                             │  📋 Processing Notes        │
│                             │  • High confidence on all   │
│                             │  • Manual review needed: 0  │
│                             │                             │
│                             │  [Export] [Reprocess]       │
└─────────────────────────────┴─────────────────────────────┘
```

**Data Source:**
```sql
-- Main document data
SELECT d.*, i.name as institution_name
FROM documents d
JOIN institutions i ON d.institution_id = i.id
WHERE d.id = $document_id

-- Extracted transactions (filtered by account if in account context)
SELECT t.*
FROM transactions t
WHERE t.source_document_id = $document_id
  AND ($account_id IS NULL OR t.account_id = $account_id)
ORDER BY t.date DESC, t.amount DESC

-- Processing metadata
SELECT extraction_confidence, extraction_notes, raw_extraction, needs_review
FROM documents
WHERE id = $document_id
```

#### 3. PDF Integration
**Technology Choice:** PDF.js (more flexible) or react-pdf (simpler)

```typescript
interface PDFViewerProps {
  fileUrl: string
  highlights?: Array<PDFHighlight>
  onTextSelect?: (selection: TextSelection) => void
  onPageChange?: (page: number) => void
}

interface PDFHighlight {
  page: number
  coordinates: { x: number; y: number; width: number; height: number }
  color: string
  dataId: string // Links to transaction or data point
}
```

**Features Required:**
- PDF rendering with zoom controls
- Text selection capability
- Highlight overlay system
- Page navigation
- Loading states
- Error handling (PDF failed to load)

### Key Features Needed

#### 1. Confidence Indicators
- **Visual Design:** Traffic light colors (Green/Yellow/Red)
- **Placement:** Document list, viewer header, individual transaction rows
- **Thresholds:** 
  - Green: >90% confidence
  - Yellow: 70-90% confidence  
  - Red: <70% confidence
- **Hover Details:** Show specific confidence scores for different extraction types

#### 2. Source Highlighting
- **Interaction:** Click transaction in right panel → highlight in PDF
- **Visual:** Semi-transparent colored overlay on PDF
- **Coordinate Storage:** Store x,y,width,height per page in database
- **Multiple Highlights:** Support multiple highlights per page

#### 3. Processing Status Display
```typescript
interface StatusIndicatorProps {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  confidence?: number
  notes?: string[]
}

// Status examples:
// pending: Clock icon + "Awaiting processing"
// processing: Spinner + "Claude is processing..."
// completed: Check + "Processed successfully" + confidence %
// failed: X + "Processing failed" + error reason
```

### Acceptance Criteria

- [ ] **GIVEN** a user has selected an entity, **WHEN** they click Documents tab, **THEN** display all documents for that entity sorted by date descending
- [ ] **GIVEN** a document list is displayed, **WHEN** user clicks a document, **THEN** load PDF in left pane and extracted data in right pane within 2 seconds
- [ ] **GIVEN** extracted data is displayed, **WHEN** user clicks a data row, **THEN** highlight corresponding area in PDF within 500ms
- [ ] **GIVEN** a document has confidence < 80%, **THEN** display yellow warning indicator
- [ ] **GIVEN** a document failed processing, **THEN** display red error indicator with failure reason

### Error Scenarios & Handling

#### PDF Loading Errors
- **Scenario:** PDF file missing or corrupted
- **Display:** "Unable to load PDF" message with retry button
- **Actions:** Retry load, report issue, view metadata only
- **Implementation:** Try-catch around PDF loading, fallback UI

#### Data Missing Errors  
- **Scenario:** Document processed but no extracted data
- **Display:** "No data extracted" with reprocess option
- **Actions:** Reprocess document, view raw PDF, manual entry
- **Implementation:** Check for empty transactions array

#### Context Mismatch
- **Scenario:** Viewing account-specific document that has no account data
- **Display:** "No transactions found for this account in this document"
- **Actions:** View full document, change context
- **Implementation:** Filter transactions by account_id, show message if empty

### Data Validation Rules

- Document file_hash must be unique per entity
- Processing confidence must be 0-100
- Document dates cannot be in future
- File size limit: 50MB per document
- PDF must be readable (not password protected)
- Extraction_notes must be valid JSON if present

---

## Workflow 7: Document Search & Discovery

**User Story:** "I need to find a specific transaction or document quickly"

### Search Interface Components

#### 1. Global Search Bar
```typescript
interface SearchBarProps {
  placeholder: string
  onSearch: (query: string, filters: SearchFilters) => void
  suggestions?: SearchSuggestion[]
}

interface SearchFilters {
  entityIds?: string[]
  accountIds?: string[]
  documentTypes?: DocumentType[]
  dateRange?: { start: Date; end: Date }
  amountRange?: { min: number; max: number }
  confidenceThreshold?: number
}
```

**Features:**
- Autocomplete with recent searches
- Smart query parsing (e.g., "$1,234.56" → amount filter)
- Natural language date ranges ("last month", "Q1 2024")
- Search-as-you-type with debouncing
- Search history persistence

#### 2. Advanced Filters Panel
```typescript
interface AdvancedFiltersProps {
  filters: SearchFilters
  onChange: (filters: SearchFilters) => void
  onReset: () => void
}
```

**Filter Categories:**
- **Entity Selection:** Multi-select dropdown with entity names
- **Account Selection:** Hierarchical selection (Entity → Institution → Account)
- **Document Type:** Checkboxes for statement, tax form, confirmation, etc.
- **Date Range:** Calendar picker with presets (This Month, Last Quarter, YTD)
- **Amount Range:** Slider or input fields with currency formatting
- **Confidence Score:** Slider from 0-100% with visual indicators

#### 3. Search Results Display
```typescript
interface SearchResult {
  type: 'document' | 'transaction' | 'account' | 'entity'
  id: string
  title: string
  description: string
  relevanceScore: number
  highlights: string[] // Text snippets with highlighted terms
  metadata: {
    date?: string
    amount?: number
    entity?: string
    account?: string
    confidence?: number
  }
  context: string // How this result relates to the search
}
```

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Search: "FSIXX dividend"                        [Advanced ▼] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 47 results found (0.23 seconds)               [Export CSV]  │
│                                                             │
│ 📄 January 2024 Statement - Milton Preschool              │
│    "FSIXX dividend payment of $4,327.68 on 01/31/2024"     │
│    Confidence: 94% | Entity: Milton Preschool | Jan 2024    │
│                                                             │
│ 💰 FSIXX Dividend - $4,327.68                              │
│    Transaction on 01/31/2024 in account Z40-394067         │
│    Document: January 2024 Statement | High confidence       │
│                                                             │
│ 📄 February 2024 Statement - Milton Preschool             │
│    "FSIXX dividend payment of $4,445.12 on 02/29/2024"     │
│    Confidence: 91% | Entity: Milton Preschool | Feb 2024    │
│                                                             │
│ [Show more results...]                          [1] 2 3 >   │
└─────────────────────────────────────────────────────────────┘
```

### Search Implementation

#### 1. Full-Text Search Backend
```sql
-- Create search indexes
CREATE INDEX idx_documents_search ON documents 
USING gin(to_tsvector('english', file_name || ' ' || COALESCE(extraction_notes, '')));

CREATE INDEX idx_transactions_search ON transactions 
USING gin(to_tsvector('english', description));

-- Search query example
WITH document_search AS (
  SELECT d.*, 
         ts_rank(to_tsvector('english', d.file_name || ' ' || COALESCE(d.extraction_notes, '')), 
                  plainto_tsquery('english', $search_term)) as rank
  FROM documents d
  WHERE to_tsvector('english', d.file_name || ' ' || COALESCE(d.extraction_notes, '')) 
        @@ plainto_tsquery('english', $search_term)
), transaction_search AS (
  SELECT t.*, d.file_name,
         ts_rank(to_tsvector('english', t.description), 
                 plainto_tsquery('english', $search_term)) as rank
  FROM transactions t
  JOIN documents d ON t.source_document_id = d.id
  WHERE to_tsvector('english', t.description) 
        @@ plainto_tsquery('english', $search_term)
)
SELECT * FROM document_search 
UNION ALL
SELECT * FROM transaction_search
ORDER BY rank DESC
LIMIT 50;
```

#### 2. Smart Query Parsing
```typescript
interface ParsedQuery {
  searchTerms: string[]
  filters: {
    amounts?: { exact?: number; range?: { min: number; max: number } }
    dates?: { exact?: Date; range?: { start: Date; end: Date } }
    entities?: string[]
    accounts?: string[]
  }
}

function parseSearchQuery(query: string): ParsedQuery {
  const parsers = [
    // Amount patterns: "$1,234.56", "1000-2000", ">500"
    /\$?([0-9,]+\.?[0-9]*)/g,
    // Date patterns: "2024-01-31", "Jan 2024", "last month"
    /\b(\d{4}-\d{2}-\d{2}|\w+\s+\d{4}|last\s+\w+|this\s+\w+)\b/g,
    // Entity patterns: entity:"Milton Preschool"
    /entity:"([^"]+)"/g,
  ]
  
  // Implementation details...
}
```

#### 3. Search Performance Requirements
- **Latency:** < 500ms for 100k transactions
- **Result Limit:** 100 per page with pagination  
- **Autocomplete:** < 100ms response time
- **Caching:** Cache frequent searches for 5 minutes
- **Indexing:** Full-text indexes on searchable fields

### Search Capabilities

#### 1. Amount Search
- **Exact Match:** "$1234.56" finds transactions with that exact amount
- **Range Search:** "1000-2000" finds amounts between $1,000 and $2,000
- **Comparison:** ">500", "<1000" for greater/less than searches
- **Currency Parsing:** Handle "$", commas, decimal points automatically

#### 2. Date Search  
- **Exact Date:** "2024-01-31", "Jan 31, 2024"
- **Natural Language:** "last month", "Q1 2024", "this year"
- **Date Ranges:** "Jan 2024 - Mar 2024", "2024-01-01:2024-03-31"
- **Relative Dates:** "30 days ago", "last quarter"

#### 3. Description Search
- **Fuzzy Matching:** Handle typos and variations
- **Stemming:** "dividend" matches "dividends", "div"
- **Phrase Search:** "wire transfer" as exact phrase
- **Wildcard:** "FSIXX*" matches FSIXX dividend, FSIXX purchase

#### 4. Entity/Account Filtering
- **Entity Names:** "Milton Preschool", "Entity A"
- **Account Numbers:** "Z40-394067", "*4567" (partial match)
- **Institution Names:** "Fidelity", "Bank of America"
- **Account Types:** "brokerage", "checking"

### Acceptance Criteria

- [ ] **GIVEN** user enters search term, **WHEN** pressing enter, **THEN** return results within 2 seconds
- [ ] **GIVEN** search results exist, **THEN** display with relevance ranking
- [ ] **GIVEN** user applies filters, **THEN** update results without clearing search term  
- [ ] **GIVEN** user clicks result, **THEN** open document/transaction detail within 1 second
- [ ] **GIVEN** amount search with "$" or ",", **THEN** parse correctly (e.g., "$1,234.56" = 1234.56)

### Error Handling

#### No Results Found
- **Message:** "No matches found. Try broadening your search."
- **Suggestions:** Remove filters, check spelling, try related terms
- **Actions:** Clear filters button, search suggestions

#### Invalid Date Format
- **Message:** "Please enter a valid date (MM/DD/YYYY)"
- **Visual:** Highlight field in red, show format examples
- **Actions:** Format examples, date picker alternative

#### Invalid Amount Format  
- **Message:** "Please enter a valid amount"
- **Examples:** "$1,234.56", "1000-2000", ">500"
- **Actions:** Format validation, input mask

#### Search Timeout
- **Message:** "Search is taking longer than expected. Please try again."
- **Actions:** Retry button, simplify search suggestion
- **Logging:** Log slow queries for optimization

### Integration with Document Viewer

#### Search-to-View Flow
1. User searches for "FSIXX dividend January"
2. Results show documents and transactions
3. User clicks document result
4. Document viewer opens with search term highlighted
5. PDF shows highlighted areas, data panel shows filtered results

#### Context Preservation
- **URL State:** Include search parameters in URL for bookmarking
- **Navigation:** Back button returns to search results with state
- **Highlighting:** Maintain search highlights when viewing documents
- **Filtering:** Apply search context to document data panel

## Implementation Guidelines

### Component Architecture
```typescript
// Main document workflows page
export default function DocumentsPage() {
  return (
    <DocumentLayout>
      <SearchHeader />
      <DocumentFilters />
      <DocumentResults />
    </DocumentLayout>
  )
}

// Document viewer with context
export default function DocumentViewerPage({ documentId, searchQuery }) {
  return (
    <DocumentViewer
      documentId={documentId}
      highlightTerms={parseSearchTerms(searchQuery)}
      context={getViewerContext()}
    />
  )
}
```

### State Management
```typescript
// Search state
const useSearchStore = create((set) => ({
  query: '',
  filters: defaultFilters,
  results: [],
  loading: false,
  setQuery: (query) => set({ query }),
  setFilters: (filters) => set({ filters }),
  executeSearch: async (query, filters) => {
    set({ loading: true })
    const results = await searchDocuments(query, filters)
    set({ results, loading: false })
  }
}))
```

### Performance Optimizations
- Implement virtual scrolling for large result sets
- Use React Query for search result caching
- Debounce search input (300ms delay)
- Lazy load PDF rendering
- Optimize database queries with proper indexes

---

*This guide provides complete context for document workflow implementation. All user flows, data sources, and component specifications are included for autonomous development.*