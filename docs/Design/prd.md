# Frontend Product Requirements Document (PRD)

**Created:** 09/09/25 10:45PM ET  
**Updated:** 09/11/25 3:15PM ET - Added detailed Dashboard Section Specifications with layouts, data sources, and interactions  
**Status:** DRAFT - In Active Development  
**Purpose:** Define user interface requirements for Claude-assisted financial data management system

## Executive Summary

### Vision Statement
Create a read-only reporting and analysis interface that displays financial data processed by Claude Code, supporting multiple entities (S-Corps, LLCs, Individual) across multiple institutions and accounts, with consolidated and detailed views of cash flows and tax implications.

### System Architecture
- **Processing:** Claude Code via terminal (NOT API) - manual document processing
- **Storage:** Local Supabase PostgreSQL database
- **Viewing:** Web-based frontend for reporting and analysis only
- **Entities:** Multiple business entities + individual, each with multiple accounts

### Core Value Proposition
- **Multi-Entity Management:** Track 4-5 S-Corps/LLCs plus individual accounts
- **Consolidated Views:** See cash flows by entity, institution, or in aggregate
- **Source Transparency:** View original PDFs alongside extracted data
- **Tax Intelligence:** Understand implications across all entities
- **Claude-Powered Processing:** Leverage Claude's intelligence, not rigid algorithms

## Critical Workflow: Document Processing (Outside Frontend)

### How Documents Get Into the System
This happens in VS Code terminal with Claude Code, NOT in the frontend:

1. **Manual Download:** User downloads statements/documents from various institutions
2. **Drop in Folder:** User drags files into `/documents/unprocessed/` in VS Code
3. **Claude Interaction:** User engages Claude via terminal: "Process the documents in unprocessed"
4. **Intelligent Processing:** 
   - Claude reads each document
   - Claude has context of all entities/institutions/accounts
   - If confident → processes automatically
   - If uncertain → asks user for clarification
5. **Database Update:** Claude stores extracted data in correct entity/account
6. **File Management:** Claude moves processed files to appropriate folders

### Key Design Decision
The frontend is **read-only** - it displays what Claude has processed. All data entry happens through Claude's document processing intelligence.

## User Personas

### Primary: Multi-Entity Business Owner
- **Who:** Individual managing 4-5 business entities plus personal finances
- **Goal:** Consolidated cash flow visibility and tax understanding
- **Process:** Downloads documents → Claude processes → Views in frontend
- **Needs:** 
  - See data by entity or in aggregate
  - Track cash in/out across all businesses
  - Understand tax implications per entity

### Secondary: Future Tax Preparer/CPA
- **Who:** Professional preparing taxes from this data
- **Goal:** Quick access to organized, categorized tax data by entity
- **Needs:** Export capabilities, clear entity separation

## Frontend Interface Design (Fidelity-Inspired)

### Dashboard Landing Page
Multi-level hierarchy with drill-down capability:

```
┌──────────────────────────────────────────────────────────────┐
│ Financial Dashboard                   As of: Jan 31, 2024    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ TOTAL NET WORTH: $8,962,626.88                               │
│                                                              │
│ By Asset Type:                                               │
│ ┌─────────────┬──────────────┬────────────┬──────────────┐   │
│ │ Cash & MM   │ CDs          │ Bonds      │ Stocks       │   │
│ │ $2,345,678  │ $1,234,567   │ $3,456,789 │ $1,925,592   │   │
│ │ 26.2%       │ 13.8%        │ 38.6%      │ 21.5%        │   │
│ └─────────────┴──────────────┴────────────┴──────────────┘   │
│                                                              │
│ Entity Hierarchy:                                            │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ ▼ Business Entities                    $7,234,567.89   │   │
│ │   ▼ S-Corps                            $6,234,567.89   │   │ 
│ │     ▶ Milton Preschool Inc             $2,234,567.89   │   │
│ │       Fidelity (Z40-394067)            $2,234,567.89   │   │
│ │     ▶ Entity A Corp                    $2,000,000.00   │   │
│ │       Bank of America                  $1,500,000.00   │   │
│ │       Fidelity                          $500,000.00    │   │
│ │     ▶ Entity C Corp                    $2,000,000.00   │   │
│ │   ▼ LLCs                               $1,000,000.00   │   │
│ │     ▶ Entity B LLC                     $1,000,000.00   │   │
│ │                                                        │   │
│ │ ▼ Personal                             $1,728,059.99   │   │
│ │   ▶ Individual                         $1,728,059.99   │   │
│ │     Fidelity (X12-345678)               $928,059.99    │   │
│ │     Schwab                              $800,000.00    │   │ 
│ └────────────────────────────────────────────────────────┘   │ 
│                                                              │
│ Recent Processing:                                           │
│ • Jan 31: Processed 4 statements - "All entities reconciled" │
│ • Jan 30: Processed Milton Preschool 1099 - "No notes"       │
└──────────────────────────────────────────────────────────────┘
```

### Left Navigation Panel
Hierarchical account structure with visual groupings:

- **All accounts** (total across everything)
  - **Business** (subtotal)
    - Entity A (S-Corp) with account numbers
    - Entity B (LLC) with account numbers  
    - Entity C (S-Corp) with account numbers
    - Milton Preschool Inc
  - **Personal** (subtotal)
    - Individual accounts
    - Joint accounts

### Top Navigation Tabs
Context-sensitive based on selection in left panel:

- **Summary:** Overview, cash flow, recent activity
- **Positions:** Holdings by security (if applicable)
- **Activity & Orders:** Transaction history
- **Balances:** Account balances over time
- **Documents:** Source PDFs with extracted data view
- **Tax Center:** Federal/state breakdowns, exemptions
- **Planning:** Future cash flow projections

## Navigation Architecture & Context Model

### Core Concept: Hierarchical Context
The entire application is built around a **context-aware hierarchy** where data visibility cascades based on the current context level. Context acts as a filter, not a container.

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

### URL Structure
Clean, hierarchical URLs that mirror the navigation structure:
```
/                                                    → Global Dashboard
/entities                                           → Entity List
/entities/milton-preschool                         → Entity Dashboard
/entities/milton-preschool/institutions            → Institution List  
/entities/milton-preschool/institutions/fidelity   → Institution Dashboard
/entities/milton-preschool/accounts               → Account List
/entities/milton-preschool/accounts/brokerage-4567 → Account Dashboard
/entities/milton-preschool/accounts/brokerage-4567/documents → Document List
/entities/milton-preschool/accounts/brokerage-4567/documents/statements/2024-01 → Statement View
```

### Context-Based Data Visibility

| In Context | Documents Shown | Transactions Shown | Accounts Shown |
|------------|----------------|-------------------|----------------|
| **Global** | ALL documents | ALL transactions | ALL accounts grouped by entity |
| **Entity** | All docs containing data for entity's accounts | All transactions for entity's accounts | All accounts owned by entity |
| **Institution** | All docs from that institution for current entity | All transactions at that institution for entity | All entity's accounts at institution |
| **Account** | Only docs linked to this account | Only this account's transactions | Just this account (detail view) |

