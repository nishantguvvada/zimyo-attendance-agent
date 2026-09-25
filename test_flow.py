import httpx

client = httpx.Client()

print("Step 1: GET https://zimyo.work/")
r1 = client.get("https://zimyo.work/", follow_redirects=True)
print(f"  Status: {r1.status_code}")
print(f"  Cookies: {dict(client.cookies)}")

print("\nStep 2: POST login")
login_resp = client.post("https://loginapi.zimyo.work/user/login", json={
    "username": "nishant.guvvada@idctechnologies.com",
    "password": "okhxckfzr0",
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
print(f"  Status: {login_resp.status_code}")
login_data = login_resp.json()
token = login_data['data']['token']
employee_id = login_data['data']['auth']['employee_id']
print(f"  Token: {token[:20]}...")
print(f"  Employee ID: {employee_id}")
print(f"  Cookies after login: {dict(client.cookies)}")

print("\nStep 3: GET dashboard")
dashboard_resp = client.get("https://www.zimyo.work/ess/dashboard/my-dashboard", headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://zimyo.work/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
})
print(f"  Status: {dashboard_resp.status_code}")
print(f"  Cookies after dashboard: {dict(client.cookies)}")

print("\nStep 4: POST attendance")
att_resp = client.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json={
    "employee_id": employee_id,
    "source": "WEB",
}, headers={
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://zimyo.work",
    "referer": "https://zimyo.work/",
    "token": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
})
print(f"  Status: {att_resp.status_code}")
print(f"  Response: {att_resp.text[:500]}")
