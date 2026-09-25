import httpx
from datetime import datetime

# Login first
print('Logging in...')
login_resp = httpx.post(
    'https://loginapi.zimyo.work/user/login',
    json={'username': 'nishant.guvvada@idctechnologies.com', 'password': 'okhxckfzr0'},
    headers={
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'app_lang': 'en',
        'app_name': 'Account',
        'content-type': 'application/json',
        'origin': 'https://zimyo.work',
        'referer': 'https://zimyo.work/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
    }
)
if login_resp.status_code != 200:
    print('Login failed:', login_resp.text)
    exit(1)
login_data = login_resp.json()
token = login_data['data']['token']
employee_id = login_data['data']['auth']['employee_id']
print(f'Employee ID: {employee_id}')

# Prepare payload for today
date_str = datetime.now().strftime('%Y-%m-%d')
payload = {
    'EMP_ID': employee_id,
    'SOURCE': 'Web',
    'DATE': date_str,
    'PLACE': '',
}
print(f'Payload: {payload}')

# Headers from the successful request in the initial message (as seen in the user's first block)
headers = {
    'accept': 'application/json',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'access-control-allow-origin': 'https://www.zimyo.work',
    'content-type': 'application/json',
    'origin': 'https://zimyo.work',
    'priority': 'u=1, i',
    'referer': 'https://zimyo.work/',
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'token': token,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
}
cookies = login_resp.cookies

print('\\n--- Sending clock-in request first ---')
resp_in = httpx.post(
    'https://www.zimyo.work/apiv2/auth/hrms/clock-in-out',
    headers=headers,
    cookies=cookies,
    json=payload,
)
print(f'Clock-in Status: {resp_in.status_code}')
print(f'Clock-in Response: {resp_in.text}')

print('\\n--- Sending clock-out request second ---')
resp_out = httpx.post(
    'https://www.zimyo.work/apiv2/auth/hrms/clock-in-out',
    headers=headers,
    cookies=cookies,
    json=payload,
)
print(f'Clock-out Status: {resp_out.status_code}')
print(f'Clock-out Response: {resp_out.text}')