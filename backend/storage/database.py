import json
import os
from datetime import datetime

class Database:
    def __init__(self, file_path="storage/data.json"):
        self.file_path = file_path
        self._ensure_storage()
        self.data = self._load_data()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"incidents": [], "activity_counts": {}}, f)

    def _load_data(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def log_incident(self, alert_type, level, details=None):
        incident = {
            "timestamp": datetime.now().isoformat(),
            "alert": alert_type,
            "level": level,
            "details": details or {}
        }
        self.data["incidents"].append(incident)
        
        # Update activity counts
        event_key = alert_type.lower().replace(" ", "_")
        self.data["activity_counts"][event_key] = self.data["activity_counts"].get(event_key, 0) + 1
        
        self._save_data()
        return incident

    def get_all_incidents(self):
        return self.data["incidents"]

    def get_analytics(self):
        return {
            "total_incidents": len(self.data["incidents"]),
            "activity_counts": self.data["activity_counts"]
        }
