import httpx
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv("ZIMYO_USERNAME")
PASSWORD = os.getenv("ZIMYO_PASSWORD")

# Step 1: Login to get a fresh token and cookies
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
print(f"Got token: {token[:20]}...")
print(f"Employee ID: {employee_id}")

# Step 2: Visit dashboard to get cookies (if needed)
print("\nVisiting dashboard to get cookies...")
dashboard_resp = httpx.get("https://www.zimyo.work/ess/dashboard/my-dashboard", headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://zimyo.work/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
}, cookies=login_resp.cookies)
print(f"Dashboard status: {dashboard_resp.status_code}")
print(f"Cookies after dashboard: {dict(dashboard_resp.cookies)}")

# Step 3: Try the exact request from the user's curl (without cookies, just token header)
print("\n--- Trying exact curl request (no cookies) ---")
resp1 = httpx.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json={
    "employee_id": employee_id,
    "source": "WEB",
}, headers={
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "token": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
})
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text}")

# Step 4: Try with cookies from dashboard
print("\n--- Trying with cookies from dashboard ---")
resp2 = httpx.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json={
    "employee_id": employee_id,
    "source": "WEB",
}, headers={
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "token": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
}, cookies=dashboard_resp.cookies)
print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text}")

# Step 5: Try with cookies from login (if any) and token
print("\n--- Trying with cookies from login ---")
resp3 = httpx.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json={
    "employee_id": employee_id,
    "source": "WEB",
}, headers={
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "token": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
}, cookies=login_resp.cookies)
print(f"Status: {resp3.status_code}")
print(f"Response: {resp3.text}")
