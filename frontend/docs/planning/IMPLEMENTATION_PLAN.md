# Detailed Implementation Plan

**Created:** 09/24/25 9:30PM
**Updated:** 09/24/25 9:40PM - Added quality assurance protocol with git commit strategy and testing requirements
**Updated:** 09/25/25 1:15AM - Enhanced quality checkpoints, added Week 2 chart requirements
**Updated:** 09/25/25 8:57AM - Added KISS principles and anti-patterns to avoid
**Updated:** 09/25/25 9:07AM - Added specific anti-patterns based on Day 6 learnings
**Updated:** 09/25/25 9:57AM - Added comprehensive documentation standards with file headers and strategic commenting
**Updated:** 09/25/25 10:00AM - Aligned documentation format with automated quality reminders
**Updated:** 09/25/25 10:24AM - Added mandatory build verification and pre-creation checks based on Day 9 learnings
**Updated:** 09/25/25 4:06PM - Added Week 4+ user-driven feature implementation plan with 21 prioritized features from comprehensive page-by-page review
**Updated:** 09/25/25 6:37PM - Marked Days 1-2 and Days 3-5 as complete with detailed implementation results
**Updated:** 09/26/25 2:34PM - Added Days 6-8 completion status and comprehensive progress documentation
**Purpose:** Step-by-step coding tasks for building core infrastructure and dashboard functionality

## ⚠️ CRITICAL QUALITY REQUIREMENTS

**MANDATORY after creating EACH component:**
```bash
# 1. Run quality checks FIRST
npm run quality      # Must pass with ZERO errors/warnings

# 2. Verify BUILD works (NEW - CRITICAL!)
npm run build        # Must complete without errors

# 3. Verify dev server
npm run dev          # Must compile without errors

# 4. Test in browser
# - Check for console errors
# - Verify component renders correctly
# - Test interactions work

# 5. ONLY commit after passing ALL checks
git add -A
git commit -m "Component: [name] - quality verified"
```

**BEFORE Creating New Files:**
```bash
# Verify project structure
find . -name "page.tsx" | head -5    # Check where pages live
find . -name "layout.tsx" | head -5   # Check layout locations

# Verify database schema
grep -n "table_name:" src/types/supabase.ts  # Check exact fields
```

## 📝 Documentation Standards

**MANDATORY File Headers (Compatible with Auto-Reminders):**

**For NEW files:**
```typescript
// Created: [MM/DD/YY HH:MM AM/PM]
// Purpose: [Clear one-line description of what this file does]
//
// Context:
// - Used by: [List parent components/pages that use this]
// - Uses: [List key dependencies or child components]
// - Data source: [Database tables or APIs this interacts with]
```

**For EXISTING files (significant changes):**
```typescript
// Created: [Original date - PRESERVE]
// Updated: [MM/DD/YY HH:MM AM/PM] - [Brief description of changes]
// Purpose: [Original purpose - PRESERVE]
//
// Context: [Update if relationships changed]
```

**Note:** Use `//` comments for headers to match the automated reminder format. This ensures consistency with the quality reminders you receive.

**When to Update Headers:**
- ✅ ADD timestamp: Significant logic changes, new features, bug fixes
- ❌ SKIP timestamp: Minor edits, typo fixes, formatting, import changes
- ✅ PRESERVE history: Never delete previous "Updated:" entries

**Strategic Code Comments:**
```typescript
// ❗ IMPORTANT: Positions table may be empty for bank accounts
// This uses hybrid calculation strategy (see balanceCalculations.ts)
const balance = calculateAccountBalance(account)

// 🔄 This effect runs when entityId changes
// Fetches fresh data and invalidates cache
useEffect(() => {
  // Detailed explanation for complex logic
}, [entityId])

// 🚨 TODO: Add pagination when accounts exceed 100
// Currently limited to 500 for performance
```

**Comment Guidelines:**
- **WHY over WHAT**: Explain reasoning, not obvious code
- **Gotchas**: Flag non-obvious behavior or edge cases
- **TODOs**: Mark future improvements with context
- **Dependencies**: Note relationships between files
- **Business Logic**: Explain financial calculations

**Use Emoji Markers for Scanning:**
- ❗ IMPORTANT: Critical information
- 🚨 TODO/FIXME: Future work needed
- 🔄 Side Effects: State changes, API calls
- 💡 Optimization: Performance considerations
- 🐛 Bug Workaround: Temporary fixes

