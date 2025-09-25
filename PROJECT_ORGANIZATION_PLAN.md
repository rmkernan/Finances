# Project Organization Plan
**Financial Data Management System Documentation Reorganization**

**Created:** 09/24/25 5:35PM
**Purpose:** Comprehensive plan for intuitive, Claude-optimized documentation structure with hierarchical CLAUDE.md system

---

## 🎯 Core Philosophy: Hierarchical Context System

After deep analysis, the optimal approach is a **hierarchical CLAUDE.md system** where:

1. **Root CLAUDE.md** = Project compass and navigation hub
2. **Directory-specific CLAUDE.md files** = Context-specialized guidance that builds upon the root
3. **Clear inheritance model** = Each directory assumes you've read the parent context

This approach solves the fundamental problem: **different Claude tasks need different knowledge**, but that knowledge should be **discoverable and coherent**.

---

## 🗂️ Proposed Directory Structure

```
📁 /Users/richkernan/Projects/Finances/
├── 📋 CLAUDE.md                        # 🎯 MISSION CONTROL - Navigation hub
│
├── 📁 docs/
│   ├── 📋 CLAUDE.md                    # Documentation navigation & conventions
│   │
│   ├── 📁 start/                       # 🚀 FIRST STOP for new Claude instances
│   │   ├── 📋 CLAUDE.md               # Orientation & quickstart guidance
│   │   ├── quickstart.md              # 5-minute project understanding
│   │   ├── project-overview.md        # Architecture & business context
│   │   └── development-setup.md       # Environment & tools setup
│   │
│   ├── 📁 processes/                   # 🔄 HOW things work
│   │   ├── 📋 CLAUDE.md               # Process execution guidance & safety
│   │   ├── document-processing.md     # Complete extraction pipeline
│   │   ├── database-operations.md     # Query patterns & maintenance
│   │   ├── frontend-development.md    # UI development workflow
│   │   └── configuration-management.md # Safe config changes
│   │
│   ├── 📁 reference/                   # 📚 WHAT things are
│   │   ├── 📋 CLAUDE.md               # How to navigate specs & lookup info
│   │   ├── 📁 database/
│   │   │   ├── schema.md              # Complete 12-table structure
│   │   │   └── query-patterns.md      # Common queries & examples
│   │   ├── 📁 api/
│   │   │   └── endpoints.md           # Frontend-backend interface
│   │   └── 📁 configuration/
│   │       ├── account-mappings.md    # Mapping system reference
│   │       └── institution-guides.md  # Extraction patterns per bank
│   │
│   └── 📁 workflows/                   # 🛠️ STEP-BY-STEP implementation guides
│       ├── 📋 CLAUDE.md               # Component development guidance
│       ├── dashboards.md              # Dashboard implementation
│       ├── financial-transactions.md  # Transaction views
│       ├── document-viewer.md         # PDF viewer components
│       ├── tax-reporting.md           # Tax workflow UI
│       ├── admin-functions.md         # Admin interface
│       └── document-processing-ui.md  # Processing interface
│
├── 📁 .claude/
│   ├── 📋 CLAUDE.md                   # Agent & command usage guidance
│   ├── 📁 agents/                     # Specialized extraction agents
│   │   ├── fidelity-statement-extractor.md
│   │   └── database-manager.md
│   └── 📁 commands/                   # Executable workflows
│       ├── process-inbox.md           # Streamlined execution steps
│       ├── load-extractions.md        # Database loading
│       └── backup-database.md         # Backup procedures
│
└── 📁 config/                         # System configuration (UNCHANGED)
    ├── 📋 CLAUDE.md                   # Configuration change guidance
    └── [existing structure preserved]
```

---

## 🧭 Hierarchical CLAUDE.md System Design

### **Root CLAUDE.md (Mission Control)**
```markdown
# CLAUDE.md - Financial Data Management System

## 🎯 What This System Does
[Current project description - streamlined]

## 🚀 First Time Here? Start Here
👉 **READ FIRST:** `/docs/start/CLAUDE.md` - Essential orientation

## 🧭 Navigation by Task
**Document Processing:** → `/docs/processes/CLAUDE.md`
**Frontend Development:** → `/docs/workflows/CLAUDE.md`
**Database Operations:** → `/docs/processes/CLAUDE.md`
**Configuration Changes:** → `/config/CLAUDE.md`
**Command Execution:** → `/.claude/CLAUDE.md`

## 🚨 Emergency Protocols
- Always backup before destructive operations
- Verify accounts before processing documents
- Test database connections before bulk operations

[Streamlined - remove detailed process knowledge]
```

### **Directory-Specific CLAUDE.md Pattern**

**Each directory CLAUDE.md follows this template:**

