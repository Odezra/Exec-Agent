from datetime import date
from ..schema import Headline

def get_headlines(iso_date: str) -> list[Headline]:
    """Return top business headlines for the given ISO date (stub)."""
    _ = date.fromisoformat(iso_date)        # validate
    return [
        Headline(title="ACME profits hit record high",
                 url="https://example.com/acme"),
        Headline(title="Central Bank holds rates at 4.35 %",
                 url="https://example.com/rates"),
        Headline(title="Tech merger wave gains pace",
                 url="https://example.com/mergers"),
    ]