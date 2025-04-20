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
    port = int(os.getenv("SMTP_PORT", 465))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(user, pwd)
        smtp.send_message(msg)