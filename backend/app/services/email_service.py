"""
FK94 Security Platform - Email Service
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.resend_api_key = settings.RESEND_API_KEY
        self.to_email = settings.CONTACT_EMAIL_TO

    @property
    def is_configured(self) -> bool:
        return bool(self.resend_api_key and self.to_email)

    async def send_new_lead_notification(self, *, name: str, email: str, subject: str, message: str) -> bool:
        """Send a lead notification email if Resend is configured."""
        if not self.is_configured:
            return False

        payload = {
            "from": "FK94 Platform <onboarding@resend.dev>",
            "to": [self.to_email],
            "subject": f"[FK94 Lead] {subject}",
            "html": (
                "<h3>New lead received</h3>"
                f"<p><strong>Name:</strong> {name}</p>"
                f"<p><strong>Email:</strong> {email}</p>"
                f"<p><strong>Subject:</strong> {subject}</p>"
                f"<p><strong>Message:</strong><br>{message}</p>"
            ),
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if res.status_code >= 300:
                    logger.error(f"Resend send failed [{res.status_code}]: {res.text[:200]}")
                    return False
            return True
        except Exception as exc:
            logger.error(f"Resend send exception: {exc}")
            return False


email_service = EmailService()
