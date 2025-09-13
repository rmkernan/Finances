# Frontend Technical Design Document

**Created:** 09/09/25 8:45PM ET  
**Updated:** 09/11/25 1:19PM ET - Added net worth tracking components and data models  
**Purpose:** Comprehensive technical design for financial management frontend application  
**Status:** Complete specification ready for implementation

## Executive Summary

This document outlines the technical architecture, design patterns, and implementation approach for a sophisticated financial management frontend inspired by eMoney Advisor's proven UX patterns. The system will support multi-entity financial tracking with a professional, polished interface suitable for high net worth portfolio management.

## Architecture Overview

### Technology Stack

```yaml
Framework: Next.js 14 with App Router
Language: TypeScript 5.x
UI Library: shadcn/ui (Radix UI + Tailwind CSS)
State Management: Zustand + TanStack Query v5
Charts: Recharts + D3.js for custom visualizations
Tables: TanStack Table v8
Forms: React Hook Form + Zod validation
PDF Viewer: react-pdf-viewer-js
Date Handling: date-fns
Icons: Lucide React
Testing: Jest + React Testing Library + Playwright
Build Tool: Turbopack (Next.js 14)
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser Client                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Next.js Frontend Application                │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │          Presentation Layer (React)              │ │ │
│  │  │    • Pages & Layouts                            │ │ │
│  │  │    • shadcn/ui Components                       │ │ │
│  │  │    • Custom Business Components                 │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │          State Management Layer                  │ │ │
│  │  │    • Zustand Stores (UI State)                  │ │ │
│  │  │    • TanStack Query (Server State)              │ │ │
│  │  │    • React Context (Theme/Auth)                 │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │             API Layer (Next.js)                  │ │ │
│  │  │    • Server Actions                             │ │ │
│  │  │    • Route Handlers                             │ │ │
│  │  │    • Database Queries                           │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Local Supabase Database                    │
│                    PostgreSQL (Port 54322)                   │
└─────────────────────────────────────────────────────────────┘
```

## UI/UX Design System

### Design Principles (eMoney-Inspired)

1. **"Financial House" Metaphor**
   - Foundation: Cash & liquid assets
   - Walls: Investment portfolio
   - Roof: Real estate & alternatives
   - Visual hierarchy reflects importance

2. **Professional Polish**
   - Subtle gradients and shadows
   - Consistent spacing (8px grid)
   - Muted color palette with accent colors
   - Premium typography (Inter/SF Pro)

3. **Information Density**
   - High data density without clutter
   - Progressive disclosure patterns
   - Context-sensitive detail levels
   - Smart defaults with customization

### Color System

```css
/* Core Palette */
--primary: hsl(222, 47%, 11%);        /* Deep Navy */
--primary-foreground: hsl(0, 0%, 100%);
--secondary: hsl(214, 32%, 91%);      /* Light Blue-Gray */
--accent: hsl(142, 71%, 45%);         /* Success Green */
--destructive: hsl(0, 84%, 60%);      /* Alert Red */
--muted: hsl(210, 40%, 96%);          /* Background Gray */

/* Semantic Colors */
--income: hsl(142, 71%, 45%);         /* Green */
--expense: hsl(0, 84%, 60%);          /* Red */
--neutral: hsl(214, 32%, 50%);        /* Blue-Gray */
--warning: hsl(38, 92%, 50%);         /* Amber */

/* Chart Colors */
--chart-1: hsl(215, 70%, 50%);        /* Blue */
--chart-2: hsl(160, 60%, 45%);        /* Teal */
--chart-3: hsl(30, 80%, 55%);         /* Orange */
--chart-4: hsl(280, 65%, 60%);        /* Purple */
--chart-5: hsl(340, 75%, 55%);        /* Pink */
```

### Typography Scale

```css
/* Type Scale (rem) */
--text-xs: 0.75rem;     /* 12px - Captions */
--text-sm: 0.875rem;    /* 14px - Body Small */
--text-base: 1rem;      /* 16px - Body */
--text-lg: 1.125rem;    /* 18px - Body Large */
--text-xl: 1.25rem;     /* 20px - Heading 3 */
--text-2xl: 1.5rem;     /* 24px - Heading 2 */
--text-3xl: 1.875rem;   /* 30px - Heading 1 */
--text-4xl: 2.25rem;    /* 36px - Display */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

## Component Architecture

### Core Layout Components

#### 1. AppShell Component
```typescript
interface AppShellProps {
  children: React.ReactNode;
  sidebar?: boolean;
  header?: boolean;
}