### Smart Breadcrumb Navigation
Breadcrumbs with dropdown navigation for lateral movement without going back up the hierarchy:

```
Milton Preschool ▼ > Fidelity ▼ > Brokerage ***4567 ▼ > Documents ▼ > Statements ▼
                ↓            ↓                      ↓              ↓              ↓
        [Other Entities] [Other Inst.] [Other Accounts]  [Tax Forms]  [Jan, Feb, Mar...]
```

### Dashboard Hierarchy & Section Specifications

Each level in the hierarchy has its own dashboard with fixed sections optimized for that context level. These are not moveable widgets but rather fixed page sections that load fresh data on navigation.

#### Design Philosophy
- **Fixed Layouts**: No drag-and-drop or customization complexity
- **Data Freshness**: Query database on page load, manual refresh button available
- **Progressive Disclosure**: More detail as you drill down the hierarchy
- **Consistent Structure**: Similar layout patterns across all dashboards

---

### 1. Global Dashboard (`/`)

**Purpose**: Bird's-eye view of entire financial picture across all entities

**Layout**: Single column with full-width sections

#### Section 1: Net Worth Summary
- **Position**: Top, full width
- **Height**: 200px
- **Content**:
  - Large headline number: Total net worth across all entities
  - Breakdown bar: Financial Assets | Real Assets | Liabilities
  - Trend sparkline: 12-month net worth trend
  - Period selector: MTD, QTD, YTD, All Time
- **Data Source**: 
  ```sql
  SELECT SUM(financial_assets + real_assets - liabilities) as net_worth
  FROM net_worth_summary
  ```
- **Interactions**: Click breakdown sections to filter entity cards below

#### Section 2: Entity Cards Grid
- **Position**: Below summary
- **Layout**: Responsive grid (4 columns desktop, 2 tablet, 1 mobile)
- **Content per card**:
  - Entity name and type badge (S-Corp/LLC/Individual)
  - Current net worth
  - MTD change ($amount and %)
  - Mini pie chart: Asset allocation
  - Quick stats: Cash balance, YTD income
- **Data Source**: One query per entity for current values
- **Interactions**: Click card → Entity dashboard
- **Visual Design**: Cards with subtle shadows, hover state

#### Section 3: Recent Activity & Upcoming Items
- **Position**: Bottom, two columns
- **Layout**: 60% Recent Activity, 40% Upcoming Items

**Recent Activity** (Left):
- Last 10 transactions across all entities
- Format: Date | Entity | Account | Description | Amount
- Color coding: Green for income, Red for expenses
- Click row → Transaction detail modal

**Upcoming Items** (Right):
- Next 5 upcoming items (tax payments, expected documents)
- Format: Date | Type | Entity | Description | Amount
- Visual indicators: Warning icons for overdue items
- Click row → Relevant section

---

### 2. Entity Dashboard (`/entities/{entity}`)

**Purpose**: Complete financial picture for a single entity

**Context Note**: This is where users spend most time - reviewing a specific business or personal finances

#### Section 1: Entity Header
- **Position**: Top, full width
- **Height**: 120px
- **Content**:
  - Entity name with type badge
  - Net worth with MTD/YTD changes
  - Key metrics bar: Cash | Investments | Properties | Liabilities
  - Last refreshed timestamp
  - Manual refresh button
- **Visual Design**: Subtle gradient background, entity type color coding

#### Section 2: Accounts Overview
- **Position**: Below header
- **Layout**: Grouped cards by institution
- **Content per institution group**:
  - Institution name and logo (if available)
  - Total balance at institution
  - Account list with: Type icon | Account name | Number (masked) | Balance | Last activity
  - Subtotal per institution
- **Interactions**: 
  - Click institution header → Institution dashboard
  - Click account row → Account dashboard
- **Technical Note**: Single query with JOIN on institutions and accounts tables

#### Section 3: Financial Metrics Row
- **Position**: Middle, full width
- **Layout**: 4 metric cards in a row
- **Cards**:
  1. **Cash Flow**: Current month in/out/net with mini chart
  2. **Tax Liability**: YTD federal/state estimates
  3. **Document Status**: Processed/pending/failed counts
  4. **Investment Performance**: YTD return % (if applicable)
- **Visual Design**: Flat cards with icons, no borders

#### Section 4: Recent Documents
- **Position**: Bottom left, 50% width
- **Content**:
  - Last 5 processed documents
  - Format: Date | Type | Institution | Confidence score
  - Color coding: Green (>90%), Yellow (70-90%), Red (<70%)
  - "View All Documents" link
- **Interactions**: Click row → Document viewer

#### Section 5: Entity Notes
- **Position**: Bottom right, 50% width
- **Content**:
  - Free-form text area for notes
  - Last modified timestamp
  - Edit button (saves to entity notes field)
- **Technical**: Stores in entities.notes column

---

### 3. Institution Dashboard (`/entities/{entity}/institutions/{institution}`)

**Purpose**: View all accounts and activity at a specific institution for an entity

**Context Note**: Useful for reviewing consolidated statements and institution-wide changes

#### Section 1: Institution Summary
- **Position**: Top, full width
- **Content**:
  - Institution name and entity context
  - Total balance across all accounts
  - Number of accounts
  - Percentage of entity's total portfolio
  - Last statement date

#### Section 2: Account List
- **Position**: Left side, 40% width
- **Content**:
  - Detailed account list
  - Per account: Type | Number | Balance | YTD interest/dividends | Last transaction
  - Totals row at bottom
- **Interactions**: Click account → Account dashboard

#### Section 3: Recent Transactions
- **Position**: Right side, 60% width
- **Content**:
  - Last 30 days of transactions across all accounts at institution
  - Format: Date | Account | Type | Description | Amount | Balance
  - Filter buttons: All | Deposits | Withdrawals | Dividends | Fees
  - Export button (CSV)
- **Technical**: Paginated query, limit 50 initially

#### Section 4: Document Library
- **Position**: Bottom, full width
- **Layout**: Document tiles grouped by type
- **Content**:
  - Tabs: All | Statements | Tax Forms | Confirmations | Correspondence
  - Document grid: Type icon | Date | Description | Status
  - Quick filters: Year selector, document type
- **Interactions**: Click document → PDF viewer

---

### 4. Account Dashboard (`/entities/{entity}/accounts/{account}`)

**Purpose**: Deep dive into a specific account's activity and holdings

**Context Note**: Most detailed view - where users verify transactions and review specifics

#### Section 1: Account Header
- **Position**: Top, full width
- **Content**:
  - Account name and number (masked)
  - Current balance with 30-day change
  - Account type and tax treatment badges
  - Mini balance trend chart (last 12 months)

#### Section 2: Holdings Table (Investment Accounts Only)
- **Position**: Below header (conditional)
- **Content**:
  - Current positions: Symbol | Description | Quantity | Price | Value | Day Change | Total Gain/Loss
  - Sortable columns
  - Grouping options: Asset class | Performance | Value
- **Technical**: Only show for account_type IN ('brokerage', 'ira', '401k')

