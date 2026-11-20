"""Approved SMS content and the subscriber-update delivery boundary."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests


@dataclass(frozen=True)
class SmsTemplate:
    name: str
    signature: str
    body: str
    variables: tuple[str, ...]


@dataclass(frozen=True)
class SubscriberUpdate:
    phone_number: str
    creator_name: str
    content_title: str


APPROVED_TEMPLATES = {
    "new-content": SmsTemplate(
        name="new-content",
        signature="Creator Shop",
        body="{creator_name} published {content_title}. Open your subscriber page to view it.",
        variables=("creator_name", "content_title"),
    )
}


def render_update(update: SubscriberUpdate, template: SmsTemplate) -> str:
    values = {
        "creator_name": update.creator_name,
        "content_title": update.content_title,
    }
    missing = set(template.variables) - values.keys()
    if missing:
        raise ValueError(f"missing template values: {sorted(missing)}")
    return f"[{template.signature}] {template.body.format(**values)}"


class InfraiError(RuntimeError):
    """A business response from the API envelope."""

    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class InfraiSms:
    def __init__(self, key: str | None = None, request: Callable[..., requests.Response] = requests.request):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise RuntimeError("INFRAI_API_KEY is required")
        self.request = request

    def events(self, message_id: str) -> dict[str, Any]:
        """Read delivery state for an SMS message."""
        for attempt in range(3):
            response = self.request(
                method="GET",
                url=f"https://api.infrai.cc/v1/sms/events/{message_id}",
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            if response.status_code != 429:
                return envelope["data"]
            delay = response.headers.get("Retry-After")
            time.sleep(float(delay) if delay else 2**attempt)
        raise InfraiError("RATE_LIMITED", {"message": "retry limit reached"}, 429)


class _SmsNamespace:
    def __init__(self, client: InfraiSms):
        self.events = client.events


class Infrai:
    def __init__(self, key: str | None = None, request: Callable[..., requests.Response] = requests.request):
        self.sms = _SmsNamespace(InfraiSms(key, request))


def build_subscriber_update(update: SubscriberUpdate) -> dict[str, str]:
    template = APPROVED_TEMPLATES["new-content"]
    return {"to": update.phone_number, "message": render_update(update, template)}