// Features:
// - Responsive sidebar with collapsible navigation
// - Persistent header with global controls
// - Entity selector dropdown
// - Time period selector
// - User menu with settings
```

#### 2. NavigationSidebar Component
```typescript
interface NavigationItem {
  id: string;
  label: string;
  icon: LucideIcon;
  href?: string;
  children?: NavigationItem[];
  badge?: string | number;
}

// Hierarchical navigation with:
// - Expandable/collapsible sections
// - Active state indicators
// - Quick action buttons
// - Account balance summaries
```

#### 3. EntitySelector Component
```typescript
interface Entity {
  id: string;
  name: string;
  type: 'S-Corp' | 'LLC' | 'Individual';
  accounts: Account[];
  balance: number;
}

// Global entity filter with:
// - Grouped dropdown (Business/Personal)
// - Multi-select capability
// - Quick "All Entities" toggle
// - Balance preview
```

### Data Display Components

#### 1. HierarchicalDataTable
```typescript
interface HierarchicalDataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  expandable?: boolean;
  groupBy?: keyof T;
  aggregations?: AggregationConfig;
}

// Features:
// - Expandable rows with child data
// - Column sorting and filtering
// - Aggregation rows
// - Export functionality
// - Virtualization for large datasets
```

#### 2. FinancialChart
```typescript
interface ChartConfig {
  type: 'line' | 'bar' | 'area' | 'pie' | 'waterfall';
  data: TimeSeriesData[];
  dimensions: string[];
  measures: string[];
  interactive?: boolean;
}

// Capabilities:
// - Multiple chart types
// - Responsive sizing
// - Interactive tooltips
// - Legend with toggles
// - Zoom and pan
// - Export as image
```

#### 3. MetricCard
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  sparkline?: number[];
  onClick?: () => void;
}

// Dashboard cards with:
// - Formatted values
// - Trend indicators
// - Mini sparkline charts
// - Drill-down capability
```

### Domain-Specific Components

#### 1. AssetAllocationView
```typescript
// Visual breakdown by asset class
// - Donut chart with drill-down
// - Tabular view with percentages
// - Target vs actual comparison
// - Rebalancing suggestions
```

#### 2. TaxSummaryPanel
```typescript
// Comprehensive tax information
// - Federal vs State breakdown
// - Quarterly payment tracking
// - YoY comparisons
// - Georgia exemption calculations
// - Export for tax software
```

#### 3. DocumentViewer
```typescript
// PDF viewing with data overlay
// - Split-screen PDF + extracted data
// - Highlight corresponding sections
// - Confidence indicators
// - Processing status
// - Navigation between documents
```

## State Management Architecture

### Zustand Store Structure

```typescript
// Global UI Store
interface UIStore {
  // Navigation
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  
  // Global Filters
  selectedEntities: string[];
  setSelectedEntities: (entities: string[]) => void;
  
  dateRange: DateRange;
  setDateRange: (range: DateRange) => void;
  
  // View Preferences
  viewMode: 'consolidated' | 'detailed';
  setViewMode: (mode: 'consolidated' | 'detailed') => void;
  
  // Saved Views
  savedViews: SavedView[];
  saveCurrentView: (name: string) => void;
  loadView: (id: string) => void;
}

// Financial Data Store
interface FinancialStore {
  // Cached Calculations
  netWorth: {
    total: number;
    financialAssets: number;
    realAssets: number;
    liabilities: number;
  };
  cashFlow: CashFlowData;
  taxLiability: TaxData;
  
  // Asset Performance
  assetPerformance: Map<string, PerformanceData>;
  
  // Real Assets & Liabilities
  realAssets: RealAsset[];
  liabilities: Liability[];
  
  // Refresh Methods
  refreshNetWorth: () => Promise<void>;
  refreshCashFlow: () => Promise<void>;
  updateAssetValuation: (assetId: string, value: number) => Promise<void>;
  updateLiabilityBalance: (liabilityId: string, balance: number) => Promise<void>;
}

// Real Asset Interface
interface RealAsset {
  id: string;
  entityId: string;
  assetType: 'primary_residence' | 'rental_property' | 'commercial_property' | 'vehicle' | 'other';
  description: string;
  currentValue: number;
  valuationDate: Date;
  monthlyIncome?: number;
  monthlyExpense?: number;
}

// Liability Interface
interface Liability {
  id: string;
  entityId: string;
  realAssetId?: string;
  liabilityType: 'mortgage' | 'home_equity' | 'auto_loan' | 'business_loan' | 'other';
  lenderName: string;
  currentBalance: number;
  interestRate: number;
  monthlyPayment: number;
  escrowAmount?: number;
}
```

