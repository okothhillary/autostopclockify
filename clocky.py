import os
import requests
from datetime import datetime, timezone

# Fetch API key, workspace, and user ID from environment variables
API_KEY = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID = os.getenv("USER_ID")

BASE_URL = "https://api.clockify.me/api/v1"

# Headers for all API requests
headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def stop_running_timer():
    # Get currently running time entry
    response = requests.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true", headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch running time entry.")
        print(response.text)
        return

    data = response.json()
    if not data:
        print("No running timer found.")
        return

    time_entry_id = data[0]['id']

    # Stop the timer by sending a PUT request
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{time_entry_id}"
    stop_response = requests.put(stop_url, headers=headers, json={"end": datetime.now(timezone.utc).isoformat()})

    if stop_response.status_code == 200:
        print("Timer stopped successfully.")
    else:
        print("Failed to stop the timer.")
        print(stop_response.text)

# Call the function
stop_running_timer()
