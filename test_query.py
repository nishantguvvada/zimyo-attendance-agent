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

# Try with query parameter
url = f"https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status?employee_id={employee_id}"
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
resp = httpx.post(url, headers=headers, json={})  # empty JSON body
print(f"Query param status: {resp.status_code}")
print(f"Response: {resp.text}")

# Try with source in query too
url2 = f"https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status?employee_id={employee_id}&source=WEB"
resp2 = httpx.post(url2, headers=headers, json={})
print(f"Query param with source status: {resp2.status_code}")
print(f"Response: {resp2.text}")
