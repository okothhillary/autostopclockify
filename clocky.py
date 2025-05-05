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
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("⚠️ Could not fetch projects:", resp.text)
        return None
    projects = resp.json()
    return projects[0]["id"] if projects else None

def stop_running_timer():
    # 1) Fetch in-progress entry
    resp = requests.get(
        f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?in-progress=true",
        headers=HEADERS
    )
    if resp.status_code != 200:
        print("❌ Error fetching running entry:", resp.text)
        return
    entries = resp.json()
    if not entries:
        print("ℹ️ No running timer.")
        return

    entry = entries[0]
    entry_id   = entry["id"]
    start_raw  = entry["timeInterval"]["start"]

    # 2) Reformat start to "YYYY-MM-DDTHH:MM:SSZ"
    start = isoparse(start_raw).strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3) Determine projectId (fallback if missing)
    project_id = entry.get("projectId") or get_active_project_id()
    if not project_id:
        print("❌ No valid projectId available.")
        return

    # 4) Build & print payload for debugging
    payload = {"start": start, "end": end, "projectId": project_id}
    print("🔧 Payload:", payload)

    # 5) Send stop request
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}"
    stop_resp = requests.put(stop_url, headers=HEADERS, json=payload)

    if stop_resp.status_code == 200:
        print("✅ Timer stopped successfully.")
    else:
        print("❌ Failed to stop the timer:", stop_resp.text)

if __name__ == "__main__":
    stop_running_timer()
