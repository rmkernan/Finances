#!/usr/bin/env python3
"""
Hook Name: Universal Header Reminder
Created: 09/19/25 12:52PM
Updated: 09/19/25 12:52PM - Added explicit instructions to preserve update history
Updated: 09/19/25 4:02PM - Added time throttling and multi-step editing awareness
Purpose: Reminds Claude to add/update timestamps in all file types without overwriting history
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "")

# Process only specified file types
supported_extensions = ['.md', '.py', '.ts', '.tsx', '.js', '.jsx']

# Time throttling - only show reminder every 2 minutes
temp_file = Path("/tmp/claude_reminder_last_shown.txt")
current_time = datetime.now()
show_reminder = True

if temp_file.exists():
    try:
        last_shown_str = temp_file.read_text().strip()
        last_shown = datetime.fromisoformat(last_shown_str)
        if (current_time - last_shown).total_seconds() < 120:  # 2 minutes
            show_reminder = False
    except:
        pass  # If file corrupted, just show reminder

# Check file type and create appropriate message
current_time_str = current_time.strftime("%m/%d/%y %-I:%M%p %Z")

if file_path.endswith('.md'):
    message = f"""AUTOMATED CODE QUALITY REMINDER - Current time: {current_time_str}

If you're making multiple edits as part of a larger task, you can ignore this until you're completely finished.

WHEN YOU'RE DONE WITH ALL EDITS:

NEW FILES: Add header with:
- Created: {current_time_str}
- Purpose: [Brief description]

EXISTING FILES: Add timestamp for significant changes:
- Updated: {current_time_str} - [Brief description of changes]
- PRESERVE ALL PREVIOUS Update entries (don't overwrite history)

SKIP timestamp updates entirely for: minor edits, typo fixes, or experimental changes"""

elif any(file_path.endswith(ext) for ext in ['.py', '.ts', '.tsx', '.js', '.jsx']):
    message = f"""AUTOMATED CODE QUALITY REMINDER - Current time: {current_time_str}

If you're making multiple edits as part of a larger task, you can ignore this until you're completely finished.

WHEN YOU'RE DONE WITH ALL EDITS:

NEW FILES: Add header with:
- Created: {current_time_str}
- Purpose: [Brief description]

EXISTING FILES: Add timestamp for significant changes:
- Updated: {current_time_str} - [Brief description of changes]

CODE QUALITY: When completing this task or reaching a logical stopping point:
- Add/edit comments for future Claude context
- Check for syntax/logic errors
- Verify imports and dependencies
- Consider running lint/format if changes are complete

SKIP ALL CHECKS if you're:
- Still making related edits to this or other files
- In the middle of a refactoring sequence
- Planning immediate follow-up changes
- Making a quick fix that's part of a larger task"""

else:
    # Default message for other supported types
    message = f"""AUTOMATED CODE QUALITY REMINDER - Current time: {current_time_str}

If you're making multiple edits as part of a larger task, you can ignore this until you're completely finished.

WHEN YOU'RE DONE WITH ALL EDITS:

NEW FILES: Add header with:
- Created: {current_time_str}
- Purpose: [Brief description]

EXISTING FILES: Add timestamp for significant changes:
- Updated: {current_time_str} - [Brief description of changes]

SKIP timestamp updates entirely for: minor edits, typo fixes, or experimental changes"""

if any(file_path.endswith(ext) for ext in supported_extensions) and show_reminder:
    # Update timestamp file when showing reminder
    try:
        temp_file.write_text(current_time.isoformat())
    except:
        pass  # If can't write, continue anyway

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message
        }
    }
    print(json.dumps(output))

sys.exit(0)