### TanStack Query Patterns

```typescript
// Query Keys Factory
const queryKeys = {
  all: ['finance'] as const,
  entities: () => [...queryKeys.all, 'entities'] as const,
  entity: (id: string) => [...queryKeys.entities(), id] as const,
  
  transactions: () => [...queryKeys.all, 'transactions'] as const,
  transactionsByEntity: (entityId: string) => 
    [...queryKeys.transactions(), { entityId }] as const,
  
  documents: () => [...queryKeys.all, 'documents'] as const,
  document: (id: string) => [...queryKeys.documents(), id] as const,
};

// Query Hooks
export const useEntities = () => {
  return useQuery({
    queryKey: queryKeys.entities(),
    queryFn: fetchEntities,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTransactions = (filters: TransactionFilters) => {
  return useQuery({
    queryKey: [...queryKeys.transactions(), filters],
    queryFn: () => fetchTransactions(filters),
    keepPreviousData: true, // For pagination
  });
};
```

## Navigation & Information Architecture

### Primary Navigation Structure

```
Dashboard (Home)
├── Overview
│   ├── Net Worth Summary
│   ├── Cash Flow
│   └── Recent Activity
│
├── Net Worth
│   ├── Complete Breakdown
│   ├── Real Assets
│   ├── Liabilities
│   └── Trends & History
│
├── Accounts
│   ├── By Entity
│   ├── By Institution
│   └── By Asset Class
│
├── Transactions
│   ├── All Activity
│   ├── By Period
│   └── Search & Filter
│
├── Documents
│   ├── Recent Processing
│   ├── Statements
│   └── Tax Forms
│
├── Tax Center
│   ├── Current Year Summary
│   ├── Payment Tracker
│   ├── YoY Comparison
│   └── Projections
│
├── Investments
│   ├── Portfolio Overview
│   ├── Asset Performance
│   ├── Rebalancing
│   └── Strategy Notes
│
├── Reports
│   ├── Standard Reports
│   ├── Custom Reports
│   └── Exports
│
└── Settings
    ├── Entities & Accounts
    ├── Real Assets
    └── Liabilities
    ├── Tax Configuration
    ├── Preferences
    └── Database Controls
```

### Routing Strategy (Next.js App Router)

```
app/
├── (dashboard)/
│   ├── layout.tsx                 # Dashboard shell with sidebar
│   ├── page.tsx                    # Overview dashboard
│   ├── accounts/
│   │   ├── page.tsx                # Accounts list
│   │   └── [id]/page.tsx           # Account detail
│   ├── transactions/
│   │   ├── page.tsx                # Transactions list
│   │   └── [id]/page.tsx           # Transaction detail
│   ├── documents/
│   │   ├── page.tsx                # Documents list
│   │   └── [id]/page.tsx           # Document viewer
│   ├── tax/
│   │   ├── page.tsx                # Tax center
│   │   ├── payments/page.tsx       # Payment tracker
│   │   └── comparison/page.tsx     # YoY comparison
│   ├── investments/
│   │   ├── page.tsx                # Portfolio overview
│   │   └── [symbol]/page.tsx       # Asset detail
│   └── settings/
│       ├── page.tsx                # Settings home
│       ├── entities/page.tsx       # Entity management
│       └── database/page.tsx       # Database controls
│
├── api/
│   ├── entities/route.ts           # Entities API
│   ├── transactions/route.ts       # Transactions API
│   ├── documents/route.ts          # Documents API
│   └── database/
│       ├── start/route.ts          # Start database
│       └── stop/route.ts           # Stop database
│
└── auth/
    ├── login/page.tsx              # Login (Phase 2)
    └── layout.tsx                  # Auth layout
```

