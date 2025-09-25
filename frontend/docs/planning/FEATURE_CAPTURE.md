# Feature Capture - Page-by-Page Review

**Created:** 09/25/25 1:55PM ET
**Purpose:** Systematic capture of user-requested features through page-by-page walkthrough
**Status:** Ready for review sessions

## Review Methodology

**Approach:** User navigates each page and provides observations
**Documentation:** Capture requests in structured format with priority levels
**Output:** Prioritized, sequenced feature backlog for implementation

## Priority Levels
- 🔴 **Critical** - Blocks workflow, must fix immediately
- 🟠 **High** - Significant improvement to daily usage
- 🟡 **Medium** - Nice to have, enhances experience
- 🟢 **Low** - Polish/future enhancement

## Pages to Review

- [ ] Dashboard (main landing)
- [ ] Accounts (primary navigation)
- [ ] Account Detail Pages (daily usage)
- [ ] Transactions (data analysis)
- [ ] Entities (business structure)
- [ ] Documents (processing workflow)
- [ ] Admin/Data Status (monitoring)

---

## Feature Requests by Page

### Dashboard
**Review Status:** ✅ Complete
**Current Observations:** Top metrics bar, portfolio summary, entity overview cards, all accounts section, recent activity section

**Requested Features:**

🟠 **Navigation Enhancement - Top Metrics Bar**
- Make entities, accounts, institutions counts clickable → navigate to respective pages
- Priority: High (improves navigation efficiency)

🟠 **Dynamic Portfolio Summary**
- Add dropdowns to filter portfolio summary by entity or institution
- Make summary card responsive to user selections
- Priority: High (core workflow improvement)

🟠 **Dynamic Entity Overview Cards**
- Make entity cards responsive to filtering criteria
- Allow dynamic content based on user selection
- Priority: High (matches portfolio summary functionality)

🟠 **Collapsible All Accounts Section**
- Add expand/collapse functionality for accounts grouped by institution
- Make all account names hyperlinked to account detail pages
- Priority: High (daily navigation improvement)

🟠 **Interactive Recent Activity**
- Make activity items clickable → navigate to specific transaction
- Add expandable detail view with toggle functionality
- Allow multiple items expanded simultaneously
- Priority: High (transaction analysis workflow)

### Accounts
**Review Status:** ✅ Complete
**Current Observations:** Main accounts landing page, individual account detail pages with Overview/Transactions/Positions tabs

**Requested Features:**

🔴 **Edit Functionality - Universal**
- Add edit function for accounts, entities, institutions
- Implement "_screen" attributes for display names (preserves data integrity)
- Separate user-facing names from system matching data
- Priority: Critical (core content management)

🟠 **Accounts Landing Page Layout**
- Organize accounts by institution (match other pages)
- Consistent look and feel across application
- Priority: High (visual consistency)

🟠 **Account Overview Tab Design**
- Design Overview tab content based on available account data
- Include income summary tables from source statements
- Default to most recent month data
- Add month/date range selection controls
- Priority: High (core account analysis)

### Account Detail Pages
**Review Status:** ✅ Complete
**Current Observations:** Tabbed interface (Overview, Transactions, Positions) with varying completeness

**Requested Features:**

🟠 **Consistent Table Design**
- Transactions tab matches other transaction tables (expandable rows, sorting)
- Positions tab matches other position tables (same look/feel)
- Priority: High (user experience consistency)

🔴 **Date Display Fix**
- Fix "July 30th" → "August 31st" for positions as-of dates
- Correct month-end date logic (28th/30th/31st based on actual month)
- Priority: Critical (data accuracy)

### Transactions
**Review Status:** Not started
**Current Observations:** [To be captured]

**Requested Features:**
[To be populated during review]

### Entities
**Review Status:** ✅ Complete
**Current Observations:** Entity cards navigate to detail pages, account breakdown section, portfolio holdings section, transactions table

**Requested Features:**

🟡 **URL-Friendly Entity Pages**
- Make entity page URLs match entity names (truncated, unique identifiers)
- Example: `/entities/milton-preschool` instead of `/entities/123`
- Priority: Medium (SEO/bookmarking improvement)

🟠 **Enhanced Account Breakdown**
- Match Dashboard's all accounts functionality
- Add expand/collapse for accounts grouped by institution
- Priority: High (consistency across pages)

🟡 **Visual Enhancement - Institution/Account Icons**
- Use institution logos for institution icons
- Use account-type-specific icons (brokerage, retirement, etc.)
- Priority: Medium (visual polish, user experience)