#### Section 3: Transaction List
- **Position**: Main content area
- **Layout**: Full-width data table
- **Content**:
  - Columns: Date | Description | Type | Amount | Balance | Document Link
  - Filters: Date range | Type | Amount range
  - Search box for description/amount
  - Pagination: 50 per page
- **Interactions**: 
  - Click row → Transaction detail modal
  - Click document link → PDF viewer at specific page
- **Technical**: Include source_document_id for linking

#### Section 4: Account Metrics Row
- **Position**: Bottom
- **Layout**: 3 cards
- **Cards**:
  1. **Cash Flow Summary**: YTD in/out/net
  2. **Tax Summary**: YTD dividends, interest, cap gains by tax treatment
  3. **Document Count**: Statements/tax forms/confirms available

#### Section 5: Account Notes
- **Position**: Very bottom
- **Content**: Account-specific notes and reminders
- **Technical**: Stores in accounts.notes column

### Document-Account Relationship Model
- Documents belong to one institution
- Documents can be linked to multiple accounts (e.g., consolidated statements)
- Transactions extracted from documents are attributed to specific accounts
- When viewing a document through an account context, only see transactions for that account
- "View Document" always shows the complete PDF

### Notes & Metadata Support
Each hierarchy level supports notes and metadata:
- **Global**: General reminders, system-wide notes
- **Entity**: Tax strategies, entity-specific notes
- **Institution**: Login credentials, contact info
- **Account**: Investment strategies, account-specific reminders

## Core User Workflows

### 🔄 Workflow 1: Viewing Processed Documents
**User Story:** "I want to see what Claude extracted from my statements"

**Navigation Path:**
1. Select entity/account in left panel
2. Click "Documents" tab
3. See list of processed documents with status indicators
4. Click document to view PDF + extracted data side-by-side

**Key Features Needed:**
- Document list with processing status
- Split-screen PDF viewer + data table
- Confidence indicators from Claude's processing
- Source highlighting (click data → highlight in PDF)

**Acceptance Criteria:**
- [ ] GIVEN a user has selected an entity, WHEN they click Documents tab, THEN display all documents for that entity sorted by date descending
- [ ] GIVEN a document list is displayed, WHEN user clicks a document, THEN load PDF in left pane and extracted data in right pane within 2 seconds
- [ ] GIVEN extracted data is displayed, WHEN user clicks a data row, THEN highlight corresponding area in PDF within 500ms
- [ ] GIVEN a document has confidence < 80%, THEN display yellow warning indicator
- [ ] GIVEN a document failed processing, THEN display red error indicator with failure reason

**Error Scenarios:**
- PDF fails to load: Display "Unable to load PDF" with retry button
- Extracted data missing: Show "No data extracted" with link to reprocess
- Entity has no documents: Display "No documents found" with upload instructions

**Data Validation:**
- Document file_hash must be unique per entity
- Processing confidence must be 0-100
- Document dates cannot be in future
- File size limit: 50MB per document

### 💰 Workflow 2: Cash Flow Analysis
**User Story:** "I want to see money in/out for any time period"

**Steps:**
1. Select date range (month, quarter, year, custom)
2. View cash flow summary dashboard
3. Drill down into specific transactions
4. Click through to source documents
5. Export for QuickBooks

**Key Features Needed:**
- Interactive date range selector
- Cash flow waterfall chart
- Transaction drill-down table
- Source document quick-view
- QBO export button

**Acceptance Criteria:**
- [ ] GIVEN user selects date range, WHEN range is valid, THEN update cash flow data within 1 second
- [ ] GIVEN cash flow is displayed, THEN show: opening balance + inflows - outflows = closing balance
- [ ] GIVEN user clicks a category in waterfall, THEN display transaction list for that category
- [ ] GIVEN transaction list is shown, WHEN user clicks transaction, THEN load source document modal
- [ ] GIVEN user clicks export, WHEN data exists, THEN generate QBO file with all transactions in range

**Business Rules:**
- Date ranges cannot exceed 5 years
- Custom date range must have start < end
- All amounts must reconcile: sum(transactions) = net cash flow
- Inflows are positive amounts, outflows are negative
- Export must include: date, amount, description, account, entity

**Error Scenarios:**
- No data in range: Display "No transactions found for selected period"
- Export fails: Show specific error ("File write failed", "Invalid data format")
- Date range invalid: Highlight field red with "End date must be after start date"

**Performance Requirements:**
- Initial load: < 2 seconds for 1 year of data
- Date range change: < 1 second refresh
- Export generation: < 5 seconds for 10,000 transactions

### 📈 Workflow 3: Asset Performance Analysis
**User Story:** "I want to see complete history and P&L for GOOG across all my entities"

**Asset Detail View Example - Google (GOOG):**
```
┌────────────────────────────────────────────────────────────────-┐
│ GOOGLE (GOOG) - All Entities          Next Earnings: Feb 1      │
├────────────────────────────────────────────────────────────────-┤
│                                                                 │
│ Summary Metrics:                                                │
│ Total Position: 500 shares | Avg Cost: $1,300 | Current: $1,500 │
│ Total Invested: $650,000 | Current Value: $750,000              │
│ Unrealized Gain: $100,000 (+15.4%) | Realized (2024): $25,000   │
│                                                                 │
│ Investment Notes & Strategy:                    [Edit Notes]    │
│ ┌─────────────────────────────────────────────────────┐         │
│ │ Price Target: $1,650 by Q4 2024                     │         │
│ │ Strategy: Long-term hold, add on dips below $1,400  │         │
│ │ Tax Notes: Holding for LTCG treatment               │         │
│ │ Last Review: Jan 15, 2024                           │         │
│ └─────────────────────────────────────────────────────┘         │
│                                                                 │
│ Holdings by Entity:                                             │
│ ┌─────────────────┬────────┬──────────┬──────────┬─────────┐    │
│ │ Entity          │ Shares │ Cost Basis│ Current │ Unreal. │    │
│ ├─────────────────┼────────┼──────────┼──────────┼─────────┤    │
│ │ Milton Preschool│ 300    │ $390,000 │ $450,000 │ +$60,000│    │
│ │ Entity A        │ 150    │ $195,000 │ $225,000 │ +$30,000│    │
│ │ Personal        │ 50     │ $65,000  │ $75,000  │ +$10,000│    │
│ │ TOTAL           │ 500    │ $650,000 │ $750,000 │+$100,000│    │
│ └─────────────────┴────────┴──────────┴──────────┴─────────┘    │
│                                                                 │
│ Transaction History:                                            │
│ ┌──────────┬────────────────┬──────┬───────┬────────────────┐   │
│ │ Date     │ Entity         │ Type │ Shares│ Amount         │   │
│ ├──────────┼────────────────┼──────┼───────┼────────────────┤   │
│ │ Jan 2024 │ Milton Pre     │ BUY  │ 100   │ -$130,000      │   │
│ │ Dec 2023 │ Entity A       │ SELL │ 50    │ +$72,500       │   │
│ │ Dec 2023 │ Entity A       │ DIV  │ -     │ +$450          │   │
│ │ Nov 2023 │ Personal       │ BUY  │ 50    │ -$65,000       │   │
│ └──────────┴────────────────┴──────┴───────┴────────────────┘   │
│                                                                 │
│ [Chart: Price & Holdings Over Time]                             │
│ [Chart: Cash Flows In/Out by Quarter]                           │
│ [Chart: Realized vs Unrealized Gains Timeline]                  │
└───────────────────────────────────────────────────────────────-─┘
```

