"""
Central configuration helper.

Reads Azure Graph credentials from environment and returns them in a dict
so the rest of the code can do `c = cfg()` and access:

    c["AZURE_CLIENT_ID"]
    c["AZURE_TENANT_ID"]
    c.get("AZURE_CLIENT_SECRET")   # optional

If either `AZURE_CLIENT_ID` or `AZURE_TENANT_ID` is missing, cfg() raises
RuntimeError so callers fail fast.
"""

from __future__ import annotations

import os
from typing import Dict


def cfg() -> Dict[str, str]:
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    secret = os.getenv("AZURE_CLIENT_SECRET")  # optional

    if not client_id or not tenant_id:
        raise RuntimeError(
            "AZURE_CLIENT_ID and AZURE_TENANT_ID must be set in environment"
        )

    conf = {
        "AZURE_CLIENT_ID": client_id,
        "AZURE_TENANT_ID": tenant_id,
    }

    if secret:
        conf["AZURE_CLIENT_SECRET"] = secret

    return conf