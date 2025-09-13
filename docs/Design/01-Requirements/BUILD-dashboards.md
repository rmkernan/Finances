# BUILD: Dashboard Implementation Guide

**Created:** 09/12/25 5:51PM ET  
**Purpose:** Complete context for dashboard implementation - all layouts, data sources, interactions  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement hierarchical dashboard system with fixed sections and progressive disclosure  
**Prerequisites:** Next.js 14, TypeScript, shadcn/ui, Supabase connection, entity/account data structure  
**Key Decisions Made:** Fixed layouts (no drag-drop), context-aware data filtering, 4-level hierarchy  
**Output Expected:** Responsive dashboard components with drill-down navigation and real-time data

## Quick Reference

**Context Levels:**
- **Global Dashboard** (`/`) - All entities overview
- **Entity Dashboard** (`/entities/{entity}`) - Single entity focus  
- **Institution Dashboard** (`/entities/{entity}/institutions/{institution}`) - Entity's accounts at specific institution
- **Account Dashboard** (`/entities/{entity}/accounts/{account}`) - Individual account details

**Data Flow:** Context selection → SQL filtering → Component rendering → User interaction → Navigation/drill-down

**Key Components:** MetricCard, EntityCard, TransactionTable, DocumentList, NetWorthChart, AccountOverview

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

### URL Structure
```
/                                                    → Global Dashboard
/entities/{entity}                                  → Entity Dashboard
/entities/{entity}/institutions/{institution}       → Institution Dashboard
/entities/{entity}/accounts/{account}               → Account Dashboard
```

### Context-Based Data Visibility
| In Context | Documents Shown | Transactions Shown | Accounts Shown |
|------------|----------------|-------------------|----------------|
| **Global** | ALL documents | ALL transactions | ALL accounts grouped by entity |
| **Entity** | All docs for entity's accounts | All transactions for entity's accounts | All accounts owned by entity |
| **Institution** | All docs from institution for entity | All transactions at institution for entity | Entity's accounts at institution |
| **Account** | Only docs linked to account | Only account's transactions | Just this account (detail view) |

## Dashboard Hierarchy & Section Specifications

### Design Philosophy
- **Fixed Layouts**: No drag-and-drop or customization complexity
- **Data Freshness**: Query database on page load, manual refresh button available
- **Progressive Disclosure**: More detail as you drill down the hierarchy
- **Consistent Structure**: Similar layout patterns across all dashboards

---

## 1. Global Dashboard (`/`)

**Purpose**: Bird's-eye view of entire financial picture across all entities  
**Layout**: Single column with full-width sections

### Section 1: Net Worth Summary
- **Position**: Top, full width
- **Height**: 200px
- **Content**:
  - Large headline number: Total net worth across all entities
  - Breakdown bar: Financial Assets | Real Assets | Liabilities
  - Trend sparkline: 12-month net worth trend
  - Period selector: MTD, QTD, YTD, All Time
- **Data Source**: 
  ```sql
  SELECT SUM(financial_assets + real_assets - liabilities) as net_worth
  FROM net_worth_summary
  WHERE date_range = selected_period
  ```
- **Interactions**: Click breakdown sections to filter entity cards below
- **Component**: `<NetWorthSummary />`

### Section 2: Entity Cards Grid
- **Position**: Below summary
- **Layout**: Responsive grid (4 columns desktop, 2 tablet, 1 mobile)
- **Content per card**:
  - Entity name and type badge (S-Corp/LLC/Individual)
  - Current net worth
  - MTD change ($amount and %)
  - Mini pie chart: Asset allocation
  - Quick stats: Cash balance, YTD income
- **Data Source**: One query per entity for current values
  ```sql
  SELECT e.name, e.entity_type, 
         SUM(a.balance) as net_worth,
         SUM(CASE WHEN t.date >= date_trunc('month', CURRENT_DATE) 
             THEN t.amount ELSE 0 END) as mtd_change
  FROM entities e
  JOIN accounts a ON e.id = a.entity_id
  LEFT JOIN transactions t ON a.id = t.account_id
  GROUP BY e.id
  ```
- **Interactions**: Click card → Entity dashboard
- **Visual Design**: Cards with subtle shadows, hover state
- **Component**: `<EntityCard />` in `<EntityGrid />`

### Section 3: Recent Activity & Upcoming Items
- **Position**: Bottom, two columns
- **Layout**: 60% Recent Activity, 40% Upcoming Items

**Recent Activity** (Left):
- Last 10 transactions across all entities
- Format: Date | Entity | Account | Description | Amount
- Color coding: Green for income, Red for expenses
- Click row → Transaction detail modal
- **Data Source**:
  ```sql
  SELECT t.*, e.name as entity_name, a.account_name
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  JOIN entities e ON a.entity_id = e.id
  ORDER BY t.date DESC
  LIMIT 10
  ```
