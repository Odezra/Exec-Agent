import pytest
import json
from brief_agent.tools.market import get_financials

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

@pytest.fixture(autouse=True)
def mock_requests_get(monkeypatch):
    # Prepare fake FX data and Yahoo Finance data
    fake_fx = {"rates": {"USD": 0.75}}
    fake_yf = {"quoteResponse": {"result": [{"regularMarketPreviousClose": 14000.0}]}}

    def fake_get(url, params=None):
        if "exchangerate.host" in url:
            return DummyResponse(fake_fx)
        if "finance.yahoo.com" in url:
            return DummyResponse(fake_yf)
        raise RuntimeError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("brief_agent.tools.market.requests.get", fake_get)
    yield

def test_get_financials_with_mocked_api():
    aud_usd, nasdaq_close = get_financials()
    assert aud_usd == 0.75
    assert nasdaq_close == 14000.0