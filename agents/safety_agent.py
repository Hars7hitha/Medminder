import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now importing from MCP server tools directly
from mcp_server.fda_tool import check_drug_interaction, get_drug_info

def run_safety_check(new_drug: str, patient_data: dict) -> dict:
    """
    Checks new drug against all existing medications for interactions.
    Calls MCP server tools for drug validation and interaction checking.
    """
    existing_meds = [m["name"] for m in patient_data["medications"]]
    interactions_found = []

    # Step 1: Validate drug exists via MCP tool
    drug_info = get_drug_info(new_drug)
    if not drug_info["found"]:
        return {
            "status": "warning",
            "drug": new_drug,
            "message": f"⚠️ Drug '{new_drug}' not recognized. Please verify the name.",
            "interactions": []
        }

    # Step 2: Check against every existing med via MCP tool
    for existing_med in existing_meds:
        result = check_drug_interaction(new_drug, existing_med)
        if result.get("interaction_found"):
            interactions_found.append({
                "conflicting_drug": existing_med,
                "warning": result["warning"]
            })

    if interactions_found:
        return {
            "status": "blocked",
            "drug": new_drug,
            "message": f"⚠️ {new_drug} has interactions with existing medications. Addition blocked.",
            "interactions": interactions_found
        }

    return {
        "status": "approved",
        "drug": new_drug,
        "message": f"✅ {new_drug} cleared. No interactions found.",
        "interactions": []
    }