- **Component**: `<RecentActivity />`

**Upcoming Items** (Right):
- Next 5 upcoming items (tax payments, expected documents)
- Format: Date | Type | Entity | Description | Amount
- Visual indicators: Warning icons for overdue items
- Click row → Relevant section
- **Data Source**: `tax_payments` table + scheduled items
- **Component**: `<UpcomingItems />`

---

## 2. Entity Dashboard (`/entities/{entity}`)

**Purpose**: Complete financial picture for a single entity  
**Context Note**: This is where users spend most time - reviewing specific business/personal finances

### Section 1: Entity Header
- **Position**: Top, full width
- **Height**: 120px
- **Content**:
  - Entity name with type badge
  - Net worth with MTD/YTD changes
  - Key metrics bar: Cash | Investments | Properties | Liabilities
  - Last refreshed timestamp
  - Manual refresh button
- **Visual Design**: Subtle gradient background, entity type color coding
- **Data Source**:
  ```sql
  SELECT e.*, 
         SUM(a.balance) as net_worth,
         SUM(CASE WHEN a.account_type = 'cash' THEN a.balance ELSE 0 END) as cash,
         SUM(CASE WHEN a.account_type IN ('investment', 'brokerage') THEN a.balance ELSE 0 END) as investments
  FROM entities e
  JOIN accounts a ON e.id = a.entity_id
  WHERE e.id = $entity_id
  GROUP BY e.id
  ```
- **Component**: `<EntityHeader />`

### Section 2: Accounts Overview
- **Position**: Below header
- **Layout**: Grouped cards by institution
- **Content per institution group**:
  - Institution name and logo (if available)
  - Total balance at institution
  - Account list with: Type icon | Account name | Number (masked) | Balance | Last activity
  - Subtotal per institution
- **Interactions**: 
  - Click institution header → Institution dashboard
  - Click account row → Account dashboard
- **Technical Note**: Single query with JOIN on institutions and accounts tables
- **Data Source**:
  ```sql
  SELECT i.name as institution_name, i.logo_url,
         a.id, a.account_name, a.account_number, a.balance, a.account_type,
         MAX(t.date) as last_activity
  FROM institutions i
  JOIN accounts a ON i.id = a.institution_id
  LEFT JOIN transactions t ON a.id = t.account_id
  WHERE a.entity_id = $entity_id
  GROUP BY i.id, a.id
  ORDER BY i.name, a.account_name
  ```
- **Component**: `<AccountsOverview />` with `<InstitutionGroup />` and `<AccountRow />`

### Section 3: Financial Metrics Row
- **Position**: Middle, full width
- **Layout**: 4 metric cards in a row
- **Cards**:
  1. **Cash Flow**: Current month in/out/net with mini chart
  2. **Tax Liability**: YTD federal/state estimates
  3. **Document Status**: Processed/pending/failed counts
  4. **Investment Performance**: YTD return % (if applicable)
- **Visual Design**: Flat cards with icons, no borders
- **Data Sources**:
  ```sql
  -- Cash Flow
  SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as inflows,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as outflows
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE a.entity_id = $entity_id 
    AND date >= date_trunc('month', CURRENT_DATE)
  
  -- Tax Liability
  SELECT 
    SUM(CASE WHEN federal_taxable THEN amount ELSE 0 END) * 0.25 as fed_tax,
    SUM(CASE WHEN state_taxable THEN amount ELSE 0 END) * 0.06 as state_tax
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE a.entity_id = $entity_id 
    AND date >= date_trunc('year', CURRENT_DATE)
  
  -- Document Status
  SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as processed,
    SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as failed
  FROM documents d
  WHERE d.entity_id = $entity_id
  ```
- **Component**: `<FinancialMetrics />` with individual `<MetricCard />`

### Section 4: Recent Documents
- **Position**: Bottom left, 50% width
- **Content**:
  - Last 5 processed documents
  - Format: Date | Type | Institution | Confidence score
  - Color coding: Green (>90%), Yellow (70-90%), Red (<70%)
  - "View All Documents" link
- **Interactions**: Click row → Document viewer
- **Data Source**:
  ```sql
  SELECT d.*, i.name as institution_name
  FROM documents d
  JOIN institutions i ON d.institution_id = i.id
  WHERE d.entity_id = $entity_id
  ORDER BY d.created_at DESC
  LIMIT 5
  ```
- **Component**: `<RecentDocuments />`

### Section 5: Entity Notes
- **Position**: Bottom right, 50% width
- **Content**:
  - Free-form text area for notes
  - Last modified timestamp
  - Edit button (saves to entity notes field)
- **Technical**: Stores in entities.notes column
- **Component**: `<EntityNotes />` with inline editing

---

## 3. Institution Dashboard (`/entities/{entity}/institutions/{institution}`)

