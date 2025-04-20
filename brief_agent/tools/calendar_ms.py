from datetime import datetime as dt
import msal
import requests
import os
from brief_agent.schema import Meeting
from brief_agent.config import cfg

# expected cfg() keys for confidential flow:
# AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID

_TOKEN_CACHE = msal.SerializableTokenCache()

def _acquire_token() -> str:
    """
    Acquire an access token for Microsoft Graph.
    Priority:
    1) Confidential client flow if AZURE_CLIENT_SECRET is set
    2) Device‑code flow (interactive) as fallback
    """
    c = cfg()

    # --- confidential‑client flow ----------------------------
    if "AZURE_CLIENT_SECRET" in c:
        app = msal.ConfidentialClientApplication(
            client_id=c["AZURE_CLIENT_ID"],
            client_credential=c["AZURE_CLIENT_SECRET"],
            authority=f"https://login.microsoftonline.com/{c['AZURE_TENANT_ID']}",
            token_cache=_TOKEN_CACHE,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(result.get("error_description", "client‑cred auth failed"))

    # --- device‑code fallback -------------------------------
    app = msal.PublicClientApplication(
        client_id=c["AZURE_CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{c['AZURE_TENANT_ID']}",
        token_cache=_TOKEN_CACHE,
    )
    scopes = ["https://graph.microsoft.com/Calendars.Read"]
    accounts = app.get_accounts()
    result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to initiate device flow: {flow.get('error')}")
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        return result["access_token"]
    raise RuntimeError(result.get("error_description", "Failed to acquire access token"))

def get_meetings(iso_date: str) -> list[Meeting]:
    """
    Fetch calendar events for the given date via Microsoft Graph (UTC).
    Uses confidential‑client token if available, otherwise falls back to device flow.
    """
    # Stub out calendar lookup in CI (e.g. GitHub Actions) to avoid auth errors
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return []
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