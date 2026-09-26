#!/usr/bin/env python3
"""
Debug status check - capture full error
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client

print("=== Debugging status check with full output ===")

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

response = client.client.post(
    url,
    json=payload,
    headers=client._auth_headers(),
)
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Content-Encoding: {response.headers.get('content-encoding')}")

# Try to parse response
try:
    json_data = response.json()
    print(f"JSON: {json_data}")
except Exception as e:
    print(f"JSON parse error: {e}")
    print(f"Raw content (first 500): {response.content[:500]}")

# Also test via the method
print("\n3. Testing via get_attendance_status method...")
status = client.get_attendance_status()
if status:
    print("   ✅ Status fetch successful")
    print(f"   Date: {status.date}")
    print(f"   Status: {status.in_out_status}")
else:
    print("   ❌ Status fetch failed")

exit(0)