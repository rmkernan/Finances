# CLAUDE.md - Finances Project Configuration

**Created:** 09/09/25 2:14PM ET  
**Updated:** 09/09/25 2:35PM ET - Converted to selective individual file symlinks  
**Purpose:** Explains selective symlinked configuration from ProjectToolkit

## Project Setup

This project uses selective individual file symlinks from ProjectToolkit to maintain shared functionality while allowing project-specific customizations.

## Symlinked Components

### hooks/unified-reminder.py → ProjectToolkit
**What:** Individual file symlink to shared header reminder hook  
**Function:** Shows "AUTOMATED CODE QUALITY REMINDER" after Write/Edit/MultiEdit operations  
**Supported Files:** .md, .py, .ts, .tsx, .js, .jsx  
**Why Symlinked:** Hook improvements in ProjectToolkit automatically apply here

### commands/DistillConvo.md → ProjectToolkit  
**What:** Individual file symlink to conversation analysis command  
**Function:** `/distill-convo` command for analyzing conversation patterns  
**Why Symlinked:** Shared utility useful across projects

### commands/ReviewConvos.md → ProjectToolkit
**What:** Individual file symlink to conversation review command  
**Function:** `/review-convos` command for reviewing conversation quality  
**Why Symlinked:** Shared utility useful across projects

### settings.json → ProjectToolkit
**What:** File symlink to shared configuration  
**Contains:**
- PostToolUse hook configuration for unified-reminder.py
- Comprehensive autoApprove settings for safe operations
- Consistent behavior across all projects

## Project-Specific Flexibility

### Local Directories
- **hooks/** - Local directory for finance-specific hooks
- **commands/** - Local directory for finance-specific commands
- Can add budget analysis hooks, tax calculation commands, etc.

### Individual File Control
- Each symlink is independent - can remove/add specific shared files
- Deleting a symlinked file only affects this project, not ProjectToolkit
- Can override by creating local file with same name

### settings.local.json (not present)
**Purpose:** Add this file manually for Finances-specific permissions/overrides  
**Precedence:** Local settings override symlinked settings.json

## Hook Behavior

When you create or edit supported files, you'll see:
```
AUTOMATED CODE QUALITY REMINDER - Current time: MM/DD/YY H:MMAM/PM ET

NEW FILES: Consider adding appropriate header with:
- Created: [timestamp]
- Purpose: [Brief description]

EXISTING FILES with significant changes:
- Updated: [timestamp] - [Brief description of changes]

FOR CODE FILES: Also consider:
- Add/edit comments for future Claude context
- Check for syntax/logic errors
- Verify imports and dependencies

SKIP for: minor edits, typo fixes, or multi-step work in progress
```

## Benefits of Selective Symlink Approach

1. **Granular Control:** Choose exactly which shared files you want
2. **Project Independence:** Can add finance-specific hooks/commands safely  
3. **Automatic Updates:** Symlinked files update when ProjectToolkit is updated
4. **No Conflicts:** Local files coexist with symlinked files
5. **Safe Deletion:** Removing symlinks doesn't affect other projects

## Available Commands

- `/distill-convo` - Analyze conversation patterns (symlinked)
- `/review-convos` - Review conversation quality (symlinked)
- *Add finance-specific commands to local commands/ directory*

## Adding Project-Specific Files

**For finance-specific commands:**
```bash
# Create local command file
echo "Finance budget analysis command" > /Finances/.claude/commands/budget-analysis.md
```

**For finance-specific hooks:**
```bash  
# Create local hook file
cp template-hook.py /Finances/.claude/hooks/finance-validator.py
# Update settings.json to reference the new hook
```

## Important Notes

- **Restart Claude Code** after adding/removing symlinks
- **Edit shared files in ProjectToolkit** - changes propagate automatically
- **Edit local files directly** in this project
- **Hook requires JSON output format** to display in transcript

---

*This project uses selective symlinks for optimal flexibility. For full ProjectToolkit documentation, see `/Projects/ProjectToolkit/CLAUDE.md`*