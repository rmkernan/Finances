# Handoff Protocol for Multi-Instance Development

**Created:** 09/24/25 9:45PM
**Updated:** 09/24/25 9:51PM - Integrated /DistillConvo command for efficient conversation handoffs
**Purpose:** Standardized process for transitioning between Claude instances during development

## Overview
This document defines how to efficiently transition work between multiple Orchestrator and Implementer Claude instances.

---

## Instance Roles

### Orchestrator (Architect)
- **Model:** Opus preferred for complex reasoning
- **Responsibilities:**
  - System design and architectural decisions
  - Review implementation work
  - Resolve blockers and ambiguities
  - Update documentation as needed
  - Track overall progress

### Implementer (Developer)
- **Model:** Sonnet preferred for speed
- **Responsibilities:**
  - Execute implementation plans exactly
  - Write production code
  - Run quality checks
  - Report completion and issues
  - Never make architectural decisions

### Human Proxy (Coordinator)
- **Responsibilities:**
  - Transfer messages between instances
  - Execute /distill command when needed
  - Manage conversation transitions
  - Maintain context documents

---

## Handoff Process

### 1. Ending a Session

#### For Orchestrator:
Before ending, create/update:
```markdown
File: frontend/docs/SESSION_STATE.md

## Current State
**Date:** [Date]
**Last Completed:** [Specific task/file]
**Next Task:** [Exact next step]
**Blockers:** [Any unresolved issues]

## Progress Summary
- ✅ Day 1: Project setup [COMPLETE/PARTIAL/NOT STARTED]
- ✅ Day 2: Layout & Navigation [Status]
- ✅ Day 3: Data Layer [Status]
[etc.]

## Important Decisions Made
- [List any architectural decisions]
- [Configuration choices]
- [Problem resolutions]

## Open Questions
- [Any pending decisions]
```

#### For Implementer:
Before ending, ensure:
1. All code is committed with descriptive message
2. Run `npm run quality` and document results
3. Update progress in implementation plan
4. Note any questions for architect

### 2. Using /DistillConvo Command

**When to use /DistillConvo:**
- After completing a major phase
- Before switching instance roles
- When conversation exceeds ~20 exchanges or ~30k tokens
- Before ending work session
- When debugging cycles consumed many tokens

**How to invoke:**
1. Human Proxy types: `/DistillConvo`
2. Current Claude proposes what to keep/remove
3. Human reviews and approves
4. Claude creates timestamped transcript file
5. Save as: `transcript-YYYY-MM-DD-HHMM-dashboard-[phase].md`

**What gets preserved automatically:**
- Initial requirements and context
- All file paths and documentation references
- Working solutions and implementations
- Key architectural decisions
- Current state and next steps
- Established communication patterns

**What gets removed:**
- Failed debugging attempts
- Repetitive error messages
- Tangential discussions
- Back-and-forth clarifications that led nowhere
- Routine git status checks

**Example filename for our project:**
```bash
transcript-2025-09-24-2200-dashboard-day1-setup.md
transcript-2025-09-25-1400-dashboard-day2-components.md
```

### 3. Starting New Session

#### New Orchestrator Startup Prompt:
```markdown
You are the Orchestrator for a Personal Wealth Manager dashboard project.

**Project Location:** /Users/richkernan/Projects/Finances/frontend/

**Read these documents in order:**
1. docs/HANDOFF_PROTOCOL.md (this document)
2. docs/SESSION_STATE.md (current progress)
3. docs/DESIGN.md (architecture)
4. docs/ROADMAP.md (phases)
5. docs/IMPLEMENTATION_PLAN.md (detailed tasks)

**Previous Session Summary:**
[Paste /distill output here]

**Your immediate task:**
[Specific next step from SESSION_STATE.md]

Please confirm you've read the documents and are ready to continue orchestrating.
```

