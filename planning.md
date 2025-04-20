Below is a kick‑off package for Project 1 – the Executive Daily Briefing Agent, implemented with the OpenAI Agents SDK plus a lightweight Python scheduler and a Slack webhook for delivery.

⸻

1 — Mini Product Requirements Document (PRD)

Section	Details
Goal	Every weekday 06:30 AEST, deliver a single Slack (or e‑mail) message summarising: • top 3 tech/finance headlines • today’s Davidson meetings (09:00‑17:00 window) • Melbourne weather (min/max, chance of rain) • AUD → USD & NASDAQ close
Success metrics	• Message sent ≤ 1 min after schedule • News relevance score ≥ 4 / 5 (manual) • ≤ US$0.04 OpenAI cost per run
Functional scope	• Pull news via web‑search tool (OpenAI “web-search”) • Pull events via Google Calendar API • Pull weather via BOM API or Open‑Meteo • Compose markdown, post to Slack
NFRs	• Secrets in .env, never hard‑coded • Idempotent (if rerun, edits the existing Slack post instead of spamming) • Logged to logs/briefing_YYYYMMDD.log
Out‑of‑scope (v1)	Personalised action suggestions, sentiment analysis
Stakeholders	Owner: You (DTC)  Reviewer: EA / Ops lead  Users: Exec team



⸻

2 — Repo Scaffold

daily_briefing_agent/
├─ brief_agent/
│   ├─ __init__.py
│   ├─ agent_runner.py          # main entrypoint
│   ├─ tools/
│   │   ├─ news.py              # get_news()
│   │   ├─ calendar.py          # get_todays_events()
│   │   ├─ weather.py           # get_weather()
│   ├─ utils/
│   │   ├─ formatter.py         # build_slack_block()
│   │   └─ scheduler.py         # cron / schedule wrapper
│   └─ prompts/
│       └─ system_prompt.md
├─ tests/
│   └─ test_tools.py
├─ .env.example
├─ pyproject.toml
└─ README.md

Key dependencies (pyproject excerpt)

[project]
requires-python = ">=3.11"

[project.dependencies]
openai = "^1.23"
python-dotenv = "^1.0"
schedule = "^1.2"     # or APScheduler
requests = "^2.32"
slack-sdk = "^3.28"
pydantic = "^2.7"

The schedule library keeps everything in‑process; swap to cron in production if you prefer system‑level scheduling  ￼.

⸻

3 — Step‑by‑Step Build Plan

#	Task	Main files	Est. time
0	Bootstrap: git init, create virtual‑env, copy scaffold, poetry install	all	0.5 h
1	Implement tool stubs (news.py, calendar.py, weather.py) returning hard‑coded JSON for now	tools/*	1 h
2	Write system prompt and create Agent with tool schemas in agent_runner.py	agent_runner.py, prompts/system_prompt.md	1 h
3	Replace stubs with real API calls (News → OpenAI web-search, Calendar → Google, Weather → BOM)	tools/*	2 h
4	Build formatter.build_slack_block() → nice markdown / Slack blocks	utils/formatter.py	0.5 h
5	Add Slack sender using incoming webhook URL (env var SLACK_WEBHOOK)	utils/formatter.py	0.5 h
6	Wire scheduler: schedule.every().day.at("06:30").do(run_briefing); unit‑test with .run_pending() loop	utils/scheduler.py	1 h
7	Logging & error handling (retry up to 3, write log file)	agent_runner.py	0.5 h
8	Test cases: pytest for each tool + dry‑run mode	tests/test_tools.py	1 h
9	Deployment: create systemd service or GitHub Actions + cron on a small EC2/Lambda	README.md	1 h
Total	≈ 9 h focused coding time		



⸻

4 — Key Code Snippets

Tool schema & function (news.py)

# brief_agent/tools/news.py
import requests, datetime
from pydantic import BaseModel

class NewsPayload(BaseModel):
    date: str

def get_news(date: str):
    """Return top 3 fintech headlines for the date (ISO)."""
    query = f"fintech OR AI consulting site:news {date}"
    response = openai.tools.web_search({"query": query, "k": 3})
    return {"headlines": response["results"]}

schema = {
    "type": "function",
    "name": "get_news",
    "description": "Fetch top 3 headlines for a given date",
    "parameters": NewsPayload.model_json_schema()
}

Agent creation (agent_runner.py)

from openai import Assistant
from brief_agent.tools import news, calendar, weather
from brief_agent.utils.formatter import build_slack_block

assistant = Assistant(
    model="o3",
    tools=[news.schema, calendar.schema, weather.schema],
    instructions=open("prompts/system_prompt.md").read()
)

def run_briefing():
    today = datetime.date.today().isoformat()
    messages=[{"role": "user", "content": f"Daily briefing for {today}"}]
    res = assistant.chat(messages=messages, stream=False)
    block = build_slack_block(res.choices[0].message.content)
    send_to_slack(block)

Scheduler (scheduler.py)

import schedule, time
from brief_agent.agent_runner import run_briefing

schedule.every().day.at("06:30").do(run_briefing)

def start():
    while True:
        schedule.run_pending()
        time.sleep(30)

See OpenAI Agents SDK docs for full usage and tracing options  ￼; Slack webhook payload format in Slack API guide  ￼.

⸻

5 — Secrets & Configuration (.env.example)

OPENAI_API_KEY=sk-...
SLACK_WEBHOOK=https://hooks.slack.com/services/...
GOOGLE_CAL_ID=primary
GOOGLE_SERVICE_ACCOUNT_JSON=./creds/gcal.json
WEATHER_API_KEY=...
LOCATION_LAT=-37.8136
LOCATION_LON=144.9631



⸻

6 — Next Actions for You
	1.	Clone scaffold & wire secrets
	2.	Follow the task list above—commit after each milestone.
	3.	Ping me once the skeleton runs in dry‑run mode; we’ll tighten prompts and evaluate cost vs. quality.

Ready to start? Let me know if you’d like deeper guidance on any particular step (e.g., Slack formatting or Google Calendar auth).