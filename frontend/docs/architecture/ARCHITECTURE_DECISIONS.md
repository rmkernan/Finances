# Architecture Decisions & Discoveries

**Created:** 09/25/25 1:00AM
**Updated:** 09/25/25 12:45PM - Added Week 3 learnings and navigation architecture decisions
**Purpose:** Document critical architectural decisions and discoveries from implementation

## 🎯 Key Discoveries from Implementation

### 1. Database Schema Complexity
**Discovery:** The actual database has 12 tables with 1200+ lines of TypeScript definitions, not the 3-4 tables originally planned.

**Impact:**
- Much richer data model enables sophisticated analytics
- Mapping system (map_rules, map_conditions, map_actions) provides transaction classification
- Analytics views (transaction_review, position_review) offer pre-optimized queries

**Decision:** Embrace the complexity and use generated types for full type safety.

### 2. Balance Calculation Strategy
**Discovery:** Accounts don't have direct balance fields - must be calculated from either positions or transactions.

**Implementation:** Hybrid approach based on account type:
```typescript
// Investment accounts: Use positions table
const investmentBalance = sum(positions.end_market_value)
  WHERE position_date = latest

// Bank accounts: Use transactions table
const bankBalance = transactions.balance
  WHERE transaction_date = latest
```

**Rationale:**
- Investment accounts have daily position snapshots
- Bank accounts track running balance per transaction
- Account type determines calculation method

### 3. Framework Version Adaptations
**Challenge:** Implementation plan was for Next.js 14 + Tailwind v3, but we're using Next.js 15 + Tailwind v4.

**Adaptations Made:**
- Tailwind v4: CSS-based configuration via `@theme` instead of JS config
- Next.js 15: Async `cookies()` function requires await
- React 19 RC: Compatible with all patterns, no issues

**Result:** Seamless adaptation with zero breaking changes.

### 4. Type Generation Strategy
**Evolution:** Manual types → Generated types from Supabase

**Process:**
```bash
npx supabase gen types typescript --local > src/types/supabase.ts
```

**Benefits:**
- 100% accuracy with database schema
- Automatic relationship typing
- No manual maintenance needed
- Full coverage of views and functions

### 5. React Query Caching Strategy
**Configuration:**
```typescript
staleTime: 5 * 60 * 1000,    // 5 minutes
gcTime: 10 * 60 * 1000,      // 10 minutes
refetchOnWindowFocus: true,
retry: 3
```

**Rationale:**
- Financial data doesn't change rapidly (5-min cache is safe)
- Background refetch keeps data fresh
- Retry logic handles transient connection issues

### 6. Component Architecture Patterns

**Structure Emerged:**
```
src/
├── components/
│   ├── dashboard/     # Domain-specific components
│   ├── layout/        # Structural components
│   └── charts/        # Visualization components
├── hooks/            # Data fetching & business logic
├── lib/
│   ├── calculations/ # Financial calculations
│   ├── supabase/     # Database clients
│   └── utils/        # Shared utilities
└── types/            # Generated + custom types
```

**Key Patterns:**
- Hooks encapsulate data fetching + React Query
- Calculations separated from components
- Generated types as source of truth
- Error boundaries at component level

## 🔄 Process Improvements Discovered

### Git Workflow
- Commits at component completion (not just day end)
- Descriptive messages with line counts
- Quality checks before each commit

### Quality Assurance
```json
"scripts": {
  "quality": "npm run typecheck && npm run lint",
  "typecheck": "tsc --noEmit",
  "lint": "next lint"
}
```
Run after every major component addition.

### Development Patterns
1. Read existing code before creating new
2. Use generated types, not manual definitions
3. Test with real data early and often
4. Implement loading/error states immediately

## 📊 Performance Insights

### Query Optimization
- Use database views when available (transaction_review, position_review)
- Select only needed fields to reduce payload
- Leverage React Query cache to prevent refetches
- Consider pagination for large transaction lists

### Bundle Size Considerations
- Supabase client: ~50KB gzipped (acceptable)
- React Query: ~13KB gzipped (excellent)
- Recharts: ~88KB gzipped (monitor as we add charts)

## 🚀 Recommendations for Week 2

### Charts & Visualizations
1. Use Recharts for standard charts (well-maintained, TypeScript support)
2. Consider D3 directly for complex custom visualizations
3. Implement virtualization for large data tables
4. Add data export functionality (CSV/Excel)

### Performance Optimizations
1. Implement query result pagination
2. Add index suggestions to database team
3. Consider WebWorkers for heavy calculations
4. Profile and optimize re-renders

