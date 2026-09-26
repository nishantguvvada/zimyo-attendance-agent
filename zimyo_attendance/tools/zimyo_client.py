"""Zimyo API client for authentication and attendance operations."""
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel

from zimyo_attendance.config.settings import get_settings


class ZimyoAuthResponse(BaseModel):
    """Zimyo login response model."""
    error: bool
    code: int
    message: str
    timestamp: int
    data: Optional[Dict[str, Any]] = None


class ZimyoAttendanceResponse(BaseModel):
    """Zimyo attendance response model."""
    error: bool
    code: int
    message: str
    time: int
    data: Dict[str, Any]


class AttendanceData(BaseModel):
    """Parsed attendance data from Zimyo."""
    date: str
    date_format: str
    total_punch_time: str
    current_time: str
    in_out_status: str
    shift_end: str
    timezone: str
    web_punchin: str
    enable_selfie_attendance: int
    shift_name: str
    shift_code: str
    day_start_time: str
    day_end_time: str
    shift_json: Dict[str, Any]


class ZimyoClient:
    """Client for interacting with Zimyo API."""

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.Client(
            base_url=self.settings.zimyo_base_url,
            timeout=30.0,
            follow_redirects=True,
        )
        self._session_cookies: Dict[str, str] = {}
        self._authenticated = False
        self._token: Optional[str] = None
        self._employee_id: Optional[int] = None

    def login(self) -> bool:
        """Authenticate with Zimyo portal."""
        # Login API is on a different subdomain
        login_url = "https://loginapi.zimyo.work/user/login"

        payload = {
            "username": self.settings.zimyo_username,
            "password": self.settings.zimyo_password,
        }

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US,en;q=0.9",
            "app_lang": "en",
            "app_name": "Account",
            "content-type": "application/json",
            "origin": "https://zimyo.work",
            "referer": "https://zimyo.work/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        }

        try:
            response = self.client.post(login_url, json=payload, headers=headers)
            response.raise_for_status()

            auth_data = ZimyoAuthResponse(**response.json())

            if not auth_data.error and auth_data.code == 200:
                # Store token and employee_id from response
                self._token = auth_data.data.get("token")
                auth_info = auth_data.data.get("auth", {})
                self._employee_id = auth_info.get("employee_id")
                self._authenticated = True
                # Note: cookies from login are already in self.client.cookies

                # Now access ESS dashboard to establish proper session for the main domain
                # This is needed because login API is on a different subdomain
                try:
                    dashboard_url = "https://zimyo.work/ess/dashboard/my-dashboard"
                    dashboard_headers = {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "accept-encoding": "gzip, deflate, br",
                        "accept-language": "en-US,en;q=0.9",
                        "referer": "https://zimyo.work/",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
                    }
                    self.client.get(dashboard_url, headers=dashboard_headers)
                    # cookies from dashboard are now also in self.client.cookies
                except Exception:
                    # If dashboard fails, we still have the token from login
                    pass

                return True
            else:
                print(f"Login failed: {auth_data.message}")
                return False

        except httpx.HTTPError as e:
            print(f"Login HTTP error: {e}")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def _auth_headers(self) -> Dict[str, str]:
        """Headers for authenticated requests."""
        if not self._token:
            return {}
        return {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "access-control-allow-origin": "https://www.zimyo.work",
            "content-type": "application/json",
            "origin": "https://zimyo.work",
            "priority": "u=1, i",
            "referer": "https://zimyo.work/",
            "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "token": self._token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        }

    def get_attendance_status(self) -> Optional[AttendanceData]:
        """Fetch current attendance status using check-clock-in-out-status."""
        if not self._authenticated:
            if not self.login():
                return None

        url = f"{self.settings.zimyo_base_url}/apiv2/auth/hrms/check-clock-in-out-status"
        # Use the working payload format: EMP_ID, SOURCE, DATE, PLACE
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "EMP_ID": self._employee_id,
            "SOURCE": "Web",
            "DATE": date_str,
            "PLACE": "",
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._auth_headers(),
                # Cookies are handled by the client's cookie jar
            )
            response.raise_for_status()
            data = ZimyoAttendanceResponse(**response.json())
            if not data.error and data.code == 200:
                att = data.data.get("attendance", {})
                shift_json = att.get("SHIFT_JSON", {})
                return AttendanceData(
                    date=att.get("DATE", ""),
                    date_format=att.get("DATE_FORMAT", ""),
                    total_punch_time=att.get("TOTAL_PUNCH_TIME", ""),
                    current_time=att.get("CURRENT_TIME", ""),
                    in_out_status=att.get("IN_OUT_STATUS", ""),
                    shift_end=att.get("SHIFT_END", ""),
                    timezone=att.get("TIMEZONE", "Asia/Dubai"),
                    web_punchin=att.get("WEB_PUNCHIN", "Yes"),
                    enable_selfie_attendance=att.get("ENABLE_SELFIE_ATTENDANCE", 1),
                    shift_name=shift_json.get("SHIFT_NAME", ""),
                    shift_code=shift_json.get("SHIFT_CODE", ""),
                    day_start_time=shift_json.get("DAY_START_TIME", "09:00 AM"),
                    day_end_time=shift_json.get("DAY_END_TIME", "06:00 PM"),
                    shift_json=shift_json,
                )
            else:
                print(f"Failed to get attendance: {data.message}")
                return None

        except httpx.HTTPStatusError as e:
            # Try to parse error response for 422
            try:
                error_data = e.response.json()
                print(f"Attendance fetch failed ({e.response.status_code}): {error_data.get('message', 'Unknown error')}")
            except Exception:
                print(f"Attendance fetch HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Attendance fetch error: {e}")
            return None
    def clock_in(self) -> bool:
        """Record clock-in attendance."""
        if not self._authenticated:
            if not self.login():
                return False

        url = f"{self.settings.zimyo_base_url}/apiv2/auth/hrms/clock-in-out"
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "EMP_ID": self._employee_id,
            "SOURCE": "Web",
            "DATE": date_str,
            "PLACE": "",
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._auth_headers(),
            )
            response.raise_for_status()
            data = ZimyoAttendanceResponse(**response.json())
            if not data.error and data.code == 200:
                print(f"Clock-in successful: {data.message}")
                return True
            else:
                print(f"Clock-in failed: {data.message}")
                return False
        except httpx.HTTPStatusError as e:
            try:
                ed = e.response.json()
                print(f"Clock-in failed ({e.response.status_code}): {ed.get("message", "Unknown error")}")
            except Exception:
                print(f"Clock-in HTTP error: {e}")
            return False
        except Exception as e:
            print(f"Clock-in request failed: {e}")
            return False

    def clock_out(self) -> bool:
        """Record clock-out attendance."""
        if not self._authenticated:
            if not self.login():
                return False

        url = f"{self.settings.zimyo_base_url}/apiv2/auth/hrms/clock-in-out"
        # Use the payload format that works: EMP_ID, SOURCE, DATE, PLACE
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "EMP_ID": self._employee_id,
            "SOURCE": "Web",
            "DATE": date_str,
            "PLACE": "",
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._auth_headers(),
                # Cookies are handled by the client's cookie jar
            )
            response.raise_for_status()
            data = ZimyoAttendanceResponse(**response.json())
            if not data.error and data.code == 200:
                print(f"Clock-out successful: {data.message}")
                return True
            else:
                print(f"Clock-out failed: {data.message}")
                return False
        except httpx.HTTPStatusError as e:
            # Try to parse error response for 422
            try:
                error_data = e.response.json()
                print(f"Clock-out failed ({e.response.status_code}): {error_data.get('message', 'Unknown error')}")
            except Exception:
                print(f"Clock-out HTTP error: {e}")
            return False
        except Exception as e:
            print(f"Clock-out request failed: {e}")
            return False

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_zimyo_client() -> ZimyoClient:
    """Factory function to create ZimyoClient instance."""
    return ZimyoClient()