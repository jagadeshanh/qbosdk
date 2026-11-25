"""Verify and decode QuickBooks Online CloudEvents webhook deliveries."""

import base64
import hmac
import json
from dataclasses import dataclass, field
from typing import Optional


class WebhookError(ValueError):
    """A QuickBooks webhook could not be verified or decoded."""


class WebhookSignatureError(WebhookError):
    """The Intuit signature is missing or does not match the request body."""


class WebhookPayloadError(WebhookError):
    """An authenticated delivery does not match the QuickBooks event format."""


@dataclass(frozen=True)
class WebhookEvent:
    """A QuickBooks change notification. Timestamps retain their wire precision."""

    event_id: str
    event_type: str
    occurred_at: str
    realm_id: str
    entity_id: str
    data: dict = field(repr=False)


class WebhookVerifier:
    """Verify webhook deliveries for one Intuit app and environment."""

    def __init__(self, verifier_token: str):
        if not isinstance(verifier_token, str) or not verifier_token.strip():
            raise ValueError("A QuickBooks webhook verifier token is required.")
        self._key = verifier_token.encode("utf-8")

    def parse(self, body: bytes, signature: Optional[str]) -> list[WebhookEvent]:
        """Verify the raw request body, then return events in delivery order."""
        if not isinstance(body, bytes):
            raise TypeError("QuickBooks webhook body must be the raw request bytes.")
        if not isinstance(signature, str) or not signature.isascii():
            raise WebhookSignatureError("Missing or invalid Intuit webhook signature.")
        expected = base64.b64encode(hmac.digest(self._key, body, "sha256"))
        if not hmac.compare_digest(expected, signature.encode("ascii")):
            raise WebhookSignatureError("Missing or invalid Intuit webhook signature.")

        try:
            records = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object,
                                 parse_constant=_reject_json_constant)
        except (ValueError, RecursionError):
            raise WebhookPayloadError("QuickBooks webhook body must contain valid UTF-8 JSON.") from None
        if not isinstance(records, list):
            raise WebhookPayloadError("QuickBooks webhook body must be a CloudEvents array.")
        return [_parse_event(record, index) for index, record in enumerate(records)]


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON object key.")
        value[key] = item
    return value


def _reject_json_constant(_value):
    raise ValueError("Invalid JSON constant.")


def _parse_event(record, index):
    if not isinstance(record, dict):
        raise WebhookPayloadError(f"Webhook event {index} must be an object.")
    if record.get("specversion") != "1.0":
        raise WebhookPayloadError(f"Webhook event {index} must use CloudEvents specversion 1.0.")
    for key in ("id", "type", "time", "intuitaccountid", "intuitentityid"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise WebhookPayloadError(f"Webhook event {index} requires a nonempty string for {key}.")
    data = record.get("data")
    if data is not None and not isinstance(data, dict):
        raise WebhookPayloadError(f"Webhook event {index} data must be an object when present.")
    return WebhookEvent(
        event_id=record["id"],
        event_type=record["type"],
        occurred_at=record["time"],
        realm_id=record["intuitaccountid"],
        entity_id=record["intuitentityid"],
        data={} if data is None else data,
    )
