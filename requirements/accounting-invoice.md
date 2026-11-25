# Invoice

Source: [Intuit Invoice API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /invoice` with `CustomerRef` and at least one line; sales, group and inline subtotal lines are documented. `DocNumber` is limited to 21 characters and `PrivateNote` to 4,000. Currency, tax, project, address and email requirements depend on company configuration. Taxable transactions are limited to 750 lines.
- Read `GET /invoice/{id}`, query `GET /query`, and retrieve PDF using `GET /invoice/{id}/pdf`. Send `POST /invoice/{id}/send`, optionally with `sendTo`, which sends an email and changes delivery information.
- Full update `POST /invoice` includes the current `Id`, `SyncToken`, and all writable fields to retain; omitted writable fields become null. Sparse update sets `sparse: true` and changes only supplied fields. `include=allowduplicatedocnum` is an explicit opt-in for duplicate document numbers.
- Delete `POST /invoice?operation=delete` with current identity after unlinking related transactions. Void `POST /invoice?operation=void` with current identity: amounts and quantities become zero and `Voided` is added to the private note. Preserve responses and faults; do not automatically retry writes or sends.