```markdown
# [Directory] Context Guide

## 🎯 Purpose
What this directory handles and why it exists

## 📋 Prerequisites
- Assumes you've read root CLAUDE.md
- [Any specific setup or permissions needed]

## 🗂️ Key Files
[File-by-file breakdown with purposes]

## 🔄 Common Tasks
[Step-by-step for frequent operations in this context]

## ⚠️ Safety & Gotchas
[Context-specific warnings and best practices]

## 🔗 Related Contexts
[Cross-references to other directories when needed]

## 📞 When to Escalate
[When to ask user vs. proceed autonomously]
```

---

## 🎯 Benefits of This Approach

### **1. Intelligent Context Loading**
- Claude working on frontend doesn't load database internals
- Claude processing documents gets safety protocols immediately
- Claude doing configuration changes gets change control guidance

### **2. Discoverable Knowledge**
- Root CLAUDE.md routes to the right specialized context
- Each context builds logically on the parent
- Cross-references prevent knowledge siloes

### **3. Maintainable System**
- Domain experts maintain their specific CLAUDE.md files
- Changes propagate through clear inheritance
- Consistency through standardized templates

### **4. Scalable Architecture**
- New domains get their own CLAUDE.md easily
- Complex projects don't overwhelm simple tasks
- Knowledge grows organically with system complexity

---

## 🚀 Implementation Phases

### **Phase 1: Foundation (Week 1)**
1. **Create directory structure** with placeholder CLAUDE.md files
2. **Migrate root CLAUDE.md** to navigation hub model
3. **Extract buried knowledge** from process-inbox.md to proper locations
4. **Create /docs/start/** directory with essential orientation

### **Phase 2: Context Development (Week 2)**
1. **Write directory-specific CLAUDE.md files** using standard template
2. **Extract and organize process knowledge** into logical workflows
3. **Consolidate redundant frontend docs** into single source of truth
4. **Move BUILD docs** to /docs/workflows/ with proper naming

### **Phase 3: Enhancement (Week 3)**
1. **Cross-reference optimization** - link related contexts effectively
2. **Safety protocol integration** - embed warnings where needed
3. **User testing** - validate navigation with fresh Claude instances
4. **Documentation of the documentation** - meta-guides for maintenance

---

## 📍 Navigation Flow Examples

### **New Claude Instance - Document Processing Task**
```
1. User: "Process the documents in inbox"
2. Claude reads: Root CLAUDE.md → routes to /docs/processes/CLAUDE.md
3. Processes CLAUDE.md → loads document-processing.md
4. Gets context-specific safety protocols and execution guidance
5. Executes via /.claude/commands/process-inbox.md (streamlined)
```

### **New Claude Instance - Frontend Development**
```
1. User: "Build a dashboard component"
2. Claude reads: Root CLAUDE.md → routes to /docs/workflows/CLAUDE.md
3. Workflows CLAUDE.md → loads dashboards.md
4. Gets component patterns and development conventions
5. References /docs/reference/api/ for backend integration
```

### **New Claude Instance - Database Query**
```
1. User: "Show me all transactions for entity X"
2. Claude reads: Root CLAUDE.md → routes to /docs/processes/CLAUDE.md
3. Processes CLAUDE.md → loads database-operations.md
4. Gets query patterns and safety protocols
5. References /docs/reference/database/ for schema details
```

---

## 🎯 Success Metrics

### **Before Reorganization**
- ❌ New Claude needs 17,000+ lines across scattered docs
- ❌ Critical knowledge buried in 503-line command file
- ❌ 87% redundancy in frontend specifications
- ❌ No clear starting point for different task types

### **After Reorganization**
- ✅ New Claude reads root CLAUDE.md (200 lines) → specialized context (300 lines)
- ✅ Task-specific knowledge immediately accessible
- ✅ Single source of truth for all specifications
- ✅ Clear inheritance and cross-reference system
- ✅ Self-documenting navigation structure

---

## 🔧 Migration Strategy

### **Immediate Actions (This Week)**
1. Create directory structure with placeholder CLAUDE.md files
2. Move transcripts and temporary files to /docs/archive/
3. Extract critical process knowledge from process-inbox.md
4. Write /docs/start/quickstart.md for immediate orientation

### **Content Migration (Next Week)**
1. Merge redundant frontend specifications
2. Reorganize BUILD documents into workflows/
3. Standardize all CLAUDE.md files using template
4. Implement cross-reference system

### **Validation (Following Week)**
1. Test navigation with fresh Claude instances
2. Validate knowledge discoverability
3. Optimize based on real usage patterns
4. Document maintenance procedures

---

## 🎯 Conclusion

The hierarchical CLAUDE.md system solves the fundamental challenge: **different tasks need different knowledge, but that knowledge must be discoverable and coherent**.

By creating specialized contexts that build upon a central navigation hub, we achieve:
- **Faster Claude orientation** (5 minutes instead of hours)
- **Task-appropriate knowledge loading** (no information overload)
- **Maintainable knowledge architecture** (clear ownership and inheritance)
- **Scalable system** (grows with project complexity)

This approach transforms documentation from a **knowledge dump** into an **intelligent guidance system** optimized for Claude's cognitive patterns and the user's collaborative workflow.