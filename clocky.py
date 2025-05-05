import os
import requests
from datetime import datetime, timezone
from dateutil.parser import isoparse  # pip install python-dateutil

# Load secrets from environment
API_KEY      = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID      = os.getenv("USER_ID")
BASE_URL     = "https://api.clockify.me/api/v1"
HEADERS      = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def get_active_project_id():
    """Return the first non-archived project ID in the workspace."""
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects?archived=false"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("⚠️ Failed to fetch projects:", resp.text)
        return None
    projects = resp.json()
    if not projects:
        print("⚠️ No active projects found.")
        return None
    return projects[0]["id"]

def stop_running_timer():
    # 1) Fetch the in-progress entry
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("❌ Error fetching time entry:", resp.text)
        return
    entries = resp.json()
    if not entries:
        print("ℹ️ No running timer.")
        return

    entry = entries[0]
    entry_id = entry["id"]

    # 2) Reformat timestamps
    start = isoparse(entry["timeInterval"]["start"]).strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3) Always pick a valid project
    project_id = get_active_project_id()
    if not project_id:
        print("❌ Cannot stop timer: no valid project.")
        return

    # 4) Build payload & send stop request
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
