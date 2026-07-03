import requests

def check_drug_interaction(drug1: str, drug2: str) -> dict:
    """
    Checks for known interactions between two drugs using openFDA API.
    Returns interaction info or a safe signal.
    """
    url = "https://api.fda.gov/drug/label.json"
    
    # Search for drug1's label which lists interactions
    params = {
        "search": f'warnings:"{drug2}" AND openfda.brand_name:"{drug1}"',
        "limit": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            warnings = data["results"][0].get("warnings", ["No specific warning text found"])
            return {
                "interaction_found": True,
                "drug1": drug1,
                "drug2": drug2,
                "warning": warnings[0][:300]  # trim long text
            }
        else:
            # fallback: search reverse
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


def get_drug_info(drug_name: str) -> dict:
    """
    Fetches basic drug info from RxNorm API.
    """
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json"
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
        return {"drug_name": drug_name, "found": False, "error": str(e)}