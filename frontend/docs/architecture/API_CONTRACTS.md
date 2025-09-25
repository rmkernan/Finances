# API & Data Contracts

**Created:** 09/24/25 9:28PM
**Updated:** 09/25/25 1:03AM - Reference generated types as source of truth
**Purpose:** Type definitions and data contracts for frontend-backend communication

## ⚠️ IMPORTANT: Type Source Update

**Generated types are now the source of truth:**
```typescript
// All database types are auto-generated from Supabase schema
import { Database } from '@/types/supabase'

// Access types like:
type Entity = Database['public']['Tables']['entities']['Row']
type Account = Database['public']['Tables']['accounts']['Row']
type Transaction = Database['public']['Tables']['transactions']['Row']
```

**To regenerate types after schema changes:**
```bash
cd /Users/richkernan/Projects/Finances/frontend/wealth-manager
npx supabase gen types typescript --local > src/types/supabase.ts
```

## Core Type Definitions (Reference Only - See src/types/supabase.ts)

### Entity Types
```typescript
interface Entity {
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

interface Institution {
  id: string
  institution_name: string
  institution_type: 'brokerage' | 'bank' | 'credit_union' | 'insurance' | 'retirement_plan' | 'other'
  status: 'active' | 'inactive' | 'closed'
  notes?: string
  created_at: string
  updated_at: string
}

interface Account {
  id: string
  entity_id: string
  institution_id: string
  account_number: string
  account_number_display: string
  account_holder_name: string
  account_name?: string
  account_type: 'checking' | 'savings' | 'brokerage' | 'ira' | '401k' | 'roth_ira' | 'cash_management' | 'business'
  account_subtype?: string
  account_status: 'active' | 'inactive' | 'closed' | 'transferred'
  is_tax_deferred: boolean
  is_tax_free: boolean
  balance?: number  // Current balance (calculated)
  // Relations
  entity?: Entity
  institution?: Institution
}

interface Transaction {
  id: string
  entity_id: string
  document_id: string
  account_id: string
  transaction_date?: string
  settlement_date?: string
  transaction_type: 'dividend' | 'interest' | 'buy' | 'sell' | 'transfer_in' | 'transfer_out' | 'fee' | 'other'
  transaction_subtype?: string
  description: string
  amount: number
  security_name?: string
  security_identifier?: string
  quantity?: number
  price_per_unit?: number
  cost_basis?: number
  fees?: number
  balance?: number
  federal_taxable?: boolean
  state_taxable?: boolean
  created_at: string
  updated_at: string
}

interface Position {
  id: string
  document_id: string
  account_id: string
  entity_id: string
  position_date: string
  sec_ticker?: string
  cusip?: string
  sec_name: string
  sec_type: string
  quantity: number
  price: number
  end_market_value: number
  cost_basis?: number
  unrealized_gain_loss?: number
  estimated_ann_inc?: number
  est_yield?: number
  created_at: string
  updated_at: string
}
```

## Dashboard Data Contracts

### Global Dashboard
```typescript
interface GlobalDashboardData {
  netWorth: {
    total: number
    change: number
    changePercent: number
    breakdown: {
      financialAssets: number
      realAssets: number
      liabilities: number
    }
    trend: Array<{
      date: string
      value: number
    }>
  }
  entities: Array<{
    id: string
    name: string
    type: 'individual' | 's_corp' | 'llc'
    netWorth: number
    mtdChange: number
    mtdChangePercent: number
    allocation: {
      cash: number
      investments: number
      other: number
    }
    accountCount: number
  }>
  recentActivity: Array<{
    date: string
    entityName: string
    accountName: string
    description: string
    amount: number
    type: string
  }>
  upcomingItems: Array<{
    date: string
    type: 'tax_payment' | 'document_expected' | 'other'
    description: string
    amount?: number
    entityName: string
  }>
}
```

### Entity Dashboard
```typescript
interface EntityDashboardData {
  entity: Entity
  summary: {
    netWorth: number
    mtdChange: number
    ytdChange: number
    cashBalance: number
    investmentBalance: number
    lastRefreshed: string
  }
  accountsByInstitution: Array<{
    institution: Institution
    totalBalance: number
    accounts: Array<{
      id: string
      accountName: string
      accountNumber: string
      balance: number
      lastActivity?: string
    }>
  }>
  financialMetrics: {
    cashFlow: {
      monthlyInflows: number
      monthlyOutflows: number
      netCashFlow: number
    }
    taxLiability: {
      federalEstimate: number
      stateEstimate: number
      nextPaymentDue?: string
    }
    documentStatus: {
      processed: number
      pending: number
      failed: number
    }
    investmentPerformance?: {
      ytdReturn: number
      ytdReturnPercent: number
    }
  }
  recentDocuments: Array<{
    id: string
    documentType: string
    periodStart: string
    periodEnd: string
    institutionName: string
    processedAt: string
    confidenceScore?: number
  }>
  transactions: Transaction[]
}
```

