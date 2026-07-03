from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.fda_tool import check_drug_interaction, get_drug_info
from agents.scheduler_agent import add_medication, get_todays_schedule, remove_medication
from agents.caregiver_agent import generate_caregiver_summary

DATA_PATH = "data/patient_data.json"

def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


# --- Tool functions for ADK ---

def tool_view_schedule() -> str:
    """Returns today's medication schedule for the patient."""
    data = load_data()
    result = get_todays_schedule(data)
    lines = [f"Schedule for {result['patient']} — {result['date']}"]
    for item in result["schedule"]:
        lines.append(f"  {item['time']} → {item['medication']} {item['dose']}")
    lines.append(f"Total doses: {result['total_doses']}")
    return "\n".join(lines)


def tool_safety_check(drug_name: str) -> str:
    """
    Checks if a drug is safe to add given current medications.
    Always call this before adding a new medication.
    """
    data = load_data()
    from agents.safety_agent import run_safety_check
    result = run_safety_check(drug_name, data)
    return result["message"]


def tool_add_medication(drug_name: str, dose: str, time: str) -> str:
    """
    Adds a medication to the patient schedule after safety check passes.
    Args:
        drug_name: Name of the medication
        dose: Dosage e.g. '10mg'
        time: Time in HH:MM format e.g. '08:00'
    """
    data = load_data()
    from agents.safety_agent import run_safety_check
    
    safety = run_safety_check(drug_name, data)
    if safety["status"] == "blocked":
        return safety["message"]
    
    result = add_medication(data, drug_name, dose, [time])
    save_data(data)
    return result["message"]


def tool_remove_medication(drug_name: str) -> str:
    """Removes a medication from the patient's schedule."""
    data = load_data()
    result = remove_medication(data, drug_name)
    save_data(data)
    return result["message"]


def tool_caregiver_summary() -> str:
    """
    Generates a privacy-filtered summary report for the caregiver.
    Never exposes raw patient data — only what patient has consented to share.
    """
    data = load_data()
    result = generate_caregiver_summary(data)
    return json.dumps(result["report"], indent=2)


# --- Build ADK Agent ---

medminder_agent = Agent(
    name="MedMinder",
    model="gemini-2.5-flash",
    description="AI medication coordination agent for safe medication management",
    instruction="""
    You are MedMinder, a warm and professional AI medication coordination assistant.
    
    You help elderly patients manage medications safely. You have tools to:
    - View today's medication schedule
    - Check if a new drug is safe (ALWAYS do this before adding)
    - Add medications to the schedule
    - Remove medications
    - Generate caregiver summary reports
    
    Rules:
    - ALWAYS run safety check before adding any medication
    - Explain interaction warnings in simple, non-scary language
    - Be warm and reassuring — users may be elderly or anxious
    - Never show raw JSON — translate everything to friendly text
    - For caregiver reports, remind user that privacy is protected
    """,
    tools=[
        FunctionTool(tool_view_schedule),
        FunctionTool(tool_safety_check),
        FunctionTool(tool_add_medication),
        FunctionTool(tool_remove_medication),
        FunctionTool(tool_caregiver_summary),
    ]
)