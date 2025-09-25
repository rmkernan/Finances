# 📖 Quick Reference

**Created:** 09/25/25 1:05PM
**Purpose:** Useful patterns and gotchas discovered during implementation

## Code Quality Essentials

### File Documentation
```typescript
// Created: MM/DD/YY HH:MM AM/PM
// Purpose: [One-line description]
// Context:
// - Used by: [Parent components]
// - Uses: [Dependencies]
// - Data source: [Database tables]

// For updates to existing files:
// Updated: MM/DD/YY HH:MM AM/PM - [What changed]
```

### Code Standards
- **Component size:** Under 200 lines (split if larger)
- **TypeScript:** No `any` types - use proper interfaces
- **Comments:** Strategic only - explain WHY, not WHAT
- **Quality gates:** Run after each component

### Strategic Comments (Use Sparingly)
```typescript
// ❗ IMPORTANT: Positions table may be empty for bank accounts
const balance = calculateBalance(account)

// 🔄 This recalculates when account data changes
useEffect(() => {
  updateMetrics()
}, [accounts])

// 🚨 TODO: Add pagination when transactions > 100
const displayTransactions = allTransactions.slice(0, 50)

// 💡 Using hybrid calculation: positions for investments, transactions for banks
function getAccountBalance(account: Account) { ... }
```

### What NOT to Comment
```typescript
// ❌ Don't explain obvious code
const total = items.reduce((sum, item) => sum + item.value, 0) // Calculate total

// ❌ Don't repeat component/function names
function formatCurrency(amount: number) {
  // Format currency - NO, this is obvious
}

// ✅ DO explain business logic
function formatCurrency(amount: number) {
  // Always show 2 decimals for financial accuracy
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount)
}
```

## Common Patterns That Work
```typescript
// Query pattern that works well
export function useAccounts(entityId?: string) {
  return useQuery({
    queryKey: ['accounts', entityId],
    queryFn: async () => {
      let query = supabase.from('accounts').select('*, entity:entities(*)')
      if (entityId) query = query.eq('entity_id', entityId)
      const { data, error } = await query
      if (error) throw error
      return data
    },
    staleTime: 5 * 60 * 1000,
  })
}

// Component pattern that works
export function ComponentName({ prop }: Props) {
  const { data, isLoading } = useQuery()

  if (isLoading) return <SkeletonCard />
  if (!data) return <EmptyState message="No data" />

  return <div>{/* content */}</div>
}
```

## Schema Gotchas (Real Issues Found)
See **[SCHEMA_CHEATSHEET.md](./SCHEMA_CHEATSHEET.md)** for complete field reference.

```typescript
// ❌ These assumptions caused TypeScript errors
account.account_id  // → account.id
account_type === 'investment'  // → 'brokerage' | 'cash_management'
position.symbol     // → position.sec_ticker

// ✅ Quick verification
grep "interface Account" src/types/supabase.ts -A 10
```

## Quick Commands
```bash
# Verify schema before coding
grep "interface TableName" src/types/supabase.ts -A 20

# Check what values actually exist
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres -c "SELECT DISTINCT field_name FROM table_name LIMIT 5"

# Find existing patterns
grep -r "from('accounts')" src/hooks/
ls src/components/similar-feature/

# Quality check sequence
npm run quality && npm run build && npm run dev
```

## Project-Specific Quality Standards

### Import Organization
```typescript
// 1. React/Next
import { useState } from 'react'
import { useRouter } from 'next/navigation'

// 2. External libraries
import { useQuery } from '@tanstack/react-query'

// 3. Internal utilities
import { formatCurrency } from '@/lib/utils'
import { createClient } from '@/lib/supabase/client'

// 4. Components
import { MetricCard } from '@/components/dashboard/MetricCard'

// 5. Types
import type { Account } from '@/types/database'
```

### Error Handling Standards
```typescript
// Always handle Supabase errors
const { data, error } = await supabase.from('accounts').select('*')
if (error) throw error

// Graceful component error states
if (error) return <div className="text-red-600">Failed to load data</div>
if (isLoading) return <SkeletonCard />
if (!data) return <EmptyState message="No accounts found" />
```

### Naming Conventions
```typescript
// Components: PascalCase
export function AccountDetails() {}

// Hooks: camelCase with 'use'
export function useAccountData() {}

// Constants: UPPER_SNAKE_CASE
const MAX_TRANSACTIONS_PER_PAGE = 50

// Props interfaces: ComponentNameProps
interface AccountDetailsProps {
  accountId: string
}
```

## Current System Context
- **Hybrid balance calculation:** Positions for investments, transactions for banks
- **Client-side filtering:** Works fine at current scale (267 transactions)
- **Existing components:** MetricCard, FilterSelect, SkeletonCard, EmptyState available
- **Navigation:** Landing pages → detail pages pattern established
- **Database:** All tables have generated TypeScript interfaces in `src/types/supabase.ts`
- **Styling:** Tailwind CSS with Fidelity green (#00945F) as primary color