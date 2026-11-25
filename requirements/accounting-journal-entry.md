# JournalEntry

Source: [Intuit JournalEntry API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalentry), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /journalentry` with at least one debit and one credit distribution line whose totals balance; tax settings and details may affect the balance. `CurrencyRef` and `GlobalTaxCalculation` can be required depending on company configuration. `DocNumber` is limited to 21 characters and `PrivateNote` to 4,000.
- Read `GET /journalentry/{id}` and query `GET /query`, with pagination. Full update `POST /journalentry` includes current `Id`, `SyncToken` and all writable fields and lines to retain; omitted fields are cleared. Sparse update sets `sparse: true` and leaves omitted fields untouched.
- Delete `POST /journalentry?operation=delete` using current `Id` and `SyncToken`. Opt in to `include=allowduplicatedocnum` for duplicate numbers or `include=allowautodocnum` for automatic numbering. The SDK exposes these as mutually exclusive options pending confirmation that Intuit supports combining them.
- QuickBooks validates accounting balance and tax rules; preserve faults and do not automatically retry writes.