**Key Features for Asset Views:**
- **Editable investment notes** (price targets, strategy, tax planning)
- Multi-entity aggregation with entity-level breakdown
- Complete transaction history across all entities
- Cash flow tracking (buys, sells, dividends)
- Realized and unrealized P&L over time
- Cost basis tracking (by lot for tax purposes)
- Next earnings date (future: via Perplexity integration)
- Performance charts with entity filtering
- Export capability for tax reporting

### 📊 Workflow 4: Tax Analysis & Reporting
**User Story:** "I need to prepare quarterly taxes for each entity and understand total liability"

**Acceptance Criteria:**
- [ ] GIVEN user selects a tax year and quarter, WHEN data exists, THEN display income breakdown by tax category
- [ ] GIVEN income is displayed, THEN show federal taxable vs state taxable amounts
- [ ] GIVEN FSIXX dividends exist, THEN apply 97% Georgia exemption automatically
- [ ] GIVEN SPAXX dividends exist, THEN apply 55% Georgia exemption automatically
- [ ] GIVEN multiple entities selected, THEN show consolidated view with per-entity breakdown
- [ ] GIVEN user requests export, THEN generate CSV with all tax-relevant transactions

**Business Rules:**
- Tax year = calendar year (Jan 1 - Dec 31)
- Georgia exemptions: FSIXX ~97%, SPAXX ~55%
- Municipal bonds: GA bonds = double exempt, other state = GA taxable
- S-Corp/LLC income flows through to personal return
- Qualified dividends get preferential rate treatment

**Data Validation:**
- Tax categories must match IRS definitions
- All transactions must have federal_taxable and state_taxable flags
- Amounts must be NUMERIC(15,2) for precision
- Tax year cannot be future year

**Test Scenarios:**
- Verify FSIXX $1000 dividend = $1000 federal, $30 GA taxable
- Verify SPAXX $1000 dividend = $1000 federal, $450 GA taxable
- Verify GA muni bond interest = $0 federal, $0 GA
- Verify other state muni = $0 federal, full amount GA taxable
- Verify consolidated totals = sum of all entity totals

**Tax Center - Multiple Views:**

#### A. Entity-Specific Tax Summary
```
┌──────────────────────────────────────────────────────────────┐
│ Milton Preschool Inc - Q1 2024 Tax Summary                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Income Summary:                                              │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Income Type         │ Amount   │ Federal  │ Georgia      │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ FSIXX Dividends     │ $4,327   │ $4,327   │ $130 (3%)    │ │
│ │ SPAXX Dividends     │ $2       │ $2       │ $1 (45%)     │ │
│ │ Corporate Dividends │ $12,000  │ $12,000  │ $12,000      │ │
│ │ Municipal (GA)      │ $5,000   │ $0       │ $0           │ │
│ │ Municipal (Other)   │ $3,000   │ $0       │ $3,000       │ │
│ │ Capital Gains       │ $25,000  │ $25,000  │ $25,000      │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ TOTAL               │ $49,329  │ $41,329  │ $40,131      │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│                                                              │
│ Estimated Tax Due:                                           │
│ Federal: $8,265 | Georgia: $2,407                            │
│                                                              │
│ [Export for Tax Software] [Generate 1120S Draft]             │
└──────────────────────────────────────────────────────────────┘
```

#### B. Consolidated Multi-Entity Tax View
```
┌─────────────────────────────────────────────────────────────-┐
│ All Entities - Q1 2024 Tax Summary                           │
├─────────────────────────────────────────────────────────────-┤
│                                                              │
│ Total Tax Liability (Flows to Personal):                     │
│ Federal: $45,678 | Georgia: $8,234                           │
│                                                              │
│ By Entity:                                                   │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Entity              │ Income   │ Fed Tax  │ GA Tax       │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ Milton Preschool    │ $49,329  │ $8,265   │ $2,407       │ │
│ │ Entity A Corp       │ $75,000  │ $15,000  │ $4,500       │ │
│ │ Entity B LLC*       │ $35,000  │ $7,000   │ $2,100       │ │
│ │ Entity C Corp       │ $45,000  │ $9,000   │ $2,700       │ │
│ │ Personal           │ $32,500  │ $6,413   │ -$3,473**     │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ TOTAL               │ $236,829 │ $45,678  │ $8,234       │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│ * Pass-through entity  ** After credits                      │
│                                                              │
│ [Generate Consolidated Report] [Export All]                  │
└──────────────────────────────────────────────────────────────┘
```

#### C. Income Type Analysis (All Entities)
```
┌─────────────────────────────────────────────────────────────┐
│ Q1 2024 - Income Analysis by Type (All Entities)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────┬──────────┬──────────┬─────────────┐ │
│ │ Income Category     │ Amount   │ Federal  │ Georgia     │ │
│ ├─────────────────────┼──────────┼──────────┼─────────────┤ │
│ │ Ordinary Dividends  │ $58,535  │ $58,535  │ $27,450*    │ │
│ │   FSIXX (97% exempt)│ $43,275  │ $43,275  │ $1,298      │ │
│ │   SPAXX (55% exempt)│ $203     │ $203     │ $91         │ │
│ │   Corporate        │ $15,057  │ $15,057  │ $15,057      │ │
│ │ Qualified Dividends │ $12,000  │ $12,000  │ $12,000     │ │
│ │ Municipal Interest  │          │          │             │ │
│ │   Georgia issuers  │ $25,000  │ $0       │ $0           │ │
│ │   Other states     │ $15,000  │ $0       │ $15,000      │ │
│ │ Capital Gains       │          │          │             │ │
│ │   Short-term       │ $8,000   │ $8,000   │ $8,000       │ │
│ │   Long-term        │ $45,000  │ $45,000  │ $45,000      │ │
│ │ Interest Income     │ $5,500   │ $5,500   │ $5,500      │ │
│ ├─────────────────────┼──────────┼──────────┼─────────────┤ │
│ │ TOTAL               │ $169,035 │ $129,035 │ $112,950    │ │
│ └─────────────────────┴──────────┴──────────┴─────────────┘ │
│ * After Georgia exemptions applied                          │
│                                                             │
│ [Drill Down by Entity] [Export for Tax Prep]                │
└─────────────────────────────────────────────────────────────┘
```

**Key Tax Features:**
- Entity-specific tax summaries with export capability
- Consolidated view showing flow-through to personal return
- Income type analysis across all entities
- Georgia exemption calculations (FSIXX ~97%, SPAXX ~55%)
- Federal vs State taxable amount tracking
- Quarterly and annual views
- Export formats for various tax software
- Pass-through entity handling
- Corporate exemption status tracking

