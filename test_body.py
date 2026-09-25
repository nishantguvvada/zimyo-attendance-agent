import httpx
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv("ZIMYO_USERNAME")
PASSWORD = os.getenv("ZIMYO_PASSWORD")

print("Logging in...")
login_resp = httpx.post("https://loginapi.zimyo.work/user/login", json={
    "username": USERNAME,
    "password": PASSWORD,
}, headers={
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "app_lang": "en",
    "app_name": "Account",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
})

login_data = login_resp.json()
token = login_data['data']['token']
employee_id = login_data['data']['auth']['employee_id']
print(f"Token: {token[:20]}...")
print(f"Employee ID: {employee_id}")

# Try various bodies
bodies = [
    {},
    {"employee_id": employee_id},
    {"employee_id": str(employee_id)},
    {"id": employee_id},
    {"employeeId": employee_id},
    {"source": "WEB"},
    {"employee_id": employee_id, "source": "WEB"},
    {"id": employee_id, "source": "WEB"},
    {"employeeId": employee_id, "source": "WEB"},
]

for body in bodies:
    print(f"\nTesting body: {body}")
    resp = httpx.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json=body, headers={
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://zimyo.work",
        "referer": "https://zimyo.work/",
        "token": token,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
    }, cookies=login_resp.cookies)
    print(f"  Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Response: {resp.text[:200]}")
    else:
        print(f"  Success: {resp.json()}")
        break
