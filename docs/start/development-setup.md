# Development Environment Setup

**Created:** 09/24/25 8:54PM
**Purpose:** Complete development environment configuration for financial management system

## 🎯 Current State: No Frontend Codebase Yet

**Status:** Backend operational, frontend to be created from scratch
- ✅ **Database:** PostgreSQL via local Supabase (localhost:54322) with 12-table schema loaded
- ✅ **Data:** Financial transactions, entities, accounts populated
- ✅ **Processing:** Document extraction pipeline working
- ❌ **Frontend:** Not created yet - will build with Next.js 14

## 🚀 Frontend Project Creation

### When Ready to Build Dashboard:

**1. Create Next.js Project**
```bash
npx create-next-app@latest financial-dashboard --typescript --tailwind --eslint --app
cd financial-dashboard
```

**2. Install Required Dependencies**
```bash
# UI Components
npm install @radix-ui/react-icons
npm install @radix-ui/react-slot
npm install class-variance-authority
npm install clsx
npm install lucide-react
npm install tailwind-merge

# Data Fetching & State
npm install @tanstack/react-query
npm install @supabase/supabase-js

# Charts & Visualization
npm install recharts
npm install @tremor/react

# Forms & Validation
npm install react-hook-form
npm install @hookform/resolvers
npm install zod

# Date Handling
npm install date-fns
```

**3. Setup shadcn/ui Components**
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card table badge dialog
```

**4. Configure Supabase Connection**
```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'http://localhost:54322'
const supabaseKey = 'your-anon-key' // Get from local Supabase dashboard

export const supabase = createClient(supabaseUrl, supabaseKey)
```

## 🗄️ Database Connection Details

### Local Supabase Access
- **URL:** http://localhost:54322
- **Dashboard:** http://localhost:54323
- **Database:** postgres
- **Direct Connection:** postgresql://postgres:postgres@localhost:54322/postgres

### Key Tables for Frontend
```sql
-- Core data tables
entities          -- Business entities and personal accounts
accounts          -- Financial accounts (checking, investment, etc.)
transactions      -- All financial transactions
documents         -- Processed financial documents
holdings          -- Investment positions

-- Configuration tables
map_rules         -- Transaction classification rules
institutions      -- Banks and financial institutions
tax_categories    -- Tax classification system
```

## 📁 Recommended Project Structure

**When creating frontend:**
```
financial-dashboard/
├── app/                          # Next.js 14 app router
│   ├── globals.css
│   ├── layout.tsx               # Root layout with nav
│   ├── page.tsx                 # Global dashboard
│   └── entities/
│       ├── [entity]/
│       │   ├── page.tsx         # Entity dashboard
│       │   ├── institutions/
│       │   └── accounts/
├── components/
│   ├── ui/                      # shadcn/ui components
│   ├── dashboard/               # Dashboard-specific components
│   │   ├── net-worth-summary.tsx
│   │   ├── entity-card.tsx
│   │   └── transaction-table.tsx
│   └── layout/
│       ├── main-nav.tsx
│       └── sidebar.tsx
├── lib/
│   ├── supabase.ts             # Database connection
│   ├── queries.ts              # SQL query functions
│   └── utils.ts                # Utility functions
├── types/
│   └── database.ts             # TypeScript interfaces
└── hooks/
    └── use-dashboard-data.ts   # Data fetching hooks
```

## 🔧 Development Workflow

### Before Starting Frontend Development:

**1. Verify Database Connection**
```bash
# Test connection to local Supabase
psql postgresql://postgres:postgres@localhost:54322/postgres -c "SELECT COUNT(*) FROM entities;"
```

**2. Check Data Availability**
```sql
-- Verify you have data to work with
SELECT e.name, COUNT(a.id) as account_count, COUNT(t.id) as transaction_count
FROM entities e
LEFT JOIN accounts a ON e.id = a.entity_id
LEFT JOIN transactions t ON a.id = t.account_id
GROUP BY e.id, e.name;
```

**3. Review Configuration Files**
- `/config/account-mappings.json` - Entity/account relationships
- `/docs/Design/Database/schema.md` - Complete database structure
- `/docs/Design/01-Requirements/BUILD-dashboards.md` - UI specifications

## 🎨 Design System Ready

### Technology Stack (Decided)
- **Framework:** Next.js 14 with App Router
- **Styling:** Tailwind CSS with shadcn/ui components
- **Database:** Supabase client for PostgreSQL
- **Charts:** Recharts for financial visualizations
- **State Management:** React Query for server state

### UI Components Available
- Responsive layouts (mobile-first)
- Financial metric cards
- Transaction tables with filtering
- Entity/account navigation
- Document viewers

## 🚨 Security & Safety

### Local Development Only
- **NEVER** connect to cloud databases
- **ALWAYS** verify localhost:54322 connection
- **BACKUP** before any database changes
- **TEST** queries with small datasets first

### Data Protection
- Mask account numbers in UI
- Never log sensitive financial data
- Use proper TypeScript types for data validation

## 🎯 Next Steps

**When user says "Build the dashboard":**

1. **Create Next.js project** with above setup
2. **Configure database connection** and verify data access
3. **Build layout infrastructure** (nav, routing, responsive design)
4. **Implement Global Dashboard** following BUILD-dashboards.md specifications
5. **Test with real financial data** from loaded database

The BUILD guides contain complete component specifications, SQL queries, and interaction patterns - everything needed for autonomous frontend development.