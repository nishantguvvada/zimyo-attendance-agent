"""JSON file storage for attendance records."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


class JSONStorage:
    """Thread-safe JSON file storage for attendance data."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create file with default structure if it doesn't exist."""
        if not self.file_path.exists():
            default_data = {
                "records": [],
                "last_updated": None,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self._write(default_data)
    
    def _read(self) -> Dict[str, Any]:
        """Read data from JSON file."""
        with self._lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {"records": [], "last_updated": None, "metadata": {}}
    
    def _write(self, data: Dict[str, Any]) -> None:
        """Write data to JSON file atomically."""
        with self._lock:
            data["last_updated"] = datetime.now().isoformat()
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(self.file_path)
    
    def add_record(self, record: Dict[str, Any]) -> None:
        """Add a new attendance record."""
        data = self._read()
        record["id"] = len(data["records"]) + 1
        record["timestamp"] = datetime.now().isoformat()
        data["records"].append(record)
        self._write(data)
    
    def get_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get attendance records, optionally limited."""
        data = self._read()
        records = data["records"]
        if limit:
            return records[-limit:]
        return records
    
    def get_latest_record(self) -> Optional[Dict[str, Any]]:
        """Get the most recent attendance record."""
        data = self._read()
        records = data["records"]
        return records[-1] if records else None
    
    def get_today_record(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get today's attendance record if exists."""
        data = self._read()
        for record in reversed(data["records"]):
            if record.get("date") == date_str:
                return record
        return None
    
    def update_record(self, record_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing record by ID."""
        data = self._read()
        for record in data["records"]:
            if record.get("id") == record_id:
                record.update(updates)
                record["updated_at"] = datetime.now().isoformat()
                self._write(data)
                return True
        return False
    
    def clear_all(self) -> None:
        """Clear all records (for testing)."""
        self._write({"records": [], "last_updated": None, "metadata": {}})


def create_storage(file_path: Path) -> JSONStorage:
    """Factory function to create JSONStorage instance."""
    return JSONStorage(file_path)