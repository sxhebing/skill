#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import re

print("=========================================================")
print("🎯 Gemini Skill Foreground Loop Monitor Active...")
print("📡 Monitoring logcat for 'RECOVERY STATS' & 'FRESH STATS'")
print("📡 Threshold: > 8s (8000ms)")
print("=========================================================")

# Clear logcat initially to start fresh
subprocess.run(["adb", "logcat", "-c"])

check_count = 0
last_processed_line = ""

try:
    while True:
        check_count += 1
        # Fetch last line of RECOVERY STATS or FRESH STATS
        res = subprocess.run("adb logcat -v time -d | grep -iE 'RECOVERY STATS|FRESH STATS' | tail -n 1", shell=True, capture_output=True, text=True)
        line = res.stdout.strip()
        
        if line and line != last_processed_line:
            last_processed_line = line
            # Parse Success: XXX ms
            match = re.search(r"Success:\s*([0-9]+)\s*ms", line)
            if match:
                duration = int(match.group(1))
                print(f"[Check {check_count}] Latest Recovery: {duration} ms")
                if duration > 8000:
                    print(f"🚨 [ANOMALY] Recovery duration {duration} ms exceeds 8 seconds!")
                    # Dump the failure logs
                    dump_res = subprocess.run("adb logcat -v time -d | tail -n 500", shell=True, capture_output=True, text=True)
                    with open("recovery_timeout_dump.log", "w", encoding='utf-8') as f:
                        f.write(dump_res.stdout)
                    sys.exit(101) # Anomaly exit code
        else:
            # Print a simple heartbeat if no new logs to prevent idle timeout
            if check_count % 5 == 0:
                print(f"[Check {check_count}] Waiting for new recovery stats...")
                
        time.sleep(3)
except KeyboardInterrupt:
    print("\n[*] Monitor stopped by user.")
    sys.exit(0)
