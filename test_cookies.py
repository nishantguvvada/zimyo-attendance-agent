import httpx

# Step 1: GET the zimyo.work homepage to get cookies
print("Step 1: GET https://zimyo.work/")
r1 = httpx.get("https://zimyo.work/", follow_redirects=True)
print(f"Status: {r1.status_code}")
print(f"Cookies after GET: {dict(r1.cookies)}")

# Step 2: POST to login with credentials
print("\nStep 2: POST login")
login_resp = httpx.post("https://loginapi.zimyo.work/user/login", json={
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
}, cookies=r1.cookies)  # Include cookies from step 1
print(f"Login status: {login_resp.status_code}")
login_data = login_resp.json()
token = login_data['data']['token']
employee_id = login_data['data']['auth']['employee_id']
print(f"Token: {token[:20]}...")
print(f"Employee ID: {employee_id}")
print(f"Cookies after login: {dict(login_resp.cookies)}")

# Combine cookies from step 1 and step 2 (login may not set new ones)
combined_cookies = {}
combined_cookies.update(r1.cookies)
combined_cookies.update(login_resp.cookies)
print(f"Combined cookies: {combined_cookies}")

# Step 3: Test attendance endpoint
print("\nStep 3: GET attendance? Actually POST check-clock-in-out-status")
att_resp = httpx.post("https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status", json={
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
}, cookies=combined_cookies)
print(f"Attendance status: {att_resp.status_code}")
print(f"Response: {att_resp.text}")
