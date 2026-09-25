import httpx
from zimyo_attendance.config.settings import get_settings
from zimyo_attendance.tools.zimyo_client import ZimyoClient

settings = get_settings()
print(f"Zimyo base URL from settings: {settings.zimyo_base_url}")

# Login using the client's login method to get token and cookies
client = ZimyoClient()
if client.login():
    print("Login successful")
    print(f"Token: {client._token}")
    print(f"Employee ID: {client._employee_id}")
    print(f"Session cookies: {client._session_cookies}")
    print(f"Auth headers: {client._auth_headers()}")

    # Now access ESS dashboard to establish proper session for the main domain (as in login method)
    try:
        dashboard_url = "https://zimyo.work/ess/dashboard/my-dashboard"
        dashboard_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://zimyo.work/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        }
        client.client.get(dashboard_url, headers=dashboard_headers)
        # Update session cookies after dashboard visit
        client._session_cookies = dict(client.client.cookies)
        print(f"Updated session cookies after dashboard: {client._session_cookies}")
    except Exception as e:
        print(f"Dashboard visit failed: {e}")

    # Now make a request using the same method as clock_in but print more details
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "EMP_ID": client._employee_id,
        "SOURCE": "Web",
        "DATE": date_str,
        "PLACE": "",
    }
    print(f"Payload: {payload}")
    url = f"{settings.zimyo_base_url}/apiv2/auth/hrms/clock-in-out"
    print(f"URL: {url}")
    headers = client._auth_headers()
    print(f"Headers: {headers}")
    cookies = client._session_cookies
    print(f"Cookies: {cookies}")

    try:
        response = client.client.post(
            url,
            json=payload,
            headers=headers,
            cookies=cookies,
        )
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
else:
    print("Login failed")