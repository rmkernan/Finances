# BUILD: Administrative Workflows Implementation Guide

**Created:** 09/12/25 6:03PM ET  
**Purpose:** Complete context for administrative workflows including entity management, transfers, forecasting, and system controls  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement administrative workflows for entity/account management, inter-entity transfers, cash flow forecasting, and system administration  
**Prerequisites:** Entity/account CRUD operations, transfer tracking system, forecasting algorithms, database controls  
**Key Decisions Made:** Form-based entity creation, transfer recording with tax treatment, calendar-based forecasting, system status monitoring  
**Output Expected:** Administrative interfaces, transfer management system, forecasting dashboard, database control panel

## Quick Reference

**Core Workflows:**
- **Workflow 8:** Cash Flow Forecasting & Planning (calendar view, expected transactions)
- **Workflow 9:** Inter-Entity Transfers & Cash Management (transfer recording, tracking)
- **Workflow 10:** Portfolio Rebalancing & Alerts (allocation monitoring, opportunities)
- **Workflow 11:** Administrative Functions (entity/account management, database controls)

**Key Components:** EntityManager, TransferRecorder, CashFlowCalendar, AllocationMonitor, SystemControls

**Administrative Features:** Entity CRUD, account assignment, transfer tracking, database management, alert configuration

## Navigation Architecture (For Context)

### Administrative Access Levels
```
System Admin (Full Access)
    ↓
Entity Admin (Entity-Specific Management)
    ↓
Read-Only User (View Only)
```

### Admin URL Structure
```
/admin                                      → Admin Dashboard
/admin/entities                            → Entity Management
/admin/entities/new                        → Add Entity Form
/admin/entities/{id}/edit                  → Edit Entity Form
/admin/accounts                           → Account Management  
/admin/accounts/assign                    → Account Assignment
/admin/transfers                          → Transfer Management
/admin/system                            → System Controls
/admin/forecasting                       → Cash Flow Planning
/admin/alerts                            → Alert Configuration
```

---

## Workflow 8: Cash Flow Forecasting & Planning

**User Story:** "I want to know when money is coming in and plan for tax payments"

### Core Components

#### 1. Cash Flow Calendar
```typescript
interface CashFlowEvent {
  id: string
  date: string
  type: 'expected_dividend' | 'expected_interest' | 'tax_payment' | 'transfer' | 'manual'
  entityId: string
  accountId?: string
  description: string
  amount: number
  confidence: 'high' | 'medium' | 'low'
  recurring?: RecurrenceRule
  source?: 'historical' | 'manual' | 'projected'
  status: 'scheduled' | 'occurred' | 'missed' | 'cancelled'
  notes?: string
}

interface RecurrenceRule {
  frequency: 'monthly' | 'quarterly' | 'semi_annually' | 'annually'
  interval: number // e.g., every 3 months
  endDate?: string
}

function CashFlowCalendar({ month, year, entities }: CashFlowCalendarProps) {
  const { data: events } = useCashFlowEvents(month, year, entities)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  
  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          Cash Flow Forecast - {format(new Date(year, month - 1), 'MMMM yyyy')}
        </h2>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => navigateMonth(-1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button 
            variant="outline"
            onClick={() => setSelectedDate(format(new Date(), 'yyyy-MM-dd'))}
          >
            Today
          </Button>
          <Button 
            variant="outline" 
            onClick={() => navigateMonth(1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Monthly Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Expected Cash In"
          value={events.filter(e => e.amount > 0).reduce((sum, e) => sum + e.amount, 0)}
          format="currency"
          trend="positive"
        />
        <MetricCard
          title="Expected Cash Out"
          value={Math.abs(events.filter(e => e.amount < 0).reduce((sum, e) => sum + e.amount, 0))}
          format="currency"
          trend="negative"
        />
        <MetricCard
          title="Net Expected"
          value={events.reduce((sum, e) => sum + e.amount, 0)}
          format="currency"
        />
        <MetricCard
          title="High Confidence Events"
          value={events.filter(e => e.confidence === 'high').length}
          format="number"
        />
      </div>
      
      {/* Calendar Grid */}
      <Card>
        <CardContent className="p-0">
          <Calendar
            mode="single"
            selected={selectedDate ? new Date(selectedDate) : undefined}
            onSelect={(date) => setSelectedDate(date ? format(date, 'yyyy-MM-dd') : null)}
            components={{
              Day: ({ date }) => (
                <CalendarDay
                  date={date}
                  events={events.filter(e => 
                    format(new Date(e.date), 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
                  )}
                  onEventClick={(event) => setSelectedEvent(event)}
                />
              )
            }}
            className="rounded-md border-0"
          />
        </CardContent>
      </Card>
      
      {/* Event Details Panel */}
      {selectedDate && (
        <Card>
          <CardHeader>
            <CardTitle>
              Events for {format(new Date(selectedDate), 'EEEE, MMMM d, yyyy')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <EventList
              events={events.filter(e => 
                format(new Date(e.date), 'yyyy-MM-dd') === selectedDate
              )}
              onAddEvent={() => setShowAddEvent(true)}
              onEditEvent={(event) => setEditingEvent(event)}
            />
          </CardContent>
        </Card>
      )}
      
      {/* Alerts Section */}
      <Card>
        <CardHeader>
          <CardTitle>Cash Flow Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <AlertsList alerts={generateCashFlowAlerts(events)} />
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 2. Event Prediction System
```typescript
interface EventPredictor {
  predictDividends(symbol: string, entityIds: string[]): Promise<CashFlowEvent[]>
  predictTaxPayments(year: number, entityIds: string[]): Promise<CashFlowEvent[]>
  predictRecurringTransfers(entityIds: string[]): Promise<CashFlowEvent[]>
}

