import os
import requests
from datetime import datetime, timezone

API_KEY      = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID      = os.getenv("USER_ID")

BASE_URL = "https://api.clockify.me/api/v1"
HEADERS  = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def stop_running_timer():
    # 1) Fetch the in-progress entry
    get_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true"
    resp = requests.get(get_url, headers=HEADERS)
    if resp.status_code != 200:
        print("❌ Error fetching running entry:", resp.text)
        return
    entries = resp.json()
    if not entries:
        print("ℹ️ No running timer.")
        return

    entry_id = entries[0]["id"]

    # 2) Format end time as Clockify expects
    end_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3) Call the stop endpoint
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}/end"
    stop_resp = requests.patch(stop_url, headers=HEADERS, json={"end": end_time})

    if stop_resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop the timer:", stop_resp.text)

if __name__ == "__main__":
    stop_running_timer()
