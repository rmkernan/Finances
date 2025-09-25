# 🛠️ Implementer Resources

**Updated:** 09/25/25 1:49PM - Added navigation breadcrumb, quality gate mandate, and database connection test
**Found via:** Root CLAUDE.md → Frontend Development → Quick Start
**Working Directory:** `/Users/richkernan/Projects/Finances/frontend/wealth-manager/`

## Quality Gates (Must Pass)
```bash
npm run quality && npm run build && npm run dev
```
**→ Required before any code changes** (see root CLAUDE.md for details)

## Schema Quick Reference (Common Traps)
```typescript
// ❌ Wrong (logical assumptions)
account.account_id  // → account.id
account_type === 'investment'  // → 'brokerage' | 'cash_management'

// ✅ Verify first
grep "interface Account" src/types/supabase.ts -A 10
PGPASSWORD=postgres psql -c "SELECT DISTINCT account_type FROM accounts"
```

## TypeScript Errors → Quick Fixes
- `Property 'X' does not exist` → Check field names in `src/types/supabase.ts`
- `Cannot find module '@/components/ui/X'` → Check existing UI patterns first
- `Type 'undefined' not assignable` → Add `|| null` or optional chaining

## Current System State
- 3 active accounts (brokerage: 2, cash_management: 1)
- Both account types can have positions (152 total positions)
- PostgreSQL at `localhost:54322` (password: postgres)

**Quick Connection Test:**
```bash
PGPASSWORD=postgres psql -h localhost -p 54322 -d postgres -c "SELECT COUNT(*) FROM accounts;"
```

## Before Writing Code
1. **Find existing patterns:** `grep -r "similar_feature" src/`
2. **Verify schema:** Check database or existing hooks
3. **Test small:** Write minimal query first
4. **Quality check early:** After each component

## Resources (When Needed)
- **[REFERENCE.md](./REFERENCE.md)** - Patterns, commands, gotchas
- **[SCHEMA_CHEATSHEET.md](./SCHEMA_CHEATSHEET.md)** - Database field reference

## Component Standards
- Under 200 lines (split if larger)
- Use existing UI components: `ls src/components/ui/`
- Strategic comments only (WHY, not WHAT)

---
*Trust your skills. These are just the project-specific gotchas.*