class CashFlowPredictor implements EventPredictor {
  async predictDividends(symbol: string, entityIds: string[]): Promise<CashFlowEvent[]> {
    // Analyze historical dividend patterns
    const history = await this.getDividendHistory(symbol, entityIds)
    const pattern = this.analyzeDividendPattern(history)
    
    return pattern.expectedDates.map(date => ({
      id: generateId(),
      date: date.toISOString(),
      type: 'expected_dividend',
      entityId: pattern.primaryEntity,
      description: `${symbol} Dividend Payment`,
      amount: pattern.estimatedAmount,
      confidence: this.calculateConfidence(pattern.consistency),
      recurring: {
        frequency: pattern.frequency,
        interval: 1
      },
      source: 'projected',
      status: 'scheduled'
    }))
  }
  
  async predictTaxPayments(year: number, entityIds: string[]): Promise<CashFlowEvent[]> {
    const taxEstimates = await this.calculateTaxEstimates(year, entityIds)
    const quarterlyDueDates = [
      new Date(year, 3, 15), // Q1 - April 15
      new Date(year, 5, 15), // Q2 - June 15  
      new Date(year, 8, 15), // Q3 - September 15
      new Date(year + 1, 0, 15) // Q4 - January 15
    ]
    
    return quarterlyDueDates.flatMap((dueDate, quarterIndex) => {
      return entityIds.map(entityId => ({
        id: generateId(),
        date: dueDate.toISOString(),
        type: 'tax_payment',
        entityId,
        description: `Q${quarterIndex + 1} Estimated Tax Payment`,
        amount: -taxEstimates[entityId].quarterly,
        confidence: 'high',
        source: 'projected',
        status: 'scheduled'
      }))
    })
  }
  
  private calculateConfidence(consistency: number): 'high' | 'medium' | 'low' {
    if (consistency > 0.9) return 'high'
    if (consistency > 0.7) return 'medium'
    return 'low'
  }
}
```

#### 3. Calendar Day Component
```typescript
interface CalendarDayProps {
  date: Date
  events: CashFlowEvent[]
  onEventClick: (event: CashFlowEvent) => void
}

