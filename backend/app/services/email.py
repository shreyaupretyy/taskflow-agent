from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import aiosmtplib

from app.core.config import settings


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM

    async def send_email(self, to: List[str], subject: str, body: str, html: bool = False) -> dict:
        """Send an email."""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.email_from
            message["To"] = ", ".join(to)
            message["Subject"] = subject

            if html:
                part = MIMEText(body, "html")
            else:
                part = MIMEText(body, "plain")

            message.attach(part)

            if self.smtp_user and self.smtp_password:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    use_tls=True,
                )

                return {"success": True, "message": "Email sent successfully", "to": to}
            else:
                # Email not configured, just log
                print(f"Email would be sent to {to} with subject: {subject}")
                return {"success": True, "message": "Email not configured - logged only", "to": to}

        except Exception as e:
            return {"success": False, "error": str(e), "to": to}

    async def send_workflow_notification(
        self, to: List[str], workflow_name: str, execution_status: str, execution_id: int
    ) -> dict:
        """Send workflow execution notification."""
        subject = f"Workflow '{workflow_name}' - {execution_status}"

        body = f"""
        Your workflow '{workflow_name}' has {execution_status}.

        Execution ID: {execution_id}
        Status: {execution_status}

        View details in your TaskFlow Agent dashboard.
        """

        return await self.send_email(to, subject, body)


# Global instance
email_service = EmailService()
