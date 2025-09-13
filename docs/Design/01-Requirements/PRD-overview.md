# Financial Management System - PRD Overview

**Created:** 09/12/25  
**Updated:** 09/12/25 8:09PM ET - Added hierarchical classification details to document processing workflow
**Purpose:** Executive summary and core architecture reference for development teams  
**Status:** Active Reference Document

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
   - Claude reads each document using hierarchical classification:
     * Entity identification (WHO owns this?)
     * Institution detection (WHERE is it from?)
     * Account matching (WHICH account?)
     * Document type classification (WHAT is it?)
   - If confident → processes automatically
   - If uncertain → asks user for clarification
   - Extracts transactions with coordinates for PDF highlighting
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

## Document-Account Relationship Model

### Core Relationships
- Documents belong to one institution
- Documents can be linked to multiple accounts (e.g., consolidated statements)
- Transactions extracted from documents are attributed to specific accounts
- When viewing a document through an account context, only see transactions for that account
- "View Document" always shows the complete PDF

### Data Flow
```
Institution Document → Contains Multiple Account Data → Individual Transactions
                    ↓
            Context-Filtered Display Based on Current View
```

### Navigation Examples
1. **From Global Context:** See all documents across all entities
2. **From Entity Context:** See only documents containing that entity's account data
3. **From Account Context:** See only transactions for that account within documents

## Notes & Metadata Support
Each hierarchy level supports notes and metadata:
- **Global:** General reminders, system-wide notes
- **Entity:** Tax strategies, entity-specific notes
- **Institution:** Login credentials, contact info
- **Account:** Investment strategies, account-specific reminders

## Core Requirements Summary

### Must-Have Features (Phase 1)
- Entity selector (persistent global filter)
- Time period selector with presets
- Progressive disclosure (summary → detail)
- Breadcrumb navigation
- Document list by entity/account
- Processing status from Claude
- Source document linkage to transactions
- Multi-perspective transaction views
- Account overview cards (clickable)
- Federal vs State tax breakdown
- Entity-specific tax summaries

### Nice-to-Have Features (Phase 2)
- Interactive cash flow charts
- Security performance tracking
- Tax projection modeling
- Bulk document processing
- Custom tax rule builder

### Future Ideas (Phase 3+)
- Mobile companion app
- AI-powered anomaly detection
- Predictive tax planning
- Investment performance analytics

## Technical Architecture Overview

### Frontend Stack
- **Framework:** Next.js 14 with TypeScript
- **UI Library:** shadcn/ui + Tailwind CSS
- **State Management:** Zustand for client state, TanStack Query for server state
- **Data Visualization:** Recharts or Chart.js
- **PDF Viewing:** PDF.js or react-pdf

### Backend Requirements
- API for database operations (using psql)
- File upload/storage handling
- PDF processing coordination with Claude
- Supabase control commands
- Export generation (QBO, CSV, etc.)

### Database Integration
- **Database:** Local Supabase PostgreSQL only
- **Connection:** postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Studio:** http://localhost:54323 (LOCAL ONLY)
- **Critical:** Never use cloud Supabase instances

## Success Metrics

### Quantitative Goals
- Time to process document: < 30 seconds
- Data accuracy: > 99.9%
- Page load time: < 2 seconds
- Time to find any transaction: < 10 seconds
- Tax calculation accuracy: 100% match with CPA

### Qualitative Goals
- User confidence in data accuracy
- Ease of finding source documents
- Clarity of tax implications
- Simplicity of reconciliation process
- Confidence that nothing is missed

---

**Next Steps:**
1. Review BUILD-* documents for specific implementation guidance
2. Start with Next.js 14 project setup
3. Implement core navigation architecture
4. Begin with dashboard and entity management features

*This overview provides the foundational context. Refer to specific BUILD-*.md files for detailed implementation guidance.*