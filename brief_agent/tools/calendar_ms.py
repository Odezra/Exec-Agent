from datetime import datetime as dt
import msal
import requests
from brief_agent.schema import Meeting
from brief_agent.config import cfg

_TOKEN_CACHE = msal.SerializableTokenCache()

def _acquire_token() -> str:
    """
    Acquire an access token for Microsoft Graph using device flow.
    """
    c = cfg()
    client_id = c["GRAPH_CLIENT_ID"]
    tenant_id = c["GRAPH_TENANT_ID"]
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=_TOKEN_CACHE,
    )
    scopes = ["https://graph.microsoft.com/Calendars.Read"]
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to initiate device flow: {flow.get('error')}")
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)
    if not result or "access_token" not in result:
        raise RuntimeError(result.get("error_description", "Failed to acquire access token"))
    return result["access_token"]

def get_meetings(iso_date: str) -> list[Meeting]:
    """
    Fetch calendar events for the given ISO date via Microsoft Graph.
    """
    token = _acquire_token()
    start = f"{iso_date}T00:00:00Z"
    end = f"{iso_date}T23:59:59Z"
    url = (
        "https://graph.microsoft.com/v1.0/me/calendarView"
        f"?startDateTime={start}&endDateTime={end}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.timezone="UTC"',
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    events = resp.json().get("value", [])
    meetings: list[Meeting] = []
    for ev in events:
        s = dt.fromisoformat(ev["start"]["dateTime"])
        e = dt.fromisoformat(ev["end"]["dateTime"])
        summary = ev.get("subject") or "(no title)"
        meetings.append(Meeting(start=s, end=e, summary=summary))
    return meetings