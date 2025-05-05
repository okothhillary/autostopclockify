import os
import requests
from datetime import datetime, timezone
from dateutil.parser import isoparse  # pip install python-dateutil

API_KEY        = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID   = os.getenv("WORKSPACE_ID")
USER_ID        = os.getenv("USER_ID")
BASE_URL       = "https://api.clockify.me/api/v1"
HEADERS        = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def get_active_project_id():
    """Fetches and returns the first active (non-archived) project in the workspace."""
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects?archived=false"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("⚠️ Failed to fetch active projects:", resp.text)
        return None
    projects = resp.json()
    if not projects:
        print("⚠️ No active projects found in workspace.")
        return None
    return projects[0]["id"]  # pick the first

def stop_running_timer():
    # 1) Get the currently running time entry
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("❌ Failed to fetch running time entry:", resp.text)
        return

    entries = resp.json()
    if not entries:
        print("ℹ️ No running timer found.")
        return

    entry = entries[0]
    entry_id = entry["id"]

    # 2) Reformat start & end times to "YYYY-MM-DDTHH:MM:SSZ"
    start_raw = entry["timeInterval"]["start"]
    start = isoparse(start_raw).strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3) Determine a valid projectId
    project_id = entry.get("projectId")
    if not project_id:
        project_id = get_active_project_id()
        if not project_id:
            print("❌ Cannot stop timer: no projectId available or found.")
            return

    # 4) Build payload and send the stop request
    payload = {"start": start, "end": end, "projectId": project_id}
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}"
    stop_resp = requests.put(stop_url, headers=HEADERS, json=payload)

    if stop_resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop the timer.")
        print("Payload:", payload)
        print(stop_resp.text)

if __name__ == "__main__":
    stop_running_timer()