🟠 **Interactive Portfolio Holdings**
- Clickable rows with expandable detail view
- Sortable by all header columns
- Change "Attribute Type" to "Class" (from sec_class DB field)
- Visual distinction for options vs other securities
- Priority: High (core data analysis workflow)

🔴 **Options Expiration Indicators**
- Red/Yellow/Green indicators for options expiring in 30/15/7 days
- Uses existing DB flags for 15-day expiration
- Priority: Critical (risk management for options trading)

🟠 **Multi-Account Holdings Display**
- Show which account(s) contain each holding
- Multiple accounts visible when row expanded
- Priority: High (position tracking across accounts)

🟠 **Dynamic As-Of Date Control**
- Fix current "August 30th" to "August 31st" (end of month)
- Add dropdown for last 24 months by end-of-month
- Priority: High (historical analysis capability)

🟠 **Enhanced Transactions Table**
- Default to previous full month instead of current filter
- Make all columns sortable
- Add account column for transaction context
- Clickable rows with expandable detail toggle
- Priority: High (transaction analysis workflow)

### Documents
**Review Status:** ✅ Complete
**Current Observations:** Document listing with processing status and metadata

**Requested Features:**

🟠 **Enhanced Document Table**
- Make all columns sortable (applies to all tables globally)
- Add PDF preview popup when clicking document names
- Priority: High (document workflow improvement)

### Institutions
**Review Status:** ✅ Complete
**Current Observations:** Institution cards with account summaries and navigation

**Requested Features:**

🟠 **Institution Detail Navigation**
- Make institution cards clickable → navigate to institution detail pages
- Add toggle for "six more accounts" to show/hide additional accounts
- Priority: High (navigation completeness)

### Global Navigation
**Review Status:** ✅ Complete
**Current Observations:** URL structure and naming conventions

**Requested Features:**

🟡 **SEO-Friendly URLs**
- Make all URLs intuitive: `/institutions/fidelity`, `/accounts/rich-ira`, `/entities/milton-preschool`
- Use name-based routing for better bookmarking/sharing
- Priority: Medium (user experience polish)

### Global Table Standards
**Review Status:** ✅ Complete
**Current Observations:** Multiple table implementations with varying capabilities

**Requested Features:**

🟠 **Universal Table Features**
- All tables sortable by header column (application-wide standard)
- Consistent expandable row functionality where applicable
- Uniform styling and interaction patterns
- Priority: High (system-wide consistency)

### Admin/Data Status
**Review Status:** Not started
**Current Observations:** [To be captured]

**Requested Features:**
[To be populated during review]

---

## Implementation Planning

### Prioritized Feature List (Dependency-Ordered)

#### 🔴 **CRITICAL - Week 4, Days 1-2**
1. **Options Expiration Indicators** (positions tables)
   - Red/Yellow/Green indicators for options expiring in 30/15/7 days
   - **Dependency**: None - standalone visual enhancement
   - **Impact**: Risk management for options trading

2. **Date Display Fix** (account positions)
   - Fix "July 30th" → "August 31st" for positions as-of dates
   - Correct month-end date logic (28th/30th/31st)
   - **Dependency**: None - data accuracy fix
   - **Impact**: Critical data integrity

#### 🟠 **HIGH PRIORITY - Week 4, Days 3-5**

**Foundation Layer:**
3. **Universal Table Features** (system-wide)
   - All tables sortable by header column
   - Consistent expandable row functionality
   - Uniform styling and interaction patterns
   - **Dependency**: Must come before other table enhancements
   - **Impact**: Enables all subsequent table features

4. **Edit Functionality Core** (accounts, entities, institutions)
   - Add "_screen" attributes for display names
   - Implement edit modal component
   - **Dependency**: Database schema additions first
   - **Impact**: Foundation for content management

**Navigation & Structure:**
5. **Navigation Enhancement - Top Metrics Bar**
   - Make entities, accounts, institutions counts clickable
   - **Dependency**: Universal table features
   - **Impact**: Core navigation improvement

6. **Accounts Landing Page Layout**
   - Organize accounts by institution (match other pages)
   - **Dependency**: Universal table features
   - **Impact**: Visual consistency

#### 🟠 **HIGH PRIORITY - Week 4, Days 6-8**

**Interactive Features:**
7. **Dynamic Portfolio Summary**
   - Add dropdowns to filter by entity or institution
   - Up to 2 selection criteria simultaneously
   - **Dependency**: Edit functionality, universal tables
   - **Impact**: Core workflow improvement

