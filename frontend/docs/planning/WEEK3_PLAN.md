# Week 3 Implementation Plan: Complete Navigation Hierarchy

**Created:** 09/25/25 9:50AM
**Updated:** 09/25/25 9:53AM - Consolidated Day 9 to include entities, accounts, and documents landing pages
**Updated:** 09/25/25 10:34AM - Enhanced Day 10 with filtering, added Days 11-12 with account details and dashboard enhancements
**Purpose:** Build landing pages for main navigation items to complete the information architecture

## 📚 Prerequisites

Before starting, ensure you understand:
1. **KISS Principles** from IMPLEMENTATION_PLAN.md (lines 134-153)
2. **Quality Requirements** from IMPLEMENTATION_PLAN.md (lines 10-28)
3. **Documentation Standards** from IMPLEMENTATION_PLAN.md (lines 30-77)
4. **TypeScript Standards** from IMPLEMENTATION_PLAN.md (lines 79-133)

## 🎯 Week 3 Objectives

Fix the critical navigation gap: Users can click sidebar items but landing pages don't exist!

**Current Problems:**
- `/entities` → 404 (needs landing page)
- `/accounts` → 404 (needs landing page)
- `/institutions` → Not in nav (needs page + nav item)
- `/documents` → Not implemented

## 📋 Implementation Schedule

### Day 9: Core Landing Pages (Entities, Accounts, Documents)

#### Task 1: Entities Landing Page

**Create `/app/entities/page.tsx`**
```typescript
// Requirements:
// - Grid layout of entity cards (reuse EntityGrid component if possible)
// - Show all entities with summary data
// - Total portfolio value at top
// - Responsive grid (1 col mobile, 2 tablet, 3 desktop)
// - Click navigates to /entities/[entityId]
// - Keep under 150 lines
```

**Create `useEntitiesOverview` hook**
```typescript
// src/hooks/useEntitiesOverview.ts
// - Fetch all entities with calculated totals
// - Include account counts per entity
// - Direct Supabase queries (KISS)
```

#### Task 2: Accounts Landing Page

**Create `/app/accounts/page.tsx`**
```typescript
// Requirements:
// - Table view of ALL accounts across entities
// - Columns: Account Name, Institution, Type, Entity, Balance
// - Sortable by balance (click column header)
// - Show tax treatment with color coding
// - Click row navigates to entity page (for now)
// - Keep under 200 lines
```

**Create `useAllAccounts` hook**
```typescript
// src/hooks/useAllAccounts.ts
// - Fetch accounts with joins to entities & institutions
// - Calculate balances using existing logic
// - Return sorted by balance descending
```

#### Task 3: Documents Landing Page

**Add to Sidebar Navigation**
```typescript
// src/components/layout/Sidebar.tsx
// Add: { href: '/documents', label: 'Documents', icon: FileText }
```

**Create `/app/documents/page.tsx`**
```typescript
// Requirements:
// - Table view of documents
// - Columns: Name, Type, Date, Entity, Status
// - Sort by date (newest first)
// - Status badges: Processed (green), Pending (yellow), Error (red)
// - Keep under 200 lines
```

**Create `useDocuments` hook**
```typescript
// src/hooks/useDocuments.ts
// - Fetch from documents table
// - Join with entities for entity name
// - Order by created_at DESC
```

#### Implementation Order:
1. Start with Entities (simplest, can reuse EntityGrid)
2. Then Accounts (table pattern from TransactionList)
3. Finally Documents (similar to Accounts)

#### Quality Gates:
After EACH landing page:
```bash
npm run quality  # Must pass
npm run dev      # Test navigation
git commit -m "Day 9: [Page] landing page"
```

### Day 10: Institutions Landing & Basic Filtering

#### Task 1: Create Institutions Landing Page

**Add to Sidebar Navigation**
```typescript
// src/components/layout/Sidebar.tsx
// Add: { href: '/institutions', label: 'Institutions', icon: Building2 }
```

**Create `/app/institutions/page.tsx`**
```typescript
// Requirements:
// - Card grid of institutions
// - Show: Name, Type, # of Accounts, Total Value
// - Account type breakdown per institution
// - Status indicator (active/inactive)
// - Keep under 150 lines
```

**Create `useInstitutions` hook**
```typescript
// src/hooks/useInstitutions.ts
// - Aggregate data by institution
// - Count accounts and sum values
// - Group by institution type
```

#### Task 2: Add Basic Filtering to All Landing Pages

**Create Reusable Filter Components**
```typescript
// src/components/ui/FilterSelect.tsx
// - Generic select dropdown for filtering
// - Props: options, value, onChange, placeholder
// - Keep simple - native HTML select
```

