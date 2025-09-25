# Navigation Map - Wealth Manager Frontend

**Created:** 09/25/25 12:30PM
**Purpose:** Complete route documentation for all accessible pages in the application
**Status:** Week 3 Complete - All routes operational

## 🗺️ Route Hierarchy

```
/ (Dashboard)
├── /entities (Entities Landing)
│   └── /entities/[entityId] (Entity Detail)
│       └── Links to → /accounts filtered by entity
├── /accounts (Accounts Landing)
│   └── /accounts/[accountId] (Account Detail)
│       ├── Overview Tab (default)
│       ├── Transactions Tab
│       ├── Positions Tab (investment accounts only)
│       └── Documents Tab (placeholder)
├── /institutions (Institutions Landing)
│   └── Links to → /accounts filtered by institution
├── /documents (Documents Landing)
│   └── Status filtering (processed/pending)
└── /admin
    └── /admin/data-status (Data Completeness Monitoring)
```

## 📍 Page Descriptions

### Dashboard (`/`)
- **Purpose:** Global financial overview
- **Features:**
  - Quick stats bar (entity/account counts)
  - Net worth summary cards
  - Entity cards with balances
  - Recent activity widget (10 latest transactions)
  - "View All" links to each section

### Entities (`/entities`)
- **Purpose:** View all business entities and individuals
- **Features:**
  - Grid layout with entity cards
  - Filter by type (Individual, S-Corp, LLC)
  - Shows account count and total balance per entity
  - Click to navigate to entity detail

### Entity Detail (`/entities/[entityId]`)
- **Purpose:** Deep dive into specific entity
- **Features:**
  - Entity information header
  - Metrics cards (balance, cash flow, income)
  - Accounts list filtered to this entity
  - Links to account detail pages

### Accounts (`/accounts`)
- **Purpose:** View all accounts across entities
- **Features:**
  - Table view with sortable columns
  - Filter by institution, type, and entity
  - Shows account name, institution, type, entity, balance
  - Click account name for detail view

### Account Detail (`/accounts/[accountId]`)
- **Purpose:** Comprehensive account information
- **Features:**
  - Account header with balance
  - Breadcrumb navigation
  - Tabbed interface:
    - Overview: Summary metrics
    - Transactions: Searchable list with pagination
    - Positions: Investment holdings (if applicable)
    - Documents: Related files (placeholder)

### Institutions (`/institutions`)
- **Purpose:** View all financial institutions
- **Features:**
  - Card grid layout
  - Filter by type and status
  - Shows account counts and total values
  - Account type breakdown per institution

### Documents (`/documents`)
- **Purpose:** Track document processing
- **Features:**
  - Table view of all documents
  - Filter by status (processed/pending)
  - Shows document name, type, date, entity, status
  - Color-coded status badges

### Data Status (`/admin/data-status`)
- **Purpose:** Monitor data completeness
- **Features:**
  - Summary cards (total accounts, recent data, stale data)
  - Detailed table per account
  - Shows last transaction/position dates
  - Color-coded freshness indicators

## 🔄 Navigation Patterns

### Primary Navigation (Sidebar)
- Dashboard
- Entities
- Accounts
- Institutions
- Documents
- Admin → Data Status

### Breadcrumb Navigation
Available on detail pages:
- Dashboard > Entities > [Entity Name]
- Dashboard > Accounts > [Account Name]

### Cross-Navigation Links
- Entity cards → Entity detail pages
- Account names → Account detail pages
- Entity names in accounts → Entity detail pages
- "View All" links → Landing pages
- Recent activity items → Account detail pages

## 🎨 UI Patterns

### Filtering
All landing pages support filtering:
- Native HTML select dropdowns
- Client-side filtering with immediate updates
- "Showing X of Y items" count display

### Data Display
- Currency: Formatted with USD symbol and commas
- Dates: "MMM DD, YYYY" format
- Status: Color-coded badges (green/yellow/red)
- Empty States: Consistent empty state component

### Loading States
- Skeleton loaders for cards
- Skeleton tables for lists
- Loading spinner for data fetches

## 📊 Data Flow

```
Dashboard
    ↓ (aggregated view)
Landing Pages
    ↓ (filtered lists)
Detail Pages
    ↓ (specific entity/account)
Tabbed Data Views
```

## 🚀 Week 4 Navigation Enhancements (Planned)

- Global search bar in top navigation
- Advanced filtering with date ranges
- Saved filter preferences
- Quick actions menu
- Keyboard navigation shortcuts
- Export options on all data views

## 📝 Technical Implementation

### Routing
- Next.js 14 App Router
- Dynamic routes using [param] syntax
- Client-side navigation with next/link

### State Management
- URL params for filters
- React Query for server state
- Local state for UI interactions

### Performance
- React Query caching (5-minute stale time)
- Lazy loading for tabs
- Virtual scrolling for large lists (planned)

---

*This navigation map reflects the completed Week 3 implementation. All routes are functional and tested.*