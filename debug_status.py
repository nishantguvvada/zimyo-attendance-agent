#!/usr/bin/env python3
"""
Debug status check fix in zimyo_client.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client

print("=== Debugging status check ===")

client = create_zimyo_client()

# Test: Login and get attendance status
print("1. Testing login...")
if not client.login():
    print("   ❌ Login failed")
    exit(1)
print("   ✅ Login successful")

print("\n2. Testing get_attendance_status with manual call...")
url = f"{client.settings.zimyo_base_url}/apiv2/auth/hrms/check-clock-in-out-status"
from datetime import datetime
date_str = datetime.now().strftime("%Y-%m-%d")
payload = {
    "EMP_ID": client._employee_id,
    "SOURCE": "Web",
    "DATE": date_str,
    "PLACE": "",
}

print(f"URL: {url}")
print(f"Payload: {payload}")
print(f"Headers: {client._auth_headers()}")

response = client.client.post(
    url,
    json=payload,
    headers=client._auth_headers(),
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

exit(0)