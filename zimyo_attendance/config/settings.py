"""Configuration management for Zimyo Attendance Logger."""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Zimyo credentials
    zimyo_username: str = Field(default="", alias="ZIMYO_USERNAME")
    zimyo_password: str = Field(default="", alias="ZIMYO_PASSWORD")
    zimyo_base_url: str = Field(default="https://zimyo.work", alias="ZIMYO_BASE_URL")
    zimyo_employee_id: str = Field(default="768646", alias="ZIMYO_EMPLOYEE_ID")
    
    # Attendance rules
    clock_in_window_start: str = Field(default="08:55", alias="CLOCK_IN_WINDOW_START")
    clock_in_window_end: str = Field(default="09:05", alias="CLOCK_IN_WINDOW_END")
    clock_out_window_start: str = Field(default="16:55", alias="CLOCK_OUT_WINDOW_START")
    clock_out_window_end: str = Field(default="17:10", alias="CLOCK_OUT_WINDOW_END")
    timezone: str = Field(default="Asia/Dubai", alias="TIMEZONE")
    
    # Storage
    storage_path: Path = Field(default=Path("data/attendance.json"), alias="STORAGE_PATH")
    
    # GitHub Actions / scheduling
    github_actions: bool = Field(default=False, alias="GITHUB_ACTIONS")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()


def get_settings() -> Settings:
    """Get application settings singleton."""
    return settings