#!/usr/bin/env python3
"""
Debug status check - direct method call
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client
from datetime import datetime

print("=== Debugging status check - direct ===")

client = create_zimyo_client()

# Test: Login
print("1. Testing login...")
if not client.login():
    print("   ❌ Login failed")
    exit(1)
print("   ✅ Login successful")

# Test: Direct call to the API
print("\n2. Direct API call...")
url = f"{client.settings.zimyo_base_url}/apiv2/auth/hrms/check-clock-in-out-status"
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
print(f"Content-Encoding: {response.headers.get('content-encoding')}")

try:
    json_data = response.json()
    print(f"JSON parsed successfully")
    print(f"Error: {json_data.get('error')}")
    print(f"Code: {json_data.get('code')}")
    print(f"Message: {json_data.get('message')}")
    print(f"Data keys: {json_data.get('data', {}).keys()}")
except Exception as e:
    print(f"JSON parse error: {e}")
    import traceback
    traceback.print_exc()

# Now test the method step by step
print("\n3. Testing method internals...")
from zimyo_attendance.tools.zimyo_client import ZimyoAttendanceResponse, AttendanceData

try:
    data = ZimyoAttendanceResponse(**response.json())
    print(f"ZimyoAttendanceResponse parsed: error={data.error}, code={data.code}")
    
    if not data.error and data.code == 200:
        att = data.data.get("attendance", {})
        print(f"Attendance data keys: {att.keys()}")
        shift_json = att.get("SHIFT_JSON", {})
        print(f"Shift JSON keys: {shift_json.keys()}")
        
        attendance_obj = AttendanceData(
            date=att.get("DATE", ""),
            date_format=att.get("DATE_FORMAT", ""),
            total_punch_time=att.get("TOTAL_PUNCH_TIME", ""),
            current_time=att.get("CURRENT_TIME", ""),
            in_out_status=att.get("IN_OUT_STATUS", ""),
            shift_end=att.get("SHIFT_END", ""),
            timezone=att.get("TIMEZONE", "Asia/Dubai"),
            web_punchin=att.get("WEB_PUNCHIN", "Yes"),
            enable_selfie_attendance=att.get("ENABLE_SELFIE_ATTENDANCE", 1),
            shift_name=shift_json.get("SHIFT_NAME", ""),
            shift_code=shift_json.get("SHIFT_CODE", ""),
            day_start_time=shift_json.get("DAY_START_TIME", "09:00 AM"),
            day_end_time=shift_json.get("DAY_END_TIME", "06:00 PM"),
            shift_json=shift_json,
        )
        print(f"✅ AttendanceData created successfully")
        print(f"Date: {attendance_obj.date}")
        print(f"Status: {attendance_obj.in_out_status}")
    else:
        print(f"Failed: {data.message}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

exit(0)