## Executive Daily Briefing Email Agent

This Python agent sends a concise, plain-text Executive Daily Briefing email every weekday at 06:30 AEST.
It fetches:
- Top tech & business headlines
- Today’s calendar meetings
- Melbourne CBD weather
- AUD→USD exchange rate & NASDAQ previous close

## Deployment Options

### A. systemd (Linux)
1. Clone the repo to `/opt/brief_agent` and install dependencies:
   ```bash
   cd /opt/brief_agent
   poetry install --no-interaction
   ```
2. Place your `.env` at `/opt/brief_agent/.env` (must contain all required secrets).
3. Create `/etc/systemd/system/briefing.service`:
   ```ini
   [Unit]
   Description=Executive Daily Briefing Email Agent

   [Service]
   Type=oneshot
   WorkingDirectory=/opt/brief_agent
   EnvironmentFile=/opt/brief_agent/.env
   ExecStart=/usr/bin/env poetry run python3 -m brief_agent.agent_runner
   ```
4. Create `/etc/systemd/system/briefing.timer`:
   ```ini
   [Unit]
   Description=Run Executive Daily Briefing daily at 06:30 AEST

   [Timer]
   OnCalendar=*-*-* 06:30:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```
5. Enable & start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable briefing.timer
   sudo systemctl start briefing.timer
   ```

### B. GitHub Actions Cron
Create `.github/workflows/briefing.yml`:
```yaml
name: Executive Briefing Cron

on:
  schedule:
    # 06:30 AEST = 20:30 UTC previous day
    - cron: '30 20 * * *'
  workflow_dispatch: {}

jobs:
  briefing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: poetry install --no-interaction --no-ansi
      - name: Run briefing
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          WEATHER_API_KEY: ${{ secrets.WEATHER_API_KEY }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          RECIPIENT: ${{ secrets.RECIPIENT }}
        run: poetry run python3 -m brief_agent.agent_runner
```