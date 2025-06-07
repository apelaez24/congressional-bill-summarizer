# data_pipeline/test_api_connection.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOV_API_KEY")
BASE_URL = "https://api.congress.gov/v3/bill"

# Example: Get the 5 most recent Senate bills from the 118th Congress
params = {
    "api_key": API_KEY,
    "congress": 118,
    "chamber": "senate",
    "pageSize": 5
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    print("✅ API connection successful!")
    print("Sample bill titles:")
    for item in data.get("bills", []):
        print("-", item.get("title"))
else:
    print("❌ API request failed:", response.status_code)
    print(response.text)