### Institution Dashboard
```typescript
interface InstitutionDashboardData {
  institution: Institution
  entity: Entity
  summary: {
    totalBalance: number
    accountCount: number
    percentOfPortfolio: number
    lastStatementDate?: string
  }
  accounts: Array<{
    id: string
    accountName: string
    accountNumber: string
    accountType: string
    balance: number
    ytdIncome: number
    lastTransaction?: string
  }>
  recentTransactions: Transaction[]
  documents: Array<{
    id: string
    documentType: string
    periodStart: string
    periodEnd: string
    fileName: string
    processedAt: string
  }>
}
```

### Account Dashboard
```typescript
interface AccountDashboardData {
  account: Account & {
    entity: Entity
    institution: Institution
  }
  summary: {
    currentBalance: number
    availableCash?: number
    marginBalance?: number
    change30Day: number
    change30DayPercent: number
    balanceHistory: Array<{
      date: string
      balance: number
    }>
  }
  holdings?: Array<Position>
  transactions: Array<Transaction & {
    documentLink?: string
  }>
  metrics: {
    ytdCashFlow: {
      inflows: number
      outflows: number
      net: number
    }
    taxSummary: {
      dividends: number
      interest: number
      capitalGains: number
      qualifiedDividends: number
    }
    documentCount: {
      statements: number
      taxForms: number
      confirmations: number
    }
  }
}
```

## Component Props Contracts

### Chart Components
```typescript
interface BaseChartProps {
  data: Array<Record<string, any>>
  width?: number | string
  height?: number
  margin?: { top: number; right: number; bottom: number; left: number }
  showLegend?: boolean
  showTooltip?: boolean
  animate?: boolean
  className?: string
}

interface LineChartProps extends BaseChartProps {
  xDataKey: string
  yDataKey: string | string[]
  xAxisLabel?: string
  yAxisLabel?: string
  strokeWidth?: number
  showDots?: boolean
  showGrid?: boolean
}

interface BarChartProps extends BaseChartProps {
  xDataKey: string
  yDataKey: string | string[]
  stacked?: boolean
  horizontal?: boolean
  barGap?: number
  categoryGap?: number
}

interface PieChartProps extends BaseChartProps {
  dataKey: string
  nameKey: string
  innerRadius?: number
  outerRadius?: number
  showLabels?: boolean
  showPercentages?: boolean
}
```

### Table Components
```typescript
interface TableColumn<T> {
  id: string
  header: string | React.ReactNode
  accessor: keyof T | ((row: T) => any)
  sortable?: boolean
  filterable?: boolean
  width?: number | string
  align?: 'left' | 'center' | 'right'
  format?: (value: any) => string | React.ReactNode
}

interface TableProps<T> {
  data: T[]
  columns: TableColumn<T>[]
  sortable?: boolean
  filterable?: boolean
  paginated?: boolean
  pageSize?: number
  selectable?: boolean
  exportable?: boolean
  loading?: boolean
  emptyMessage?: string
  onRowClick?: (row: T) => void
  onSelectionChange?: (selectedRows: T[]) => void
  className?: string
}
```

### Metric Card Components
```typescript
interface MetricCardProps {
  title: string
  value: number | string
  change?: {
    value: number
    percent: number
    period: string
  }
  format?: 'currency' | 'percent' | 'number' | 'string'
  trend?: 'up' | 'down' | 'neutral'
  sparkline?: number[]
  icon?: React.ReactNode
  onClick?: () => void
  loading?: boolean
  className?: string
}
```

## Supabase Query Functions

### Account Queries
```typescript
// Get all accounts with relations
export async function getAccounts() {
  const { data, error } = await supabase
    .from('accounts')
    .select(`
      *,
      entity:entities(*),
      institution:institutions(*)
    `)
    .eq('account_status', 'active')
    .order('entity_id, institution_id')

  return { data, error }
}

// Get single account with full details
export async function getAccountById(accountId: string) {
  const { data, error } = await supabase
    .from('accounts')
    .select(`
      *,
      entity:entities(*),
      institution:institutions(*)
    `)
    .eq('id', accountId)
    .single()

  return { data, error }
}
```