## Data Fetching & API Design

### Server Actions (Next.js 14)

```typescript
// app/actions/entities.ts
'use server';

export async function getEntities() {
  const { data, error } = await db
    .from('entities')
    .select('*, accounts(*, institution(*))') 
    .order('name');
    
  if (error) throw new Error(error.message);
  return data;
}

export async function createEntity(entity: NewEntity) {
  const { data, error } = await db
    .from('entities')
    .insert(entity)
    .select()
    .single();
    
  if (error) throw new Error(error.message);
  revalidatePath('/accounts');
  return data;
}
```

### API Route Handlers

```typescript
// app/api/transactions/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const entityId = searchParams.get('entityId');
  const startDate = searchParams.get('startDate');
  const endDate = searchParams.get('endDate');
  
  const query = db
    .from('transactions')
    .select(`
      *,
      document:documents(*),
      account:accounts(*, entity:entities(*))
    `);
    
  if (entityId) {
    query.eq('account.entity_id', entityId);
  }
  
  if (startDate && endDate) {
    query.gte('transaction_date', startDate)
         .lte('transaction_date', endDate);
  }
  
  const { data, error } = await query.order('transaction_date', { ascending: false });
  
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
  
  return NextResponse.json(data);
}
```

## Performance Optimization Strategies

### 1. Code Splitting & Lazy Loading

```typescript
// Lazy load heavy components
const PDFViewer = dynamic(() => import('@/components/PDFViewer'), {
  loading: () => <PDFViewerSkeleton />,
  ssr: false,
});

const ChartsPanel = dynamic(() => import('@/components/ChartsPanel'), {
  loading: () => <ChartsSkeleton />,
});
```

### 2. Data Virtualization

```typescript
// Use TanStack Virtual for large lists
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualTransactionList({ transactions }) {
  const virtualizer = useVirtualizer({
    count: transactions.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 10,
  });
  
  // Render only visible items
}
```

### 3. Optimistic Updates

```typescript
const mutation = useMutation({
  mutationFn: updateTransaction,
  onMutate: async (newTransaction) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: queryKeys.transactions() });
    
    // Snapshot previous value
    const previous = queryClient.getQueryData(queryKeys.transactions());
    
    // Optimistically update
    queryClient.setQueryData(queryKeys.transactions(), (old) => {
      return updateTransactionInList(old, newTransaction);
    });
    
    return { previous };
  },
  onError: (err, newTransaction, context) => {
    // Rollback on error
    queryClient.setQueryData(queryKeys.transactions(), context.previous);
  },
  onSettled: () => {
    // Always refetch after error or success
    queryClient.invalidateQueries({ queryKey: queryKeys.transactions() });
  },
});
```

### 4. Strategic Caching

```typescript
// Cache configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      cacheTime: 10 * 60 * 1000,     // 10 minutes
      refetchOnWindowFocus: false,
      retry: 2,
    },
  },
});

// Prefetch critical data
export async function prefetchDashboardData() {
  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: queryKeys.entities(),
      queryFn: fetchEntities,
    }),
    queryClient.prefetchQuery({
      queryKey: queryKeys.netWorth(),
      queryFn: calculateNetWorth,
    }),
  ]);
}
```

## Responsive Design Strategy

### Breakpoint System

```css
/* Tailwind Breakpoints */
sm: 640px   /* Tablet Portrait */
md: 768px   /* Tablet Landscape */
lg: 1024px  /* Desktop */
xl: 1280px  /* Wide Desktop */
2xl: 1536px /* Ultra-wide */
```

### Responsive Patterns

```typescript
// Responsive sidebar
<aside className="
  fixed inset-y-0 left-0 z-50 w-64 
  transform transition-transform duration-200
  -translate-x-full lg:translate-x-0
  lg:static lg:inset-0
">

// Responsive grid
<div className="
  grid gap-4
  grid-cols-1 
  sm:grid-cols-2 
  lg:grid-cols-3 
  xl:grid-cols-4
">

// Responsive table
<div className="overflow-x-auto">
  <table className="min-w-full">
    {/* Hide columns on mobile */}
    <td className="hidden sm:table-cell">
```

## Security Considerations

### Data Protection

1. **Client-Side Security**
   - No sensitive data in localStorage
   - Use httpOnly cookies for auth tokens
   - Implement CSP headers
   - Sanitize all user inputs

