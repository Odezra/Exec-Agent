"""
Executive Daily Briefing agent runner.

Usage (local):
    poetry run python -m brief_agent.agent_runner

The runner:
1. Builds an OpenAI chat with function‑calling.
2. Exposes the tool stubs (news, meetings, weather, markets).
3. Iterates until the assistant returns the final e‑mail body.
"""

import datetime
import json
import logging
import os
from openai import OpenAI

from brief_agent.tools.news import get_headlines
from brief_agent.tools.calendar_ms import get_meetings
from brief_agent.tools.weather import get_weather
from brief_agent.tools.market import get_financials

LOG_DIR = os.getenv("LOG_DIR", "logs")
MODEL = "gpt-4-0613"


def _setup_logger(today_iso: str) -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger("briefing")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(os.path.join(LOG_DIR, f"briefing_{today_iso}.log"))
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def run_briefing() -> None:
    """Main orchestration loop using OpenAI function‑calling."""
    today_iso = datetime.date.today().isoformat()
    logger = _setup_logger(today_iso)
    logger.info("Starting briefing run for %s", today_iso)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    client = OpenAI(api_key=api_key)

    # ---------- function signatures -------------------------------------------------
    functions = [
        {
            "name": "get_headlines",
            "description": (
                "Return top AU‑relevant tech/biz headlines for the date."
                " If 'query' is supplied, use it verbatim in the NewsAPI request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "iso_date": {"type": "string"},
                    "query": {"type": "string"},
                    "page_size": {"type": "integer"},
                },
                "required": ["iso_date"],
            },
        },
        {
            "name": "get_meetings",
            "description": "Return calendar events (start, end, summary) for the given date.",
            "parameters": {
                "type": "object",
                "properties": {"iso_date": {"type": "string"}},
                "required": ["iso_date"],
            },
        },
        {
            "name": "get_weather",
            "description": "Return min/max °C and rain chance for the given date.",
            "parameters": {
                "type": "object",
                "properties": {"iso_date": {"type": "string"}},
                "required": ["iso_date"],
            },
        },
        {
            "name": "get_financials",
            "description": "Return latest AUD→USD fx rate and NASDAQ previous close.",
            "parameters": {"type": "object", "properties": {}},
        },
    ]

    # ---------- conversation bootstrap ----------------------------------------------
    messages = [
        {
            "role": "system",
            "content": (
                "You are an Executive Daily Briefing agent for a technology‑consulting CEO "
                "(Australia, UTC+10). Deliver a concise plain‑text e‑mail with these sections:\n"
                "1. TODAY’S HEADLINES ‑ 5‑7 bullets\n"
                "2. MEETINGS & COMMITMENTS ‑ HH:MM AEST\n"
                "3. WEATHER ‑ MELBOURNE CBD\n"
                "4. MARKETS OVERNIGHT\n\n"
                "Use ONLY the provided functions; no external calls. Omit empty sections. "
                "No HTML/markdown. ≤ 200 words."
            ),
        },
        {"role": "user", "content": f"Generate today’s executive briefing for {today_iso}."},
    ]

    # ---------- main loop -----------------------------------------------------------
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        msg = response.choices[0].message

        if getattr(msg, "function_call", None) is None:
            email_body = msg.content
            break

        fn_call = msg.function_call
        fn_name = fn_call.name
        args = json.loads(fn_call.arguments or "{}")
        logger.info("Calling function %s with args %s", fn_name, args)

        # retry wrapper
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                if fn_name == "get_headlines":
                    res = get_headlines(**args)
                    payload = [{"title": h.title, "url": h.url} for h in res]
                elif fn_name == "get_meetings":
                    res = get_meetings(**args)
                    payload = [
                        {"start": m.start.isoformat(), "end": m.end.isoformat(), "summary": m.summary}
                        for m in res
                    ]
                elif fn_name == "get_weather":
                    w = get_weather(**args)
                    payload = {"min_c": w.min_c, "max_c": w.max_c, "rain_chance_pct": w.rain_chance_pct}
                elif fn_name == "get_financials":
                    aud_usd, nasdaq = get_financials()
                    payload = {"aud_usd": aud_usd, "nasdaq_close": nasdaq}
                else:
                    payload = {}
                break  # success
            except Exception as e:
                logger.error("Error in %s attempt %s/%s: %s", fn_name, attempt, max_attempts, e)
                if attempt == max_attempts:
                    raise
        # add function result
        messages.append(msg.model_dump())
        messages.append({"role": "function", "name": fn_name, "content": json.dumps(payload)})

    logger.info("Briefing completed; email body follows:\n%s", email_body)
    print(email_body)


if __name__ == "__main__":
    run_briefing()
```