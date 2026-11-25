# QuickBooks Online webhooks

Source: [Intuit Configure webhooks](https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks/configure-webhooks) and [webhook best practices](https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks/best-practices).

## Verification and event contract

- Intuit sends a signed JSON POST to the host application's configured endpoint. Use the app's verifier token for that endpoint's Development or Production environment. This token is separate from OAuth credentials.
- Verify the original request bytes with HMAC-SHA256 using the UTF-8 token as the key. Base64-encode the digest and compare it in constant time against the `intuit-signature` header before decoding the body.
- Accept the CloudEvents 1.0 array described in the configuration guide. Preserve event order, event ID, full event type, occurrence time as a string, entity ID, realm ID, and additional data. A delivery may include multiple realms.
- Reject an invalid signature separately from a malformed authenticated payload. Reject a malformed batch as a unit. Keep credentials, signatures, and body contents out of errors.
- The host enforces request size limits and associates each realm ID with an authorized OAuth connection.

## Host application responsibilities

Set up Development and Production subscriptions separately in the Intuit dashboard. Test companies must complete OAuth before notifications can arrive. The host should durably enqueue verified events, acknowledge with HTTP 200 within three seconds, and process asynchronously. Retries can redeliver events. Use the event ID and realm ID in an idempotency key scoped to the app and environment, and account for out-of-order delivery. Consider Change Data Capture for reconciliation where the entity supports it.

## Verification

Use synthetic signed batches to test multiple realms, mutated bodies, wrong tokens, malformed payloads, optional event data, and future event types. Live verification requires a reachable Development endpoint, an active subscription, and an authorized sandbox company.
