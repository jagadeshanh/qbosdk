# Deposit

Source: [Intuit Deposit API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /deposit` with a destination `DepositToAccountRef` and at least one line. A direct line references `DepositLineDetail.AccountRef`; a linked line specifies `LinkedTxn`. Types can be mixed. Currency and tax fields may be required depending on company configuration.
- Read `GET /deposit/{id}` and query `GET /query`, with pagination. Preserve the response and fault envelopes.
- Full update `POST /deposit` requires the current `Id`, `SyncToken`, destination account, lines, and all writable fields to retain. Omitted writable fields are cleared. Sparse update sets `sparse: true`, supplies identity and changed fields, and leaves omitted fields untouched; Intuit's example omits lines despite their required marking in the attribute table.
- Delete `POST /deposit?operation=delete` with current `Id` and `SyncToken`. `PrivateNote` is limited to 4,000 characters. No write is automatically retried.
