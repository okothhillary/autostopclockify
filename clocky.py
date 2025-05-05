import os
import requests
from datetime import datetime, timezone
from dateutil.parser import isoparse  # ensure python-dateutil is installed

API_KEY = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID = os.getenv("USER_ID")

BASE_URL = "https://api.clockify.me/api/v1"

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def stop_running_timer():
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true"
    response = requests.get(url, headers=headers)

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
    
    # Properly format the start time
    start_time_raw = time_entry['timeInterval']['start']
    start_time = isoparse(start_time_raw).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Properly format the end time
    end_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    project_id = time_entry.get('projectId')

    stop_payload = {
        "start": start_time,
        "end": end_time
    }

    if project_id:
        stop_payload["projectId"] = project_id

    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{time_entry_id}"
    stop_response = requests.put(stop_url, headers=headers, json=stop_payload)

    if stop_response.status_code == 200:
        print("Timer stopped successfully.")
    else:
        print("Failed to stop the timer.")
        print("Payload:", stop_payload)
        print(stop_response.text)

# Call the function
stop_running_timer()