**Purpose**: View all accounts and activity at a specific institution for an entity  
**Context Note**: Useful for reviewing consolidated statements and institution-wide changes

### Section 1: Institution Summary
- **Position**: Top, full width
- **Content**:
  - Institution name and entity context
  - Total balance across all accounts
  - Number of accounts
  - Percentage of entity's total portfolio
  - Last statement date
- **Data Source**:
  ```sql
  SELECT i.name, 
         COUNT(a.id) as account_count,
         SUM(a.balance) as total_balance,
         MAX(d.period_end) as last_statement
  FROM institutions i
  JOIN accounts a ON i.id = a.institution_id
  LEFT JOIN documents d ON i.id = d.institution_id AND d.entity_id = a.entity_id
  WHERE i.id = $institution_id AND a.entity_id = $entity_id
  GROUP BY i.id
  ```
- **Component**: `<InstitutionSummary />`

### Section 2: Account List
- **Position**: Left side, 40% width
- **Content**:
  - Detailed account list
  - Per account: Type | Number | Balance | YTD interest/dividends | Last transaction
  - Totals row at bottom
- **Interactions**: Click account → Account dashboard
- **Data Source**:
  ```sql
  SELECT a.*,
         SUM(CASE WHEN t.date >= date_trunc('year', CURRENT_DATE) 
             AND t.transaction_type IN ('dividend', 'interest')
             THEN t.amount ELSE 0 END) as ytd_income,
         MAX(t.date) as last_transaction
  FROM accounts a
  LEFT JOIN transactions t ON a.id = t.account_id
  WHERE a.institution_id = $institution_id AND a.entity_id = $entity_id
  GROUP BY a.id
  ORDER BY a.account_name
  ```
- **Component**: `<AccountList />`

### Section 3: Recent Transactions
- **Position**: Right side, 60% width
- **Content**:
  - Last 30 days of transactions across all accounts at institution
  - Format: Date | Account | Type | Description | Amount | Balance
  - Filter buttons: All | Deposits | Withdrawals | Dividends | Fees
  - Export button (CSV)
- **Technical**: Paginated query, limit 50 initially
- **Data Source**:
  ```sql
  SELECT t.*, a.account_name
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE a.institution_id = $institution_id 
    AND a.entity_id = $entity_id
    AND t.date >= CURRENT_DATE - INTERVAL '30 days'
  ORDER BY t.date DESC
  LIMIT 50 OFFSET $offset
  ```
- **Component**: `<TransactionList />` with filtering and pagination

### Section 4: Document Library
- **Position**: Bottom, full width
- **Layout**: Document tiles grouped by type
- **Content**:
  - Tabs: All | Statements | Tax Forms | Confirmations | Correspondence
  - Document grid: Type icon | Date | Description | Status
  - Quick filters: Year selector, document type
- **Interactions**: Click document → PDF viewer
- **Data Source**:
  ```sql
  SELECT d.*
  FROM documents d
  WHERE d.institution_id = $institution_id 
    AND d.entity_id = $entity_id
    AND ($document_type IS NULL OR d.document_type = $document_type)
    AND ($year IS NULL OR EXTRACT(YEAR FROM d.period_start) = $year)
  ORDER BY d.period_start DESC
  ```
- **Component**: `<DocumentLibrary />` with tabs and filtering

---

## 4. Account Dashboard (`/entities/{entity}/accounts/{account}`)

**Purpose**: Deep dive into a specific account's activity and holdings  
**Context Note**: Most detailed view - where users verify transactions and review specifics

### Section 1: Account Header
- **Position**: Top, full width
- **Content**:
  - Account name and number (masked)
  - Current balance with 30-day change
  - Account type and tax treatment badges
  - Mini balance trend chart (last 12 months)
- **Data Source**:
  ```sql
  SELECT a.*,
         a.balance - LAG(a.balance, 1) OVER (ORDER BY date) as change_30d,
         array_agg(balance ORDER BY date) as balance_history
  FROM accounts a
  LEFT JOIN account_snapshots s ON a.id = s.account_id
  WHERE a.id = $account_id
  AND s.date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY a.id
  ```
- **Component**: `<AccountHeader />` with `<BalanceTrendChart />`

### Section 2: Holdings Table (Investment Accounts Only)
- **Position**: Below header (conditional)
- **Content**:
  - Current positions: Symbol | Description | Quantity | Price | Value | Day Change | Total Gain/Loss
  - Sortable columns
  - Grouping options: Asset class | Performance | Value
- **Technical**: Only show for account_type IN ('brokerage', 'ira', '401k')
- **Data Source**:
  ```sql
  SELECT h.*, s.symbol, s.description, s.current_price, s.day_change
  FROM holdings h
  JOIN securities s ON h.security_id = s.id
  WHERE h.account_id = $account_id AND h.quantity > 0
  ORDER BY h.market_value DESC
  ```
