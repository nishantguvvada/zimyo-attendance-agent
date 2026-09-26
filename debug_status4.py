#!/usr/bin/env python3
"""
Debug status check with full error output
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client

print("=== Debugging status check ===")

client = create_zimyo_client()

# Test: Login
print("1. Testing login...")
if not client.login():
    print("   ❌ Login failed")
    exit(1)
print("   ✅ Login successful")

# Test: Get attendance status with full error capture
print("\n2. Testing get_attendance_status...")
try:
    status = client.get_attendance_status()
    if status:
        print("   ✅ Status fetch successful")
        print(f"   Date: {status.date}")
        print(f"   Status: {status.in_out_status}")
        print(f"   Punch In: {status.punch_in_time or 'Not punched'}")
        print(f"   Punch Out: {status.punch_out_time or 'Not punched'}")
        print(f"   Shift: {status.shift_name} ({status.shift_code})")
    else:
        print("   ❌ Status fetch returned None")
except Exception as e:
    print(f"   ❌ Exception raised: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Done ===")
exit(0)