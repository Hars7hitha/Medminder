import json
from datetime import datetime

def add_medication(patient_data: dict, drug_name: str, dose: str, times: list) -> dict:
    """
    Adds a new medication to patient schedule after safety approval.
    """
    new_med = {
        "name": drug_name,
        "dose": dose,
        "times": times,
        "added_on": datetime.today().strftime("%Y-%m-%d")
    }
    patient_data["medications"].append(new_med)
    
    return {
        "status": "added",
        "medication": new_med,
        "message": f"✅ {drug_name} {dose} added to schedule at {', '.join(times)}"
    }


def get_todays_schedule(patient_data: dict) -> dict:
    """
    Returns today's full medication schedule sorted by time.
    """
    schedule = []
    for med in patient_data["medications"]:
        for time in med["times"]:
            schedule.append({
                "time": time,
                "medication": med["name"],
                "dose": med["dose"]
            })
    
    # Sort by time
    schedule.sort(key=lambda x: x["time"])
    
    return {
        "patient": patient_data["patient"]["name"],
        "date": datetime.today().strftime("%Y-%m-%d"),
        "schedule": schedule,
        "total_doses": len(schedule)
    }


def remove_medication(patient_data: dict, drug_name: str) -> dict:
    """
    Removes a medication from the schedule.
    """
    original_count = len(patient_data["medications"])
    patient_data["medications"] = [
        m for m in patient_data["medications"]
        if m["name"].lower() != drug_name.lower()
    ]
    
    if len(patient_data["medications"]) < original_count:
        return {
            "status": "removed",
            "message": f"✅ {drug_name} removed from schedule."
        }
    
    return {
        "status": "not_found",
        "message": f"❌ {drug_name} not found in current medications."
    }