- **Component**: `<HoldingsTable />` (conditional render)

### Section 3: Transaction List
- **Position**: Main content area
- **Layout**: Full-width data table
- **Content**:
  - Columns: Date | Description | Type | Amount | Balance | Document Link
  - Filters: Date range | Type | Amount range
  - Search box for description/amount
  - Pagination: 50 per page
- **Interactions**: 
  - Click row → Transaction detail modal
  - Click document link → PDF viewer at specific page
- **Technical**: Include source_document_id for linking
- **Data Source**:
  ```sql
  SELECT t.*, d.file_name
  FROM transactions t
  LEFT JOIN documents d ON t.source_document_id = d.id
  WHERE t.account_id = $account_id
    AND ($date_start IS NULL OR t.date >= $date_start)
    AND ($date_end IS NULL OR t.date <= $date_end)
    AND ($type_filter IS NULL OR t.transaction_type = $type_filter)
    AND ($search IS NULL OR t.description ILIKE '%' || $search || '%')
  ORDER BY t.date DESC
  LIMIT 50 OFFSET $offset
  ```
- **Component**: `<TransactionTable />` with filtering and search

### Section 4: Account Metrics Row
- **Position**: Bottom
- **Layout**: 3 cards
- **Cards**:
  1. **Cash Flow Summary**: YTD in/out/net
  2. **Tax Summary**: YTD dividends, interest, cap gains by tax treatment
  3. **Document Count**: Statements/tax forms/confirms available
- **Data Sources**:
  ```sql
  -- Cash Flow
  SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as ytd_in,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as ytd_out
  FROM transactions
  WHERE account_id = $account_id 
    AND date >= date_trunc('year', CURRENT_DATE)
  
  -- Tax Summary
  SELECT 
    SUM(CASE WHEN transaction_type = 'dividend' AND federal_taxable THEN amount ELSE 0 END) as fed_dividends,
    SUM(CASE WHEN transaction_type = 'dividend' AND state_taxable THEN amount ELSE 0 END) as state_dividends,
    SUM(CASE WHEN transaction_type = 'interest' AND federal_taxable THEN amount ELSE 0 END) as fed_interest
  FROM transactions
  WHERE account_id = $account_id 
    AND date >= date_trunc('year', CURRENT_DATE)
  ```
- **Component**: `<AccountMetrics />`

### Section 5: Account Notes
- **Position**: Very bottom
- **Content**: Account-specific notes and reminders
- **Technical**: Stores in accounts.notes column
- **Component**: `<AccountNotes />` with inline editing

## Implementation Guidelines

### Component Architecture
```typescript
// Dashboard page structure
export default function DashboardPage() {
  return (
    <DashboardLayout>
      <DashboardHeader />
      <DashboardSections />
    </DashboardLayout>
  )
}

// Section components
<NetWorthSummary data={netWorthData} onFilterChange={handleFilter} />
<EntityGrid entities={entityData} onEntityClick={navigateToEntity} />
<RecentActivity transactions={recentData} onTransactionClick={showModal} />
```

### Data Fetching Strategy
```typescript
// Use React Query for data fetching
const { data: dashboardData } = useQuery({
  queryKey: ['dashboard', selectedEntities, dateRange],
  queryFn: () => fetchDashboardData(selectedEntities, dateRange),
  staleTime: 5 * 60 * 1000, // 5 minutes
})
```

### Performance Considerations
- Implement virtual scrolling for large transaction lists
- Use pagination for document lists
- Cache entity/account data aggressively
- Lazy load charts and heavy components
- Optimize SQL queries with proper indexes

## Code Generation Hints

### TypeScript Interfaces
```typescript
interface DashboardData {
  netWorth: {
    total: number
    change: number
    breakdown: Array<{ type: string; amount: number }>
    history: Array<{ date: string; value: number }>
  }
  entities: Array<{
    id: string
    name: string
    type: 'S-Corp' | 'LLC' | 'Individual'
    netWorth: number
    mtdChange: number
    allocation: Array<{ asset: string; percentage: number }>
  }>
  recentActivity: Array<Transaction>
  upcomingItems: Array<UpcomingItem>
}
```

### SQL Query Patterns
- Always filter by entity context in WHERE clauses
- Use JOINs instead of N+1 queries
- Include proper indexes on date, entity_id, account_id
- Use aggregation functions for summary data
- Include LIMIT/OFFSET for pagination

### Component Styling
- Use Tailwind classes for responsive layouts
- Implement consistent spacing: `space-y-6`, `gap-4`
- Use shadcn/ui components for consistency
- Apply hover states for interactive elements
- Ensure proper contrast ratios for accessibility

---

*This guide provides complete context for dashboard implementation. All data sources, interactions, and components are specified for autonomous development.*