**TypeScript Requirements:**
- NO `any` types - use proper typing or generics
- Unused vars must be prefixed with underscore
- All props must have interfaces
- All hooks must have return types

## 🚫 Preventing `any` Type Errors

### Common Recharts/Chart Types:
```typescript
// ❌ WRONG - Will cause eslint error
const CustomTooltip = ({ active, payload, label }: any) => {

// ✅ CORRECT - Properly typed
import { TooltipProps } from 'recharts'
const CustomTooltip = ({
  active,
  payload,
  label
}: TooltipProps<number, string>) => {

// For payload items:
interface ChartDataPoint {
  value: number
  name: string
  // add other fields as needed
}
const data = payload?.[0] as { value: number; name: string }
```

### Event Handler Types:
```typescript
// ❌ WRONG
const handleClick = (data: any) => {

// ✅ CORRECT
const handleClick = (data: { activeLabel?: string; activePayload?: Array<{value: number}> }) => {

// Or use specific Recharts types
import { CategoricalChartState } from 'recharts/types/chart/generateCategoricalChart'
const handleClick = (data: CategoricalChartState) => {
```

### Array Mapping Types:
```typescript
// ❌ WRONG
data.map((item: any) => item.value)

// ✅ CORRECT
interface DataItem {
  value: number
  label: string
}
data.map((item: DataItem) => item.value)
```

### Quick Type Escape Hatches (Use Sparingly):
```typescript
// When you truly don't know the type yet:
unknown  // Safer than any, requires type checking

// For objects with dynamic keys:
Record<string, unknown>

// For Recharts props that are complex:
type ChartProps = Parameters<typeof BarChart>[0]
```

### How to Find the Right Type:
1. **Hover in VS Code** - Often shows the inferred type
2. **Check Recharts docs** - They have TypeScript definitions
3. **Use typeof** - `type MyType = typeof someVariable`
4. **Check node_modules** - `@types/recharts` has all types

## 🎯 KISS Principles (Keep It Simple, Stupid!)

**Core Philosophy:**
- **Less is more** - Prefer 100 lines of clear code over 50 lines of clever code
- **No premature optimization** - Make it work first, optimize only when proven necessary
- **Avoid abstraction layers** - Direct database queries are fine
- **Small files** - Target < 200 lines per file, split if growing
- **Single responsibility** - Each component/hook does ONE thing well
- **No over-engineering** - We're building a dashboard, not a framework

**Red Flags to Avoid:**
- Complex inheritance hierarchies
- Abstract factory patterns
- Multiple layers of wrappers
- Premature generalization
- Configuration over convention
- Infinite scroll before proving pagination need
- Filter state persistence without user request
- Mobile-specific views before desktop works perfectly

## Overview
This document provides the exact sequence of files to create and commands to run. Follow this order to avoid dependency issues.

---

## Day 1: Project Setup & Core Infrastructure

### 1. Initialize Project (30 minutes)
```bash
# Create Next.js project
npx create-next-app@latest wealth-manager --typescript --tailwind --app --src-dir --import-alias "@/*"
cd wealth-manager

# Initialize git
git init
git add .
git commit -m "Initial Next.js setup"
```

### 2. Install Dependencies (15 minutes)
```bash
# Core dependencies
npm install @supabase/supabase-js @supabase/ssr
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install zustand
npm install clsx tailwind-merge
npm install date-fns
npm install react-number-format

# Icons and UI
npm install lucide-react
npm install @radix-ui/react-slot

# Dev dependencies
npm install -D @types/node
```

### 3. Environment Configuration (15 minutes)
```bash
# Create .env.local
touch .env.local
```

Add to `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54322
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-key-here
```

### 4. Create Folder Structure (10 minutes)
```bash
mkdir -p src/lib/{supabase,queries,utils}
mkdir -p src/hooks
mkdir -p src/types
mkdir -p src/components/{ui,layout,dashboard,tables,charts}
mkdir -p src/app/{entities,reports,api}
mkdir -p src/stores
```

### 5. Setup Tailwind Config (15 minutes)
File: `tailwind.config.ts`
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#00945F',
          50: '#E6F7F1',
          500: '#00945F',
          600: '#007A4E',
          700: '#00603D',
        },
        positive: '#00A86B',
        negative: '#DC143C',
        warning: '#FFC107',
        border: '#E5E5E5',
        background: '#F7F7F7',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Inconsolata', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
