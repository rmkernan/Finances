# BUILD: Financial Analysis Workflows Implementation Guide

**Created:** 09/12/25 5:55PM ET  
**Purpose:** Complete context for cash flow analysis, asset performance, and net worth management workflows  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement financial analysis workflows with interactive charts, drill-down capabilities, and multi-entity aggregation  
**Prerequisites:** Chart library (Recharts/Chart.js), financial data aggregation queries, export functionality  
**Key Decisions Made:** Waterfall charts for cash flow, multi-entity asset views, investment notes system, time-based filtering  
**Output Expected:** Interactive financial dashboards with cash flow analysis, asset performance tracking, net worth management

## Quick Reference

**Core Workflows:**
- **Workflow 2:** Cash Flow Analysis (waterfall charts, drill-down, export)
- **Workflow 3:** Asset Performance Analysis (multi-entity holdings, P&L tracking)
- **Workflow 11:** Net Worth Management (consolidated views, entity breakdowns)

**Key Components:** CashFlowChart, AssetPerformanceTable, NetWorthSummary, InvestmentNotesEditor, ExportButton

**Data Models:** Transaction aggregation by period, holdings with cost basis, performance calculations, investment notes

## Navigation Architecture (For Context)

### Context Hierarchy
```
Global (All Entities)
    ↓
Entity Context (e.g., Milton Preschool Inc)
    ↓  
Institution Context (e.g., Fidelity at Milton)
    ↓
Account Context (e.g., Brokerage ***4567)
```

### Financial Data Visibility by Context
| Context Level | Cash Flow Shown | Assets Shown | Performance Calculated |
|--------------|-----------------|--------------|----------------------|
| **Global** | All entities combined | All holdings aggregated | Portfolio-wide returns |
| **Entity** | Entity's cash flows only | Entity's holdings only | Entity-specific returns |
| **Account** | Account's transactions | Account's positions | Account performance |

---

## Workflow 2: Cash Flow Analysis

**User Story:** "I want to see money in/out for any time period"

### Core Components

#### 1. Date Range Selector
```typescript
interface DateRangeSelectorProps {
  value: { start: Date; end: Date }
  onChange: (range: { start: Date; end: Date }) => void
  presets?: DatePreset[]
}

interface DatePreset {
  label: string
  value: { start: Date; end: Date }
  key: string
}

const DEFAULT_PRESETS = [
  { label: 'This Month', key: 'thisMonth', value: currentMonth() },
  { label: 'Last Month', key: 'lastMonth', value: previousMonth() },
  { label: 'Quarter to Date', key: 'qtd', value: quarterToDate() },
  { label: 'Year to Date', key: 'ytd', value: yearToDate() },
  { label: 'Last Year', key: 'lastYear', value: previousYear() },
  { label: 'Custom', key: 'custom', value: null }
]
```