2. **API Security**
   - Rate limiting on all endpoints
   - Input validation with Zod
   - SQL injection prevention via parameterized queries
   - CORS configuration for local development only

3. **PDF Handling**
   - Validate file types before processing
   - Sanitize extracted text
   - Store PDFs in secure location
   - Implement access controls

## Testing Strategy

### Unit Testing

```typescript
// Component testing example
describe('EntitySelector', () => {
  it('should display all entities when opened', async () => {
    const { getByRole, findByText } = render(
      <EntitySelector entities={mockEntities} />
    );
    
    const trigger = getByRole('button');
    await userEvent.click(trigger);
    
    expect(await findByText('Milton Preschool Inc')).toBeInTheDocument();
    expect(await findByText('Entity A Corp')).toBeInTheDocument();
  });
});
```

### Integration Testing

```typescript
// API testing example
describe('GET /api/transactions', () => {
  it('should filter by entity', async () => {
    const response = await request(app)
      .get('/api/transactions')
      .query({ entityId: 'test-entity-id' });
      
    expect(response.status).toBe(200);
    expect(response.body).toHaveLength(10);
    expect(response.body[0].account.entity_id).toBe('test-entity-id');
  });
});
```

### E2E Testing with Playwright

```typescript
test('complete tax payment workflow', async ({ page }) => {
  await page.goto('/tax/payments');
  
  // Record new payment
  await page.click('text=Record Payment');
  await page.fill('[name=amount]', '45678');
  await page.selectOption('[name=type]', 'federal');
  await page.click('text=Save Payment');
  
  // Verify payment appears
  await expect(page.locator('text=$45,678')).toBeVisible();
});
```

## Deployment Architecture

### Local Development Setup

```yaml
Requirements:
  - Node.js 18+
  - PostgreSQL (via Supabase)
  - 4GB RAM minimum
  - Modern browser

Environment Variables:
  - DATABASE_URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
  - NEXT_PUBLIC_APP_URL: http://localhost:3000
  
Scripts:
  - npm run dev: Start development server
  - npm run build: Production build
  - npm run test: Run test suite
  - npm run db:start: Start local Supabase
```

### Production Deployment (Phase 2)

```yaml
Platform: Vercel / Self-hosted
Database: Supabase Cloud / Self-hosted PostgreSQL
Storage: Local filesystem / S3-compatible
CDN: Cloudflare / Vercel Edge Network
Monitoring: Sentry / DataDog
```

## Accessibility Standards

### WCAG 2.1 Level AA Compliance

- **Keyboard Navigation:** Full keyboard support
- **Screen Readers:** Proper ARIA labels
- **Color Contrast:** 4.5:1 minimum ratio
- **Focus Indicators:** Visible focus states
- **Responsive Text:** Scalable typography
- **Error Messages:** Clear, actionable errors
- **Loading States:** Announced to screen readers

## Documentation & Developer Experience

### Component Documentation

```typescript
/**
 * EntitySelector - Global entity filter component
 * 
 * @example
 * <EntitySelector
 *   entities={entities}
 *   selected={['entity-1', 'entity-2']}
 *   onChange={(selected) => console.log(selected)}
 *   multiple={true}
 * />
 */
```

### Storybook Integration

```typescript
export default {
  title: 'Components/EntitySelector',
  component: EntitySelector,
  parameters: {
    docs: {
      description: {
        component: 'Global entity filtering component with multi-select support',
      },
    },
  },
};

export const Default = {
  args: {
    entities: mockEntities,
    selected: [],
  },
};
```

## Success Criteria

### Performance Metrics
- Initial page load: < 2 seconds
- Time to Interactive: < 3 seconds
- Lighthouse score: > 90
- Bundle size: < 500KB (initial)

### User Experience Metrics
- Task completion rate: > 95%
- Error rate: < 2%
- User satisfaction: > 4.5/5
- Time to find transaction: < 10 seconds

### Technical Metrics
- Test coverage: > 80%
- TypeScript coverage: 100%
- Accessibility score: 100%
- SEO score: > 90

---

*This technical design provides a comprehensive blueprint for building a professional-grade financial management frontend that matches the sophistication of eMoney Advisor while being optimized for your specific multi-entity use case.*