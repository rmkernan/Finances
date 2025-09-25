# Personal Wealth Manager - Technical Design

## Purpose
Multi-entity financial dashboard with AI-powered analysis capabilities for tracking wealth across multiple business entities and personal accounts.

## Architecture

### Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL) - localhost:54322
- **Charts**: Recharts + ApexCharts
- **Tables**: TanStack Table
- **State**: React Query (server state), Zustand (client state)
- **Export**: xlsx (Excel), jsPDF (PDF)

### Data Flow
```
Supabase PostgreSQL (localhost:54322)
         ↓
    React Query (caching layer)
         ↓
    Transform/Format Layer
         ↓
    React Components
         ↓
    User Interface
         ↑↓
    AI Assistant (Phase 4)
```

### Core Pages Structure
```
/                                        # Global dashboard (all entities)
/entities/[id]                          # Entity view (e.g., Milton Preschool)
/entities/[id]/institutions/[id]        # Institution view (e.g., Fidelity at Milton)
/entities/[id]/accounts/[id]            # Account detail (e.g., Brokerage Z40-394067)
/reports                                # Saved reports
/chat                                   # AI assistant (Phase 4)
```

### Component Hierarchy
```
<RootLayout>                    # App-wide layout
  <Sidebar>                     # Navigation (Fidelity-style)
    <Logo />
    <NavItems />
    <AccountsList />
  </Sidebar>
  <MainArea>
    <TopBar>                    # Breadcrumbs + user info
      <Breadcrumbs />
      <QuickActions />
      <UserMenu />
    </TopBar>
    <PageContent>               # Dynamic based on route
      <Dashboard>               # Specific page component
        <MetricsRow />          # KPI cards
        <ChartsSection />       # Visualizations
        <TablesSection />       # Data grids
      </Dashboard>
    </PageContent>
  </MainArea>
  <AIAssistant />              # Floating/docked (Phase 4)
</RootLayout>
```

### Database Schema (Key Tables)
```sql
-- Current data in production
entities (2 records)
  - kernan_family (individual)
  - milton_preschool (s_corp)

institutions (1 record)
  - fidelity (brokerage)

accounts (3 records)
  - Z24-527872 (Kernan Joint Brokerage)
  - Z27-375656 (Kernan Cash Management)
  - Z40-394067 (Milton Preschool Brokerage)

transactions (~1000s of records)
  - All historical transactions

positions (100s of records)
  - Current holdings snapshots

documents (10s of records)
  - Processed PDFs with metadata
```

### Design System

#### Colors (Fidelity-Inspired)
```scss
$primary-green: #00945F;         // Fidelity's signature green
$surface-white: #FFFFFF;
$background-gray: #F7F7F7;       // Light gray background
$text-primary: #1A1A1A;          // Near black
$text-secondary: #666666;        // Gray text
$positive-green: #00A86B;        // Gains/positive
$negative-red: #DC143C;          // Losses/negative
$chart-blue: #0066CC;            // Primary chart color
$warning-amber: #FFC107;         // Warnings
$border-light: #E5E5E5;          // Borders/dividers
```

#### Typography
```scss
// Font stack
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

// Sizes
$text-xs: 0.75rem;     // 12px - metadata
$text-sm: 0.875rem;    // 14px - secondary text
$text-base: 1rem;      // 16px - body text
$text-lg: 1.125rem;    // 18px - section headers
$text-xl: 1.25rem;     // 20px - page headers
$text-2xl: 1.5rem;     // 24px - major headers
$text-3xl: 2rem;       // 32px - hero numbers

// Number formatting
.currency {
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}
```

#### Spacing
```scss
// 4px base unit (Tailwind default)
$space-1: 0.25rem;  // 4px
$space-2: 0.5rem;   // 8px
$space-3: 0.75rem;  // 12px
$space-4: 1rem;     // 16px
$space-6: 1.5rem;   // 24px
$space-8: 2rem;     // 32px
```

#### Breakpoints
```scss
$mobile: 640px;     // sm
$tablet: 768px;     // md
$desktop: 1024px;   // lg
$wide: 1280px;      // xl
```

### Performance Targets
- **Initial Load**: < 3 seconds
- **Route Change**: < 500ms
- **Data Refresh**: < 1 second
- **Chart Render**: < 500ms
- **Table Sort/Filter**: < 100ms
- **Search Results**: < 200ms

### Security Considerations
- All data local (no cloud sync)
- Supabase RLS policies enforced
- No sensitive data in localStorage
- Account numbers masked in UI
- HTTPS only in production

### Browser Support
- Chrome 90+ (primary)
- Safari 14+ (secondary)
- Firefox 88+ (secondary)
- Edge 90+ (supported)

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode support
- Proper ARIA labels

### State Management Strategy
```typescript
// Server state (React Query)
- All data from Supabase
- Caching with 5-minute stale time
- Background refetch on focus

// Client state (Zustand)
- Selected entity/account
- Date ranges
- Filter preferences
- UI state (sidebar collapsed, etc.)

// Local storage
- User preferences
- Saved report configurations
- Recently viewed items
```

### Error Handling
- Network errors: Retry with exponential backoff
- Data errors: Show fallback UI with error message
- Auth errors: Redirect to login (future)
- Validation errors: Inline field errors

### Testing Strategy (Future)
- Unit tests for utilities
- Integration tests for API calls
- E2E tests for critical paths
- Visual regression tests for charts