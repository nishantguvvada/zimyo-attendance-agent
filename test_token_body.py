import httpx
import json

# Use the token from the user's log (they provided a full token)
token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjdkOWIwYjNmLWVmNTctNDI1MS04ZjVmLTcwMjIzZjA1NGE4OSJ9.eyJjYWxsYmFja191cmwiOiJodHRwczovL3ppbXlvLndvcmsvIiwic2VydmljZSI6IkFjY291bnQiLCJyZW1vdGVfYWRkciI6IjIyMy4xOTAuODQuMTUiLCJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRWRnZSIsImRldmljZSI6IldlYiIsImRldmljZV90eXBlIjoiV2ViIiwic2FsdCI6IjY3OTY5YmY1LWQ5MjktNGViZS1hZTViLTNhNTNmM2U1NjEwMyIsImlhdCI6MTc4Nzk4MzAyNH0.PH4rdln99LTxjLnj79-vEfVn7HWtJWFnSOh-pKWaxSZMyn2Uu0OhQTsdTStmgnZdl9s_3evuxBo5UCZd6fwKeg"

url = "https://www.zimyo.work/apiv2/auth/hrms/check-clock-in-out-status"

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

# Try various payloads
payloads = [
    {},
    {"employee_id": 768646},
    {"employee_id": "768646"},
    {"id": 768646},
    {"employeeId": 768646},
    {"source": "WEB"},
    {"employee_id": 768646, "source": "WEB"},
    {"id": 768646, "source": "WEB"},
    {"employeeId": 768646, "source": "WEB"},
    {"employee_id": 768646, "type": "IN"},
    {"employee_id": 768646, "type": "OUT"},
    {"employeeId": 768646, "type": "IN"},
    {"employeeId": 768646, "type": "OUT"},
    {"employee_id": 768646, "source": "web"},  # lower case
    {"employee_id": 768646, "source": "Web"},
    {"employee_id": 768646, "source": "WEB", "timestamp": ""},
]

for payload in payloads:
    print(f"\nTesting payload: {payload}")
    resp = httpx.post(url, json=payload, headers=headers)
    print(f"  Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Response: {resp.text[:200]}")
    else:
        print(f"  Success! Response: {resp.json()}")
        break