function CalendarDay({ date, events, onEventClick }: CalendarDayProps) {
  const dayEvents = events.filter(event => 
    format(new Date(event.date), 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
  )
  
  const totalIn = dayEvents.filter(e => e.amount > 0).reduce((sum, e) => sum + e.amount, 0)
  const totalOut = Math.abs(dayEvents.filter(e => e.amount < 0).reduce((sum, e) => sum + e.amount, 0))
  const netAmount = totalIn - totalOut
  
  return (
    <div className="relative p-1 h-24 border rounded-md">
      {/* Date number */}
      <div className="text-sm font-medium text-center">
        {format(date, 'd')}
      </div>
      
      {/* Event indicators */}
      <div className="space-y-1 mt-1">
        {dayEvents.slice(0, 3).map((event, index) => (
          <div
            key={event.id}
            className={cn(
              "px-1 py-0.5 text-xs rounded cursor-pointer truncate",
              event.amount > 0 
                ? "bg-green-100 text-green-800 hover:bg-green-200"
                : "bg-red-100 text-red-800 hover:bg-red-200",
              event.confidence === 'low' && "opacity-60 italic"
            )}
            onClick={() => onEventClick(event)}
            title={`${event.description}: ${formatCurrency(event.amount)}`}
          >
            {event.type === 'expected_dividend' && '📊'}
            {event.type === 'tax_payment' && '💸'}
            {event.type === 'transfer' && '🔄'}
            {event.type === 'manual' && '📝'}
            <span className="ml-1">
              {formatCurrency(Math.abs(event.amount))}
            </span>
          </div>
        ))}
        
        {dayEvents.length > 3 && (
          <div className="text-xs text-muted-foreground text-center">
            +{dayEvents.length - 3} more
          </div>
        )}
      </div>
      
      {/* Net amount indicator */}
      {netAmount !== 0 && (
        <div className={cn(
          "absolute bottom-1 right-1 text-xs font-medium",
          netAmount > 0 ? "text-green-600" : "text-red-600"
        )}>
          {netAmount > 0 ? '+' : ''}{formatCurrency(netAmount, { compact: true })}
        </div>
      )}
    </div>
  )
}
```

### Cash Flow Data Queries
```sql
-- Historical patterns for prediction
WITH dividend_history AS (
  SELECT 
    t.symbol,
    DATE_TRUNC('month', t.date) as month,
    SUM(t.amount) as total_amount,
    COUNT(*) as payment_count,
    AVG(t.amount) as avg_amount,
    STDDEV(t.amount) as amount_stddev
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  WHERE t.transaction_type = 'dividend'
    AND t.date >= CURRENT_DATE - INTERVAL '2 years'
    AND ($entity_ids IS NULL OR a.entity_id = ANY($entity_ids))
  GROUP BY t.symbol, DATE_TRUNC('month', t.date)
  ORDER BY t.symbol, month
),
pattern_analysis AS (
  SELECT 
    symbol,
    -- Calculate frequency pattern
    MODE() WITHIN GROUP (ORDER BY 
      EXTRACT(DAY FROM month - LAG(month) OVER (PARTITION BY symbol ORDER BY month))
    ) as typical_interval_days,
    
    -- Calculate consistency
    (COUNT(*) * 1.0 / (
      EXTRACT(DAYS FROM MAX(month) - MIN(month)) / 30.0
    )) as consistency_ratio,
    
    -- Calculate trend
    AVG(total_amount) as avg_monthly_amount,
    STDDEV(total_amount) as amount_volatility
    
  FROM dividend_history
  GROUP BY symbol
),
upcoming_predictions AS (
  SELECT 
    p.symbol,
    -- Predict next payment dates based on pattern
    CASE 
      WHEN p.typical_interval_days <= 32 THEN 'monthly'
      WHEN p.typical_interval_days <= 95 THEN 'quarterly' 
      WHEN p.typical_interval_days <= 190 THEN 'semi_annually'
      ELSE 'annually'
    END as frequency,
    
    p.avg_monthly_amount as estimated_amount,
    
    CASE 
      WHEN p.consistency_ratio > 0.9 THEN 'high'
      WHEN p.consistency_ratio > 0.7 THEN 'medium'
      ELSE 'low'
    END as confidence
    
  FROM pattern_analysis p
  WHERE p.consistency_ratio > 0.3 -- Only include reasonably consistent patterns
)
SELECT * FROM upcoming_predictions;
```

---

## Workflow 9: Inter-Entity Transfers & Cash Management

**User Story:** "I need to move money between entities and track it properly"

### Core Components

#### 1. Transfer Recording Interface
```typescript
interface TransferRecord {
  id: string
  date: string
  fromEntityId: string
  toEntityId: string
  fromAccountId: string
  toAccountId: string
  amount: number
  purpose: 'distribution' | 'loan' | 'capital_contribution' | 'management_fee' | 'other'
  taxTreatment: 'non_taxable' | 'taxable_income' | 'return_of_capital' | 'loan'
  description: string
  notes?: string
  status: 'pending' | 'completed' | 'failed' | 'cancelled'
  confirmationNumber?: string
  createdAt: string
  completedAt?: string
}

function TransferManager() {
  const [transfers, setTransfers] = useState<TransferRecord[]>([])
  const [showNewTransfer, setShowNewTransfer] = useState(false)
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inter-Entity Transfer Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowHistory(true)}>
            <History className="h-4 w-4 mr-2" />
            View History
          </Button>
          <Button onClick={() => setShowNewTransfer(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Transfer
          </Button>
        </div>
      </div>
      
      {/* Quick Transfer Form */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Transfer</CardTitle>
          <CardDescription>
            Record a transfer between entities or accounts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QuickTransferForm onSubmit={handleTransferSubmit} />
        </CardContent>
      </Card>
      
      {/* Recent Transfers */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Transfers</CardTitle>
        </CardHeader>
        <CardContent>
          <TransferHistory
            transfers={transfers.slice(0, 10)}
            onViewDetails={(transfer) => setSelectedTransfer(transfer)}
            onEditTransfer={(transfer) => setEditingTransfer(transfer)}
          />
        </CardContent>
      </Card>
      
      {/* Transfer Summary Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">This Month</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(getMonthlyTransferTotal())}
            </div>
            <p className="text-sm text-muted-foreground">
              {getMonthlyTransferCount()} transfers
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Year to Date</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(getYTDTransferTotal())}
            </div>
            <p className="text-sm text-muted-foreground">
              {getYTDTransferCount()} transfers
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getPendingTransferCount()}
            </div>
            <p className="text-sm text-muted-foreground">
              {formatCurrency(getPendingTransferTotal())} total
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

#### 2. Quick Transfer Form
```typescript
interface QuickTransferFormData {
  fromEntity: string
  fromAccount: string
  toEntity: string
  toAccount: string
  amount: number
  date: string
  purpose: TransferPurpose
  taxTreatment: TaxTreatment
  description: string
  notes?: string
}

function QuickTransferForm({ onSubmit }: { onSubmit: (data: QuickTransferFormData) => Promise<void> }) {
  const { data: entities } = useEntities()
  const [formData, setFormData] = useState<Partial<QuickTransferFormData>>({
    date: format(new Date(), 'yyyy-MM-dd'),
    purpose: 'distribution',
    taxTreatment: 'non_taxable'
  })
  
  const fromAccounts = useAccountsByEntity(formData.fromEntity)
  const toAccounts = useAccountsByEntity(formData.toEntity)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData as QuickTransferFormData)
    setFormData({
      date: format(new Date(), 'yyyy-MM-dd'),
      purpose: 'distribution',
      taxTreatment: 'non_taxable'
    })
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* From Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>From Entity</Label>
          <Select
            value={formData.fromEntity}
            onValueChange={(value) => setFormData({...formData, fromEntity: value, fromAccount: ''})}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select entity" />
            </SelectTrigger>
            <SelectContent>
              {entities?.map(entity => (
                <SelectItem key={entity.id} value={entity.id}>
                  {entity.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label>From Account</Label>
          <Select
            value={formData.fromAccount}
            onValueChange={(value) => setFormData({...formData, fromAccount: value})}
            disabled={!formData.fromEntity}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select account" />
            </SelectTrigger>
            <SelectContent>
              {fromAccounts?.map(account => (
                <SelectItem key={account.id} value={account.id}>
                  {account.account_name} ({account.account_number})
                  <span className="ml-2 text-muted-foreground">
                    {formatCurrency(account.balance)}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* To Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>To Entity</Label>
          <Select
            value={formData.toEntity}
            onValueChange={(value) => setFormData({...formData, toEntity: value, toAccount: ''})}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select entity" />
            </SelectTrigger>
            <SelectContent>
              {entities?.map(entity => (
                <SelectItem key={entity.id} value={entity.id}>
                  {entity.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label>To Account</Label>
          <Select
            value={formData.toAccount}
            onValueChange={(value) => setFormData({...formData, toAccount: value})}
            disabled={!formData.toEntity}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select account" />
            </SelectTrigger>
            <SelectContent>
              {toAccounts?.map(account => (
                <SelectItem key={account.id} value={account.id}>
                  {account.account_name} ({account.account_number})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Transfer Details */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2">
          <Label>Amount</Label>
          <Input
            type="number"
            step="0.01"
            value={formData.amount || ''}
            onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
            placeholder="0.00"
            required
          />
        </div>
        
        <div className="space-y-2">
          <Label>Date</Label>
          <Input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({...formData, date: e.target.value})}
            required
          />
        </div>
        
        <div className="space-y-2">
          <Label>Purpose</Label>
          <Select
            value={formData.purpose}
            onValueChange={(value) => setFormData({...formData, purpose: value as TransferPurpose})}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="distribution">Distribution</SelectItem>
              <SelectItem value="loan">Loan</SelectItem>
              <SelectItem value="capital_contribution">Capital Contribution</SelectItem>
              <SelectItem value="management_fee">Management Fee</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div className="space-y-2">
        <Label>Tax Treatment</Label>
        <Select
          value={formData.taxTreatment}
          onValueChange={(value) => setFormData({...formData, taxTreatment: value as TaxTreatment})}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="non_taxable">Non-taxable Transfer</SelectItem>
            <SelectItem value="taxable_income">Taxable Income</SelectItem>
            <SelectItem value="return_of_capital">Return of Capital</SelectItem>
            <SelectItem value="loan">Loan (No Tax Impact)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="space-y-2">
        <Label>Description</Label>
        <Input
          value={formData.description || ''}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          placeholder="Brief description of transfer"
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label>Notes (Optional)</Label>
        <Textarea
          value={formData.notes || ''}
          onChange={(e) => setFormData({...formData, notes: e.target.value})}
          placeholder="Additional notes about this transfer"
          rows={3}
        />
      </div>
      
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={() => setFormData({})}>
          Clear
        </Button>
        <Button type="submit" disabled={!formData.amount || !formData.fromAccount || !formData.toAccount}>
          Record Transfer
        </Button>
      </div>
    </form>
  )
}
```

#### 3. Transfer Data Queries
```sql
-- Inter-entity transfer tracking
WITH transfer_summary AS (
  SELECT 
    t.id,
    t.date,
    t.amount,
    t.purpose,
    t.tax_treatment,
    t.description,
    t.status,
    
    -- From entity/account info
    fe.name as from_entity_name,
    fa.account_name as from_account_name,
    fa.account_number as from_account_number,
    
    -- To entity/account info
    te.name as to_entity_name,
    ta.account_name as to_account_name,
    ta.account_number as to_account_number,
    
    -- Classification
    CASE 
      WHEN fe.id = te.id THEN 'intra_entity'
      ELSE 'inter_entity'
    END as transfer_type
    
  FROM transfers t
  JOIN accounts fa ON t.from_account_id = fa.id
  JOIN entities fe ON fa.entity_id = fe.id
  JOIN accounts ta ON t.to_account_id = ta.id
  JOIN entities te ON ta.entity_id = te.id
  WHERE t.date >= $start_date
    AND t.date <= $end_date
    AND ($entity_ids IS NULL OR fe.id = ANY($entity_ids) OR te.id = ANY($entity_ids))
),
monthly_aggregation AS (
  SELECT 
    DATE_TRUNC('month', date) as month,
    purpose,
    COUNT(*) as transfer_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
  FROM transfer_summary
  WHERE transfer_type = 'inter_entity'
  GROUP BY DATE_TRUNC('month', date), purpose
  ORDER BY month DESC, total_amount DESC
)
SELECT * FROM transfer_summary
UNION ALL
SELECT * FROM monthly_aggregation;
```

---

## Workflow 10: Portfolio Rebalancing & Alerts

**User Story:** "I want to maintain target allocations and get alerts"

### Portfolio Health Dashboard
```typescript
interface PortfolioHealth {
  assetAllocation: {
    current: AllocationBreakdown
    target: AllocationBreakdown
    variance: AllocationVariance
  }
  rebalancingNeeds: RebalancingAction[]
  taxHarvestingOpportunities: TaxHarvestingOpportunity[]
  alerts: PortfolioAlert[]
  performance: PerformanceMetrics
}

interface AllocationBreakdown {
  cashAndMM: number
  fixedIncome: number
  equities: number
  alternatives: number
  realEstate: number
}

interface RebalancingAction {
  assetClass: string
  currentPercentage: number
  targetPercentage: number
  variance: number
  action: 'increase' | 'decrease' | 'maintain'
  suggestedAmount: number
  priority: 'high' | 'medium' | 'low'
}

function PortfolioHealthDashboard({ entityIds }: { entityIds: string[] }) {
  const { data } = usePortfolioHealth(entityIds)
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Portfolio Health Check</h1>
        <Button variant="outline" onClick={() => setShowSettings(true)}>
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>
      
      {/* Asset Allocation vs Targets */}
      <Card>
        <CardHeader>
          <CardTitle>Asset Allocation vs Targets</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Asset Class</TableHead>
                <TableHead className="text-right">Current</TableHead>
                <TableHead className="text-right">Target</TableHead>
                <TableHead className="text-right">Variance</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Cash & Money Market</TableCell>
                <TableCell className="text-right">26.2%</TableCell>
                <TableCell className="text-right">20-25%</TableCell>
                <TableCell className="text-right">
                  <span className="text-red-600">+1.2%</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm">Reduce by $200k</span>
                  </div>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Fixed Income</TableCell>
                <TableCell className="text-right">38.6%</TableCell>
                <TableCell className="text-right">40-45%</TableCell>
                <TableCell className="text-right">
                  <span className="text-green-600">In range</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">In range</span>
                  </div>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Equities</TableCell>
                <TableCell className="text-right">21.5%</TableCell>
                <TableCell className="text-right">25-30%</TableCell>
                <TableCell className="text-right">
                  <span className="text-red-600">-3.5%</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm">Add $300k</span>
                  </div>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Alternatives</TableCell>
                <TableCell className="text-right">13.7%</TableCell>
                <TableCell className="text-right">10-15%</TableCell>
                <TableCell className="text-right">
                  <span className="text-green-600">In range</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">In range</span>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* Tax Loss Harvesting */}
      <Card>
        <CardHeader>
          <CardTitle>Tax Loss Harvesting Opportunities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.taxHarvestingOpportunities.map(opportunity => (
              <div key={opportunity.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{opportunity.symbol} position ({opportunity.entityName})</h4>
                  <p className="text-sm text-muted-foreground">
                    Unrealized loss: {formatCurrency(opportunity.unrealizedLoss)}
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Review Opportunity
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Upcoming Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>April 30: Review Q1 performance</span>
              <Button variant="outline" size="sm">Schedule</Button>
            </div>
            <div className="flex items-center justify-between">
              <span>May 15: Expected statement uploads</span>
              <Button variant="outline" size="sm">Set Reminder</Button>
            </div>
            <div className="flex items-center justify-between">
              <span>June 15: Q2 estimated tax due</span>
              <Button variant="outline" size="sm">Calculate</Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Balance Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Account Balance Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.alerts.filter(alert => alert.type === 'balance').map(alert => (
              <Alert key={alert.id} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{alert.title}</AlertTitle>
                <AlertDescription>{alert.description}</AlertDescription>
              </Alert>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## Workflow 11: Administrative Functions

**User Story:** "I need to add new accounts/entities and manage relationships"

### Core Components

#### 1. Entity Management Interface
```typescript
function EntityManagement() {
  const { data: entities } = useEntities()
  const [showAddEntity, setShowAddEntity] = useState(false)
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Entity Management</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export List
          </Button>
          <Button onClick={() => setShowAddEntity(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Entity
          </Button>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Button variant="outline" className="h-20 flex-col" onClick={() => setShowAddEntity(true)}>
          <Plus className="h-6 w-6 mb-2" />
          Add Entity
        </Button>
        <Button variant="outline" className="h-20 flex-col" onClick={() => setShowAddInstitution(true)}>
          <Building className="h-6 w-6 mb-2" />
          Add Institution
        </Button>
        <Button variant="outline" className="h-20 flex-col" onClick={() => setShowAddAccount(true)}>
          <Wallet className="h-6 w-6 mb-2" />
          Add Account
        </Button>
      </div>
      
      {/* Entity List */}
      <Card>
        <CardHeader>
          <CardTitle>Entities ({entities?.length} active)</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="business">
            <TabsList>
              <TabsTrigger value="business">Business Entities</TabsTrigger>
              <TabsTrigger value="personal">Personal</TabsTrigger>
            </TabsList>
            
            <TabsContent value="business" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">S-Corps:</h4>
                  {entities?.filter(e => e.entity_type === 'S-Corp').map(entity => (
                    <EntityCard key={entity.id} entity={entity} />
                  ))}
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">LLCs:</h4>
                  {entities?.filter(e => e.entity_type === 'LLC').map(entity => (
                    <EntityCard key={entity.id} entity={entity} />
                  ))}
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="personal">
              {entities?.filter(e => e.entity_type === 'Individual').map(entity => (
                <EntityCard key={entity.id} entity={entity} />
              ))}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* Account Assignment */}
      <Card>
        <CardHeader>
          <CardTitle>Account Assignment</CardTitle>
        </CardHeader>
        <CardContent>
          <AccountAssignmentTable />
        </CardContent>
      </Card>
      
      {/* Database Controls */}
      <Card>
        <CardHeader>
          <CardTitle>System Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <SystemControlsPanel />
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 2. Add Entity Form
```typescript
interface AddEntityFormData {
  name: string
  entityType: 'S-Corp' | 'LLC' | 'Partnership' | 'Individual'
  taxId: string
  taxTreatment: 'corporate' | 'pass_through'
  status: 'active' | 'inactive'
  notes?: string
}

function AddEntityDialog({ open, onClose, onSave }: AddEntityDialogProps) {
  const [formData, setFormData] = useState<Partial<AddEntityFormData>>({
    entityType: 'S-Corp',
    taxTreatment: 'pass_through',
    status: 'active'
  })
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSave(formData as AddEntityFormData)
    onClose()
    setFormData({ entityType: 'S-Corp', taxTreatment: 'pass_through', status: 'active' })
  }
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add New Entity</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Entity Name</Label>
            <Input
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Enter entity name"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label>Entity Type</Label>
            <Select
              value={formData.entityType}
              onValueChange={(value) => setFormData({...formData, entityType: value as any})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="S-Corp">S-Corp</SelectItem>
                <SelectItem value="LLC">LLC</SelectItem>
                <SelectItem value="Partnership">Partnership</SelectItem>
                <SelectItem value="Individual">Individual</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label>Tax ID (EIN/SSN)</Label>
            <Input
              value={formData.taxId || ''}
              onChange={(e) => setFormData({...formData, taxId: e.target.value})}
              placeholder="XX-XXXXXXX"
              pattern="[0-9]{2}-[0-9]{7}"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label>Tax Treatment</Label>
            <RadioGroup
              value={formData.taxTreatment}
              onValueChange={(value) => setFormData({...formData, taxTreatment: value as any})}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="corporate" id="corporate" />
                <Label htmlFor="corporate">Corporate (files own return)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="pass_through" id="pass_through" />
                <Label htmlFor="pass_through">Pass-through (flows to personal)</Label>
              </div>
            </RadioGroup>
          </div>
          
          <div className="space-y-2">
            <Label>Status</Label>
            <RadioGroup
              value={formData.status}
              onValueChange={(value) => setFormData({...formData, status: value as any})}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="active" id="active" />
                <Label htmlFor="active">Active</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="inactive" id="inactive" />
                <Label htmlFor="inactive">Inactive</Label>
              </div>
            </RadioGroup>
          </div>
          
          <div className="space-y-2">
            <Label>Notes (Optional)</Label>
            <Textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Additional notes about this entity"
              rows={3}
            />
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={!formData.name || !formData.taxId}>
              Save Entity
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

#### 3. System Controls Panel
```typescript
function SystemControlsPanel() {
  const { data: systemStatus } = useSystemStatus()
  
  return (
    <div className="space-y-6">
      {/* Database Status */}
      <div>
        <h4 className="font-medium mb-2">Database Status</h4>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-3 h-3 rounded-full",
              systemStatus?.database === 'running' ? "bg-green-500" : "bg-red-500"
            )} />
            <span className="text-sm">
              {systemStatus?.database === 'running' ? '🟢 Running' : '🔴 Stopped'} (localhost:54322)
            </span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              Stop Database
            </Button>
            <Button variant="outline" size="sm">
              Restart Database
            </Button>
          </div>
        </div>
      </div>
      
      {/* Data Maintenance */}
      <div>
        <h4 className="font-medium mb-2">Data Maintenance</h4>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Mark account as closed:</span>
            <div className="flex gap-2">
              <Select>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Select Account" />
                </SelectTrigger>
                <SelectContent>
                  {/* Account options */}
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                Mark Closed
              </Button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm">Last backup: Jan 31, 2024 2:30 PM</span>
            <Button variant="outline" size="sm" disabled>
              Run Backup Script (Phase 2)
            </Button>
          </div>
        </div>
      </div>
      
      {/* Performance Stats */}
      <div>
        <h4 className="font-medium mb-2">Performance Statistics</h4>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="text-center">
            <div className="text-2xl font-bold">{systemStatus?.stats.totalEntities}</div>
            <div className="text-sm text-muted-foreground">Entities</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{systemStatus?.stats.totalAccounts}</div>
            <div className="text-sm text-muted-foreground">Accounts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{systemStatus?.stats.totalTransactions.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground">Transactions</div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

## Implementation Guidelines

### Database Operations
- Use transactions for multi-table operations (entity creation with accounts)
- Implement soft deletes for entities and accounts (status = 'inactive')
- Validate unique constraints (entity names, tax IDs, account numbers)
- Log all administrative changes with timestamps

### Form Validation
- Real-time validation for tax ID formats
- Check for duplicate entity names
- Validate account number formats per institution
- Required field validation with clear error messages

### State Management
- Use optimistic updates for better UX
- Implement proper error handling and rollback
- Cache entity/account lists for performance
- Sync state after successful operations

### Security Considerations
- Validate all inputs server-side
- Implement role-based access for administrative functions
- Log all entity/account modifications
- Prevent deletion of entities with active accounts/transactions

---

*This guide provides complete context for administrative workflow implementation. All forms, validation rules, and system controls are specified for autonomous development.*