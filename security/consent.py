import json

DATA_PATH = "data/patient_data.json"

def get_consent_level() -> str:
    """Returns current caregiver access level."""
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data["caregiver"]["access_level"]


def set_consent_level(level: str) -> dict:
    """
    Patient controls caregiver access.
    Levels: 'summary_only' or 'full_access'
    """
    if level not in ["summary_only", "full_access"]:
        return {"status": "error", "message": "Invalid level. Use 'summary_only' or 'full_access'"}
    
    with open(DATA_PATH) as f:
        data = json.load(f)
    
    old_level = data["caregiver"]["access_level"]
    data["caregiver"]["access_level"] = level
    
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    return {
        "status": "updated",
        "previous": old_level,
        "current": level,
        "message": f"✅ Caregiver access updated to '{level}'"
    }