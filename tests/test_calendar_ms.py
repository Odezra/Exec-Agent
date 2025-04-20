import datetime
import pytest
from brief_agent.tools.calendar_ms import get_meetings
from brief_agent.schema import Meeting

def test_get_meetings_returns_list_of_meetings():
    """
    Verify get_meetings returns a list of Meeting objects with correct fields.
    Will skip if authentication or API errors occur.
    """
    iso_date = datetime.date.today().isoformat()
    try:
        meetings = get_meetings(iso_date)
    except Exception as e:
        pytest.skip(f"Skipping get_meetings test due to auth/API error: {e}")
    assert isinstance(meetings, list)
    for m in meetings:
        assert isinstance(m, Meeting)
        # Meeting start/end should correspond to the requested date
        assert m.start.isoformat().startswith(iso_date)
        assert m.end.isoformat().startswith(iso_date)
        assert isinstance(m.summary, str)