8. **Interactive Recent Activity**
   - Make activity items clickable → navigate to transactions
   - Add expandable detail view with toggle
   - Multiple items expanded simultaneously
   - **Dependency**: Universal table features, transaction expansion details
   - **Impact**: Transaction analysis workflow

9. **Enhanced Transactions Table** (all locations)
   - Default to previous full month
   - Add account column for context
   - Clickable rows with expandable detail toggle
   - **Dependency**: Universal table features
   - **Impact**: Transaction analysis workflow

#### 🟠 **HIGH PRIORITY - Week 4, Days 9-10**

**Portfolio Features:**
10. **Interactive Portfolio Holdings**
    - Clickable rows with expandable detail view
    - Change "Attribute Type" to "Class" (from sec_class DB field)
    - Visual distinction for options vs other securities
    - **Dependency**: Universal table features, options indicators
    - **Impact**: Core data analysis workflow

11. **Multi-Account Holdings Display**
    - Show which account(s) contain each holding
    - Multiple accounts visible when row expanded
    - **Dependency**: Interactive portfolio holdings
    - **Impact**: Position tracking across accounts

12. **Account Overview Tab Design**
    - Design Overview tab based on available account data
    - Include income summary tables from source statements
    - Default to most recent month data
    - **Dependency**: Universal table features, date controls
    - **Impact**: Core account analysis

#### 🟠 **HIGH PRIORITY - Week 4, Days 11-12**

**Advanced Controls:**
13. **Dynamic As-Of Date Control**
    - Add dropdown for last 24 months by end-of-month (data months only)
    - Both simple dropdown and date range picker options
    - **Dependency**: Account overview tab
    - **Impact**: Historical analysis capability

14. **Enhanced Document Table**
    - PDF preview popup when clicking document names (new window, scrollable)
    - Use KRK_Scraper PDF viewer component pattern
    - **Dependency**: Universal table features
    - **Impact**: Document workflow improvement

15. **Institution Detail Navigation**
    - Make institution cards clickable → navigate to detail pages
    - Add toggle for "six more accounts" show/hide
    - **Dependency**: Universal navigation patterns
    - **Impact**: Navigation completeness

#### 🟡 **MEDIUM PRIORITY - Week 5**

16. **Enhanced Account Breakdown** (entity pages)
    - Match Dashboard's all accounts functionality
    - Add expand/collapse for accounts grouped by institution
    - **Dependency**: Collapsible accounts section, universal tables
    - **Impact**: Consistency across pages

17. **Collapsible All Accounts Section** (dashboard)
    - Add expand/collapse for accounts grouped by institution
    - Make all account names hyperlinked to account pages
    - **Dependency**: Universal table features
    - **Impact**: Daily navigation improvement

18. **Dynamic Entity Overview Cards**
    - Make entity cards responsive to filtering criteria
    - **Dependency**: Dynamic portfolio summary patterns
    - **Impact**: Matches portfolio summary functionality

19. **Visual Enhancement - Institution/Account Icons**
    - Use institution logos for institution icons
    - Use account-type-specific icons (brokerage, retirement, etc.)
    - **Dependency**: Icon sourcing and placeholder logic
    - **Impact**: Visual polish

20. **SEO-Friendly URLs**
    - Make all URLs intuitive: `/institutions/fidelity`, `/accounts/rich-ira`
    - **Dependency**: Routing infrastructure changes
    - **Impact**: User experience polish

21. **URL-Friendly Entity Pages**
    - Make entity page URLs match entity names (truncated, unique)
    - **Dependency**: SEO-friendly URL infrastructure
    - **Impact**: SEO/bookmarking improvement

### Implementation Strategy

**Week 4 Focus**: High-impact, core functionality improvements
- **Days 1-2**: Critical fixes (options indicators, date display)
- **Days 3-5**: Universal foundations (tables, edit functionality, navigation)
- **Days 6-8**: Interactive features (dynamic summaries, expandable content)
- **Days 9-10**: Portfolio analysis (holdings, multi-account display)
- **Days 11-12**: Advanced controls (date selection, document preview)

**Week 5+**: Polish and consistency improvements

### Technical Dependencies

**Database Schema Changes Required:**
- Add "_screen" fields to accounts, entities, institutions tables
- Update date logic for month-end calculations

**Component Architecture:**
- Universal Table component with sorting/expansion
- Edit Modal component for content management
- PDF Viewer component (adapted from KRK_Scraper)
- Date Range Picker component

**Routing Updates:**
- SEO-friendly URL structure implementation

---

**Updated:** 09/25/25 3:53PM - Complete feature capture with priority and dependency ordering