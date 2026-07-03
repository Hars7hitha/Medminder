from mcp.server.fastmcp import FastMCP
import requests

# Initialize MCP server
mcp = FastMCP("MedMinder Drug Safety Server")


@mcp.tool()
def check_drug_interaction(drug1: str, drug2: str) -> dict:
    """
    Checks for known interactions between two drugs using openFDA API.
    Use this before adding any new medication to a patient's schedule.
    
    Args:
        drug1: The new drug being considered
        drug2: An existing drug in the patient's current medications
    
    Returns:
        dict with interaction_found (bool) and warning (str) if found
    """
    url = "https://api.fda.gov/drug/label.json"
    
    params = {
        "search": f'warnings:"{drug2}" AND openfda.brand_name:"{drug1}"',
        "limit": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            warnings = data["results"][0].get("warnings", ["Potential interaction found"])
            return {
                "interaction_found": True,
                "drug1": drug1,
                "drug2": drug2,
                "warning": warnings[0][:300]
            }
        
        # Reverse search
        params["search"] = f'warnings:"{drug1}" AND openfda.brand_name:"{drug2}"'
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            warnings = data["results"][0].get("warnings", [])
            return {
                "interaction_found": True,
                "drug1": drug1,
                "drug2": drug2,
                "warning": warnings[0][:300] if warnings else "Potential interaction found"
            }
        
        return {
            "interaction_found": False,
            "drug1": drug1,
            "drug2": drug2,
            "warning": None
        }
    
    except Exception as e:
        return {
            "interaction_found": False,
            "drug1": drug1,
            "drug2": drug2,
            "error": str(e)
        }


@mcp.tool()
def get_drug_info(drug_name: str) -> dict:
    """
    Fetches basic drug info and validates drug name using RxNorm API.
    Always call this first to verify a drug exists before checking interactions.
    
    Args:
        drug_name: Name of the drug to look up
    
    Returns:
        dict with drug_name, rxcui (RxNorm ID), and found (bool)
    """
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    params = {"name": drug_name}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        rxcui = data.get("idGroup", {}).get("rxnormId", [None])[0]
        
        return {
            "drug_name": drug_name,
            "rxcui": rxcui,
            "found": rxcui is not None
        }
    except Exception as e:
        return {
            "drug_name": drug_name,
            "found": False,
            "error": str(e)
        }


@mcp.tool()
def get_drug_interactions_list(drug_name: str) -> dict:
    """
    Gets full list of known interactions for a drug from RxNorm.
    Useful for comprehensive safety checking.
    
    Args:
        drug_name: Name of the drug
    
    Returns:
        dict with drug_name and list of known interacting drugs
    """
    # First get rxcui
    rxcui_url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    try:
        r = requests.get(rxcui_url, params={"name": drug_name}, timeout=10)
        rxcui = r.json().get("idGroup", {}).get("rxnormId", [None])[0]
        
        if not rxcui:
            return {"drug_name": drug_name, "found": False, "interactions": []}
        
        # Get interactions
        interact_url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json"
        r2 = requests.get(interact_url, params={"rxcui": rxcui}, timeout=10)
        data = r2.json()
        
        interactions = []
        groups = data.get("interactionTypeGroup", [])
        for group in groups:
            for itype in group.get("interactionType", []):
                for pair in itype.get("interactionPair", []):
                    desc = pair.get("description", "")
                    drugs = [c.get("minConceptItem", {}).get("name", "") 
                            for c in pair.get("interactionConcept", [])]
                    interactions.append({
                        "drugs": drugs,
                        "description": desc
                    })
        
        return {
            "drug_name": drug_name,
            "rxcui": rxcui,
            "found": True,
            "interactions": interactions[:10]  # top 10
        }
    
    except Exception as e:
        return {"drug_name": drug_name, "found": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")