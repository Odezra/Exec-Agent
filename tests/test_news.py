import datetime
import pytest
from brief_agent.tools.news import get_headlines
from brief_agent.schema import Headline

@pytest.mark.network
def test_get_headlines_returns_list_of_headlines():
    """
    Verify get_headlines returns a list of Headline objects with non-empty title and url.
    """
    iso_date = datetime.date.today().isoformat()
    headlines = get_headlines(iso_date, page_size=5)
    assert isinstance(headlines, list)
    assert 1 <= len(headlines) <= 5
    for h in headlines:
        assert isinstance(h, Headline)
        assert isinstance(h.title, str) and h.title
        assert isinstance(h.url, str) and h.url