        # Optional Azure Graph credentials (calendar_ms.py)
        **({} if not os.getenv("AZURE_CLIENT_ID") else {
            "AZURE_CLIENT_ID": os.environ["AZURE_CLIENT_ID"]
        }),
        **({} if not os.getenv("AZURE_TENANT_ID") else {
            "AZURE_TENANT_ID": os.environ["AZURE_TENANT_ID"]
        }),
        **({} if not os.getenv("AZURE_CLIENT_SECRET") else {
            "AZURE_CLIENT_SECRET": os.environ["AZURE_CLIENT_SECRET"]
        }),