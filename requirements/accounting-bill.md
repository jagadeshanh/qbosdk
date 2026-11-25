# Bill requirements

Source: [Intuit Bill reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill), reviewed using “Copy all for AI”.

- A Bill represents an accounts-payable transaction. Preserve the complete Bill response, including nested lines, linked transactions, metadata and decimal monetary values.
- `POST /v3/company/<realmId>/bill` creates a Bill. `VendorRef` and `Line` are required; the caller supplies line detail and locale-dependent currency and tax fields. `DocNumber` has a 21-character limit and `PrivateNote` has a 4000-character limit. For a duplicate document number, Intuit documents the opt-in query parameter `include=allowduplicatedocnum`.
- `GET /query?query=...` queries Bills with pagination; `GET /bill/<id>` reads one. Preserve original response envelopes.
- `POST /bill` performs a full update with `Id`, `SyncToken`, `VendorRef`, and `Line`; omitted writable fields are cleared. Do not automatically retry or overwrite stale versions.
- `POST /bill?operation=delete` deletes a Bill using at least `Id` and `SyncToken`; callers must unlink associated transactions first. This operation changes financial data and is not used by offline tests.
- Validate structural fields, documented lengths and request safety locally; honor the `validate_fields` option for field limits. Intuit validates company-dependent preferences and nested accounting rules. Preserve fault details and decimal precision in requests and responses.
- Test create, query/pagination, read, full update, delete, duplicate-number opt-in, decimal serialization, validation and faults. Live sandbox verification remains outstanding.
