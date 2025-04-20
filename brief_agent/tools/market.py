import requests

def get_financials() -> tuple[float, float]:
    """
    Fetch live AUD->USD exchange rate and NASDAQ previous close.
    Uses exchangerate.host (no API key) and Yahoo Finance.
    """
    # Free endpoint: Financial Modeling Prep (FMP) if API key is set
    import os
    key = os.getenv("FMP_API_KEY")
    if key:
        # AUD -> USD via FMP forex endpoint (specify symbol parameter)
        fx_url = "https://financialmodelingprep.com/api/v3/forex"
        fx_resp = requests.get(fx_url, params={"apikey": key, "symbol": "AUD/USD"})
        fx_resp.raise_for_status()
        fx_data = fx_resp.json()
        # normalize to list of dicts
        if isinstance(fx_data, dict):
            fx_items = [fx_data]
        elif isinstance(fx_data, list):
            fx_items = fx_data
        else:
            fx_items = []
        aud_usd = 0.0
        for item in fx_items:
            if isinstance(item, dict) and item.get("symbol") == "AUD/USD":
                aud_usd = item.get("mid", item.get("midPrice", 0.0))
                break

        # NASDAQ previous close via FMP quote endpoint
        idx_url = "https://financialmodelingprep.com/api/v3/quote/%5EIXIC"
        idx_resp = requests.get(idx_url, params={"apikey": key})
        idx_resp.raise_for_status()
        idx_data = idx_resp.json()
        # normalize to list of dicts
        if isinstance(idx_data, dict):
            idx_items = [idx_data]
        elif isinstance(idx_data, list):
            idx_items = idx_data
        else:
            idx_items = []
        nasdaq_close = 0.0
        if idx_items and isinstance(idx_items[0], dict):
            nasdaq_close = idx_items[0].get("previousClose", idx_items[0].get("price", 0.0))

        return aud_usd, nasdaq_close
    # AUD -> USD via exchangerate.host
    fx_resp = requests.get(
        "https://api.exchangerate.host/latest",
        params={"base": "AUD", "symbols": "USD"}
    )
    fx_resp.raise_for_status()
    fx_data = fx_resp.json()
    aud_usd = fx_data.get("rates", {}).get("USD", 0.0)

    # NASDAQ previous close via Yahoo Finance
    yf_resp = requests.get(
        "https://query1.finance.yahoo.com/v7/finance/quote",
        params={"symbols": "^IXIC"}
    )
    yf_resp.raise_for_status()
    quote = yf_resp.json().get("quoteResponse", {}).get("result", [])
    if quote and "regularMarketPreviousClose" in quote[0]:
        nasdaq_close = quote[0]["regularMarketPreviousClose"]
    else:
        nasdaq_close = 0.0

    return aud_usd, nasdaq_close