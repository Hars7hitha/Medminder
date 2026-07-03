from datetime import datetime

def generate_caregiver_summary(patient_data: dict) -> dict:
    """
    Generates a filtered summary for caregiver.
    Respects access_level — never exposes raw patient data.
    """
    access_level = patient_data["caregiver"]["access_level"]
    patient = patient_data["patient"]
    meds = patient_data["medications"]
    
    # Security: summary_only = no dosage details, no conditions
    if access_level == "summary_only":
        return {
            "caregiver": patient_data["caregiver"]["name"],
            "access_level": "summary_only",
            "report": {
                "patient_id": patient["id"],  # never expose real name
                "date": datetime.today().strftime("%Y-%m-%d"),
                "total_medications": len(meds),
                "next_dose": _get_next_dose(meds),
                "alerts": [],
                "note": "Full details restricted. Patient controls access."
            }
        }
    
    # full_access level
    return {
        "caregiver": patient_data["caregiver"]["name"],
        "access_level": "full_access",
        "report": {
            "patient_name": patient["name"],
            "age": patient["age"],
            "conditions": patient["conditions"],
            "date": datetime.today().strftime("%Y-%m-%d"),
            "medications": [
                {"name": m["name"], "dose": m["dose"], "times": m["times"]}
                for m in meds
            ],
            "next_dose": _get_next_dose(meds),
            "alerts": []
        }
    }


def _get_next_dose(meds: list) -> str:
    """Finds the next upcoming dose time from now."""
    from datetime import datetime
    now = datetime.now().strftime("%H:%M")
    
    all_times = []
    for med in meds:
        for t in med["times"]:
            all_times.append((t, med["name"], med["dose"]))
    
    all_times.sort(key=lambda x: x[0])
    
    upcoming = [t for t in all_times if t[0] > now]
    if upcoming:
        t, name, dose = upcoming[0]
        return f"{name} {dose} at {t}"
    
    return "No more doses today"