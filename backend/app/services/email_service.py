import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@veogen.local")
EMAIL_SMTP = os.getenv("EMAIL_SMTP", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
EMAIL_DEV_OUTBOX = os.getenv("EMAIL_DEV_OUTBOX", "dev_emails/")

os.makedirs(EMAIL_DEV_OUTBOX, exist_ok=True)

def send_email(to: str, subject: str, body: str, html: str = None):
    """Send an email via SMTP or write to file if in dev mode."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    part1 = MIMEText(body, "plain")
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, "html")
        msg.attach(part2)
    try:
        if EMAIL_SMTP == "dev":
            # Write to file for dev
            filename = f"{EMAIL_DEV_OUTBOX}/email_{datetime.utcnow().isoformat()}_{to.replace('@','_')}.eml"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(msg.as_string())
            print(f"[DEV EMAIL] Written to {filename}")
            return True
        else:
            with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
                if EMAIL_USER and EMAIL_PASS:
                    server.starttls()
                    server.login(EMAIL_USER, EMAIL_PASS)
                server.sendmail(EMAIL_FROM, to, msg.as_string())
            print(f"[EMAIL] Sent to {to}")
            return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False 