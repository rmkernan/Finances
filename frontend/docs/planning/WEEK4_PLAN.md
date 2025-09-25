# Week 4 Implementation Plan: Advanced Features & Optimization

**Created:** 09/25/25 12:45PM
**Updated:** 09/25/25 1:30PM - Updated priorities based on user feedback
**Purpose:** Strategic plan for Week 4 based on Week 3 learnings and discoveries

## 📚 Prerequisites

Before starting Week 4, understand:
1. **Week 3 Accomplishments:** Full navigation architecture with 12/12 days complete
2. **Current Data:** 3 active accounts, 152 positions, 267 transactions
3. **Technical Foundation:** React Query, TypeScript, KISS principles maintained
4. **Key Learnings:** Schema field names matter, build checks critical, 200-line limits work

## 🎯 Week 4 Strategic Priorities

Based on Week 3 discoveries and user needs, prioritized features:

### Priority 1: Enhanced Search (Days 13-14)
**Why:** 267 transactions growing, need better discovery
- Global search bar in TopBar
- Cross-entity transaction search
- Search by amount ranges
- Search history/recent searches

### Priority 2: Advanced Filtering (Days 15-16)
**Why:** Current filters basic, need month-oriented approach
- **Month-oriented data loading:** Default to current month for all views
- Date range picker for custom ranges
- Amount range filters
- Multi-select filters (select multiple entities)
- Saved filter sets (localStorage)

### Priority 3: Performance & Polish (Days 17-18)
**Why:** Month-oriented loading and larger datasets
- **Month-oriented architecture:** Default all queries to current month
- Virtual scrolling for large monthly data
- Lazy load chart data
- Optimize React Query cache
- Lighthouse audit improvements

### Priority 4: Documents Enhancement (Day 19)
**Why:** User requested improvements
- Add "Load Date" column showing when holdings/activities were loaded
- Make document names clickable links
- PDF viewer in new window for source documents

### Priority 5: Data Quality Tools (Day 20)
**Why:** Future enhancement - leave as planned
- Refine status labels ("Stale" not "No Data")
- Configurable freshness thresholds
- Email alerts for stale accounts
- Data refresh automation hooks

## 📋 Day-by-Day Implementation

### Day 13: Global Search Implementation

**Goal:** Add search bar to TopBar

**Tasks:**
1. Create `GlobalSearch` component with dropdown results
2. Build `useGlobalSearch` hook with debouncing
3. Index searchable fields (entity names, account names, descriptions)
4. Show grouped results (Entities, Accounts, Transactions)
5. Keyboard navigation (arrow keys, enter)

**Technical Approach:**
```typescript
// Reuse existing transaction data
// Format: Date, Account, Description, Category, Amount, Balance
// Use browser download API (no server needed)
// Include metadata header (export date, filters applied)
```

### Day 14: Search Results & History

**Goal:** Enhanced search experience

**Tasks:**
1. Create `/search` results page
2. Add search filters (type, date range, amount)
3. Implement search history (localStorage)
4. Add "recent searches" dropdown
5. Search analytics (most searched terms)

### Day 15: Month-Oriented Data Architecture

**Goal:** Implement default monthly loading

**Tasks:**
1. Update all data queries to default to current month
2. Add month selector component (dropdown with recent months)
3. Modify transaction/position queries for month filtering
4. Add "View All" option for full dataset
5. Update React Query cache keys to include month

### Day 16: Date Range & Advanced Filtering

**Goal:** Custom date ranges and filter improvements

**Tasks:**
1. Create `DateRangePicker` component with presets
2. Add to transactions page, account details, documents
3. Upgrade FilterSelect for multi-select
4. Implement saved filter sets (localStorage)
5. Quick filter buttons (e.g., "Current Month", "Last Quarter")

### Day 17: Performance Optimization for Monthly Data

**Goal:** Optimize for month-oriented approach

**Tasks:**
1. Implement virtual scrolling for large monthly datasets
2. Optimize React Query cache for monthly patterns
3. Add month-based data prefetching
4. Lazy load chart data by month
5. Bundle analysis and optimization

### Day 18: Performance Polish & Testing

**Goal:** Complete performance improvements

**Tasks:**
1. React.memo for expensive components
2. Lighthouse audit and fixes
3. Test with large monthly datasets
4. Optimize re-renders during month changes
5. Performance monitoring setup

### Day 19: Documents Page Enhancement

**Goal:** Improve documents page with user requested features

**Tasks:**
1. Add "Load Date" column showing when holdings/activities were processed
2. Make document names clickable links
3. Implement PDF viewer opening in new window
4. Add document type icons for better visual identification
5. Improve sorting by load date and document date

**Technical Approach:**
```typescript
// Add load_date to documents table query
// Use window.open() for PDF viewing
// Consider PDF.js for inline viewing
```

### Day 20: Data Quality Enhancement (Future)

**Goal:** Better monitoring and alerts (deferred for now)

**Tasks:**
1. Refine data status page labels
2. Add configuration modal for thresholds
3. Create alert system for stale data
4. Add "last successful sync" tracking
5. Data quality score dashboard

## ✅ Week 4 Success Criteria

**Functional:**
- ✅ Users can export all data to CSV/PDF
- ✅ Global search works across all entities
- ✅ Date range filtering on all data views
- ✅ Performance handles 1000+ transactions smoothly
- ✅ Data quality alerts prevent stale data

**Technical:**
- ✅ Bundle size under 400KB
- ✅ Lighthouse score > 90
- ✅ All components under 200 lines
- ✅ TypeScript coverage 100%
- ✅ Zero console errors

## 🚫 What NOT to Build (KISS)

**Avoid:**
- Complex report builders (keep exports simple)
- Real-time sync (not needed yet)
- Multi-user features (single user for now)
- Cloud storage integration
- Mobile app considerations

**Defer to Week 5+:**
- AI insights
- Predictive analytics
- Automated categorization
- Tax optimization suggestions
- Investment recommendations

## 💡 Technical Considerations

### Export Architecture
```typescript
// Client-side only initially
// Use Web Workers for large exports
// Streaming for very large datasets
// Progress indicators for long operations
```

### Search Architecture
```typescript
// Client-side search initially
// Consider Fuse.js for fuzzy search
// Index in React Query cache
// Debounce at 300ms
```

### Performance Strategy
- Code splitting by route
- Lazy load heavy components
- Progressive enhancement
- Skeleton screens everywhere

## 📊 Risk Mitigation

**Risks:**
1. **Export Memory Issues** → Stream large datasets
2. **Search Performance** → Implement pagination
3. **Filter Complexity** → Keep UI simple
4. **Date Picker UX** → Use preset ranges
5. **Bundle Size** → Monitor continuously

## 🎯 Week 5 Preview

After Week 4 exports and search:
- AI-powered insights
- Automated categorization
- Tax preparation tools
- Investment analysis
- Multi-entity reports

## 📝 Daily Checkpoint Protocol

Enhanced with schema verification:
1. **NEW: Verify schema before coding** (see DEVELOPMENT_GOTCHAS.md)
2. Read relevant documentation first
3. **NEW: Check existing patterns for similar features**
4. Run quality gates after each component
5. Test in browser before committing
6. Keep components under 200 lines
7. Update SESSION_STATE.md daily

**Required Pre-Development Commands:**
```bash
# Before EVERY coding session
grep "interface [TableName]" src/types/supabase.ts -A 30
grep -r "from('[table]')" src/hooks/  # Find patterns
npm run type-check -- --watch  # Keep running
```

---

*Week 4 plan based on Week 3 learnings: User needs data export, search is essential at current scale, and performance optimization ensures future readiness.*