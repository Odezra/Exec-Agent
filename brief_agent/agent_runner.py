import datetime
from brief_agent.tools.news import get_headlines
from brief_agent.tools.calendar_ms import get_meetings
from brief_agent.tools.weather import get_weather
from brief_agent.tools.market import get_financials
# from brief_agent.utils.formatter import build_email_body  # no longer used; orchestration via OpenAI
# from brief_agent.utils.emailer import send_email

def run_briefing():
    """
    Orchestrate the Executive Daily Briefing via OpenAI function calling.
    Uses tools: get_headlines, get_meetings, get_weather, get_financials.
    Outputs a plain-text email body.
    """
    import os, json
    import logging
    from openai import OpenAI

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    client = OpenAI(api_key=api_key)
    # Setup logging
    today_iso = datetime.date.today().isoformat()
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"briefing_{today_iso}.log")
    logger = logging.getLogger("briefing")
    if logger.hasHandlers():
        logger.handlers.clear()
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    logger.info(f"Starting briefing run for {today_iso}")

    # Define available functions for the assistant
    functions = [
        {
            "name": "get_headlines",
            "description": (
                "Return top AU-relevant tech/biz headlines for the date. "
                "If 'query' is supplied, use it verbatim in the NewsAPI request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "iso_date": {"type": "string"},
                    "query": {
                        "type": "string",
                        "description": (
                            "Optional NewsAPI query string. "
                            "Default focuses on AU tech, finance, M&A."
                        )
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Max results; default 7."
                    }
                },
                "required": ["iso_date"]
            }
        },
        {
            "name": "get_meetings",
            "description": (
                "Return calendar events for the exec on the given date, "
                "with ISO‑8601 start/end and summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "iso_date": {"type": "string"}
                },
                "required": ["iso_date"]
            }
        },
        {
            "name": "get_weather",
            "description": (
                "Return min/max °C and rain chance for the given date at "
                "lat/lon env vars LOCATION_LAT/LON."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "iso_date": {"type": "string"}
                },
                "required": ["iso_date"]
            }
        },
        {
            "name": "get_financials",
            "description": (
                "Return latest AUD→USD fx rate and NASDAQ previous close."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]

    # Prepare messages
    today_iso = datetime.date.today().isoformat()
    messages = [
        {
            "role": "system",
            "content": (
                "You are an Executive Daily Briefing agent for a technology-consulting CEO "
                "(Australia, UTC+10). Deliver a concise plain-text e-mail with these sections, "
                "in order:\n\n"
                "1. TODAY’S HEADLINES          – 5-7 bullet points, AU + global tech/finance.\n"
                "2. MEETINGS & COMMITMENTS     – list in local time (HH:MM AEST), 1 line each.\n"
                "3. WEATHER - MELBOURNE CBD    – “Min °/Max ° C, Chance of rain %”.\n"
                "4. MARKETS OVERNIGHT          – “AUD/USD x.xx  | NASDAQ close n.nn (±%)”.\n\n"
                "Guidelines:\n"
                "• Use ONLY the provided functions; never hit external APIs directly.\n"
                "• If a function returns no data, omit that section entirely.\n"
                "• No markdown, HTML, links, or greetings—just the body.\n"
                "• Keep total length ≤ 200 words."
            )
        },
        {"role": "user", "content": f"Generate today’s executive briefing for {today_iso}."}
    ]

    # Iteratively handle function calls until assistant returns final content
    while True:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        msg = response.choices[0].message
        # If assistant requested a function, execute it with retries and append the result
        if getattr(msg, "function_call", None) is not None:
            fn_call = msg.function_call
            name = fn_call.name
            args = json.loads(fn_call.arguments)
            logger.info(f"Calling function {name} with args {args}")
            # Retry logic
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    if name == "get_headlines":
                        result = get_headlines(**args)
                        payload = [{"title": h.title, "url": h.url} for h in result]
                    elif name == "get_meetings":
                        result = get_meetings(**args)
                        payload = [{"start": m.start.isoformat(), "end": m.end.isoformat(), "summary": m.summary} for m in result]
                    elif name == "get_weather":
                        w = get_weather(**args)
                        payload = {"min_c": w.min_c, "max_c": w.max_c, "rain_chance_pct": w.rain_chance_pct}
                    elif name == "get_financials":
                        aud_usd, nasdaq_close = get_financials()
                        payload = {"aud_usd": aud_usd, "nasdaq_close": nasdaq_close}
                    else:
                        payload = {}
                    logger.info(f"Function {name} succeeded on attempt {attempt}")
                    break
                except Exception as e:
                    logger.error(f"Error in {name}, attempt {attempt}/{max_attempts}: {e}")
                    if attempt == max_attempts:
                        logger.error(f"{name} failed after {max_attempts} attempts, aborting briefing")
                        raise
                    logger.info(f"Retrying {name} (attempt {attempt + 1})")
            # Append the function call and its response
            messages.append(msg.model_dump())
            messages.append({"role": "function", "name": name, "content": json.dumps(payload)})
            continue
        # No function call means assistant has returned final content
        email_body = msg.content
        break

    logger.info("Briefing completed, generated email body:")
    logger.info(email_body)
    print(email_body)

if __name__ == "__main__":
    run_briefing()