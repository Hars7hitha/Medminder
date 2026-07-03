import json
import os
from datetime import datetime

LOG_PATH = "security/audit_log.json"

def log_action(action: str, details: dict, user: str = "patient_001"):
    """
    Logs every agent action with timestamp.
    Demonstrates security accountability in the system.
    """
    os.makedirs("security", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "action": action,
        "details": details
    }
    
    # Load existing log
    logs = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    
    logs.append(entry)
    
    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)
    
    return entry


def get_audit_log() -> list:
    """Returns full audit log."""
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        try:
            return json.load(f)
        except:
            return []