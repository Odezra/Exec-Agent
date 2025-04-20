from dataclasses import dataclass
from datetime import date, datetime
from typing import List

@dataclass
class Headline:
    title: str
    url: str

@dataclass
class Meeting:
    start: datetime
    end: datetime
    summary: str

@dataclass
class Weather:
    min_c: float
    max_c: float
    rain_chance_pct: int

@dataclass
class Briefing:
    date: date
    headlines: List[Headline]
    meetings: List[Meeting]
    weather: Weather
    aud_usd: float
    nasdaq_close: float