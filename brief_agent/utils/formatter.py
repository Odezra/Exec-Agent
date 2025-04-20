from brief_agent.schema import Briefing

def build_email_body(briefing: Briefing) -> str:
    lines = []
    lines.append(f"Executive Daily Briefing - {briefing.date.isoformat()}")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Headlines:")
    for h in briefing.headlines:
        lines.append(f"- {h.title} ({h.url})")
    lines.append("")
    lines.append("Meetings:")
    for m in briefing.meetings:
        start = m.start.strftime("%H:%M")
        end = m.end.strftime("%H:%M")
        lines.append(f"- {start}-{end}: {m.summary}")
    lines.append("")
    lines.append(f"Weather: {briefing.weather.min_c:.1f}°C - {briefing.weather.max_c:.1f}°C, Rain chance: {briefing.weather.rain_chance_pct}%")
    lines.append(f"AUD -> USD: {briefing.aud_usd:.4f}")
    lines.append(f"NASDAQ previous close: {briefing.nasdaq_close}")
    return "\n".join(lines)