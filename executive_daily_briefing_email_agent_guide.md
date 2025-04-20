# Executive Daily Briefing **Email** Agent – Comprehensive Build Guide  
*Generated 2025‑04‑20 08:44 AEST*

---

## 0  Introduction  

This guide shows **step‑by‑step** how to build a **Python‑based agent** that sends an email every weekday at 06:30 AEST with:  

1. Top 3 technology / finance headlines  
2. Today’s Davidson Group meetings (09:00‑17:00)  
3. Melbourne weather (min / max °C & chance of rain)  
4. AUD → USD spot rate & NASDAQ previous close  

The design is adapted from the original Slack‑first spec citeturn0file0 but replaces Slack posting with a plain‑text **e‑mail** using SMTP for maximum portability.  
The stack: **Python 3.11+, OpenAI Assistants SDK, smtplib, schedule**, and optional tools such as **Cursor IDE, Codex CLI, and the OpenAI Dev Platform** for tracing & evaluation.

---

## 1  Product Requirements Document (PRD)

| Section | Details |
|---------|---------|
| **Goal** | Deliver the briefing e‑mail by 06:31 AEST every weekday |
| **Success metrics** | • Delivery latency ≤ 1 min after schedule  • News relevance ≥ 4 / 5 (manual sample)  • OpenAI cost ≤ US$0.04 per run |
| **Functional scope** | Pull news via OpenAI web‑search tool; fetch events via Google Calendar API; weather from **Bureau of Meteorology** JSON or Open‑Meteo; FX & index quotes via public market API; compose markdown → plain text; send via SMTP |
| **NFRs** | Secrets in `.env`; idempotent (Message‑ID tied to date); logged to `logs/briefing_YYYYMMDD.log` |
| **Stakeholders** | **Owner** – You (DTC)   **Reviewer** – EA / Ops Lead   **Users** – Executive team |

---

## 2  Data Schema (Pydantic Models)

```python
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List

class Headline(BaseModel):
    title: str
    url: str

class Meeting(BaseModel):
    start: datetime = Field(description="ISO start time")
    end:   datetime
    summary: str

class Weather(BaseModel):
    min_c: float
    max_c: float
    rain_chance_pct: int

class Briefing(BaseModel):
    date:      date
    headlines: List[Headline]
    meetings:  List[Meeting]
    weather:   Weather
    aud_usd:   float
    nasdaq_close: float
```

---

## 3  Detailed Build Plan

| # | Task | Main Files | Est. Time |
|---|------|-----------|-----------|
| 0 | Bootstrap repo, `venv`, install deps (`poetry add …`) | all | 0.5 h |
| 1 | **Tool stubs** – `news.py`, `calendar.py`, `weather.py` return hard‑coded JSON | `tools/*` | 1 h |
| 2 | Write system prompt; create **Assistant** in `agent_runner.py` | `agent_runner.py`, `prompts/*` | 1 h |
| 3 | Replace stubs with real API calls (OpenAI web‑search, Google Calendar, BOM / Open‑Meteo, exchangerate API) | `tools/*` | 2 h |
| 4 | Build `formatter.build_email_body()` – plain‑text with ASCII separators | `utils/formatter.py` | 0.5 h |
| 5 | **Email sender** via `smtplib` (env vars `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `RECIPIENT`) | `utils/emailer.py` | 0.5 h |
| 6 | Scheduler: `schedule.every().day.at("06:30").do(run_briefing)` | `utils/scheduler.py` | 1 h |
| 7 | Logging & retry (≤ 3) | `agent_runner.py` | 0.5 h |
| 8 | Unit tests (`pytest`) incl. dry‑run mode | `tests/*` | 1 h |
| 9 | Deployment: `systemd` timer or GitHub Actions cron on AWS Lambda / EC2 | `README.md` | 1 h |
|   | **Total** | | **≈ 9 h** |

---

## 4  Output Prompt for ChatGPT o3  

> **System**: “You are a senior Python mentor helping me build an Executive Daily Briefing e‑mail agent. Keep instructions terse, reference file paths, and ask me to run and paste key outputs.”  
>
> **User**:  
> ```text
> Phase 1 – Tool Stubs  
> 1. Guide me to implement `brief_agent/tools/news.py` with hard‑coded JSON (use the schema defined in the guide).  
> 2. Repeat for `calendar.py` & `weather.py`.  
> 3. Write minimal `agent_runner.py` that instantiates an OpenAI Assistant with those three functions.  
> 4. Show me how to call it for a single run (`python -m brief_agent.agent_runner`).  
> ```  
>
> After I confirm Phase 1 works, present Phase 2 (replace stubs with live APIs), and so on through Phase 9.  
> Always end a phase with: **“Run the tests and paste any failures.”**

---

## 5  Prerequisites & Setup Checklist

- Python ≥ 3.11  
- Cursor IDE or VS Code + **Codex CLI** extension for inline AI assistance  
- `poetry` (or `pip + venv`)  
- OpenAI API key in `.env` (`OPENAI_API_KEY=`…)  
- SMTP credentials (use Gmail App Password for testing)  

---

## 6  Appendix – Key Code Snippets

### Email Sender (`utils/emailer.py`)
```python
import os, smtplib
from email.message import EmailMessage

def send_email(subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = os.getenv("SMTP_USER")
    msg["To"]      = os.getenv("RECIPIENT")
    msg.set_content(body)

    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST"), 465) as smtp:
        smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        smtp.send_message(msg)
```

### Scheduler Entrypoint (`brief_agent/__main__.py`)
```python
from brief_agent.utils.scheduler import start

if __name__ == "__main__":
    start()
```

*Happy building!* 🚀

---

*End of guide.*
