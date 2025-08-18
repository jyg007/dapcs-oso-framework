import requests
import json

# URL of your API server
API_URL = "http://localhost:8080/custody"

# Example metadata value (adjust as needed)
metadata_value = {"source": "custody_api"}

# Query the API
response = requests.get(API_URL)
response.raise_for_status()  # raise exception if request failed

# Parse JSON array
data = response.json()

# Loop through each item and generate a Document snippet
for i, item in enumerate(data, start=1):
    doc_id = f"doc{i}"  # generate unique document id
    content = item.get("content", "")
    
    snippet = f"""case "frontend":
    doc = V1_3.Document(
        id="{doc_id}",
        content="{content}",
        metadata=metadata_value,
    )"""
    
    print(snippet)

