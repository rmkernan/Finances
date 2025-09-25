# Component Development Context

**Updated:** 09/24/25 8:56PM - Fixed file paths, added development setup prerequisites, corrected BUILD document references
**Updated:** 09/25/25 1:17PM - Added frontend implementer guide reference for sub-agent orientation
**Updated:** 09/25/25 1:33PM - Reorganized frontend/docs references with new directory structure, separated frontend vs backend guides

## 🎯 Purpose
Step-by-step implementation guides for frontend components

## 📋 Prerequisites
- Root CLAUDE.md understanding
- Read /docs/start/development-setup.md for frontend project creation
- Database connection verified (localhost:54322)

## 🗂️ Key Files

### Frontend Development Guides
- /frontend/implementer/README.md - Quick implementer guide for sub-agents (quality gates, gotchas, patterns)
- /frontend/docs/planning/IMPLEMENTATION_PLAN.md - Master frontend implementation strategy
- /frontend/docs/planning/WEEK3_PLAN.md - Current week navigation implementation tasks
- /frontend/docs/planning/WEEK4_PLAN.md - Next week advanced features roadmap
- /frontend/docs/development/COMPONENT_CATALOG.md - Existing component patterns
- /frontend/docs/development/DEVELOPMENT_GOTCHAS.md - Schema and common pitfalls

### Backend Specifications
- /docs/Design/01-Requirements/BUILD-dashboards.md - Complete dashboard specifications and implementation guide
- /docs/Design/01-Requirements/BUILD-workflows-financial.md - Financial transaction view components
- /docs/Design/01-Requirements/BUILD-workflows-documents.md - Document processing and viewer components
- /docs/Design/Database/schema.md - Database schema reference for data models
- /config/account-mappings.json - Entity/account configuration structure

## 🔄 Common Tasks
1. Build dashboard components
2. Implement transaction views
3. Create document processing UI

## ⚠️ Safety & Gotchas
- Follow existing component patterns
- Test database connections in development
- Verify responsive design

## 🔗 Related Contexts
- `/docs/reference/api/` - Backend integration
- `/docs/reference/database/` - Data models

## 📞 When to Escalate
Ask user for:
- UI/UX design decisions
- Business logic clarifications
- Performance requirements
