from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field

class Headline(BaseModel):
    title: str
    url: str

class Meeting(BaseModel):
    start: datetime = Field(description="ISO start")
    end:   datetime
    summary: str

class Weather(BaseModel):
    min_c: float
    max_c: float
    rain_chance_pct: int

class Briefing(BaseModel):
    date: date
    headlines: List[Headline]
    meetings:  List[Meeting]
    weather:   Weather
    aud_usd: float
    nasdaq_close: float