### Transaction Queries
```typescript
// Get transactions with filters
export async function getTransactions(params: {
  accountId?: string
  entityId?: string
  startDate?: string
  endDate?: string
  type?: string
  limit?: number
  offset?: number
}) {
  let query = supabase
    .from('transactions')
    .select('*', { count: 'exact' })

  if (params.accountId) query = query.eq('account_id', params.accountId)
  if (params.entityId) query = query.eq('entity_id', params.entityId)
  if (params.startDate) query = query.gte('transaction_date', params.startDate)
  if (params.endDate) query = query.lte('transaction_date', params.endDate)
  if (params.type) query = query.eq('transaction_type', params.type)

  query = query
    .order('transaction_date', { ascending: false })
    .range(params.offset || 0, (params.offset || 0) + (params.limit || 50) - 1)

  const { data, error, count } = await query

  return { data, error, count }
}
```

### Position Queries
```typescript
// Get current positions for account
export async function getPositions(accountId: string) {
  const { data, error } = await supabase
    .from('positions')
    .select('*')
    .eq('account_id', accountId)
    .gt('quantity', 0)
    .order('end_market_value', { ascending: false })

  return { data, error }
}

// Get position history for symbol
export async function getPositionHistory(symbol: string, entityId?: string) {
  let query = supabase
    .from('positions')
    .select(`
      *,
      account:accounts(account_name, entity_id)
    `)
    .eq('sec_ticker', symbol)

  if (entityId) {
    query = query.eq('entity_id', entityId)
  }

  const { data, error } = await query.order('position_date', { ascending: false })

  return { data, error }
}
```

### Dashboard Aggregation Queries
```typescript
// Calculate net worth across all entities
export async function getGlobalNetWorth() {
  const { data, error } = await supabase.rpc('calculate_net_worth', {
    entity_ids: null,
    as_of_date: new Date().toISOString()
  })

  return { data, error }
}

// Get entity summary with calculated metrics
export async function getEntitySummary(entityId: string) {
  const { data, error } = await supabase.rpc('get_entity_dashboard', {
    p_entity_id: entityId,
    p_start_date: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString(),
    p_end_date: new Date().toISOString()
  })

  return { data, error }
}
```

## AI Assistant Contracts (Phase 4)

### Query Processing
```typescript
interface AIQuery {
  id: string
  query: string                    // User's natural language query
  timestamp: string
  context: {
    currentPage: string
    selectedEntity?: string
    selectedAccount?: string
    dateRange?: {
      start: string
      end: string
    }
    previousQueries?: string[]
  }
}

interface AIResponse {
  queryId: string
  interpretation: {
    intent: 'position_analysis' | 'performance' | 'tax' | 'cash_flow' | 'comparison' | 'other'
    entities: string[]
    symbols?: string[]
    dateRange?: { start: string; end: string }
    metrics: string[]
  }
  data: any[]
  visualization: {
    type: 'table' | 'line_chart' | 'bar_chart' | 'pie_chart' | 'metric_cards' | 'mixed'
    components: Array<{
      type: string
      props: any
      data: any[]
    }>
  }
  narrative?: string               // Text explanation of results
  suggestions?: string[]           // Follow-up query suggestions
  saveable: boolean
  confidence: number
}
```

### Report Generation
```typescript
interface GeneratedReport {
  id: string
  title: string
  query: string
  generatedAt: string
  components: Array<{
    id: string
    type: 'chart' | 'table' | 'metrics' | 'text'
    config: any
    data: any[]
  }>
  layout: {
    grid: Array<{
      componentId: string
      x: number
      y: number
      w: number
      h: number
    }>
  }
  filters: {
    entities?: string[]
    accounts?: string[]
    dateRange?: { start: string; end: string }
  }
  exportFormats: ('pdf' | 'excel' | 'csv')[]
}

interface SavedReport extends GeneratedReport {
  userId: string
  name: string
  description?: string
  isPinned: boolean
  isPublic: boolean
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly'
    time: string
    recipients: string[]
  }
  lastRun: string
  runCount: number
  tags: string[]
}
```

## Error Response Contract
```typescript
interface ErrorResponse {
  error: {
    code: string
    message: string
    details?: any
    timestamp: string
    requestId?: string
  }
  retryable: boolean
  suggestedAction?: string
}
```

## Real-time Subscription Events
```typescript
interface RealtimeEvent {
  event: 'INSERT' | 'UPDATE' | 'DELETE'
  table: string
  old?: Record<string, any>
  new?: Record<string, any>
  timestamp: string
}

// Subscribe to account balance changes
supabase
  .channel('account-changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'accounts',
    filter: `entity_id=eq.${entityId}`
  }, (payload: RealtimeEvent) => {
    // Handle real-time updates
  })
  .subscribe()
```