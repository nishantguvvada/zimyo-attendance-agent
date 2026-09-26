#!/usr/bin/env python3
"""
Verify status check fix in zimyo_client.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client

print("=== Verifying status check fix ===")

client = create_zimyo_client()

# Test: Login and get attendance status
print("1. Testing login...")
if not client.login():
    print("   ❌ Login failed")
    exit(1)
print("   ✅ Login successful")

print("\n2. Testing get_attendance_status...")
status = client.get_attendance_status()
if status:
    print("   ✅ Status fetch successful")
    print(f"   Date: {status.date}")
    print(f"   Status: {status.in_out_status}")
    print(f"   Punch In: {status.punch_in_time or 'Not punched'}")
    print(f"   Punch Out: {status.punch_out_time or 'Not punched'}")
    print(f"   Shift: {status.shift_name} ({status.shift_code})")
else:
    print("   ❌ Status fetch failed (check error message above)")
    exit(1)

print("\n=== Verification complete ===")
exit(0)