#### New Implementer Startup Prompt:
```markdown
You are the Implementer for a Personal Wealth Manager dashboard project.

**Project Location:** /Users/richkernan/Projects/Finances/frontend/

**Read these documents:**
1. docs/HANDOFF_PROTOCOL.md (this document)
2. docs/SESSION_STATE.md (current progress)
3. docs/IMPLEMENTATION_PLAN.md (your tasks)

**Previous Session Summary:**
[Paste /distill output here]

**Current Task:**
[Specific task from SESSION_STATE.md]

**Important:**
- Follow the implementation plan exactly
- Make commits at checkpoints
- Run quality checks as specified
- Pause and ask if anything is unclear
- The Orchestrator is available for questions

Please confirm you've read the documents and state which Day/Task you're implementing.
```

---

## Session State Tracking

### Progress Indicators
Use these consistent markers in SESSION_STATE.md:
- 🟢 **COMPLETE** - Fully implemented and tested
- 🟡 **IN PROGRESS** - Partially complete
- 🔴 **BLOCKED** - Cannot proceed without resolution
- ⚪ **NOT STARTED** - Not yet begun
- 🔵 **NEEDS REVIEW** - Complete but needs architect review

### Commit Message Format
```bash
git commit -m "[Role] [Phase]: [Description]"

# Examples:
git commit -m "Impl Day1: Complete project setup and dependencies"
git commit -m "Arch: Update dashboard component specifications"
git commit -m "Fix: Resolve TypeScript errors in AccountsList"
```

---

## Document Hierarchy

### Always Current (Update These)
```
docs/
├── SESSION_STATE.md      # Current progress (UPDATE EVERY SESSION)
├── HANDOFF_PROTOCOL.md   # This document (static)
└── IMPLEMENTATION_PLAN.md # Update completed checkboxes
```

### Reference Documents (Read Only)
```
docs/
├── DESIGN.md             # Architecture decisions
├── ROADMAP.md           # Phase definitions
└── API_CONTRACTS.md     # Type definitions
```

---

## Quality Gates Between Handoffs

### Before Implementer → Orchestrator:
1. ✅ All code committed
2. ✅ `npm run quality` passes
3. ✅ Browser tested (no console errors)
4. ✅ SESSION_STATE.md updated
5. ✅ Questions documented

### Before Orchestrator → Implementer:
1. ✅ Clear next task defined
2. ✅ Any blockers resolved
3. ✅ Documentation updated if needed
4. ✅ SESSION_STATE.md current

---

## Emergency Recovery

If session state is lost:

1. **Check git log:**
```bash
git log --oneline -10  # See recent commits
git status            # Check working directory
```

2. **Verify project state:**
```bash
npm run quality       # Check code health
npm run dev          # Test if app runs
```

3. **Read SESSION_STATE.md** for last known state

4. **Use /distill on previous conversation** if available

---

## Communication Templates

### Implementer Requesting Help:
```markdown
🛑 PAUSE - Need Architect Guidance

**Context:** [What you were doing]
**Issue:** [What happened]
**Options:** [Available choices]
**Recommendation:** [Your suggestion]

Awaiting guidance before proceeding.
```

### Orchestrator Giving Direction:
```markdown
## Architect Direction

**Decision:** [Clear choice]
**Rationale:** [Why this choice]
**Implementation:** [Specific steps]
**Quality Check:** [How to verify]

Proceed with implementation.
```

### Session Handoff:
```markdown
## Session Complete

**Role:** [Orchestrator/Implementer]
**Completed:** [What was done]
**Next Step:** [Exact next task]
**State:** [Link to SESSION_STATE.md]
**Notes:** [Any important context]

Ready for handoff.
```

---

## Best Practices

1. **Keep sessions focused** - One day's work or one major feature
2. **Document immediately** - Update SESSION_STATE.md before ending
3. **Use consistent paths** - Always work from `/Users/richkernan/Projects/Finances/frontend/`
4. **Preserve context** - Don't delete previous session states, archive them
5. **Test before handoff** - Ensure code runs before switching

---

## Optimization Tips

### For Speed:
- Implementer (Sonnet) for code generation
- Batch similar tasks in one session
- Clear, specific task definitions

### For Quality:
- Orchestrator (Opus) reviews complex work
- Run quality checks at boundaries
- Document decisions immediately

### For Continuity:
- Always update SESSION_STATE.md
- Use descriptive commit messages
- Keep distillations under 500 lines