**Add Filters to Each Page:**

1. **Entities Page** (`/entities`)
   - Filter by entity type (All, Individual, S-Corp, LLC)

2. **Accounts Page** (`/accounts`)
   - Filter by institution (dropdown)
   - Filter by account type (checking, savings, investment)
   - Filter by entity (dropdown)

3. **Documents Page** (`/documents`)
   - Filter by status (All, Processed, Pending, Error)
   - Filter by entity (dropdown)

4. **Institutions Page** (`/institutions`)
   - Filter by type (All, Bank, Brokerage, Credit Union)
   - Filter by status (All, Active, Inactive)

**Implementation Notes:**
- Use URL search params to maintain filter state
- Filters should update immediately (no Apply button)
- Show result count: "Showing X of Y items"
- Keep it simple - just dropdowns, no complex UI

### Day 11: Individual Account Detail Pages

#### Create Account Detail Pages
```typescript
// src/app/accounts/[accountId]/page.tsx
// - Account header with balance
// - Transactions table for this account
// - Positions table (for investment accounts)
// - Recent activity chart
```

#### Update Navigation
- Accounts landing page rows → link to detail pages
- Entity page account lists → link to detail pages

### Day 12: Dashboard Enhancements & Data Status

#### Enhance Main Dashboard
```typescript
// Updates to src/app/page.tsx
// - Add "View All →" links to cards
// - Quick stats bar (4 entities, 12 accounts, etc.)
// - Recent documents widget (last 5)
```

#### Create Data Status Page
```typescript
// src/app/admin/data-status/page.tsx
// - Table showing data completeness per account
// - Which accounts have positions/transactions
// - Last update dates
// - Missing data alerts
// - Add to sidebar under "Admin" section
```

### Week 4 Preview (Future Work)
- Advanced filtering with date ranges
- Export functionality for all landing pages
- Bulk operations (multi-select)
- Search across all entities/accounts
- Performance optimizations as needed

## ✅ Quality Gates (MANDATORY)

After EACH component:
```bash
npm run quality     # MUST pass - zero errors
npm run dev         # MUST compile
# Test in browser - verify no console errors
git add -A
git commit -m "Week 3: [Component name]"
```

## 🚫 What NOT to Build (KISS)

**Avoid:**
- Individual account detail pages (not yet)
- Complex filtering UI (simple selects only)
- Bulk operations (not yet)
- Edit capabilities (read-only for now)
- Custom routing logic (use Next.js defaults)

**Keep Simple:**
- Reuse existing components where possible
- Direct Supabase queries (no abstraction)
- Native HTML inputs for filters
- Standard Next.js routing

## 📊 Success Metrics

Week 3 is complete when:
- ✅ All sidebar links work (no 404s)
- ✅ Users can see all entities at `/entities`
- ✅ Users can see all accounts at `/accounts`
- ✅ Users can see all institutions at `/institutions`
- ✅ Users can see all documents at `/documents`
- ✅ All pages load in < 2 seconds
- ✅ Mobile responsive
- ✅ TypeScript/ESLint clean

## 🎨 UI Patterns to Follow

Use consistent patterns from Week 1-2:
- **Loading:** Use SkeletonCard and SkeletonTable
- **Empty States:** Use EmptyState component
- **Currency:** Use formatCurrency utility
- **Colors:** Fidelity green (#00945F) for primary
- **Icons:** Use lucide-react consistently

## 📝 Component Size Limits

Enforce simplicity through size constraints:
- Landing pages: < 200 lines
- Hooks: < 100 lines
- Reusable components: < 150 lines
- No file should exceed 250 lines

## 🔄 Daily Flow

1. **Start of Day:**
   ```bash
   git pull
   npm run dev
   # Review existing code for patterns
   ```

2. **During Development:**
   - Write component
   - Run `npm run quality`
   - Fix any issues
   - Test in browser
   - Commit

3. **End of Day:**
   - Verify all pages work
   - Check responsive design
   - Update progress in response

## 💡 Quick Reference

**Existing Patterns to Reuse:**
- `EntityGrid` component for entity cards
- `formatCurrency()` for money display
- `useMultiEntityDashboard()` as reference
- `TransactionList` table patterns
- `PortfolioSummaryCard` layout patterns

**Database Tables:**
- `entities` - Business entities and individuals
- `accounts` - All financial accounts
- `institutions` - Banks, brokerages, etc.
- `documents` - Uploaded/processed documents
- `doc_level_data` - Document metadata

---

**Remember: Simple working pages > Complex perfect pages**

Start with Day 9: Entities Landing Page!