```

### 6. Create Supabase Client (20 minutes)
File: `src/lib/supabase/client.ts`
```typescript
import { createBrowserClient } from '@supabase/ssr'
import { Database } from '@/types/supabase'

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

File: `src/lib/supabase/server.ts`
```typescript
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { Database } from '@/types/supabase'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          cookieStore.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          cookieStore.delete({ name, ...options })
        },
      },
    }
  )
}
```

### 7. Setup React Query Provider (20 minutes)
File: `src/lib/providers.tsx`
```typescript
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            gcTime: 10 * 60 * 1000, // 10 minutes
            refetchOnWindowFocus: true,
            retry: 3,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### 8. Create Base Types (30 minutes)
File: `src/types/database.ts`
```typescript
export interface Entity {
  id: string
  entity_name: string
  entity_type: 'individual' | 's_corp' | 'llc' | 'other'
  tax_id: string
  tax_id_display: string
  primary_taxpayer: string
  georgia_resident: boolean
  entity_status: 'active' | 'inactive'
  notes?: string
  created_at: string
  updated_at: string
}

export interface Institution {
  id: string
  institution_name: string
  institution_type: 'brokerage' | 'bank' | 'credit_union' | 'other'
  status: 'active' | 'inactive' | 'closed'
  notes?: string
}

export interface Account {
  id: string
  entity_id: string
  institution_id: string
  account_number: string
  account_number_display: string
  account_holder_name: string
  account_name?: string
  account_type: string
  balance?: number
  // Relations
  entity?: Entity
  institution?: Institution
}

export interface Transaction {
  id: string
  account_id: string
  transaction_date?: string
  description: string
  amount: number
  transaction_type: string
  balance?: number
}
```

---

## Day 2: Layout & Navigation

### 1. Create Layout Components (45 minutes)
File: `src/components/layout/Sidebar.tsx`
```typescript
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Building2, Wallet, FileText, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/', label: 'Dashboard', icon: Home },
  { href: '/entities', label: 'Entities', icon: Building2 },
  { href: '/accounts', label: 'Accounts', icon: Wallet },
  { href: '/documents', label: 'Documents', icon: FileText },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white border-r border-border h-screen">
      <div className="p-6">
        <h1 className="text-xl font-semibold text-primary">Wealth Manager</h1>
      </div>

      <nav className="px-4">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              pathname === item.href
                ? "bg-primary/10 text-primary"
                : "hover:bg-gray-100"
            )}
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-0 w-full p-4">
        <button className="flex items-center gap-3 w-full px-4 py-3 rounded-lg hover:bg-gray-100">
          <MessageSquare className="w-5 h-5" />
          AI Assistant
        </button>
      </div>
    </aside>
  )
}
```

File: `src/components/layout/TopBar.tsx`
```typescript
'use client'

import { ChevronRight } from 'lucide-react'

interface TopBarProps {
  breadcrumbs?: Array<{ label: string; href?: string }>
}

export function TopBar({ breadcrumbs = [] }: TopBarProps) {
  return (
    <header className="h-16 bg-white border-b border-border px-6 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {breadcrumbs.map((crumb, index) => (
          <div key={index} className="flex items-center gap-2">
            {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400" />}
            {crumb.href ? (
              <a href={crumb.href} className="text-gray-600 hover:text-primary">
                {crumb.label}
              </a>
            ) : (
              <span className="text-gray-900 font-medium">{crumb.label}</span>
            )}
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600">
          Last refresh: {new Date().toLocaleTimeString()}
        </span>
        <button className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-600">
          Refresh
        </button>
      </div>
    </header>
  )
}
```

### 2. Update Root Layout (20 minutes)
File: `src/app/layout.tsx`
```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/lib/providers'
import { Sidebar } from '@/components/layout/Sidebar'
import { TopBar } from '@/components/layout/TopBar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Personal Wealth Manager',
  description: 'Multi-entity financial dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="flex h-screen bg-background">
            <Sidebar />
            <main className="flex-1 flex flex-col overflow-hidden">
              <TopBar />
              <div className="flex-1 overflow-auto p-6">
                {children}
              </div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}
