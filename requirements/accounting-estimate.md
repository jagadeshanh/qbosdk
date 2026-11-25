# Estimate

Source: [Intuit Estimate API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/estimate), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /estimate` with `CustomerRef` and at least one sales-item or group line. Currency, tax, project, shipping-origin, and email requirements depend on company configuration and email status.
- Read `GET /estimate/{id}`, query `GET /query`, and retrieve PDF via `GET /estimate/{id}/pdf`. Return complete response data and preserve faults.
- Delete `POST /estimate?operation=delete` with current `Id` and `SyncToken`. Send via `POST /estimate/{id}/send`, optionally specifying the email recipient according to the Intuit reference. This sends an email and changes delivery status.
- Full update `POST /estimate` uses current identity and all writable fields to retain; omitted fields are cleared. Sparse update sets `sparse: true` and changes only supplied fields. `DocNumber` is limited to 21 characters and `PrivateNote` to 4,000; company preferences and locale affect document numbers. A taxable estimate is limited to 750 lines. Do not automatically retry mutations or sending.
