import json
import os
import requests

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "catalog.json")
CATALOG_URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"

def fetch_shl_catalog():
    print(f"Fetching SHL catalog from {CATALOG_URL}...")
    try:
        response = requests.get(CATALOG_URL, timeout=15)
        response.raise_for_status()
        
        # Use strict=False to ignore unescaped control characters in the JSON text
        raw_data = json.loads(response.text, strict=False)
        
        # Map the real JSON fields to our app's expected format
        processed_catalog = []
        for item in raw_data:
            # SHL's JSON uses "link" instead of "url", and "keys" instead of category
            keys = item.get("keys", [])
            test_type = keys[0] if keys else "Unknown"
            
            processed_catalog.append({
                "name": item.get("name", ""),
                "url": item.get("link", ""),
                "description": item.get("description", ""),
                "category": test_type,
                "test_type": test_type,
                "skills_measured": keys
            })
            
        return processed_catalog

    except Exception as e:
        print(f"Failed to fetch catalog: {e}")
        return []

if __name__ == "__main__":
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    catalog = fetch_shl_catalog()
    
    if catalog:
        with open(RAW_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=4)
        print(f"Saved {len(catalog)} assessments to {RAW_DATA_PATH}")
    else:
        print("Catalog fetch failed. Data not updated.")
