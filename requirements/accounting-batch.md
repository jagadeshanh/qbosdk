# Batch API requirements

Source: [Intuit Batch reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/batch), reviewed using “Copy all for AI”.

- Submit `POST /v3/company/<realmId>/batch` with `BatchItemRequest` containing up to 30 independent items. Items may create, update, delete, read or query supported entities. Individual items must not depend on another item's outcome, and execution order is not guaranteed.
- Preserve the entire `BatchItemResponse` including item `bId`, successes, and per-item faults; a successful HTTP response does not imply all items succeeded. Do not automatically retry mutations or ambiguous failures.
- Authenticate once using the configured company and environment. The API documents a limit of 40 batch requests per minute per realm and up to 1,000 returned objects; callers remain responsible for throttling.
- Test request encoding, bounds, item correlation, partial faults, malformed responses, and HTTP failures. Live sandbox verification is outstanding.
