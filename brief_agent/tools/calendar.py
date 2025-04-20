import os
import requests
import msal
from datetime import datetime
from brief_agent.schema import Meeting

# MSAL configuration
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CACHE_PATH = os.getenv("AZURE_TOKEN_CACHE", ".azure_token_cache.bin")
SCOPES = ["https://graph.microsoft.com/Calendars.Read"]

def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        cache.deserialize(open(CACHE_PATH, "r").read())
    return cache

def _save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        f.write(cache.serialize())

def _get_token():
    if not CLIENT_ID or not TENANT_ID:
        raise RuntimeError("AZURE_CLIENT_ID and AZURE_TENANT_ID must be set in environment")
    cache = _load_cache()
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )
    # Try to get token silently
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    # Interactive device code flow if silent fails
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to initiate device flow: {flow.get('error')}")
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)
    if not result or "access_token" not in result:
        raise RuntimeError(f"Failed to acquire token: {result.get('error_description') if result else result}")
    _save_cache(cache)
    return result["access_token"]

def get_meetings(iso_date: str) -> list[Meeting]:
    """
    Fetch calendar events for the given ISO date via Microsoft Graph.
    """
    # Microsoft Graph expects full datetime range
    start = iso_date + "T00:00:00Z"
    end = iso_date + "T23:59:59Z"
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/calendarview"
    params = {
        "startDateTime": start,
        "endDateTime": end,
        "$orderby": "start/dateTime"
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    items = resp.json().get("value", [])
    meetings = []
    for e in items:
        # Parse ISO datetime strings
        s = datetime.fromisoformat(e["start"]["dateTime"])
        t = datetime.fromisoformat(e["end"]["dateTime"])
        meetings.append(Meeting(start=s, end=t, summary=e.get("subject", "")))
    return meetings