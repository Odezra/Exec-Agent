import requests

def get_financials() -> tuple[float, float]:
    """
    Fetch live AUD->USD exchange rate and NASDAQ previous close.
    Uses exchangerate.host (no API key) and Yahoo Finance.
    """
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