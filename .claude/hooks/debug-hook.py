#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

# Write to a log file to confirm hook execution
log_path = os.path.expanduser("~/hook-debug.log")
with open(log_path, "a") as f:
    f.write(f"\n[{datetime.now()}] Hook triggered!\n")

    try:
        data = json.load(sys.stdin)
        f.write(f"Tool: {data.get('tool_name', 'unknown')}\n")
        f.write(f"Input: {json.dumps(data.get('tool_input', {}))}\n")
    except:
        f.write("Could not parse stdin\n")

# Also output to stdout for transcript
print("DEBUG: Hook executed successfully")
sys.exit(0)