#### 2. Cash Flow Dashboard
**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Cash Flow Analysis - Q1 2024                    [Export ▼]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Summary Cards:                                                  │
│ ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│ │ Opening Bal  │ Total Inflows│ Total Outflows│ Closing Bal  │   │
│ │ $2,450,000   │ +$485,000    │ -$320,000     │ $2,615,000   │   │
│ │ Jan 1, 2024  │ (156 trans)  │ (89 trans)    │ Mar 31, 2024 │   │
│ └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                 │
│ Cash Flow Waterfall Chart:                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │    $2.6M ██                                      ██ $2.6M   │ │
│ │          ║                                       ║          │ │
│ │    $2.4M ██   +$485K ██                         ██          │ │
│ │          ║         ░░ ║                         ║          │ │
│ │          ║         ░░ ║    -$320K ██           ║          │ │
│ │          ║         ░░ ║          ░░ ║           ║          │ │
│ │       Opening    Inflows   Outflows         Closing      │ │
│ │       Balance              -$320K           Balance      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Category Breakdown:                       Monthly Trend:        │
│ ┌─────────────────────────────┬─────────────────────────────┐   │
│ │ Inflows:                    │                             │   │
│ │ • Dividends      $285,000   │    [Monthly chart here]     │   │
│ │ • Interest       $125,000   │                             │   │
│ │ • Capital Gains   $75,000   │                             │   │
│ │                             │                             │   │
│ │ Outflows:                   │                             │   │
│ │ • Transfers      $200,000   │                             │   │
│ │ • Fees            $15,000   │                             │   │
│ │ • Taxes          $105,000   │                             │   │
│ └─────────────────────────────┴─────────────────────────────┘   │
│                                                                 │
│ [Drill Down to Transactions] [Export to QBO] [Share Report]    │
└─────────────────────────────────────────────────────────────────┘
```

#### 3. Data Source Queries
```sql
-- Cash flow summary for date range
WITH cash_flow_summary AS (
  SELECT 
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_inflows,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_outflows,
    COUNT(CASE WHEN t.amount > 0 THEN 1 END) as inflow_count,
    COUNT(CASE WHEN t.amount < 0 THEN 1 END) as outflow_count,
    MIN(t.date) as period_start,
    MAX(t.date) as period_end
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
    AND t.date >= $date_start 
    AND t.date <= $date_end
),
opening_balance AS (
  SELECT SUM(
    COALESCE(
      (SELECT SUM(amount) FROM transactions t2 
       WHERE t2.account_id = a.id AND t2.date < $date_start), 
      0
    )
  ) as opening_bal
  FROM accounts a
  WHERE ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
),
category_breakdown AS (
  SELECT 
    t.transaction_type,
    CASE WHEN t.amount > 0 THEN 'inflow' ELSE 'outflow' END as flow_type,
    SUM(ABS(t.amount)) as total_amount,
    COUNT(*) as transaction_count
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
    AND t.date >= $date_start 
    AND t.date <= $date_end
  GROUP BY t.transaction_type, CASE WHEN t.amount > 0 THEN 'inflow' ELSE 'outflow' END
  ORDER BY total_amount DESC
)
SELECT * FROM cash_flow_summary, opening_balance, category_breakdown;
```

#### 4. Interactive Waterfall Chart
```typescript
interface CashFlowChartProps {
  data: CashFlowData
  onCategoryClick: (category: string, flowType: 'inflow' | 'outflow') => void
  showEntityBreakdown?: boolean
}

interface CashFlowData {
  openingBalance: number
  closingBalance: number
  categories: Array<{
    name: string
    amount: number
    type: 'inflow' | 'outflow'
    transactionCount: number
    color: string
  }>
  monthlyTrend: Array<{
    month: string
    inflows: number
    outflows: number
    net: number
  }>
}