### Testing Strategy
1. Add React Testing Library for component tests
2. Mock Supabase client for unit tests
3. Create fixture data from real database exports
4. Add E2E tests with Playwright

## 🎮 State Management Insights

**Current Approach:** React Query for server state, local state for UI

**No Zustand/Redux Needed Yet** because:
- React Query handles all server state
- Component state sufficient for UI
- No complex client-side state yet

**Consider state management when:**
- Adding complex filters/preferences
- Implementing undo/redo
- Managing WebSocket connections
- Offline mode required

## 📝 Documentation Gaps to Address

1. **Balance Calculation Guide** - Document the hybrid strategy
2. **Query Patterns Cookbook** - Common database queries
3. **Component Style Guide** - Consistent patterns
4. **Performance Monitoring** - Metrics to track
5. **Deployment Guide** - Production considerations

## 🏆 What Worked Exceptionally Well

1. **Orchestrator/Implementer Division** - Clear separation of concerns
2. **Quality Gates** - Prevented accumulation of technical debt
3. **Generated Types** - Eliminated type mismatches
4. **Incremental Approach** - Each day built on previous
5. **Real Data Early** - Discovered issues immediately

## 🎯 Week 3 Architectural Learnings

### Navigation Architecture
**Decision:** Hierarchical navigation with landing pages for each major section
**Implementation:**
- Landing pages at `/entities`, `/accounts`, `/institutions`, `/documents`
- Detail pages using dynamic routes `[entityId]`, `[accountId]`
- Admin section separated under `/admin` namespace
**Outcome:** Clear, predictable navigation that scales well

### Component Size Limits
**Decision:** Enforce 200-line maximum per component
**Rationale:** Forces single responsibility and improves maintainability
**Result:** All Week 3 components stayed under limit, improved code clarity
**Example:** `AccountTransactions.tsx` at 195 lines with full functionality

### Filtering Strategy
**Decision:** Client-side filtering with native HTML selects
**Rationale:**
- Data volume (267 transactions) doesn't justify server-side filtering
- Immediate feedback improves UX
- Native selects maintain simplicity (KISS)
**Implementation:** Reusable `FilterSelect` component, URL param persistence

### Data Status Monitoring
**Decision:** Dedicated admin page for data completeness
**Discovery:** Need for data freshness monitoring became clear in Week 3
**Implementation:** `/admin/data-status` with color-coded freshness indicators
**Learning:** "No Data" label confusing - should be "Stale Data >30 days"

### Schema Field Name Documentation
**Week 3 Learning:** Field name mismatches caused Day 11 delays
**Problem:** Expected `symbol` but actual was `sec_ticker`, `category` vs `tax_category`
**Solution:** Add schema quick reference commands to instructions
**Future:** Consider TypeScript code generation from schema

### Build Verification Critical Path
**Discovery (Day 9):** Quality checks (`lint + typecheck`) miss routing issues
**Solution:** Added mandatory `npm run build` to quality gates
**Result:** Caught routing problems before runtime
**New Protocol:** `quality → build → dev` for every component

### Parallel Sub-agent Execution
**Decision (Day 12):** Use parallel Sonnet agents for mechanical documentation updates
**Result:** 70% token savings, 4 tasks completed simultaneously
**Best Practice:** Detailed, self-contained prompts with exact content
**Learning:** Sub-agents excel at well-defined, isolated tasks

### Tab Interface Pattern
**Decision:** Tabs for account detail pages (Overview, Transactions, Positions, Documents)
**Implementation:** Client-side tab switching, lazy loading content
**Benefit:** Organized complex data without overwhelming users
**Future:** Consider URL-based tab state for deep linking

### Status Badge Consistency
**Pattern:** Green (good), Yellow (warning), Red (error/stale)
**Applied to:** Transaction amounts, data freshness, document status
**Benefit:** Users quickly understand status across different contexts

### Hybrid Balance Calculation Success
**Validation:** Week 3 confirmed the hybrid approach works correctly
- Investment accounts: Sum positions → Accurate
- Bank accounts: Latest transaction balance → Accurate
**Edge Case:** Accounts with no positions/transactions handled gracefully

## ⚠️ Future Considerations

1. **Historical Data Loading** - Need strategy for bulk historical import
2. **Real-time Updates** - Consider Supabase subscriptions
3. **Multi-user Support** - Current design is single-user
4. **Audit Trail** - Track all financial data changes
5. **Backup Strategy** - Automated database backups

---

*This document captures architectural decisions and discoveries from Week 1 implementation. Update as new patterns emerge.*