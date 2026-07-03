import json
import os
from agents.safety_agent import run_safety_check
from agents.scheduler_agent import add_medication, get_todays_schedule, remove_medication
from agents.caregiver_agent import generate_caregiver_summary
from security.audit_log import log_action

DATA_PATH = "data/patient_data.json"

def load_patient_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_patient_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def handle_intent(intent: str, params: dict = {}) -> str:
    patient_data = load_patient_data()

    if intent == "view_schedule":
        result = get_todays_schedule(patient_data)
        log_action("view_schedule", {"patient": patient_data["patient"]["id"]})
        return format_schedule(result)

    elif intent == "add_med":
        drug = params.get("drug")
        dose = params.get("dose")
        times = params.get("times", ["08:00"])

        safety = run_safety_check(drug, patient_data)
        log_action("safety_check", {"drug": drug, "result": safety["status"]})

        if safety["status"] == "blocked":
            log_action("add_med_blocked", {"drug": drug})
            return f"{safety['message']}\nConflicts:\n" + "\n".join(
                [f"  - With {i['conflicting_drug']}: {i['warning'][:100]}..."
                 for i in safety["interactions"]]
            )

        result = add_medication(patient_data, drug, dose, times)
        save_patient_data(patient_data)
        log_action("add_med_approved", {"drug": drug, "dose": dose, "times": times})
        return result["message"]

    elif intent == "remove_med":
        drug = params.get("drug")
        result = remove_medication(patient_data, drug)
        save_patient_data(patient_data)
        log_action("remove_med", {"drug": drug, "result": result["status"]})
        return result["message"]

    elif intent == "caregiver_summary":
        result = generate_caregiver_summary(patient_data)
        log_action("caregiver_summary_accessed", {
            "access_level": patient_data["caregiver"]["access_level"],
            "caregiver": patient_data["caregiver"]["name"]
        })
        return json.dumps(result["report"], indent=2)

    elif intent == "safety_check":
        drug = params.get("drug")
        result = run_safety_check(drug, patient_data)
        log_action("safety_check_standalone", {"drug": drug, "result": result["status"]})
        return result["message"]

    return "❌ Unknown intent."


def format_schedule(schedule_data: dict) -> str:
    lines = [f"📋 Schedule for {schedule_data['patient']} — {schedule_data['date']}"]
    for item in schedule_data["schedule"]:
        lines.append(f"  {item['time']} → {item['medication']} {item['dose']}")
    lines.append(f"Total doses today: {schedule_data['total_doses']}")
    return "\n".join(lines)