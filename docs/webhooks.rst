Webhooks
========

Configure the endpoint URL and subscribe to entities and operations under **Webhooks** in your Intuit app dashboard. Configure Development and Production separately. Each company must authorize the app through OAuth. Copy the verifier token from the matching environment into your secret store. See `Intuit's configuration guide <https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks/configure-webhooks>`_.

Receive notifications
---------------------

Construct a verifier once for each endpoint. In your POST handler, read the original bytes and retrieve the ``intuit-signature`` header through your framework's case-insensitive header lookup. Pass the raw bytes to the verifier before accessing any framework-parsed JSON::

    import os

    from qbosdk import WebhookPayloadError, WebhookSignatureError, WebhookVerifier

    verifier = WebhookVerifier(os.environ["QBO_WEBHOOK_VERIFIER_TOKEN"])

    def receive_webhook(raw_body, signature):
        try:
            events = verifier.parse(raw_body, signature)
        except WebhookSignatureError:
            return 401
        except WebhookPayloadError:
            return 400

        enqueue_batch(events)  # Replace with your application's durable queue.
        return 200

Enforce a request body size limit at your server. Acknowledge after the queue accepts the batch and within three seconds. Let enqueue failures return a non-200 response so Intuit can retry. The SDK checks the signature and parses the CloudEvents array. Your application's HTTP layer sends the response.

Process queued events
---------------------

Each ``WebhookEvent`` has ``realm_id``, ``entity_id``, ``event_id``, ``event_type`` (for example, ``qbo.account.created.v1``), ``occurred_at`` in its original wire representation, and a ``data`` dictionary. Look up the OAuth connection by ``realm_id`` for every event. A batch can contain events for multiple companies.

Use a durable idempotency key such as ``(realm_id, event_id)``, scoped to the app and environment. Webhooks can arrive out of order, so use the occurrence time for ordering and reconcile missing updates with ``AccountingClient.change_data_capture()`` where supported. See `Intuit's webhook best practices <https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks/best-practices>`_.
