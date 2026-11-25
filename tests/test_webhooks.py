import base64
import hashlib
import hmac
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

from qbosdk import WebhookEvent, WebhookPayloadError, WebhookSignatureError, WebhookVerifier


def signature_for(body, token="sandbox-verifier"):
    digest = hmac.new(token.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.verifier = WebhookVerifier("sandbox-verifier")
        self.event = {
            "specversion": "1.0",
            "id": "event-1",
            "source": "intuit.example",
            "type": "qbo.account.created.v1",
            "datacontenttype": "application/json",
            "time": "2025-09-10T21:31:25.179851517Z",
            "intuitentityid": "1234",
            "intuitaccountid": "310687",
            "data": {"memo": "Café"},
        }

    def test_signed_multi_realm_batch_preserves_ids_and_wire_time(self):
        second = {**self.event, "id": "event-2", "intuitaccountid": "310688",
                  "intuitentityid": "5678", "type": "qbo.futureentity.changed.v2"}
        del second["data"]
        body = json.dumps([self.event, second], indent=2, ensure_ascii=False).encode("utf-8")
        result = self.verifier.parse(body, signature_for(body))
        first = WebhookEvent("event-1", "qbo.account.created.v1", self.event["time"],
                             "310687", "1234", {"memo": "Café"})
        self.assertEqual(result, [
            first,
            replace(first, event_id="event-2", event_type="qbo.futureentity.changed.v2",
                    realm_id="310688", entity_id="5678", data={}),
        ])

    def test_independent_signature_vector_and_empty_batch(self):
        signature = "0EGLsAbq/mVLecUSBCMYSlQ5Elh5fUoweuYq/n98Ky8="
        self.assertEqual(self.verifier.parse(b"[]", signature), [])

    def test_bad_signatures_fail_before_json_parsing(self):
        body = b"[]"
        original = signature_for(body)
        cases = (
            (body, None), (body, ""), (body, "☃"), (body, original + ", " + original),
            (body, signature_for(body, "production-verifier")), (b"[]\n", original),
            (b"{broken", original),
        )
        with patch("qbosdk.webhooks.json.loads") as decode:
            for data, signature in cases:
                with self.subTest(data=data), self.assertRaises(WebhookSignatureError):
                    self.verifier.parse(data, signature)
            decode.assert_not_called()

    def test_malformed_authenticated_batches(self):
        cases = (
            b"\xff", b"{broken", b'{"eventNotifications":[]}', b"[null]",
            b'[{"id":"one","id":"two"}]', b"[NaN]",
            json.dumps([self.event, {**self.event, "intuitaccountid": None}]).encode(),
            json.dumps([{**self.event, "specversion": "2.0"}]).encode(),
            json.dumps([{**self.event, "data": []}]).encode(),
        )
        for body in cases:
            with self.subTest(body=body), self.assertRaises(WebhookPayloadError) as error:
                self.verifier.parse(body, signature_for(body))
            self.assertNotIn("sandbox-verifier", str(error.exception))
            self.assertNotIn("310687", str(error.exception))

    def test_null_event_data_is_empty(self):
        body = json.dumps([{**self.event, "data": None}]).encode()
        self.assertEqual(self.verifier.parse(body, signature_for(body))[0].data, {})

    def test_constructor_and_raw_body_validation(self):
        for token in ("", " ", None):
            with self.subTest(token=token), self.assertRaises(ValueError):
                WebhookVerifier(token)
        with self.assertRaises(TypeError):
            self.verifier.parse("[]", signature_for(b"[]"))