// Chart implementation with Recharts
function CashFlowWaterfallChart({ data, onCategoryClick }: CashFlowChartProps) {
  const chartData = buildWaterfallData(data)
  
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip formatter={(value, name) => [formatCurrency(value), name]} />
        <Bar 
          dataKey="amount" 
          fill={(entry) => entry.type === 'inflow' ? '#10B981' : '#EF4444'}
          onClick={(data) => onCategoryClick(data.name, data.type)}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
```

### Key Features

#### 1. Transaction Drill-Down
**Flow:** User clicks category in waterfall → Shows transaction table for that category
```typescript
interface TransactionDrillDownProps {
  category: string
  flowType: 'inflow' | 'outflow'
  dateRange: { start: Date; end: Date }
  entityIds?: string[]
}

function TransactionDrillDown({ category, flowType, dateRange, entityIds }: TransactionDrillDownProps) {
  const { data, loading } = useTransactionsByCategory(category, flowType, dateRange, entityIds)
  
  return (
    <Modal>
      <ModalHeader>
        {flowType === 'inflow' ? 'Income' : 'Expenses'} - {category}
        <span className="text-sm text-muted-foreground">
          {formatDateRange(dateRange)}
        </span>
      </ModalHeader>
      <ModalContent>
        <DataTable
          columns={transactionColumns}
          data={data}
          loading={loading}
          onRowClick={(transaction) => openDocumentViewer(transaction.source_document_id)}
        />
      </ModalContent>
    </Modal>
  )
}
```

#### 2. QuickBooks Export
```typescript
interface QBOExportProps {
  dateRange: { start: Date; end: Date }
  entityIds?: string[]
  includeTransfers?: boolean
}

function generateQBOExport(props: QBOExportProps): Promise<Blob> {
  // QBO format implementation
  const transactions = await fetchTransactionsForExport(props)
  
  const qboData = {
    QBXML: {
      QBXMLMsgsRq: {
        ItemInventoryAddRq: transactions.map(t => ({
          Name: t.description,
          Date: formatDate(t.date),
          Amount: t.amount,
          Account: mapAccountToQBO(t.account_id),
          Class: mapEntityToQBO(t.entity_id),
          Memo: t.notes
        }))
      }
    }
  }
  
  return new Blob([JSON.stringify(qboData)], { type: 'application/json' })
}
```

### Business Rules

#### Date Range Validation
- Date ranges cannot exceed 5 years
- Custom date range must have start < end
- Future dates allowed only for projections
- Warn if range spans multiple tax years

#### Reconciliation Logic
- All amounts must reconcile: sum(transactions) = net cash flow
- Opening + inflows - outflows = closing balance
- Handle rounding errors (< $0.01 acceptable)
- Flag discrepancies for review

#### Cash Flow Categorization
- Inflows are positive amounts, outflows are negative
- Transfers between accounts within same entity = neutral
- Inter-entity transfers = outflow from source, inflow to destination
- Fee transactions always classified as outflows

### Acceptance Criteria

- [ ] **GIVEN** user selects date range, **WHEN** range is valid, **THEN** update cash flow data within 1 second
- [ ] **GIVEN** cash flow is displayed, **THEN** show: opening balance + inflows - outflows = closing balance
- [ ] **GIVEN** user clicks a category in waterfall, **THEN** display transaction list for that category
- [ ] **GIVEN** transaction list is shown, **WHEN** user clicks transaction, **THEN** load source document modal
- [ ] **GIVEN** user clicks export, **WHEN** data exists, **THEN** generate QBO file with all transactions in range

### Error Scenarios

#### No Data in Range
- **Message:** "No transactions found for selected period"
- **Actions:** Suggest broadening date range, check entity selection
- **Visual:** Show empty state with helpful suggestions

#### Export Failures
- **File Write Failed:** "Unable to generate export file. Please try again."
- **Invalid Data Format:** "Some transactions contain invalid data. Please review and try again."
- **Actions:** Retry export, download partial data, report issue

#### Reconciliation Errors  
- **Imbalance Detected:** "Cash flow doesn't balance. Difference: $X.XX"
- **Actions:** Show discrepancy details, identify problem transactions
- **Visual:** Highlight imbalanced categories in chart

---

## Workflow 3: Asset Performance Analysis

**User Story:** "I want to see complete history and P&L for GOOG across all my entities"

### Core Components

#### 1. Asset Detail View
**Example Layout for GOOG:**
```
┌─────────────────────────────────────────────────────────────┐
│ GOOGLE (GOOG) - All Entities          Next Earnings: Feb 1  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Summary Metrics:                                            │
│ Total Position: 500 shares | Avg Cost: $1,300 | Current: $1,500 │
│ Total Invested: $650,000 | Current Value: $750,000          │
│ Unrealized Gain: $100,000 (+15.4%) | Realized (2024): $25,000 │
│                                                             │
│ Investment Notes & Strategy:                    [Edit Notes]│
│ ┌─────────────────────────────────────────────────────┐     │
│ │ Price Target: $1,650 by Q4 2024                     │     │
│ │ Strategy: Long-term hold, add on dips below $1,400  │     │
│ │ Tax Notes: Holding for LTCG treatment               │     │
│ │ Last Review: Jan 15, 2024                           │     │
│ └─────────────────────────────────────────────────────┘     │
│                                                             │
│ Holdings by Entity:                                         │
│ ┌─────────────────┬────────┬──────────┬──────────┬─────────┐ │
│ │ Entity          │ Shares │ Cost Basis│ Current │ Unreal. │ │
│ ├─────────────────┼────────┼──────────┼──────────┼─────────┤ │
│ │ Milton Preschool│ 300    │ $390,000 │ $450,000 │ +$60,000│ │
│ │ Entity A        │ 150    │ $195,000 │ $225,000 │ +$30,000│ │
│ │ │Personal        │ 50     │ $65,000  │ $75,000  │ +$10,000│ │
│ │ TOTAL           │ 500    │ $650,000 │ $750,000 │+$100,000│ │
│ └─────────────────┴────────┴──────────┴──────────┴─────────┘ │
│                                                             │
│ Transaction History:                                        │
│ ┌──────────┬────────────────┬──────┬───────┬──────────────┐ │
│ │ Date     │ Entity         │ Type │ Shares│ Amount       │ │
│ ├──────────┼────────────────┼──────┼───────┼──────────────┤ │
│ │ Jan 2024 │ Milton Pre     │ BUY  │ 100   │ -$130,000    │ │
│ │ Dec 2023 │ Entity A       │ SELL │ 50    │ +$72,500     │ │
│ │ Dec 2023 │ Entity A       │ DIV  │ -     │ +$450        │ │
│ │ Nov 2023 │ Personal       │ BUY  │ 50    │ -$65,000     │ │
│ └──────────┴────────────────┴──────┴───────┴──────────────┘ │
│                                                             │
│ [Charts: Price & Holdings | Cash Flows | Realized vs Unrealized] │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Data Source Queries
```sql
-- Asset summary across entities
WITH security_positions AS (
  SELECT 
    h.security_id,
    s.symbol,
    s.description,
    SUM(h.quantity) as total_shares,
    SUM(h.cost_basis) as total_cost_basis,
    SUM(h.market_value) as total_market_value,
    AVG(h.cost_basis / NULLIF(h.quantity, 0)) as avg_cost_per_share
  FROM holdings h
  JOIN securities s ON h.security_id = s.id
  JOIN accounts a ON h.account_id = a.id
  WHERE s.symbol = $symbol
    AND ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
    AND h.quantity > 0
  GROUP BY h.security_id, s.symbol, s.description
),
entity_breakdown AS (
  SELECT 
    e.name as entity_name,
    h.quantity,
    h.cost_basis,
    h.market_value,
    h.market_value - h.cost_basis as unrealized_gain
  FROM holdings h
  JOIN accounts a ON h.account_id = a.id
  JOIN entities e ON a.entity_id = e.id
  JOIN securities s ON h.security_id = s.id
  WHERE s.symbol = $symbol
    AND h.quantity > 0
),
transaction_history AS (
  SELECT 
    t.date,
    e.name as entity_name,
    t.transaction_type,
    t.quantity,
    t.amount,
    t.price_per_share
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  JOIN entities e ON a.entity_id = e.id
  WHERE t.symbol = $symbol
    AND t.transaction_type IN ('buy', 'sell', 'dividend')
  ORDER BY t.date DESC
),
realized_gains AS (
  SELECT 
    SUM(CASE WHEN transaction_type = 'sell' 
             THEN amount - (quantity * avg_cost_basis) 
             ELSE 0 END) as ytd_realized_gain
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE t.symbol = $symbol
    AND t.date >= date_trunc('year', CURRENT_DATE)
    AND ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
)
SELECT * FROM security_positions, entity_breakdown, transaction_history, realized_gains;
```

#### 3. Investment Notes System
```typescript
interface InvestmentNote {
  id: string
  security_symbol: string
  entity_id?: string // null = applies to all entities
  note_type: 'strategy' | 'price_target' | 'tax_note' | 'review' | 'general'
  content: string
  created_at: string
  updated_at: string
  created_by: string
}

interface InvestmentNotesEditorProps {
  symbol: string
  entityId?: string
  notes: InvestmentNote[]
  onSave: (notes: InvestmentNote[]) => Promise<void>
}

function InvestmentNotesEditor({ symbol, entityId, notes, onSave }: InvestmentNotesEditorProps) {
  const [editMode, setEditMode] = useState(false)
  const [noteText, setNoteText] = useState('')
  
  const handleSave = async () => {
    const newNote: InvestmentNote = {
      id: generateId(),
      security_symbol: symbol,
      entity_id: entityId,
      note_type: 'general',
      content: noteText,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: 'user'
    }
    
    await onSave([...notes, newNote])
    setEditMode(false)
    setNoteText('')
  }
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Investment Notes & Strategy</CardTitle>
        <Button variant="outline" onClick={() => setEditMode(true)}>
          <Edit className="h-4 w-4 mr-2" />
          Edit Notes
        </Button>
      </CardHeader>
      <CardContent>
        {editMode ? (
          <div className="space-y-4">
            <Textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Add investment notes, strategy, price targets..."
              rows={6}
            />
            <div className="flex gap-2">
              <Button onClick={handleSave}>Save</Button>
              <Button variant="outline" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {notes.map(note => (
              <div key={note.id} className="border-l-4 border-blue-500 pl-4">
                <p className="text-sm text-muted-foreground">
                  {formatDate(note.updated_at)}
                </p>
                <p>{note.content}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

#### 4. Performance Charts
```typescript
interface AssetPerformanceChartsProps {
  symbol: string
  timeframe: '1M' | '3M' | '1Y' | '5Y' | 'ALL'
  showEntityBreakdown: boolean
}

function AssetPerformanceCharts({ symbol, timeframe, showEntityBreakdown }: AssetPerformanceChartsProps) {
  const { data: priceHistory } = usePriceHistory(symbol, timeframe)
  const { data: holdingsHistory } = useHoldingsHistory(symbol, timeframe)
  const { data: cashFlowHistory } = useCashFlowHistory(symbol, timeframe)
  
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Price & Holdings Over Time */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Price & Holdings Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={combineChartData(priceHistory, holdingsHistory)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="price" orientation="left" />
              <YAxis yAxisId="shares" orientation="right" />
              <Tooltip />
              <Line 
                yAxisId="price" 
                type="monotone" 
                dataKey="price" 
                stroke="#8884d8"
                name="Price per Share"
              />
              <Bar 
                yAxisId="shares" 
                dataKey="totalShares" 
                fill="#82ca9d"
                name="Total Shares Held"
                opacity={0.6}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      {/* Cash Flows In/Out */}
      <Card>
        <CardHeader>
          <CardTitle>Cash Flows</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cashFlowHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="buys" fill="#ef4444" name="Purchases" />
              <Bar dataKey="sells" fill="#10b981" name="Sales" />
              <Bar dataKey="dividends" fill="#3b82f6" name="Dividends" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Key Features for Asset Views

#### 1. Multi-Entity Aggregation
- **Consolidated View:** Total position across all entities
- **Entity Breakdown:** Holdings per entity with separate cost basis
- **Performance Attribution:** Which entities contributing to gains/losses
- **Tax Implications:** Different treatment per entity type

#### 2. Cost Basis Tracking
- **FIFO/LIFO Methods:** Support different cost basis calculation methods
- **Lot Tracking:** Track individual purchase lots for tax purposes
- **Wash Sale Detection:** Flag potential wash sale violations
- **Tax Efficiency:** Show long-term vs short-term holding periods

#### 3. Performance Metrics
- **Unrealized P&L:** Current market value vs cost basis
- **Realized P&L:** Actual gains/losses from sales
- **Total Return:** Including dividends and capital appreciation
- **Annualized Returns:** Time-weighted return calculations

---

## Workflow 11: Net Worth Management

**User Story:** "I want to track my net worth across all entities and see the breakdown"

### Core Components

#### 1. Net Worth Summary Dashboard
```typescript
interface NetWorthData {
  total: number
  change: {
    amount: number
    percentage: number
    period: string
  }
  breakdown: {
    financialAssets: number
    realAssets: number
    liabilities: number
  }
  byEntity: Array<{
    entityId: string
    entityName: string
    netWorth: number
    change: number
    percentage: number
  }>
  history: Array<{
    date: string
    netWorth: number
    financialAssets: number
    realAssets: number
    liabilities: number
  }>
}

function NetWorthSummary({ data, dateRange, onEntityClick }: NetWorthSummaryProps) {
  return (
    <div className="space-y-6">
      {/* Header Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Total Net Worth"
          value={data.total}
          change={data.change}
          format="currency"
        />
        <MetricCard
          title="Financial Assets"
          value={data.breakdown.financialAssets}
          format="currency"
        />
        <MetricCard
          title="Real Assets"
          value={data.breakdown.realAssets}
          format="currency"
        />
        <MetricCard
          title="Liabilities"
          value={data.breakdown.liabilities}
          format="currency"
          trend="negative"
        />
      </div>
      
      {/* Net Worth Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Net Worth Trend</CardTitle>
          <div className="flex gap-2">
            {['1M', '3M', '6M', '1Y', '5Y', 'ALL'].map(period => (
              <Button
                key={period}
                variant={selectedPeriod === period ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedPeriod(period)}
              >
                {period}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data.history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Area 
                type="monotone" 
                dataKey="financialAssets" 
                stackId="1"
                stroke="#3b82f6" 
                fill="#3b82f6"
                fillOpacity={0.6}
                name="Financial Assets"
              />
              <Area 
                type="monotone" 
                dataKey="realAssets" 
                stackId="1"
                stroke="#10b981" 
                fill="#10b981"
                fillOpacity={0.6}
                name="Real Assets"
              />
              <Area 
                type="monotone" 
                dataKey="liabilities" 
                stackId="1"
                stroke="#ef4444" 
                fill="#ef4444"
                fillOpacity={0.6}
                name="Liabilities"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      {/* Entity Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Net Worth by Entity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.byEntity.map(entity => (
              <div 
                key={entity.entityId}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent cursor-pointer"
                onClick={() => onEntityClick(entity.entityId)}
              >
                <div>
                  <h4 className="font-medium">{entity.entityName}</h4>
                  <p className="text-sm text-muted-foreground">
                    {entity.percentage.toFixed(1)}% of total
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatCurrency(entity.netWorth)}</p>
                  <p className={cn(
                    "text-sm",
                    entity.change >= 0 ? "text-green-600" : "text-red-600"
                  )}>
                    {entity.change >= 0 ? '+' : ''}{formatCurrency(entity.change)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 2. Net Worth Calculation Query
```sql
-- Net worth calculation with history
WITH current_balances AS (
  SELECT 
    a.entity_id,
    e.name as entity_name,
    SUM(CASE 
        WHEN a.account_type IN ('checking', 'savings', 'brokerage', 'ira', '401k') 
        THEN a.balance 
        ELSE 0 
    END) as financial_assets,
    SUM(CASE 
        WHEN a.account_type IN ('real_estate', 'property') 
        THEN a.balance 
        ELSE 0 
    END) as real_assets,
    SUM(CASE 
        WHEN a.account_type IN ('credit_card', 'loan', 'mortgage') 
        THEN ABS(a.balance)
        ELSE 0 
    END) as liabilities
  FROM accounts a
  JOIN entities e ON a.entity_id = e.id
  WHERE a.status = 'active'
  GROUP BY a.entity_id, e.name
),
net_worth_by_entity AS (
  SELECT *,
         financial_assets + real_assets - liabilities as net_worth
  FROM current_balances
),
historical_snapshots AS (
  SELECT 
    snapshot_date,
    SUM(financial_assets) as total_financial_assets,
    SUM(real_assets) as total_real_assets,
    SUM(liabilities) as total_liabilities,
    SUM(net_worth) as total_net_worth
  FROM net_worth_snapshots
  WHERE snapshot_date >= $start_date
  GROUP BY snapshot_date
  ORDER BY snapshot_date
)
SELECT 
  -- Current totals
  (SELECT SUM(net_worth) FROM net_worth_by_entity) as current_net_worth,
  (SELECT SUM(financial_assets) FROM net_worth_by_entity) as current_financial_assets,
  (SELECT SUM(real_assets) FROM net_worth_by_entity) as current_real_assets,
  (SELECT SUM(liabilities) FROM net_worth_by_entity) as current_liabilities,
  
  -- Entity breakdown
  (SELECT json_agg(row_to_json(net_worth_by_entity)) FROM net_worth_by_entity) as entity_breakdown,
  
  -- Historical data
  (SELECT json_agg(row_to_json(historical_snapshots)) FROM historical_snapshots) as history;
```

#### 3. Asset Allocation Visualization
```typescript
interface AssetAllocationProps {
  data: NetWorthData
  viewType: 'pie' | 'treemap' | 'sankey'
  groupBy: 'assetType' | 'entity' | 'institution'
}

function AssetAllocationChart({ data, viewType, groupBy }: AssetAllocationProps) {
  const chartData = useMemo(() => {
    switch (groupBy) {
      case 'assetType':
        return [
          { name: 'Cash & Money Market', value: data.cashAndMM, color: '#3b82f6' },
          { name: 'Fixed Income', value: data.fixedIncome, color: '#10b981' },
          { name: 'Equities', value: data.equities, color: '#f59e0b' },
          { name: 'Real Estate', value: data.realEstate, color: '#8b5cf6' },
          { name: 'Other', value: data.other, color: '#6b7280' }
        ]
      case 'entity':
        return data.byEntity.map(entity => ({
          name: entity.entityName,
          value: entity.netWorth,
          color: getEntityColor(entity.entityId)
        }))
      case 'institution':
        return data.byInstitution.map(inst => ({
          name: inst.institutionName,
          value: inst.totalBalance,
          color: getInstitutionColor(inst.institutionId)
        }))
    }
  }, [data, groupBy])
  
  if (viewType === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => formatCurrency(value)} />
        </PieChart>
      </ResponsiveContainer>
    )
  }
  
  // Additional chart types (treemap, sankey) implementation...
}
```

### Performance Requirements

#### Database Optimization
- **Materialized Views:** Pre-calculated net worth snapshots
- **Indexes:** On entity_id, date, account_type for fast aggregation
- **Caching:** Cache heavy calculations for 5-10 minutes
- **Pagination:** For large transaction lists and historical data

#### Chart Performance
- **Lazy Loading:** Load charts only when tabs/sections are visible
- **Data Sampling:** For long time series, sample data points appropriately
- **Virtualization:** Virtual scrolling for large entity/account lists
- **Memoization:** Cache expensive calculations in React components

---

*This guide provides complete context for financial analysis workflow implementation. All calculations, visualizations, and user interactions are specified for autonomous development.*