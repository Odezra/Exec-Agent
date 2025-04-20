import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date
from email.utils import parsedate_to_datetime
from brief_agent.schema import Headline

def get_headlines(iso_date: str, query: str = None, page_size: int = 7) -> list[Headline]:
    """
    Fetch the top 3 business and technology news headlines for the given date
    by scraping Google News RSS feeds. Returns a list of Headline(title, url).
    """
    # Validate date format
    _ = date.fromisoformat(iso_date)
    # RSS feed URLs for business and technology
    feeds = [
        "https://news.google.com/rss/headlines/section/topic/BUSINESS",
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY"
    ]
    headlines: list[Headline] = []
    # Determine how many headlines to fetch
    limit = page_size or 7
    # Attempt to collect from business first, then technology
    for feed in feeds:
        try:
            resp = requests.get(feed, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            items = root.findall('.//item')
            for item in items:
                if len(headlines) >= limit:
                    break
                title_elem = item.find('title')
                link_elem = item.find('link')
                date_elem = item.find('pubDate')
                if title_elem is None or link_elem is None or date_elem is None:
                    continue
                try:
                    pub = parsedate_to_datetime(date_elem.text)
                    if pub.date().isoformat() != iso_date:
                        continue
                except Exception:
                    pass
                headlines.append(Headline(title=title_elem.text or "", url=link_elem.text or ""))
        except Exception:
            continue
        if len(headlines) >= 3:
            break
    # If less than limit, fill remaining from earliest items
    if len(headlines) < limit:
        for feed in feeds:
            try:
                resp = requests.get(feed, timeout=10)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
                items = root.findall('.//item')
                for item in items:
                    if len(headlines) >= limit:
                        break
                    title = item.findtext('title', default="")
                    link = item.findtext('link', default="")
                    if title and link and not any(h.url == link for h in headlines):
                        headlines.append(Headline(title=title, url=link))
            except Exception:
                continue
            if len(headlines) >= 3:
                break
    return headlines