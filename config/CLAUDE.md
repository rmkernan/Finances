# Configuration Management Context

## 🎯 Purpose
Safe configuration changes and system settings

## 📋 Prerequisites
- Root CLAUDE.md understanding
- Backup of current configuration

## 🗂️ Key Files
- account-mappings.json - Entity/account relationships
- institution-guides/ - Extraction patterns
- mapping-rules.csv - Transaction classification rules

## 🔄 Common Tasks
1. Update account mappings for new accounts
2. Modify institution extraction patterns
3. Adjust transaction classification rules

## ⚠️ Safety & Gotchas
- ALWAYS backup before changes
- Test changes with small dataset first
- Validate JSON structure after edits

## 🔗 Related Contexts
- `/docs/processes/` - How changes affect workflows
- `/.claude/commands/` - Reloading configurations

## 📞 When to Escalate
STOP and ask before:
- Major mapping rule changes
- New institution configuration
- Account structure modifications
