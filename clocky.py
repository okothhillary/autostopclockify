import os
import requests
from datetime import datetime, timezone
from dateutil.parser import isoparse  # pip install python-dateutil

API_KEY      = os.getenv("CLOCKIFY_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
USER_ID      = os.getenv("USER_ID")
BASE_URL     = "https://api.clockify.me/api/v1"
HEADERS      = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def get_active_project_id():
    """Return the first non-archived project ID in the workspace, or None."""
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects?archived=false"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("⚠️ Could not fetch active projects:", r.text)
        return None
    projs = r.json()
    return projs[0]["id"] if projs else None

def stop_running_timer():
    # 1) Fetch the running entry
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ Error fetching entry:", r.text); return
    entries = r.json()
    if not entries:
        print("ℹ️ No running timer."); return

    entry = entries[0]
    entry_id    = entry["id"]
    raw_start   = entry["timeInterval"]["start"]

    # 2) Normalize timestamps to "YYYY-MM-DDTHH:MM:SSZ"
    start = isoparse(raw_start).strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3) Pick a valid projectId
    project_id = entry.get("projectId") or get_active_project_id()
    if not project_id:
        print("❌ No valid project to assign."); return

    # 4) Build payload & send PUT to the correct endpoint
    payload = {"start": start, "end": end, "projectId": project_id}
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}"
    stop_resp = requests.put(stop_url, headers=HEADERS, json=payload)

    if stop_resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop timer:")
        print("Payload:", payload)
        print(stop_resp.status_code, stop_resp.text)

if __name__ == "__main__":
    stop_running_timer()
