from zimyo_attendance.tools.zimyo_client import create_zimyo_client
import httpx

client = create_zimyo_client()
if client.login():
    print("Login successful")
    print(f"Token: {client._token}")
    print(f"Employee ID: {client._employee_id}")
    print(f"Session cookies: {client._session_cookies}")
    print(f"Auth headers: {client._auth_headers()}")

    # Now mimic the clock_in method but with detailed logging
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "EMP_ID": client._employee_id,
        "SOURCE": "Web",
        "DATE": date_str,
        "PLACE": "",
    }
    print(f"Payload: {payload}")
    url = f"{client.settings.zimyo_base_url}/apiv2/auth/hrms/clock-in-out"
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
        response.raise_for_status()
        # If we get here, the status was 2xx
        print("Request succeeded!")
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}")
        print(f"Response status: {e.response.status_code if e.response else 'No response'}")
        print(f"Response text: {e.response.text if e.response else 'No response'}")
    except Exception as e:
        print(f"Other error: {e}")
else:
    print("Login failed")