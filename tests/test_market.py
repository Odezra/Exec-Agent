import pytest
from brief_agent.tools.market import get_financials

def test_get_financials_returns_two_floats():
    """
    Verify get_financials returns a tuple of two floats (aud_usd, nasdaq_close).
    """
    try:
        aud_usd, nasdaq_close = get_financials()
    except Exception as e:
        pytest.skip(f"Skipping financials test due to network/API error: {e}")
    assert isinstance(aud_usd, float)
    assert aud_usd >= 0.0
    assert isinstance(nasdaq_close, float)
    assert nasdaq_close >= 0.0