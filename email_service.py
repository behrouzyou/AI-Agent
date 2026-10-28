import smtplib
import ssl
from email.message import EmailMessage

from config import GMAIL_ADDRESS, GMAIL_PASSWORD


def send_gmail(to, subject, content):
    if not GMAIL_ADDRESS:
        raise ValueError("GMAIL_ADDRESS is not set")

    if not GMAIL_PASSWORD:
        raise ValueError("is not set")

    message = EmailMessage()
    message["From"] = GMAIL_ADDRESS
    message["To"] = to
    message["Subject"] = subject
    message.set_content(content)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        smtp.send_message(message)

    return {
        "status": "sent",
        "to": to,
        "subject": subject
    }