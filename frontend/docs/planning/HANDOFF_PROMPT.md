# Page-by-Page Feature Review - Handoff Prompt

**Created:** 09/25/25 2:16PM ET
**Purpose:** Handoff prompt for comprehensive feature capture session

---

## Context for New Conversation

**Project:** Personal Wealth Manager frontend - multi-entity financial tracking system
**Current Status:** Week 3 COMPLETE (12/12 days) - Full navigation architecture operational
**Data Scale:** 3 active accounts, 152 positions, 267 transactions
**Tech Stack:** Next.js 14, TypeScript, Tailwind, React Query, Supabase (localhost:54322)

## Previous Plan vs New Approach

**Previous Plan:** Week 4 implementation with predetermined features (search, exports, etc.)
**NEW APPROACH:** User-driven page-by-page review to capture real workflow needs

## Your Mission

Conduct systematic page-by-page review with user to capture feature requests:

1. **Review Each Page:** User navigates and provides observations
2. **Capture Requests:** Document in structured format with priorities
3. **Ask Clarifying Questions:** Fill gaps in requirements
4. **Maintain Organization:** Keep feature capture document updated
5. **Prioritize & Sequence:** Create implementation backlog when complete

## Key Resources

**Feature Capture Document:** `/frontend/docs/planning/FEATURE_CAPTURE.md` (already created)
**Project Context:** Root `/CLAUDE.md` and `/frontend/implementer/README.md`
**Current Architecture:** `/frontend/docs/architecture/SESSION_STATE.md`

## Pages to Review (in order)

1. Dashboard (main landing)
2. Accounts (primary navigation)
3. Account Detail Pages (daily usage)
4. Transactions (data analysis)
5. Entities (business structure)
6. Documents (processing workflow)
7. Admin/Data Status (monitoring)

## Priority Framework

- 🔴 **Critical** - Blocks workflow
- 🟠 **High** - Significant daily usage improvement
- 🟡 **Medium** - Nice to have enhancement
- 🟢 **Low** - Polish/future

## Communication Guidelines

**Remember:** User is technical but cannot read code
- ❌ Don't show code blocks to explain issues
- ✅ Do explain problems in technical English with examples
- ✅ Do ask clarifying questions to understand requirements
- ✅ Do maintain organized documentation throughout

## Working Directory

`/Users/richkernan/Projects/Finances/frontend/wealth-manager/`

## Start Here

Begin by reading the feature capture document, then ask the user to navigate to the Dashboard page and start the systematic review. Update the document as you capture each page's requirements.

**Goal:** Transform user observations into a prioritized, sequenced implementation backlog that reflects real workflow needs rather than assumed requirements.

---

*This comprehensive review will consume many tokens but will result in a much better-targeted Week 4+ implementation plan.*