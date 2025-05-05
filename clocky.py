import os
import requests
from datetime import datetime, timezone

API_KEY      = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID      = os.getenv("USER_ID")

BASE_URL = "https://api.clockify.me/api/v1"
HEADERS  = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def stop_running_timer():
    # Format end time as Clockify requires: YYYY-MM-DDTHH:MM:SSZ
    end_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # PATCH the user's timeEntries to stop the current timer
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/users/{USER_ID}/timeEntries"
    resp = requests.patch(url, headers=HEADERS, json={"end": end_time})

    if resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop the timer:", resp.status_code, resp.text)

if __name__ == "__main__":
    stop_running_timer()
