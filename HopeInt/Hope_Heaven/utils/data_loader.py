import json
from pathlib import Path

# Constants
DONATION_TYPES = [
    "food",
    "food_per_person", 
    "clothing", 
    "books", 
    "toys", 
    "school_supplies", 
    "hygiene_products",
    "medical_supplies"
]

AGE_GROUPS = ["infant", "1-4", "5-12", "13-18", "all"]

def load_orphanages():
    """Load and process orphanage data with proper error handling"""
    try:
        # Adjust path for correct root-relative location
        data_path = Path(__file__).resolve().parents[1] / "data" / "Orphanages_data.json"

        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found at: {data_path}")

        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict) or "orphanages" not in data:
            raise ValueError("Invalid JSON structure")

        processed = []
        for o in data["orphanages"]:
            if not all(k in o for k in ["id", "name", "address"]):
                continue
            
            # Ensure capacity is set
            if "capacity" not in o:
                o["capacity"] = max([need.get("quantity_needed", 0) for need in o.get("current_needs", [])] or 30)
            
            # Convert coordinates to tuple
            if "coordinates" in o.get("address", {}):
                try:
                    o["address"]["coordinates"] = tuple(o["address"]["coordinates"])
                except (TypeError, ValueError):
                    o["address"]["coordinates"] = (0, 0)
            
            processed.append(o)

        return processed

    except Exception as e:
        # Return the error string to let main app display it via Streamlit
        return f"ERROR: {str(e)}"

# Only load when running directly, not on import
if __name__ == "__main__":
    orphanages = load_orphanages()
    if isinstance(orphanages, str):
        print(orphanages)
    else:
        print(f"Loaded {len(orphanages)} orphanages.")

# If needed for other modules:
ORPHANAGES = load_orphanages()