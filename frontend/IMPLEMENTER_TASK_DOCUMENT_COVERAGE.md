# Implementation Task: Document Coverage Map & Data Status Enhancement

**Created:** 09/26/25
**Purpose:** Standalone implementation guide for Document Coverage Map feature
**Priority:** HIGH - User-requested critical feature

## 🎯 Your Mission

You are implementing a Document Coverage Map that visually shows which months have financial statements loaded for each account/entity combination. This is a critical feature for tracking data completeness across the financial management system.

## 📋 Pre-Implementation Checklist

**MANDATORY - Complete these steps before writing any code:**

1. **Read Project Context:**
   ```bash
   # Read the root CLAUDE.md to understand the project
   cat /Users/richkernan/Projects/Finances/CLAUDE.md
   ```

2. **Verify Development Environment:**
   ```bash
   cd /Users/richkernan/Projects/Finances/frontend/wealth-manager
   npm run quality && npm run build && npm run dev
   ```
   - ✅ All checks must pass before proceeding
   - ✅ Development server must start successfully

3. **Review Existing Architecture:**
   ```bash
   # Understand the foundation components
   cat src/components/ui/UniversalTable.tsx
   cat src/app/admin/data-status/page.tsx
   cat src/hooks/useDataStatus.ts
   ```

## 🏗️ Implementation Requirements

### Feature 1: Document Coverage Map (Primary)

**User Story:** As a financial manager, I need to see at a glance which months have statements loaded for each account, so I can identify gaps in my financial records.

**Visual Design:**
```
Account Name | Entity | 2024                        | 2025
                      | J F M A M J J A S O N D | J F M A M J J A S O N D
-------------+--------+------------------------+------------------------
Kern Brok    | R&L    | ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ❌ ❌ ❌ | ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ❌ ❌ ❌ ❌
Kern CMA     | R&L    | ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ❌ ❌ ❌ | ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ❌ ❌ ❌ ❌
```

**Technical Requirements:**

1. **Create New Page:** `/admin/document-coverage/page.tsx`
   - Must follow the same pattern as `/admin/data-status/page.tsx`
   - Use existing UI components from `@/components/ui/`

2. **Data Hook:** Create `useDocumentCoverage` hook
   - Query documents table grouped by account_id and extract(month/year from document_date)
   - Return structured data showing coverage by account/month
   - Include smart defaults: If first document exists, expect all months from 2024-01 through current month

3. **Coverage Logic:**
   - ✅ Green check: Document exists for this month
   - ❌ Red X: Expected but missing (after first document date)
   - Empty: Not expected (before first document date)

4. **Visual Features:**
   - Collapsible by entity (group accounts under their entities)
   - Hover tooltips showing document count for each month
   - Click on month to see document list (modal or drawer)
   - Summary statistics at top (total coverage %, missing documents count)

### Feature 2: Enhanced Data Status Integration

**Requirement:** Add a "Document Coverage" summary card to the existing `/admin/data-status` page

**Implementation:**
1. Add coverage percentage calculation to `useDataStatus` hook
2. Create new summary card showing:
   - Total document coverage percentage
   - Number of missing expected documents
   - Link to full Document Coverage Map

### Feature 3: Navigation Updates

**Requirement:** Add Document Coverage Map to admin navigation

**Implementation:**
1. Update admin layout or navigation component
2. Add menu item: "Document Coverage" with appropriate icon (Calendar, FileText, or CheckSquare from lucide-react)
3. Ensure consistent navigation patterns with existing admin pages

## 🗄️ Database Schema Reference

```sql
-- Key tables you'll need to query
-- documents table structure:
- id: uuid
- account_id: uuid (FK to accounts)
- document_date: date
- document_type: text
- file_path: text
- created_at: timestamp

-- accounts table structure:
- id: uuid
- account_name: text
- entity_id: uuid (FK to entities)
- institution_id: uuid
- account_type: text

-- entities table structure:
- id: uuid
- entity_name: text
```

## 🧪 Testing Requirements

**MANDATORY - Complete ALL testing before marking as complete:**

