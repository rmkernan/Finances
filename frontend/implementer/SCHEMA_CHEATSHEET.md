# 📋 Schema Cheat Sheet

**Updated:** 09/25/25 1:56PM - Added documents table fields and verification commands
**Purpose:** Prevent field name mismatches and type assumptions

## Key Tables & Fields

### accounts
```typescript
id: string                    // ⚠️ NOT account_id
account_name: string | null
account_type: string          // 'brokerage' | 'cash_management'
entity_id: string
institution_id: string
account_status: string        // Filter: 'active'
```

### transactions
```typescript
id: string
account_id: string           // References accounts.id
transaction_date: string
amount: number
description: string | null
transaction_type: string
```

### positions
```typescript
id: string
account_id: string           // References accounts.id
position_date: string
sec_ticker: string | null    // ⚠️ NOT symbol
sec_name: string | null
quantity: number
price: number
end_market_value: number
```

### entities
```typescript
id: string
entity_name: string
entity_type: string
```

### institutions
```typescript
id: string
institution_name: string
```

### documents
```typescript
id: string
file_name: string
document_type: string
created_at: string | null
processed_at: string | null
activities_loaded: string | null    // ⚠️ Timestamp for activities loading
positions_loaded: string | null     // ⚠️ Timestamp for holdings loading
institution_id: string
```

## Account Type Logic
```typescript
// ✅ Both types can have positions
'brokerage'        // Investment accounts (stocks, bonds, etc.)
'cash_management'  // Can hold money market, bonds, deposits

// ⚠️ Don't assume 'investment' type exists
```

## Verification Commands
```bash
# Check field names
\d+ accounts;
\d+ positions;
\d+ documents;

# Check actual values
SELECT DISTINCT account_type FROM accounts;
SELECT DISTINCT transaction_type FROM transactions;
SELECT DISTINCT document_type FROM documents;

# Quick counts
SELECT account_type, COUNT(*) FROM accounts GROUP BY account_type;
SELECT document_type, COUNT(*) FROM documents GROUP BY document_type;
```

## Query Patterns That Work
```typescript
// With relations
.select('*, entity:entities(*), institution:institutions(*)')

// Filter active accounts
.eq('account_status', 'active')

// Order by date (newest first)
.order('transaction_date', { ascending: false })
```