### 💸 Workflow 5: Tax Payment Tracking
**User Story:** "I need to track quarterly estimated tax payments and see what I owe vs what I've paid"

**Tax Payment Center:**
```
┌──────────────────────────────────────────────────────────────-─┐
│ Tax Payment Tracker - 2024                  [Compare to 2023]  │
├───────────────────────────────────────────────────────────────-┤
│                                                                │
│ Estimated vs Paid:                                             │
│ ┌─────────────┬──────────┬──────────┬──────────┬────────────┐  │
│ │ Quarter     │ Fed Est. │ Fed Paid │ GA Est.  │ GA Paid    │  │
│ ├─────────────┼──────────┼──────────┼──────────┼────────────┤  │
│ │ Q1 2024     │ $45,678  │ $45,678 ✓│ $8,234   │ $8,234 ✓      │
│ │ Q2 2024     │ $48,000  │ $0 ⚠️    │ $8,500   │ $0 ⚠️      │  │
│ │ Q3 2024     │ $47,500  │ $0       │ $8,400   │ $0         │  │
│ │ Q4 2024     │ $46,000  │ $0       │ $8,200   │ $0         │  │
│ ├─────────────┼──────────┼──────────┼──────────┼────────────┤  │
│ │ Total       │ $187,178 │ $45,678  │ $33,334  │ $8,234     │  │
│ │ Remaining   │          │ $141,500 │          │ $25,100    │  │
│ └─────────────┴──────────┴──────────┴──────────┴────────────┘  │
│                                                                │
│ Payment History:                       [+ Record Payment]      │
│ ┌──────────┬────────────┬──────────┬────────────────────────┐  │
│ │ Date     │ Entity     │ Amount   │ Notes                  │  │
│ ├──────────┼────────────┼──────────┼────────────────────────┤  │
│ │ Apr 15   │ Personal   │ $45,678  │ Q1 Fed estimated tax   │  │
│ │ Apr 15   │ Personal   │ $8,234   │ Q1 GA estimated tax    │  │
│ │ Jan 15   │ Milton Pre │ $12,000  │ Q4 2023 corporate tax  │  │
│ └──────────┴────────────┴──────────┴────────────────────────┘  │
│                                                                │
│ Next Payment Due: June 15, 2024 (Q2 Estimated)                 │
│ [Set Reminder] [Calculate Q2 Payment]                          │
└───────────────────────────────────────────────────────────────-┘
```

### 📊 Workflow 6: Year-Over-Year Comparisons
**User Story:** "I want to see how this year compares to last year"

**Comparative Analysis View:**
```
┌─────────────────────────────────────────────────────────────-┐
│ Year-Over-Year Comparison         [2024 vs 2023] [Change ▼]  │
├─────────────────────────────────────────────────────────────-┤
│                                                              │
│ Income Comparison (All Entities):                            │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Category            │ 2024 YTD │ 2023 YTD │ Change       │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ Dividend Income     │ $158,535 │ $142,000 │ +$16,535 ↑   │ │
│ │ Interest Income     │ $45,000  │ $38,000  │ +$7,000 ↑    │ │
│ │ Capital Gains       │ $125,000 │ $95,000  │ +$30,000 ↑   │ │
│ │ Total Income        │ $328,535 │ $275,000 │ +$53,535 ↑   │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│                                                              │
│ Tax Liability Comparison:                                    │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Tax Type            │ 2024 Est │ 2023 Act │ Change       │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ Federal Tax         │ $187,178 │ $165,000 │ +$22,178 ↑   │ │
│ │ Georgia Tax         │ $33,334  │ $28,500  │ +$4,834 ↑    │ │
│ │ Effective Rate      │ 28.5%    │ 27.2%    │ +1.3%        │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│                                                              │
│ [View by Entity] [View by Quarter] [Export Comparison]       │
└──────────────────────────────────────────────────────────────┘
```

### 🔍 Workflow 7: Document Search & Discovery
**User Story:** "I need to find a specific transaction or document quickly"

**Steps:**
1. Search by amount, date, security, or description
2. Filter by document type, account, tax category
3. View search results with context
4. Open source documents
5. Trace transaction history

**Key Features Needed:**
- Full-text search across all data
- Advanced filters
- Search result previews
- Document viewer integration
- Transaction lineage view

**Acceptance Criteria:**
- [ ] GIVEN user enters search term, WHEN pressing enter, THEN return results within 2 seconds
- [ ] GIVEN search results exist, THEN display with relevance ranking
- [ ] GIVEN user applies filters, THEN update results without clearing search term
- [ ] GIVEN user clicks result, THEN open document/transaction detail within 1 second
- [ ] GIVEN amount search with "$" or ",", THEN parse correctly (e.g., "$1,234.56" = 1234.56)

**Search Capabilities:**
- Amount: Exact match or range (e.g., "1000-2000")
- Date: Single date or range using natural language ("last month", "Q1 2024")
- Description: Fuzzy matching with stemming
- Security: By symbol or CUSIP
- Entity: Filter by one or multiple entities

**Performance Requirements:**
- Search latency: < 500ms for 100k transactions
- Result limit: 100 per page with pagination
- Autocomplete suggestions: < 100ms response

**Error Handling:**
- No results: "No matches found. Try broadening your search."
- Invalid date: "Please enter a valid date (MM/DD/YYYY)"
- Invalid amount: "Please enter a valid amount"
- Search timeout: "Search is taking longer than expected. Please try again."

### 📅 Workflow 8: Cash Flow Forecasting & Planning
**User Story:** "I want to know when money is coming in and plan for tax payments"

**Cash Flow Calendar:**
```
┌────────────────────────────────────────────────────────────────┐
│ Cash Flow Forecast - Q2 2024                    [Month ▼]      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ April 2024:                                                    │
│ ┌────┬──────────────────────────────────────────────────────┐  │
│ │ 15 │ 📥 FSIXX Dividend (Milton)              +$4,500 exp  │  │
│ │    │ 📥 Bond Interest (Entity A)             +$2,500 exp  │  │
│ │    │ 📤 Q1 Federal Tax Payment              -$45,678 ⚠️   │  │
│ │    │ 📤 Q1 Georgia Tax Payment              -$8,234 ⚠️    │  │
│ │ 20 │ 📥 GOOG Dividend (All entities)         +$1,250 exp  │  │
│ │ 30 │ 📥 Municipal Bond Interest (Entity C)   +$5,000 exp  │  │
│ └────┴──────────────────────────────────────────────────────┘  │
│                                                                │
│ Expected Cash In: $13,250 | Expected Out: $53,912              │
│ Net Expected: -$40,662                                         │
│                                                                │
│ Alerts:                                                        │
│ ⚠️ Tax payments due April 15 - ensure sufficient liquidity     │
│ ℹ️ GOOG ex-dividend date April 18 - hold positions             │
│                                                                │
│ [Add Manual Entry] [Update Expectations] [Export Calendar]     │
└────────────────────────────────────────────────────────────────┘
```

### 🔄 Workflow 9: Inter-Entity Transfers & Cash Management
**User Story:** "I need to move money between entities and track it properly"