1. **Quality Gates:**
   ```bash
   npm run quality   # Must pass with zero errors
   npm run build     # Must build successfully
   npm run dev       # Must run without console errors
   ```

2. **Functional Testing:**
   - [ ] Navigate to `/admin/document-coverage` - page loads without errors
   - [ ] Verify all active accounts are displayed
   - [ ] Check that coverage indicators are accurate (cross-reference with documents table)
   - [ ] Test collapsible entity groups (if implemented)
   - [ ] Verify hover tooltips work
   - [ ] Click on covered months - shows document details
   - [ ] Verify summary statistics are accurate

3. **Integration Testing:**
   - [ ] Check `/admin/data-status` shows new coverage card
   - [ ] Navigation links work correctly
   - [ ] No TypeScript errors in IDE
   - [ ] No console errors in browser

## 📝 Implementation Steps (Suggested Order)

1. **Create the data hook first** (`useDocumentCoverage`)
   - Start with a simple query to get document dates by account
   - Build the coverage calculation logic
   - Test with console.log to verify data structure

2. **Build the basic page structure**
   - Copy `/admin/data-status/page.tsx` as template
   - Create simple table showing accounts and months
   - Add coverage indicators (✅/❌)

3. **Add visual enhancements**
   - Implement entity grouping
   - Add hover tooltips
   - Create click handlers for month cells

4. **Integrate with existing pages**
   - Update data-status page with coverage card
   - Add navigation links

5. **Polish and optimize**
   - Add loading states
   - Handle errors gracefully
   - Optimize queries if needed

## ⚠️ Important Constraints

1. **Use Existing Components:** Leverage components from `@/components/ui/` - DO NOT create new base components
2. **Follow Patterns:** Match the coding patterns in existing admin pages
3. **TypeScript Strict:** All code must be fully typed - no `any` types
4. **Performance:** Consider pagination or virtualization if dealing with many accounts
5. **Responsive:** Must work on desktop and tablet (mobile is nice-to-have)

## ✅ Definition of Done

**Your implementation is complete when:**

1. [ ] All quality checks pass (`npm run quality && npm run build`)
2. [ ] Document Coverage Map page is fully functional at `/admin/document-coverage`
3. [ ] Coverage summary integrated into `/admin/data-status`
4. [ ] Navigation updated with new menu item
5. [ ] All TypeScript types are properly defined (no `any`)
6. [ ] User can see coverage at a glance and identify gaps
7. [ ] User has tested and confirmed acceptance
8. [ ] Code is committed to Git with descriptive commit message

## 🚀 Final Steps

**After implementation is complete and tested:**

1. **Run Final Quality Check:**
   ```bash
   npm run quality && npm run build && npm run dev
   ```

2. **Inform User for Testing:**
   - Show them the new Document Coverage Map
   - Demonstrate the coverage indicators
   - Get explicit confirmation that it meets their needs

3. **Commit to Git (ONLY after user approval):**
   ```bash
   git add .
   git status  # Review changes
   git commit -m "feat: Add Document Coverage Map for tracking statement completeness

   - Created visual monthly coverage grid showing ✅/❌ indicators
   - Added smart detection of expected vs missing documents
   - Integrated coverage statistics into data-status page
   - Implemented entity grouping and interactive month details

   Closes: Week 4 Day 11 High Priority User Request"
   ```

## 💡 Tips for Success

1. **Start Simple:** Get a basic version working first, then add enhancements
2. **Check Existing Patterns:** Look at how `/admin/data-status` handles similar requirements
3. **Use the Database:** Write efficient SQL queries - avoid loading all documents into memory
4. **Think User-First:** The goal is to quickly identify missing statements
5. **Ask Questions:** If requirements are unclear, ask for clarification before proceeding

## 🆘 If You Get Stuck

1. Review existing admin pages for patterns
2. Check the Supabase types in `src/types/supabase.ts`
3. Look at how other hooks query the database
4. Verify your database connection is working
5. Ask for clarification on any ambiguous requirements

---

Remember: The user CANNOT read code. Communicate problems and solutions in clear English. Focus on delivering a working solution that helps them track their financial document completeness.