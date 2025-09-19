#!/usr/bin/env python3
import json
import sys
from datetime import datetime

try:
    data = json.load(sys.stdin)

    # Log to file with precise timestamp
    with open("/Users/richkernan/hook-time-test.log", "a") as f:
        f.write(f"Hook executed at: {datetime.now()}\n")

    # Print to stdout
    print(f"HOOK TIME: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

sys.exit(0)