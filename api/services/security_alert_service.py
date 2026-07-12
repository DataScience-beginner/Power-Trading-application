"""Structured security alerts with an optional bounded webhook adapter."""

import asyncio
from datetime import UTC, datetime
import json
import logging
import os

import requests


logger = logging.getLogger("innowatt.security")


async def emit_security_alert(event_type: str, correlation_id: str, source: str, detail: str) -> None:
    payload = {
        "event_type": event_type,
        "correlation_id": correlation_id,
        "source": source,
        "detail": detail[:500],
        "occurred_at": datetime.now(UTC).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
    logger.warning(json.dumps(payload, separators=(",", ":")))
    url = os.getenv("SECURITY_ALERT_WEBHOOK_URL")
    if not url:
        return
    token = os.getenv("SECURITY_ALERT_WEBHOOK_TOKEN", "")

    def deliver() -> None:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        requests.post(url, json=payload, headers=headers, timeout=3).raise_for_status()

    try:
        await asyncio.wait_for(asyncio.to_thread(deliver), timeout=4)
    except Exception:
        logger.exception("Security alert webhook delivery failed", extra={"correlation_id": correlation_id})
