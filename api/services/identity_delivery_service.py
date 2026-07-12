"""Production email/SMS adapters with fail-closed configuration."""

from email.message import EmailMessage
import json
import os
import smtplib

import requests


class IdentityDeliveryService:
    def send(self, channel: str, destination: str, code: str) -> str:
        if channel == "email":
            return self._email(destination, code)
        return self._sms(destination, code)

    def _email(self, destination: str, code: str) -> str:
        host = os.getenv("SMTP_HOST")
        sender = os.getenv("SMTP_FROM")
        if not host or not sender:
            return "not_configured"
        message = EmailMessage()
        message["Subject"] = "Innowatt account recovery"
        message["From"] = sender
        message["To"] = destination
        message.set_content(f"Your Innowatt recovery code is {code}. It expires in 10 minutes. If you did not request this, contact your administrator.")
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as server:
            server.starttls()
            username = os.getenv("SMTP_USERNAME")
            if username:
                server.login(username, os.getenv("SMTP_PASSWORD", ""))
            server.send_message(message)
        return "sent"

    def _sms(self, destination: str, code: str) -> str:
        webhook = os.getenv("SMS_WEBHOOK_URL")
        if not webhook:
            return "not_configured"
        response = requests.post(
            webhook,
            headers={"Authorization": f"Bearer {os.getenv('SMS_WEBHOOK_TOKEN', '')}", "Content-Type": "application/json"},
            data=json.dumps({"to": destination, "message": f"Innowatt recovery code: {code}. Expires in 10 minutes."}),
            timeout=10,
        )
        response.raise_for_status()
        return "sent"
