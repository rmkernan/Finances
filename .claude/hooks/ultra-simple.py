#!/usr/bin/env python3
import json
import sys

# PostToolUse with additionalContext - both Claude and user can see
output = {
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "🎉 HOOK REMINDER: Remember to update file headers according to the specification!"
    }
}
print(json.dumps(output))
sys.exit(0)