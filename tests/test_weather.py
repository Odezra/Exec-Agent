import datetime
import os
import pytest
from brief_agent.tools.weather import get_weather
from brief_agent.schema import Weather

@pytest.mark.skipif(
    not os.getenv("WEATHER_API_KEY"),
    reason="WEATHER_API_KEY not set in environment"
)
def test_get_weather_returns_weather():
    """
    Verify get_weather returns a Weather object with proper field types.
    """
    iso_date = datetime.date.today().isoformat()
    w = get_weather(iso_date)
    assert isinstance(w, Weather)
    assert isinstance(w.min_c, float)
    assert isinstance(w.max_c, float)
    assert isinstance(w.rain_chance_pct, int)