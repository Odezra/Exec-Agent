import os
import smtplib
from email.message import EmailMessage

def send_email(subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = os.getenv("RECIPIENT")
    msg.set_content(body)

    host = os.getenv("SMTP_HOST")
    # Determine SMTP port: use default 465 if unset or invalid
    port_str = os.getenv("SMTP_PORT", "").strip()
    try:
        port = int(port_str) if port_str else 465
    except ValueError:
        port = 465
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(user, pwd)
        smtp.send_message(msg)