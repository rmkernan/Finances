# API Endpoints Reference

**Created:** 09/24/25 8:54PM
**Purpose:** Frontend-backend interface specifications for dashboard development

## Database Connection

### Local Supabase Setup
- **Host:** localhost:54322
- **Database:** postgres
- **Connection:** Direct PostgreSQL queries via Supabase client
- **Environment:** LOCAL ONLY - never cloud connections

## Core Data Endpoints

### Entity Operations

#### Get All Entities
```typescript
// GET /entities
interface EntitySummary {
  id: string
  name: string
  entity_type: 'S-Corp' | 'LLC' | 'Individual'
  net_worth: number
  mtd_change: number
  ytd_change: number
  account_count: number
}
```

#### Get Entity Details
```typescript
// GET /entities/{entity_id}
interface EntityDetail extends EntitySummary {
  cash_balance: number
  investment_balance: number
  property_balance: number
  liability_balance: number
  last_updated: string
  notes: string
}
```

### Account Operations

#### Get Entity Accounts
```typescript
// GET /entities/{entity_id}/accounts
interface Account {
  id: string
  account_name: string
  account_number: string // masked
  account_type: 'cash' | 'investment' | 'brokerage' | 'ira' | '401k'
  balance: number
  institution_id: string
  institution_name: string
  last_activity: string
}
```

#### Get Account Holdings (Investment Accounts)
```typescript
// GET /accounts/{account_id}/holdings
interface Holding {
  security_id: string
  symbol: string
  description: string
  quantity: number
  unit_price: number
  market_value: number
  day_change: number
  total_gain_loss: number
}
```

### Transaction Operations

#### Get Account Transactions
```typescript
// GET /accounts/{account_id}/transactions
// Query params: limit, offset, start_date, end_date, transaction_type
interface Transaction {
  id: string
  date: string
  description: string
  transaction_type: 'buy' | 'sell' | 'dividend' | 'interest' | 'fee' | 'deposit' | 'withdrawal'
  amount: number
  balance_after: number
  source_document_id?: string
  federal_taxable: boolean
  state_taxable: boolean
}
```

#### Get Entity Transaction Summary
```typescript
// GET /entities/{entity_id}/transactions/summary
// Query params: period ('MTD' | 'QTD' | 'YTD')
interface TransactionSummary {
  total_inflows: number
  total_outflows: number
  net_flow: number
  by_category: Array<{
    transaction_type: string
    amount: number
    count: number
  }>
}
```

### Document Operations

#### Get Entity Documents
```typescript
// GET /entities/{entity_id}/documents
// Query params: document_type, year, institution_id
interface Document {
  id: string
  file_name: string
  document_type: 'statement' | 'tax_form' | 'confirmation' | 'correspondence'
  institution_name: string
  period_start: string
  period_end: string
  processing_status: 'completed' | 'pending' | 'failed'
  confidence_score: number
  created_at: string
}
```

## Dashboard-Specific Endpoints

### Global Dashboard Data
```typescript
// GET /dashboard/global
interface GlobalDashboard {
  net_worth: {
    total: number
    breakdown: {
      financial_assets: number
      real_assets: number
      liabilities: number
    }
    trend: Array<{ date: string; value: number }>
  }
  entities: EntitySummary[]
  recent_activity: Transaction[]
  upcoming_items: Array<{
    date: string
    type: 'tax_payment' | 'statement_due' | 'document_expected'
    entity_name: string
    description: string
    amount?: number
  }>
}
```

### Entity Dashboard Data
```typescript
// GET /dashboard/entities/{entity_id}
interface EntityDashboard {
  entity: EntityDetail
  accounts_by_institution: Array<{
    institution_id: string
    institution_name: string
    total_balance: number
    accounts: Account[]
  }>
  financial_metrics: {
    cash_flow: {
      mtd_inflows: number
      mtd_outflows: number
      mtd_net: number
    }
    tax_liability: {
      ytd_federal_estimate: number
      ytd_state_estimate: number
    }
    document_status: {
      total: number
      processed: number
      pending: number
      failed: number
    }
  }
  recent_documents: Document[]
}
```

## Query Patterns

### Direct PostgreSQL Queries

Use these patterns when building components:

```sql
-- Entity net worth with change calculation
SELECT
  e.id, e.name, e.entity_type,
  SUM(a.balance) as current_net_worth,
  SUM(a.balance) - LAG(SUM(a.balance), 1) OVER (ORDER BY snapshot_date) as change
FROM entities e
JOIN accounts a ON e.id = a.entity_id
LEFT JOIN account_snapshots s ON a.id = s.account_id
WHERE s.snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY e.id, s.snapshot_date
ORDER BY e.name;

-- Recent transactions across all entities
SELECT
  t.*,
  e.name as entity_name,
  a.account_name,
  i.name as institution_name
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN entities e ON a.entity_id = e.id
JOIN institutions i ON a.institution_id = i.id
ORDER BY t.date DESC
LIMIT 10;

-- Entity cash flow summary
SELECT
  DATE_TRUNC('month', t.date) as month,
  SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as inflows,
  SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as outflows
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.entity_id = $1
  AND t.date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY month
ORDER BY month;
```

## Error Handling

### Standard Error Response
```typescript
interface APIError {
  error: string
  message: string
  details?: any
}
```

### Common Errors
- `ENTITY_NOT_FOUND` - Entity ID doesn't exist
- `ACCOUNT_ACCESS_DENIED` - Account doesn't belong to entity
- `DATABASE_CONNECTION_ERROR` - Local Supabase unavailable
- `INVALID_DATE_RANGE` - Date parameters malformed

## Performance Guidelines

### Caching Strategy
- Entity list: Cache for 5 minutes
- Account balances: Cache for 2 minutes
- Transaction data: Cache for 30 seconds
- Document metadata: Cache for 10 minutes

### Pagination
- Default limit: 50 items
- Maximum limit: 200 items
- Use offset-based pagination for transactions
- Use cursor-based pagination for documents

### Query Optimization
- Always include entity_id in WHERE clauses
- Use proper indexes on date columns
- Aggregate data at query level, not client level
- Limit result sets with appropriate LIMIT clauses