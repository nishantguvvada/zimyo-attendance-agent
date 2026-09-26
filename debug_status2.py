#!/usr/bin/env python3
"""
Debug status check fix - check response headers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
from zimyo_attendance.config.settings import get_settings

print("=== Debugging status check - raw HTTP ===")

settings = get_settings()

# First login
login_url = "https://loginapi.zimyo.work/user/login"
payload = {
    "username": settings.zimyo_username,
    "password": settings.zimyo_password,
}

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "app_lang": "en",
    "app_name": "Account",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
}

client = httpx.Client(timeout=30.0, follow_redirects=True)
response = client.post(login_url, json=payload, headers=headers)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    auth_data = response.json()
    token = auth_data['data']['token']
    employee_id = auth_data['data']['auth']['employee_id']
    print(f"Token: {token[:20]}...")
    print(f"Employee ID: {employee_id}")

    # Visit dashboard
    dashboard_url = "https://zimyo.work/ess/dashboard/my-dashboard"
    dashboard_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://zimyo.work/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
    }
    client.get(dashboard_url, headers=dashboard_headers)
    print("Dashboard visited")

    # Now try check-clock-in-out-status
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    status_url = f"{settings.zimyo_base_url}/apiv2/auth/hrms/check-clock-in-out-status"
    status_payload = {
        "EMP_ID": employee_id,
        "SOURCE": "Web",
        "DATE": date_str,
        "PLACE": "",
    }
    status_headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "access-control-allow-origin": "https://www.zimyo.work",
        "content-type": "application/json",
        "origin": "https://zimyo.work",
        "priority": "u=1, i",
        "referer": "https://zimyo.work/",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "token": token,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    }

    print(f"\nRequest URL: {status_url}")
    print(f"Request Payload: {status_payload}")
    print(f"Content-Encoding in request: gzip, deflate, br, zstd")

    response = client.post(status_url, json=status_payload, headers=status_headers)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Content-Encoding: {response.headers.get('content-encoding')}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Raw content length: {len(response.content)}")
    print(f"Raw content (first 200): {response.content[:200]}")

    # Try to decode
    try:
        import gzip
        if response.headers.get('content-encoding') == 'gzip':
            decoded = gzip.decompress(response.content)
            print(f"Gzip decoded length: {len(decoded)}")
            print(f"Decoded (first 500): {decoded[:500]}")
    except Exception as e:
        print(f"Gzip decode error: {e}")

    try:
        # Try regular json
        print(f"JSON: {response.json()}")
    except Exception as e:
        print(f"JSON parse error: {e}")

    # Also try with accept-encoding removed
    print("\n--- Trying without accept-encoding in headers ---")
    status_headers_no_compress = {k: v for k, v in status_headers.items() if k != 'accept-encoding'}
    response2 = client.post(status_url, json=status_payload, headers=status_headers_no_compress)
    print(f"Response Status: {response2.status_code}")
    print(f"Content-Encoding: {response2.headers.get('content-encoding')}")
    try:
        print(f"JSON: {response2.json()}")
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw: {response2.content[:200]}")

exit(0)