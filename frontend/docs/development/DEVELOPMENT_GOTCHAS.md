# Development Gotchas & Prevention Guide

**Created:** 09/25/25 12:50PM
**Purpose:** Document common pitfalls and prevention strategies based on real implementation experiences

## 🚨 Common Schema Mismatches

### Problem 1: Field Name Assumptions
**What Goes Wrong:**
```typescript
// ❌ ASSUMED (logical but wrong)
account.account_id
transaction.transaction_id
position.symbol

// ✅ ACTUAL (from database)
account.id
transaction.id
position.sec_ticker
```

**Prevention:**
```bash
# ALWAYS check actual schema first
grep -A 10 "export interface Account" src/types/supabase.ts
# Or query database directly
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres -c "\d accounts"
```

### Problem 2: Enum Value Assumptions
**What Goes Wrong:**
```typescript
// ❌ ASSUMED
account_type === 'investment' | 'checking' | 'savings'

// ✅ ACTUAL
account_type === 'brokerage' | 'cash_management' | 'retirement'
```

**Prevention:**
```bash
# Check distinct values in database
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "SELECT DISTINCT account_type FROM accounts"
```

### Problem 3: Relationship Assumptions
**What Goes Wrong:**
```typescript
// ❌ ASSUMED
account.entity  // Direct object

// ✅ ACTUAL
account.entity_id  // Foreign key requiring join
```

**Prevention:**
```typescript
// Check existing working queries
grep -r "from('accounts')" src/hooks/
# Look for .select() patterns with joins
```

## 🔍 Pre-Development Verification Checklist

### Before Writing ANY Database Query:

1. **Check Schema Definition**
```bash
# Find exact field names
grep "export interface TableName" src/types/supabase.ts -A 20
```

2. **Verify with Existing Code**
```bash
# Find similar successful queries
grep -r "from('table_name')" src/
# Check how fields are accessed
grep -r "account\." src/hooks/
```

3. **Test with Minimal Query**
```typescript
// Write simplest possible query first
const { data } = await supabase
  .from('accounts')
  .select('*')
  .limit(1)
console.log('Fields:', Object.keys(data[0]))  // See actual fields
```

4. **Cross-Reference Types**
```bash
# Check generated types match usage
npm run type-check --watch
```

## 🛠️ Component Development Gotchas

### Problem: Missing UI Dependencies
**What Goes Wrong:**
```typescript
// ❌ Import from non-existent package
import { Card } from '@/components/ui/card'  // Doesn't exist

// ✅ Check what's actually available
ls src/components/ui/
```

**Prevention:**
```bash
# Before creating new UI component
ls src/components/ui/  # What exists?
grep -r "className.*card" src/  # How are cards implemented?
```

### Problem: Incorrect Hook Patterns
**What Goes Wrong:**
```typescript
// ❌ Wrong React Query pattern
return useQuery(['key'], fetchFunction)

// ✅ Correct v5 pattern
return useQuery({
  queryKey: ['key'],
  queryFn: fetchFunction
})
```

**Prevention:**
```bash
# Check existing hook patterns
grep -r "useQuery({" src/hooks/ | head -5
```

## 📋 Development Workflow 2.0

### Old Workflow (Error-Prone):
1. Read requirements
2. Make assumptions about schema
3. Write complete feature
4. Run quality checks
5. Fix multiple errors

### New Workflow (Verified):
```bash
# 1. Verify Schema
grep "interface Account" src/types/supabase.ts -A 30
PGPASSWORD=postgres psql -c "SELECT * FROM accounts LIMIT 1"

# 2. Check Existing Patterns
grep -r "useAccounts" src/  # Find similar hooks
grep -r "AccountsList" src/  # Find similar components

# 3. Write Minimal Test
# Create simplest version first
echo "Test query..." > test-query.ts
npm run type-check  # Verify immediately

# 4. Incremental Development
# Build one piece at a time
npm run quality  # After EACH component
npm run build    # Verify routing

# 5. Cross-Reference Working Code
# Before each new pattern, find existing example
```

## 🎯 Quick Reference Commands

### Database Schema Verification
```bash
# View all tables
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres -c "\dt"

# View specific table schema
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres -c "\d accounts"

# Check enum values
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "SELECT DISTINCT column_name FROM table_name"

# View first row (see all fields)
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "SELECT * FROM accounts LIMIT 1"
```

### Code Pattern Verification
```bash
# Find how a table is queried
grep -r "from('table_name')" src/

# Find field usage patterns
grep -r "account\." src/ | grep -v node_modules

# Check import patterns
grep -r "import.*from.*components" src/

# Find existing type definitions
grep -r "interface.*Account" src/types/
```

### Type Checking
```bash
# Run type check in watch mode
npm run type-check -- --watch

# Check specific file
npx tsc --noEmit src/hooks/useAccount.ts
```

## 🚫 Never Assume, Always Verify

### Common Incorrect Assumptions:
1. **Field naming:** `table_id` vs `id`
2. **Boolean fields:** `is_active` vs `status === 'active'`
3. **Relationships:** Direct objects vs foreign keys
4. **Enums:** Logical values vs business-specific terms
5. **Nullability:** Required vs optional fields

### Verification Before Assumption:
1. **Check the database directly**
2. **Find existing working code**
3. **Read generated types carefully**
4. **Test with minimal examples**
5. **Run quality checks incrementally**

## 💡 Pro Tips

1. **Create a Schema Cheat Sheet**
```bash
# Generate once, reference often
PGPASSWORD=postgres psql -h localhost -p 54322 -U postgres -d postgres \
  -c "\d+ accounts; \d+ transactions; \d+ positions;" > schema-reference.txt
```

2. **Use TypeScript Strict Mode**
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true
  }
}
```

3. **Install Error Lens VSCode Extension**
- Shows TypeScript errors inline
- Catches mismatches immediately

4. **Create Test Queries File**
```typescript
// src/test-queries.ts
// Keep working query examples here
const accountQuery = supabase
  .from('accounts')
  .select('*, entity:entities(*)')
```

## 🔄 Continuous Improvement

After each development session:
1. Document new gotchas discovered
2. Update this guide with solutions
3. Add verification commands used
4. Share patterns that worked

---

*Remember: The database schema is the source of truth, not our logical assumptions. When in doubt, verify!*