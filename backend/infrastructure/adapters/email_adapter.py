import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.domain.ports.email_port import EmailSenderPort

# Backwards-compat alias — older code imports `EmailPort` from here.
EmailPort = EmailSenderPort


class SMTPEmailAdapter(EmailSenderPort):
    """SMTP-based email adapter for sending emails."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@clipsmith.com")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def send(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        if not self.smtp_user or not self.smtp_password:
            print(f"[EMAIL] SMTP not configured. Would send to {to}: {subject}")
            print(f"[EMAIL] Body: {body}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, msg.as_string())
            return True
        except Exception as e:
            print(f"[EMAIL] Failed to send email to {to}: {e}")
            return False

    # Backwards-compat
    def send_email(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        return self.send(to, subject, body, html_body)


class ConsoleEmailAdapter(EmailSenderPort):
    """Console-based email adapter for development/testing."""

    def send(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        print("=" * 60)
        print(f"[DEV EMAIL] To: {to}")
        print(f"[DEV EMAIL] Subject: {subject}")
        print(f"[DEV EMAIL] Body:\n{body}")
        if html_body:
            print(f"[DEV EMAIL] HTML Body:\n{html_body}")
        print("=" * 60)
        return True

    def send_email(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        return self.send(to, subject, body, html_body)


def get_email_adapter() -> EmailSenderPort:
    if os.getenv("SMTP_HOST") and os.getenv("SMTP_USER"):
        return SMTPEmailAdapter()
    return ConsoleEmailAdapter()