```

---

## Day 3: Data Layer & First Query

### 1. Create Query Hooks (30 minutes)
File: `src/hooks/useAccounts.ts`
```typescript
import { useQuery } from '@tanstack/react-query'
import { createClient } from '@/lib/supabase/client'
import type { Account } from '@/types/database'

export function useAccounts(entityId?: string) {
  const supabase = createClient()

  return useQuery({
    queryKey: ['accounts', entityId],
    queryFn: async () => {
      let query = supabase
        .from('accounts')
        .select(`
          *,
          entity:entities(*),
          institution:institutions(*)
        `)
        .eq('account_status', 'active')

      if (entityId) {
        query = query.eq('entity_id', entityId)
      }

      const { data, error } = await query

      if (error) throw error
      return data as Account[]
    },
  })
}
```

### 2. Create Utility Functions (20 minutes)
File: `src/lib/utils.ts`
```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100)
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
```

### 3. Create Account List Component (30 minutes)
File: `src/components/dashboard/AccountsList.tsx`
```typescript
'use client'

import { useAccounts } from '@/hooks/useAccounts'
import { formatCurrency } from '@/lib/utils'
import { Wallet } from 'lucide-react'

export function AccountsList() {
  const { data: accounts, isLoading, error } = useAccounts()

  if (isLoading) return <div>Loading accounts...</div>
  if (error) return <div>Error loading accounts</div>
  if (!accounts) return null

  const groupedAccounts = accounts.reduce((acc, account) => {
    const institutionName = account.institution?.institution_name || 'Unknown'
    if (!acc[institutionName]) {
      acc[institutionName] = []
    }
    acc[institutionName].push(account)
    return acc
  }, {} as Record<string, typeof accounts>)

  return (
    <div className="space-y-6">
      {Object.entries(groupedAccounts).map(([institution, accounts]) => (
        <div key={institution} className="bg-white rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">{institution}</h3>
          <div className="space-y-2">
            {accounts.map((account) => (
              <div
                key={account.id}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Wallet className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium">{account.account_name}</p>
                    <p className="text-sm text-gray-600">
                      {account.account_number_display}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">
                    {formatCurrency(account.balance || 0)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

---

## Day 4: Dashboard Components

### 1. Create Metric Card (20 minutes)
File: `src/components/dashboard/MetricCard.tsx`
```typescript
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: number
  change?: {
    value: number
    percent: number
  }
  format?: 'currency' | 'percent' | 'number'
  className?: string
}

export function MetricCard({
  title,
  value,
  change,
  format = 'currency',
  className,
}: MetricCardProps) {
  const formatValue = () => {
    switch (format) {
      case 'currency':
        return formatCurrency(value)
      case 'percent':
        return formatPercent(value)
      default:
        return value.toLocaleString()
    }
  }

  const TrendIcon = change
    ? change.value > 0
      ? TrendingUp
      : change.value < 0
      ? TrendingDown
      : Minus
    : null

  return (
    <div className={cn("bg-white rounded-lg p-6", className)}>
      <p className="text-sm text-gray-600 mb-2">{title}</p>
      <p className="text-2xl font-semibold mb-2">{formatValue()}</p>
      {change && (
        <div className="flex items-center gap-2">
          {TrendIcon && (
            <TrendIcon
              className={cn(
                "w-4 h-4",
                change.value > 0 ? "text-positive" :
                change.value < 0 ? "text-negative" :
                "text-gray-400"
              )}
            />
          )}
          <span
            className={cn(
              "text-sm",
              change.value > 0 ? "text-positive" :
              change.value < 0 ? "text-negative" :
              "text-gray-600"
            )}
          >
            {formatCurrency(change.value)} ({formatPercent(change.percent)})
          </span>
        </div>
      )}
    </div>
  )
}
```

### 2. Create Entity Card (30 minutes)
File: `src/components/dashboard/EntityCard.tsx`
```typescript
import Link from 'next/link'
import { formatCurrency } from '@/lib/utils'
import { Building2, User } from 'lucide-react'

interface EntityCardProps {
  entity: {
    id: string
    name: string
    type: 'individual' | 's_corp' | 'llc'
    balance: number
    accountCount: number
    monthlyChange: number
    monthlyChangePercent: number
  }
}

export function EntityCard({ entity }: EntityCardProps) {
  const Icon = entity.type === 'individual' ? User : Building2

  return (
    <Link href={`/entities/${entity.id}`}>
      <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <Icon className="w-8 h-8 text-primary" />
            <div>
              <h3 className="font-semibold">{entity.name}</h3>
              <p className="text-sm text-gray-600">
                {entity.type === 's_corp' ? 'S-Corp' : entity.type}
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div>
            <p className="text-2xl font-semibold">
              {formatCurrency(entity.balance)}
            </p>
            <p className="text-sm text-gray-600">
              {entity.accountCount} accounts
            </p>
          </div>

          <div className="pt-2 border-t">
            <p className="text-sm">
              MTD:
              <span className={entity.monthlyChange >= 0 ? 'text-positive' : 'text-negative'}>
                {' '}{formatCurrency(entity.monthlyChange)}
              </span>
              <span className="text-gray-600">
                {' '}({entity.monthlyChangePercent.toFixed(2)}%)
              </span>
            </p>
          </div>
        </div>
      </div>
    </Link>
  )
}
```

### 3. Create Main Dashboard Page (45 minutes)
File: `src/app/page.tsx`
```typescript
'use client'

import { MetricCard } from '@/components/dashboard/MetricCard'
import { EntityCard } from '@/components/dashboard/EntityCard'
import { AccountsList } from '@/components/dashboard/AccountsList'

export default function DashboardPage() {
  // Mock data for now - will connect to real data
  const netWorth = {
    total: 9100694.14,
    change: { value: 913.33, percent: 0.01 },
  }

  const entities = [
    {
      id: 'kernan-family',
      name: 'Kernan Family',
      type: 'individual' as const,
      balance: 7121544.26,
      accountCount: 2,
      monthlyChange: 4812.65,
      monthlyChangePercent: 0.07,
    },
    {
      id: 'milton-preschool',
      name: 'Milton Preschool Inc',
      type: 's_corp' as const,
      balance: 1979149.88,
      accountCount: 1,
      monthlyChange: -3899.32,
      monthlyChangePercent: -0.20,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Complete view of your financial portfolio</p>
      </div>

      {/* Net Worth Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Net Worth"
          value={netWorth.total}
          change={netWorth.change}
          className="md:col-span-2"
        />
        <MetricCard
          title="Cash & Equivalents"
          value={2450000}
          format="currency"
        />
        <MetricCard
          title="Investments"
          value={6650694.14}
          format="currency"
        />
      </div>

      {/* Entity Cards */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Entities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {entities.map((entity) => (
            <EntityCard key={entity.id} entity={entity} />
          ))}
        </div>
      </div>

      {/* Accounts List */}
      <div>
        <h2 className="text-lg font-semibold mb-4">All Accounts</h2>
        <AccountsList />
      </div>
    </div>
  )
}
```

---

## Day 5: Dynamic Routing & Entity Pages

### 1. Create Dynamic Entity Route (40 minutes)
File: `src/app/entities/[entityId]/page.tsx`
```typescript
'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { createClient } from '@/lib/supabase/client'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { AccountsList } from '@/components/dashboard/AccountsList'

export default function EntityPage() {
  const params = useParams()
  const entityId = params.entityId as string
  const supabase = createClient()

  const { data: entity, isLoading } = useQuery({
    queryKey: ['entity', entityId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('entities')
        .select('*')
        .eq('id', entityId)
        .single()

      if (error) throw error
      return data
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (!entity) return <div>Entity not found</div>

  return (
    <div className="space-y-6">
      {/* Entity Header */}
      <div className="bg-white rounded-lg p-6">
        <h1 className="text-2xl font-semibold">{entity.entity_name}</h1>
        <p className="text-gray-600">
          {entity.entity_type === 's_corp' ? 'S Corporation' : 'Individual'}
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard title="Total Balance" value={0} />
        <MetricCard title="Monthly Cash Flow" value={0} />
        <MetricCard title="YTD Income" value={0} />
        <MetricCard title="Unrealized Gains" value={0} />
      </div>

      {/* Accounts */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Accounts</h2>
        <AccountsList entityId={entityId} />
      </div>
    </div>
  )
}
```

---

## Testing Checklist

### After Day 1:
- [ ] `npm run dev` starts without errors
- [ ] Tailwind colors working
- [ ] Supabase client connects

### After Day 2:
- [ ] Sidebar navigation visible
- [ ] Top bar displays
- [ ] Layout responsive

### After Day 3:
- [ ] Accounts query returns data
- [ ] React Query DevTools shows cache
- [ ] Currency formatting correct

### After Day 4:
- [ ] Dashboard displays mock data
- [ ] Entity cards clickable
- [ ] Metric cards show changes

### After Day 5:
- [ ] Dynamic routes work
- [ ] Real data from Supabase
- [ ] Entity pages load

---

## Week 4+ Implementation Plan - Feature-Driven Development

**Source:** Comprehensive page-by-page feature capture session (09/25/25)
**Approach:** User-driven requirements vs. assumed features

### Week 4: Core Feature Implementation (12 Days)

#### Days 1-2: Critical Fixes 🔴 ✅ COMPLETE
**Goal:** Address data accuracy and risk management issues

1. **Options Expiration Indicators** - positions tables ✅
   - ✅ Implemented red/yellow/green badges for 30/15/7 day expiration warnings
   - ✅ Added CALL/PUT type indicators with underlying ticker extraction
   - ✅ Created reusable OptionsBadge and ExpirationDisplay components
   - ✅ Enhanced visual distinction for options vs regular securities
   - **Files:** `src/components/ui/OptionsBadge.tsx`, `src/components/ui/ExpirationDisplay.tsx`, updated positions tables

2. **Date Display Fix** - account positions ✅
   - ✅ Fixed hardcoded "July 30th" → dynamic end-of-month dates
   - ✅ Implemented proper month-end logic with leap year handling
   - ✅ Added data load vs statement date distinction
   - ✅ Compact date formatting for space efficiency
   - **Files:** Updated `src/lib/utils.ts`, `src/components/portfolio/PositionDateIndicator.tsx`

#### Days 3-5: Foundation Layer 🟠 ✅ COMPLETE
**Goal:** Enable all subsequent table and interaction enhancements

3. **Universal Table Features** - system-wide ✅
   - ✅ Created base sortable table component with TypeScript generics
   - ✅ Implemented expandable row functionality with toggle states
   - ✅ Applied to HoldingsTable with enhanced sorting and expansion
   - ✅ Established reusable patterns for all future table implementations
   - **Files:** `src/components/ui/UniversalTable.tsx`, refactored `HoldingsTable.tsx`

4. **Edit Functionality Core** - accounts, entities, institutions ✅
   - ✅ Created universal EditModal component with form validation
   - ✅ Documented `_screen` database field strategy for data integrity
   - ✅ Implemented account editing with Supabase integration
   - ✅ Established patterns extensible to entities and institutions
   - **Files:** `src/components/ui/EditModal.tsx`, `/docs/database-schema-screen-fields.md`

5. **Navigation Enhancement** - top metrics bar ✅
   - ✅ Made entity/accounts/institutions counts clickable with navigation
   - ✅ Added hover states and accessibility improvements
   - ✅ Maintains dashboard styling while adding interactivity
   - **Files:** Updated dashboard metrics component with click handlers

6. **Accounts Landing Page Layout** - consistency ✅
   - ✅ Verified existing implementation already excellently organized by institution
   - ✅ Maintained high-quality filter system and table functionality
   - ✅ Applied universal table patterns where beneficial
   - **Files:** Quality verification confirmed - no changes needed

#### Days 6-8: Interactive Features 🟠 ✅ COMPLETE
**Goal:** Dynamic filtering and expandable content

7. **Dynamic Portfolio Summary** - dashboard ✅
   - ✅ Added entity/institution filter dropdowns with advanced logic
   - ✅ Implemented 2 simultaneous selection criteria support
   - ✅ Dynamic data updates with proper query key management
   - **Files:** Enhanced `src/components/portfolio/PortfolioSummaryCard.tsx`

8. **Interactive Recent Activity** - dashboard ✅
   - ✅ Made items clickable with navigation to account detail pages
   - ✅ Added expandable detail view supporting multiple simultaneous expansions
   - ✅ Rich transaction details: settlement_date, payee, fees, tax_category, sec_cusip
   - **Files:** Enhanced `src/components/dashboard/RecentActivity.tsx`

9. **Enhanced Transactions Table** - all locations ✅
   - ✅ Created previous full month default with `getPreviousMonthDateRange()` utility
   - ✅ Enhanced account context throughout transaction displays
   - ✅ Applied consistent patterns across all transaction table locations
   - **Files:** `src/lib/dateUtils.ts`, updated transaction components

#### Days 9-10: Portfolio Analysis 🟠
**Goal:** Advanced holdings management and multi-account tracking

10. **Interactive Portfolio Holdings** - entity pages
    - Clickable expandable rows for detail view
    - Change "Attribute Type" → "Class" (use sec_class DB field)
    - Visual distinction for options vs other securities
    - **Files:** Update holdings table, add options styling

11. **Multi-Account Holdings Display** - consolidated view
    - Show which account(s) contain each holding
    - Multiple accounts visible when row expanded
    - **Files:** Update holdings query logic, add account breakdown component

12. **Account Overview Tab Design** - account detail pages
    - Design content based on available data
    - Include income summary tables matching source statements
    - Default to most recent month with date controls
    - **Files:** Create account overview component, income summary tables

#### Days 11-12: Advanced Controls 🟠
**Goal:** Historical analysis and document workflow

13. **Dynamic As-Of Date Control** - positions and summaries
    - Dropdown for last 24 months (data months only)
    - Both dropdown and date range picker options
    - **Files:** Create date picker component, update data queries

14. **Enhanced Document Table** - document management
    - PDF preview popup (new scrollable window)
    - Adapt KRK_Scraper PDF viewer component
    - **Files:** Create PDF viewer component, update document table

15. **Institution Detail Navigation** - institutions page
    - Make cards clickable → navigate to detail pages
    - Add toggle for "six more accounts" expansion
    - **Files:** Update institution cards, add detail pages

### Week 5+: Polish & Consistency 🟡

16. **Enhanced Account Breakdown** - entity pages consistency
17. **Collapsible All Accounts Section** - dashboard navigation
18. **Dynamic Entity Overview Cards** - filtering capabilities
19. **Visual Enhancement** - institution/account type icons
20. **SEO-Friendly URLs** - name-based routing
21. **URL-Friendly Entity Pages** - bookmarkable URLs

### Implementation Strategy

**Daily Workflow:**
```bash
# Start of day
git status && git pull origin main

# Before each feature
npm run quality && npm run build && npm run dev

# End of feature
git add . && git commit -m "Feature: [name] - [brief description]"
```

**Quality Gates:**
- Every component must pass: `npm run quality && npm run build`
- Manual browser testing for each feature
- No console errors or warnings permitted
- Responsive design verification

**Dependencies Managed:**
- Universal tables → all subsequent table features
- Edit functionality → dynamic content management
- Date controls → historical analysis features
- PDF viewer → document workflow improvements

This plan prioritizes:
1. **Risk Management** (options expiration) - immediate business value
2. **Data Accuracy** (date fixes) - system integrity
3. **User Experience** (consistent tables, navigation) - daily workflow efficiency
4. **Advanced Features** (dynamic summaries, expandable content) - power user capabilities

## Quality Assurance Protocol

### Git Commit Strategy
**Commit after each major section:**
```bash
git add .
git commit -m "Complete: [Section name]"
```

**Required commit points:**
- ✅ After project initialization
- ✅ After dependency installation
- ✅ After environment configuration
- ✅ After each day's completion
- ✅ Before any experimental changes

### Code Quality Checks
**Run after each component creation:**
```bash
npm run lint        # Check for ESLint issues
npm run type-check  # Verify TypeScript types
```

**End of day verification:**
```bash
npm run quality     # Runs all checks
npm run dev         # Manual browser testing
```

### Add Scripts to package.json
After project creation, update package.json:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "quality": "npm run type-check && npm run lint"
  }
}
```

### Browser Testing Checklist
After each major component:
- [ ] Component renders without errors
- [ ] Responsive on desktop/tablet
- [ ] No console errors
- [ ] Data displays correctly
- [ ] Interactive elements work

## Common Issues & Solutions

### Supabase Connection Failed
```typescript
// Check .env.local has correct values
// Verify Supabase is running: supabase status
// Check localhost:54323 for Supabase Studio
```

### TypeScript Errors
```typescript
// Generate types from Supabase
npx supabase gen types typescript --local > src/types/supabase.ts
```

### Hydration Errors
```typescript
// Add 'use client' to components using hooks
// Ensure date formatting happens client-side
```

### Performance Issues
```typescript
// Add React.memo to expensive components
// Use React Query's staleTime appropriately
// Implement virtual scrolling for long lists
```