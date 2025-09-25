# Agent & Command Context

## 🎯 Purpose
Specialized agent usage and command execution guidance

## 📋 Prerequisites
- Root CLAUDE.md understanding
- Task-specific context loaded

## 🗂️ Key Files
- commands/process-inbox.md - Document processing workflow
- commands/load-extractions.md - Database loading
- agents/fidelity-statement-extractor.md - Specialized extraction

## 🔄 Common Tasks
1. Execute process-inbox command for document processing
2. Run load-extractions for database loading
3. Use specialized agents for complex extractions

## ⚠️ Safety & Gotchas
- Commands modify real data - verify before execution
- Agents require specific document formats
- Always check command outputs for errors

## 🔗 Related Contexts
- `/docs/processes/` - Understanding workflows
- `/config/` - System configuration

## 📞 When to Escalate
STOP immediately for:
- Command execution errors
- Unexpected agent behavior
- Data integrity warnings
