import schedule
import time
from brief_agent.agent_runner import run_briefing

def start():
    schedule.every().day.at("06:30").do(run_briefing)
    while True:
        schedule.run_pending()
        time.sleep(30)