# Component Catalog - Wealth Manager Frontend

**Created:** 09/25/25 12:30PM
**Purpose:** Comprehensive catalog of all reusable components
**Status:** Week 3 Complete - Components documented through Day 12

## 📦 Component Organization

```
src/components/
├── ui/           # Generic UI components
├── layout/       # Structural components
├── dashboard/    # Dashboard-specific components
├── accounts/     # Account-related components
├── charts/       # Data visualization components
└── tables/       # Table components
```

## 🎨 UI Components (`/components/ui/`)

### FilterSelect
- **Purpose:** Reusable dropdown filter
- **Props:** options, value, onChange, placeholder
- **Usage:** All landing pages for filtering
- **Features:** Native HTML select, immediate updates

### SkeletonCard
- **Purpose:** Loading placeholder for cards
- **Props:** className (optional)
- **Usage:** Dashboard cards during data fetch
- **Features:** Animated shimmer effect

### SkeletonTable
- **Purpose:** Loading placeholder for tables
- **Props:** rows (number of rows to show)
- **Usage:** Transaction lists, account tables
- **Features:** Realistic table structure

### EmptyState
- **Purpose:** Consistent empty data display
- **Props:** message, icon (optional)
- **Usage:** When no data available
- **Features:** Centered message with icon

### Button
- **Purpose:** Consistent button styling
- **Props:** variant, size, onClick, disabled
- **Usage:** Throughout application
- **Variants:** primary, secondary, outline

## 🏗️ Layout Components (`/components/layout/`)

### Sidebar
- **Purpose:** Main navigation
- **Location:** Left side of application
- **Features:**
  - Active state highlighting
  - Icon + label navigation items
  - Admin section with divider
  - Responsive collapse on mobile

### TopBar
- **Purpose:** Header with breadcrumbs
- **Props:** breadcrumbs array
- **Features:**
  - Breadcrumb navigation
  - Last refresh time
  - Refresh button

## 📊 Dashboard Components (`/components/dashboard/`)

### MetricCard
- **Purpose:** Display key metrics
- **Props:** title, value, change, format, className
- **Format Types:** currency, percent, number
- **Features:**
  - Trend indicators (up/down/flat)
  - Change amount and percentage
  - Responsive sizing

### EntityCard
- **Purpose:** Display entity summary
- **Props:** entity object
- **Features:**
  - Entity type icon
  - Balance display
  - Account count
  - Monthly change indicator
  - Click to navigate

### AccountsList
- **Purpose:** Display accounts grouped by institution
- **Props:** entityId (optional for filtering)
- **Features:**
  - Grouped by institution
  - Balance display
  - Account details
  - Hover effects

### RecentActivity
- **Purpose:** Show recent transactions
- **Props:** limit (default 10)
- **Features:**
  - Cross-account transactions
  - Color-coded amounts
  - Click to account detail
  - Date and description

### QuickStats
- **Purpose:** Summary statistics bar
- **Props:** None (fetches own data)
- **Features:**
  - Entity count
  - Account count
  - Institution count
  - Last refresh date

### NetWorthSummary
- **Purpose:** Total net worth display
- **Props:** entities array
- **Features:**
  - Total calculation
  - Change indicators
  - Breakdown by entity

## 💳 Account Components (`/components/accounts/`)

### AccountTransactions
- **Purpose:** Transaction list with search
- **Props:** accountId
- **Features:**
  - Search by description/payee
  - Pagination (50 per page)
  - Running balance column
  - Color-coded amounts
  - Fee display

### AccountPositions
- **Purpose:** Investment holdings display
- **Props:** accountId
- **Features:**
  - Holdings table
  - Portfolio percentages
  - Unrealized gains/losses
  - Market value totals
  - Only shows for investment accounts

### AccountDocuments
- **Purpose:** Related documents list
- **Props:** accountId
- **Status:** Placeholder implementation
- **Future:** Will show related documents

### AccountHeader
- **Purpose:** Account detail header
- **Props:** account object
- **Features:**
  - Account name and number
  - Institution and entity
  - Current balance
  - Last updated date

## 📈 Chart Components (`/components/charts/`)

### NetWorthTrendChart
- **Purpose:** Historical net worth
- **Props:** data array, height
- **Library:** Recharts
- **Features:**
  - Line chart with area fill
  - Tooltip with values
  - Responsive sizing

### PortfolioAllocationChart
- **Purpose:** Asset allocation pie chart
- **Props:** positions array
- **Library:** Recharts
- **Features:**
  - Pie chart with labels
  - Custom colors
  - Percentage display
  - Legend

### AccountBalanceChart
- **Purpose:** Account balances bar chart
- **Props:** accounts array
- **Library:** Recharts
- **Features:**
  - Grouped by tax treatment
  - Color coding
  - Tooltips

### ChartErrorBoundary
- **Purpose:** Error handling for charts
- **Props:** children
- **Features:**
  - Graceful error display
  - Prevents app crashes
  - Error logging

## 🔧 Utility Components

### ErrorBoundary
- **Purpose:** Catch React errors
- **Props:** children, fallback
- **Usage:** Wrap sections that might error
- **Features:** Custom error display

### LoadingSpinner
- **Purpose:** Loading indicator
- **Props:** size, color
- **Usage:** Inline loading states
- **Features:** Animated spinner

## 📐 Component Guidelines

### Size Limits
- Maximum 200 lines per component
- Split if exceeding limit
- Extract sub-components as needed

### TypeScript Requirements
- Full prop interfaces
- No `any` types
- Proper return types

### Documentation Standards
```typescript
// Created: [Date]
// Purpose: [Description]
// Context:
// - Used by: [Parents]
// - Uses: [Dependencies]
// - Data source: [Tables]
```

### Reusability Principles
1. Single responsibility
2. Composable design
3. Consistent prop naming
4. Default props where sensible
5. Error boundary wrapping

## 🎯 Week 4 Components (Planned)

### DataExport
- CSV export functionality
- PDF generation
- Bulk export options

### GlobalSearch
- Cross-entity search
- Real-time results
- Search history

### AdvancedFilter
- Date range picker
- Multi-select filters
- Saved filter sets

### DataQualityAlert
- Stale data warnings
- Missing data indicators
- Action suggestions

## 📊 Component Metrics

### Current Statistics
- **Total Components:** 25+
- **UI Components:** 5
- **Dashboard Components:** 6
- **Account Components:** 4
- **Chart Components:** 4
- **Average Size:** ~150 lines
- **Reusability Score:** High

### Coverage
- ✅ Loading states: 100%
- ✅ Error states: 100%
- ✅ Empty states: 100%
- ✅ TypeScript: 100%
- ✅ Responsive: 100%

---

*This catalog reflects all components built through Week 3, Day 12. All components follow KISS principles and maintain high reusability.*