**Transfer Management:**
```
┌──────────────────────────────────────────────────────────────┐
│ Inter-Entity Transfer                       [View History]   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Quick Transfer:                                              │
│                                                              │
│ From: [Milton Preschool - Fidelity Z40 ▼] Balance: $450,000  │
│ To:   [Entity A - Bank of America ▼]                         │
│ Amount: $[___________]                                       │
│ Date: [04/10/2024]                                           │
│ Purpose: [Quarterly distribution ▼]                          │
│ Tax Treatment: [Non-taxable transfer ▼]                      │
│ Notes: [_____________________________________________]       │
│                                                              │
│ Recent Transfers:                                            │
│ ┌──────────┬────────────┬────────────┬──────────┬──────────┐ │
│ │ Date     │ From       │ To         │ Amount   │ Purpose  │ │
│ ├──────────┼────────────┼────────────┼──────────┼──────────┤ │
│ │ Mar 31   │ Milton Pre │ Personal   │ $200,000 │ Distrib. │ │
│ │ Feb 28   │ Entity A   │ Entity B   │ $50,000  │ Loan     │ │
│ │ Jan 15   │ Personal   │ Milton Pre │ $100,000 │ Capital  │ │
│ └──────────┴────────────┴────────────┴──────────┴──────────┘ │
│                                                              │
│ [Record Transfer] [Cancel]                                   │
└──────────────────────────────────────────────────────────────┘
```

### 📈 Workflow 10: Portfolio Rebalancing & Alerts
**User Story:** "I want to maintain target allocations and get alerts"

**Portfolio Health Dashboard:**
```
┌───────────────────────────────────────────────────────────────┐
│ Portfolio Health Check                      [Settings]        │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Asset Allocation vs Targets:                                  │
│ ┌─────────────────┬──────────┬──────────┬───────────────────┐ │
│ │ Asset Class     │ Current  │ Target   │ Action            │ │
│ ├─────────────────┼──────────┼──────────┼───────────────────┤ │
│ │ Cash & MM       │ 26.2%    │ 20-25%   │ ⚠️ Reduce by $200k│ │
│ │ Fixed Income    │ 38.6%    │ 40-45%   │ ✅ In range       │ │
│ │ Equities        │ 21.5%    │ 25-30%   │ ⚠️ Add $300k      │ │
│ │ Alternatives    │ 13.7%    │ 10-15%   │ ✅ In range       │ │
│ └─────────────────┴──────────┴──────────┴───────────────────┘ │
│                                                               │
│ Tax Loss Harvesting Opportunities:                            │
│ • MSFT position (Entity A): -$12,000 unrealized               │
│ • Bond Fund (Personal): -$5,000 unrealized                    │
│ [Review Opportunities]                                        │
│                                                               │
│ Upcoming Actions:                                             │
│ • April 30: Review Q1 performance                             │
│ • May 15: Expected statement uploads                          │
│ • June 15: Q2 estimated tax due                               │
│                                                               │
│ Entity Minimum Balance Alerts:                                │
│ ⚠️ Entity B checking below $10k minimum (current: $8,500)     │
│                                                               │
│ [Set Alert Preferences] [Export Health Report]                │
└───────────────────────────────────────────────────────────────┘
```

### ⚙️ Workflow 11: Administrative Functions
**User Story:** "I need to add new accounts/entities and manage relationships"

**Settings/Admin Panel:**

#### Entity & Account Management
```
┌───────────────────────────────────────────────────────────┐
│ Administrative Functions                                  │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ Quick Actions:                                            │
│ [+ Add Entity] [+ Add Institution] [+ Add Account]        │
│                                                           │
│ Entity Management:                                        │
│ ┌────────────────────────────────────────────────────┐    │
│ │ Entities (5 active)                                │    │
│ │                                                    │    │
│ │ S-Corps:                                           │    │
│ │ • Milton Preschool Inc    [Edit] [View Accounts]   │    │
│ │   Tax ID: XX-XXXXXXX | Status: Active              │    │
│ │ • Entity A Corp          [Edit] [View Accounts]    │    │
│ │ • Entity C Corp          [Edit] [View Accounts]    │    │
│ │                                                    │    │
│ │ LLCs:                                              │    │
│ │ • Entity B LLC           [Edit] [View Accounts]    │    │
│ │                                                    │    │
│ │ Individual:                                        │    │
│ │ • Personal               [Edit] [View Accounts]    │    │
│ └────────────────────────────────────────────────────┘    │
│                                                           │
│ Account Assignment:                                       │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Fidelity Accounts:                                   │  │
│ │ Z40-394067 → Milton Preschool Inc    [Reassign]      │  │
│ │ X12-345678 → Personal                [Reassign]      │  │
│ │ Y99-888888 → Entity A Corp           [Reassign]      │  │
│ │                                                      │  │
│ │ Bank of America:                                     │  │
│ │ ****4567 → Entity A Corp             [Reassign]      │  |
│ │                                                      │  │
│ │ Unassigned Accounts:                                 │  │
│ │ ⚠️ Schwab ****9012 (found in recent import) [Assign] │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                           │
│ Database Controls:                                        │
│ Status: 🟢 Running (localhost:54322)                      │
│ [Stop Database] [Restart Database]                        │
│                                                           │
│ Data Maintenance:                                         │
│ • Mark account as closed: [Select Account ▼] [Mark Closed]│
│ • Last backup: Jan 31, 2024 2:30 PM                       │
│ • [Run Backup Script] (Phase 2)                           │
└───────────────────────────────────────────────────────────┘
```

#### Add New Entity Form
```
┌───────────────────────────────────────────────────────────────┐
│ Add New Entity                                                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Entity Name: [________________________]                       │
│                                                               │
│ Entity Type: [S-Corp ▼] (S-Corp, LLC, Partnership, Individual)│
│                                                               │
│ Tax ID (EIN/SSN): [XX-XXXXXXX]                                │
│                                                               │
│ Tax Treatment:                                                │
│ ○ Corporate (files own return)                                │
│ ● Pass-through (flows to personal)                            │
│                                                               │
│ Status: ● Active ○ Inactive                                   │
│                                                               │
│ Notes: [_____________________________________________]        │
│                                                               │
│ [Cancel] [Save Entity]                                        │
└───────────────────────────────────────────────────────────────┘
```

#### Add New Account Form
```
┌───────────────────────────────────────────────────────────────┐
│ Add New Account                                               │
├──────────────────────────────────────────────────────────────-┤
│                                                               │
│ Institution: [Fidelity ▼] or [+ Add New Institution]          │
│                                                               │
│ Account Number: [_______________]                             │
│                                                               │
│ Account Name/Description: [_____________________]             │
│                                                               │
│ Assign to Entity: [Milton Preschool Inc ▼]                    │
│                                                               │
│ Account Type: [Investment ▼] (Investment, Checking, Savings)  │
│                                                               │
│ Status: ● Active ○ Closed                                     │
│                                                               │
│ [Cancel] [Save Account]                                       │
└───────────────────────────────────────────────────────────────┘
```

