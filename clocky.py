import os
import requests
from datetime import datetime, timezone

API_KEY      = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
BASE_URL     = "https://api.clockify.me/api/v1"
HEADERS      = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def stop_running_timer():
    # Format end time exactly as Clockify expects: "YYYY-MM-DDTHH:MM:SSZ"
    end_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Call the built-in “endStarted” endpoint
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/timeEntries/endStarted"
    resp = requests.put(url, headers=HEADERS, json={"end": end_time})

    if resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop the timer:", resp.text)

if __name__ == "__main__":
    stop_running_timer()
