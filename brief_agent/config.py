import os

def cfg() -> dict[str, str]:
    """
    Return configuration for Microsoft Graph authentication.
    Reads AZURE_CLIENT_ID and AZURE_TENANT_ID from environment.
    """
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    if not client_id or not tenant_id:
        raise RuntimeError("AZURE_CLIENT_ID and AZURE_TENANT_ID must be set in environment")
    return {
        "GRAPH_CLIENT_ID": client_id,
        "GRAPH_TENANT_ID": tenant_id,
    }