**Key Administrative Features:**
- Quick-add buttons for entities, institutions, accounts
- Entity hierarchy display with edit capabilities
- Account-to-entity assignment management
- Reassignment capability for existing accounts
- Detection of unassigned accounts from imports
- Mark accounts/entities as inactive/closed
- Database start/stop controls
- Future: Backup script execution
- No duplicate merge UI (handled via Claude)

## Data Organization Strategy (Based on Industry Best Practices)

### Hierarchical Data Model
Primary hierarchy for organizing multi-dimensional financial data:

```
Level 1: Entity Selection (Global Filter)
    ↓
Level 2: View Mode (Tabs/Navigation)
    - By Account
    - By Asset Class  
    - By Time Period
    - By Institution
    ↓
Level 3: Drill-Down Details
    - Individual transactions
    - Document sources
    - Tax implications
```

### Multi-Perspective Transaction Views

#### View 1: Statement-Centric (Document Focus)
```
┌──────────────────────────────────────────────────────────────┐
│ Milton Preschool - Fidelity Z40-394067                       │
│ Statement: January 2024                  [Previous] [Next]   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [PDF Viewer]                    Transaction List             │
│ ┌──────────────┐               ┌──────────────────────────┐  │
│ │              │               │ Jan 31: FSIXX Div +$4,327 │ │
│ │  Statement   │               │ Jan 31: Wire Out -$200k   │ │
│ │   PDF Page   │               │ Jan 15: Bond Int +$1,250  │ │
│ │              │               │ Total: -$194,423          │ │
│ └──────────────┘               └──────────────────────────┘  │
│                                                              │
│ [View All Statements] [Export This Statement]                │
└──────────────────────────────────────────────────────────────┘
```

#### View 2: Time-Based Aggregation (Period Focus)
```
┌─────────────────────────────────────────────────────────────┐
│ Activity View - January 2024          [◀ Dec] [Feb ▶]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Filter: ☑ All Entities ☐ Business Only ☐ Personal Only      │
│        ☑ Milton ☑ Entity A ☑ Entity B ☐ Entity C            │
│                                                             │
│ Grouped by Entity:                                          │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ▼ Milton Preschool Inc              Net: -$195,672     │  │
│ │   Jan 31: FSIXX Dividend (Fidelity)        +$4,327     │  │
│ │   Jan 31: Wire Transfer (Fidelity)       -$200,000     │  │
│ │                                                        │  │
│ │ ▼ Entity A Corp                      Net: +$45,000     │  │
│ │   Jan 15: Bond Interest (Fidelity)         +$5,000     │  │
│ │   Jan 20: Stock Sale (Schwab)             +$40,000     │  │
│ │                                                        │  │
│ │ ▶ Entity B LLC                       Net: +$12,000     │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                             │
│ Period Total: -$138,672                                     │
│ [Export Period] [View by Asset Class] [View by Institution] │
└─────────────────────────────────────────────────────────────┘
```

#### View 3: Asset Class Perspective
```
┌────────────────────────────────────────────────────────────┐
│ Holdings by Asset Class - As of Jan 31, 2024               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Filter: ☑ All Entities  Time: [YTD ▼]                      │
│                                                            │
│ ┌─────────────────────────────────────────────────┐        │
│ │ ▼ Cash & Money Market             $2,345,678    │        │
│ │   FSIXX (Milton, Entity A)         $1,845,678   │        │
│ │   SPAXX (Personal)                   $500,000   │        │
│ │                                                 │        │
│ │ ▼ Fixed Income                    $3,456,789    │        │
│ │   ▼ Municipal Bonds                $2,456,789   │        │
│ │     GA Municipals (Fed & GA exempt) $1,456,789  │        │
│ │     Other State Munis (GA taxable)  $1,000,000  │        │
│ │   ▶ Corporate Bonds                $1,000,000   │        │ 
│ │                                                 │        │
│ │ ▶ Equities                        $1,925,592    │        │
│ └─────────────────────────────────────────────────┘        │
│                                                            │
│ [Drill into Holdings] [Performance View] [Tax Impact View] │
└───────────────────────────────────────────────────────────-┘
```

### Progressive Disclosure Pattern
Following industry best practices for managing complexity:

1. **Start Simple:** Dashboard shows totals only
2. **One Click Deeper:** Click entity to see accounts
3. **Two Clicks Deeper:** Click account to see transactions
4. **Full Detail:** Click transaction to see source document

### Persistent UI Elements
Always visible regardless of view:
- **Entity Selector** (dropdown or tabs at top)
- **Time Period Selector** (This Month, QTD, YTD, Custom)
- **View Mode Switcher** (By Account, By Time, By Asset)
- **Quick Filters** (checkboxes for entities/accounts)

## Feature Brainstorming

### 🎯 Must-Have Features (Phase 1)

#### Core Navigation & Views
- [ ] Entity selector (persistent global filter)
- [ ] Time period selector with presets
- [ ] View mode tabs (Account/Time/Asset/Tax)
- [ ] Progressive disclosure (summary → detail)
- [ ] Breadcrumb navigation

#### Document Management
- [ ] Statement-centric view with PDF viewer
- [ ] Document list by entity/account
- [ ] Processing status from Claude
- [ ] Source document linkage to transactions

#### Data Display
- [ ] Multi-perspective transaction views
- [ ] Expandable/collapsible groupings
- [ ] Account overview cards (clickable)
- [ ] Quick stats dashboard
- [ ] Asset class breakdown

#### Tax Features
- [ ] Federal vs State breakdown
- [ ] Entity-specific tax summaries
- [ ] Georgia exemption calculations
- [ ] Income type analysis
- [ ] Consolidated tax liability view

#### Administrative
- [ ] Entity/Account management
- [ ] Account-to-entity assignment
- [ ] Database start/stop controls
- [ ] Add new entities/accounts/institutions

### 🚀 Nice-to-Have Features (Phase 2)

#### Enhanced Visualizations
- [ ] Interactive cash flow charts
- [ ] Security performance tracking
- [ ] Tax projection modeling
- [ ] Trend analysis graphs

#### Advanced Tools
- [ ] Bulk document processing
- [ ] Automated reconciliation suggestions
- [ ] Custom tax rule builder
- [ ] Multi-year comparisons

#### Integration Features
- [ ] QuickBooks Desktop sync
- [ ] Tax software export formats
- [ ] Cloud backup capabilities
- [ ] Multi-user support

### 💡 Future Ideas (Phase 3+)

- [ ] Mobile companion app
- [ ] Voice-controlled queries ("Show me Q1 dividends")
- [ ] AI-powered anomaly detection
- [ ] Predictive tax planning
- [ ] Investment performance analytics

## UI/UX Design Principles

### Visual Design
- **Clean & Professional:** Financial data needs clarity, not decoration
- **Information Hierarchy:** Most important data prominently displayed
- **Consistent Color Coding:** 
  - Green = Cash in/Income
  - Red = Cash out/Expenses  
  - Blue = Informational/Neutral
  - Yellow = Needs attention/review

