# CreditMemo

Source: [Intuit CreditMemo API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditmemo), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /creditmemo`: requires `CustomerRef` and at least one sales-item or group line. `CurrencyRef`, `ProjectRef`, tax settings, and `BillEmail` may be required depending on company configuration and email status.
- Read `GET /creditmemo/{id}`; query using `GET /query`; fetch PDF using `GET /creditmemo/{id}/pdf` with PDF response handling.
- Full update `POST /creditmemo` includes `Id`, `SyncToken`, required fields, and all writable fields to retain; omitted writable fields become null.
- Delete `POST /creditmemo?operation=delete` with `Id` and `SyncToken`; this is a destructive operation.
- Send `POST /creditmemo/{id}/send`, optionally with `sendTo`; this sends email and updates email status and delivery information.
- `DocNumber` has a 21-character limit; `PrivateNote` has a 4,000-character limit. Preserve Intuit response and fault details. Do not automatically retry writes or email sends.
