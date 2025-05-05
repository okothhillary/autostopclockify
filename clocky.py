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
    response = requests.get(
        f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true",
        headers=headers
    )
    
    if response.status_code != 200:
        print("Failed to fetch running time entry.")
        print(response.text)
        return

    data = response.json()
    if not data:
        print("No running timer found.")
        return

    time_entry = data[0]
    time_entry_id = time_entry['id']
    start_time = time_entry['timeInterval']['start']

    # Ensure both times are in the expected ISO format (ending in Z)
    end_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{time_entry_id}"
    payload = {
        "start": start_time,
        "end": end_time
    }

    stop_response = requests.put(stop_url, headers=headers, json=payload)

    if stop_response.status_code == 200:
        print("Timer stopped successfully.")
    else:
        print("Failed to stop the timer.")
        print("Payload:", payload)
        print(stop_response.text)

# Call the function
stop_running_timer()