### Interaction Patterns
- **Source of Truth Visibility:** Always show where data came from
- **Progressive Disclosure:** Details available on demand, not overwhelming
- **Confidence Indicators:** Traffic lights, percentages, or badges
- **Undo/Redo Support:** Especially for data corrections

### Responsive Behavior
- **Desktop-First:** Primary use case is desktop with large screen
- **Multi-Panel Layouts:** Resizable panels for PDF + data views
- **Keyboard Shortcuts:** Power user efficiency
- **Remember User Preferences:** Panel sizes, filters, views

## Technical Considerations

### Frontend Stack Options
1. **React + TypeScript**
   - Component library: shadcn/ui or Material-UI
   - State management: Zustand or Redux Toolkit
   - Data fetching: TanStack Query
   - PDF viewer: react-pdf or PDF.js

2. **Next.js Full-Stack**
   - Built-in API routes for database operations
   - Server-side rendering for performance
   - Integrated authentication if needed

### Backend Requirements
- API for database operations (using psql)
- File upload/storage handling
- PDF processing coordination with Claude
- Supabase control commands
- Export generation (QBO, CSV, etc.)

### Key Libraries Needed
- PDF viewing: PDF.js or similar
- Charts: Recharts or Chart.js
- Tables: TanStack Table
- Date handling: date-fns
- Export generation: json2csv, qbo-generator

## Additional User Needs (Thinking Like You)

### What You'll Actually Want Day-to-Day

**Morning Check:**
- Quick glance dashboard showing overnight/weekend changes
- Any documents Claude processed while you were away
- Upcoming deadlines (tax payments, document uploads, earnings)
- Account minimums that need attention

**Tax Planning Mode:**
- "What-if" calculator: If I sell X shares of GOOG, what's my tax hit?
- Safe-to-spend calculator: After reserving for taxes, what's truly available?
- Estimated vs actual tax reconciliation as the year progresses
- Carryforward losses and how to use them

**Audit Trail Features:**
- Complete history of every Claude decision with confidence levels
- When/why accounts were reassigned between entities
- Document processing log with any manual overrides
- Export everything for CPA with full documentation

**Practical Shortcuts:**
- Quick search: "Show me all GOOG transactions"
- One-click filters: "Hide all transactions under $1,000"
- Saved views: "My quarterly tax prep view"
- Bulk categorization: "Mark all these as qualified dividends"

**Peace of Mind Features:**
- Data integrity checks: Alert if something doesn't reconcile
- Missing document alerts: "Still waiting for Entity A's January statement"
- Duplicate payment warnings: "You already paid Q1 taxes"
- Year-end readiness dashboard: What's needed for tax filing

## TDD Requirements & Testing Strategy

### Global Validation Rules

#### Financial Data
- **Amounts**: NUMERIC(15,2) - max $999,999,999,999.99
- **Percentages**: NUMERIC(5,3) - 0.000 to 100.000
- **Dates**: Cannot be future unless explicitly allowed
- **Entity Selection**: At least one entity must always be selected
- **Tax Years**: 2020-2030 valid range

#### Business Logic
- **Net Worth**: Financial Assets + Real Assets - Liabilities
- **Cash Flow**: Opening Balance + Inflows - Outflows = Closing Balance
- **Tax Calculations**: Must match IRS rounding rules (round to nearest dollar)
- **Multi-Entity**: Consolidated totals must equal sum of entity totals

### Critical Test Scenarios

#### Data Integrity Tests
- Duplicate document prevention (by file_hash)
- Transaction reconciliation (sum = reported total)
- Entity isolation (no data leakage between entities)
- Date consistency (transaction date <= document period_end)

#### Tax Calculation Tests
- FSIXX dividends: Federal 100%, Georgia ~3%
- SPAXX dividends: Federal 100%, Georgia ~45%
- GA municipal bonds: Federal 0%, Georgia 0%
- Other state munis: Federal 0%, Georgia 100%
- Qualified dividends flagging
- S-Corp pass-through calculations

#### Performance Tests
- Dashboard load: < 2 seconds with 50k transactions
- Search response: < 500ms for 100k records
- Export generation: < 5 seconds for annual data
- PDF rendering: < 3 seconds for 50-page document

### Error Recovery Requirements

#### Network Failures
- Retry logic with exponential backoff
- Offline mode with cached data
- Queue failed operations for retry
- Clear error messages with recovery actions

#### Data Conflicts
- Optimistic locking for concurrent updates
- Conflict resolution UI for duplicates
- Audit trail for all changes
- Rollback capability for bulk operations

#### Invalid Data
- Prevent save with validation errors
- Highlight specific fields with issues
- Provide clear correction instructions
- Log validation failures for debugging

## Success Metrics

### Quantitative
- Time to process document: < 30 seconds
- Data accuracy: > 99.9%
- Discrepancy resolution: 100% explained
- Page load time: < 2 seconds
- Time to find any transaction: < 10 seconds
- Tax calculation accuracy: 100% match with CPA
- Test coverage: > 80% for critical paths
- Zero data loss incidents

### Qualitative
- User confidence in data accuracy
- Ease of finding source documents
- Clarity of tax implications
- Simplicity of reconciliation process
- Confidence that nothing is missed
- Ability to answer CPA questions immediately

## Questions for User Discussion

### Workflow Priorities
1. **Most Frequent Task:** What will you do most often? Review new statements? Check tax implications? Export for QuickBooks?

2. **Pain Points:** Beyond the $58k discrepancy, what's most frustrating about current process?

3. **Time Sensitivity:** Any specific deadlines? Tax filing? Quarterly reports?

### Feature Preferences
4. **Visualization Style:** Do you prefer tables, charts, or both? Any specific chart types you find most useful?

5. **PDF Interaction:** How important is annotating/highlighting PDFs vs just viewing?

6. **Bulk Operations:** How many documents typically processed at once? Need bulk upload?

### Technical Preferences  
7. **Export Formats:** Besides QBO, what other export formats needed?

8. **Data Retention:** How long to keep processed documents? Archive strategy?

9. **Access Patterns:** Solo use or need to share with CPA/others?

### UI Preferences
10. **Density:** Prefer information-dense screens or more spacious layouts?

11. **Color Coding:** Any specific preferences for how to indicate different states/categories?

12. **Navigation:** Prefer sidebar, top nav, or command palette style?

## Next Steps

1. **Review & Refine:** Discuss these workflows and features
2. **Wireframe Priority Screens:** Start with most critical workflow
3. **Create Component Library:** Build reusable UI components
4. **Implement MVP:** Focus on document processing + viewing first
5. **Iterate Based on Usage:** Refine based on actual usage patterns

---

## Let's Discuss!

**Starting Questions for Our Brainstorming:**

1. Walk me through your ideal day using this app - what's the first thing you'd want to see when you open it?

2. When you think about the $58k discrepancy, what views or tools would help you investigate and explain it most effectively?

3. Are there any financial apps or tools you currently use that have UI patterns you particularly like or dislike?

4. How do you envision the interaction between Claude and the UI? Should Claude's decisions/explanations be visible in the interface?

5. What would give you the most confidence that the extracted data is accurate?

*This is a living document - let's refine it together based on your specific needs and preferences.*