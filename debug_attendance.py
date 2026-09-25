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

print(f"Login status: {login_resp.status_code}")
login_data = login_resp.json()
token = login_data['data']['token']
employee_id = login_data['data']['auth']['employee_id']
print(f"Token: {token[:20]}...")
print(f"Employee ID: {employee_id}")
cookies = login_resp.cookies
print(f"Cookies: {dict(cookies)}")

# Now test attendance endpoint
url = "https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status"
payload = {
    "employee_id": employee_id,
    "source": "WEB",
}
headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "token": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
}

print(f"\nRequest URL: {url}")
print(f"Request payload: {payload}")
print(f"Request headers: {headers}")
print(f"Request cookies: {dict(cookies)}")

resp = httpx.post(url, json=payload, headers=headers, cookies=cookies)
print(f"\nResponse status: {resp.status_code}")
print(f"Response headers: {resp.headers}")
print(f"Response body: {resp.text}")
