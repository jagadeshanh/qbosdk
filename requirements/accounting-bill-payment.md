# BillPayment requirements

Source: [Intuit BillPayment reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/billpayment), reviewed using “Copy all for AI”.

- BillPayment represents a payment against bills, vendor credits or journal entries. Create and full update require `VendorRef`, `Line`, `TotalAmt`, `PayType`, and the matching `CheckPayment` or `CreditCardPayment` object; `TotalAmt` cannot be negative. Currency is conditionally required for multicurrency companies. Preserve full response envelopes and decimal amounts.
- Create `POST /billpayment`; read `GET /billpayment/<id>`; query `GET /query?query=...`, with pagination; full update `POST /billpayment` with `Id`, `SyncToken`, and all writable fields to retain. Omitted fields are cleared by a full update.
- Delete uses `POST /billpayment?operation=delete` with `Id` and `SyncToken`. Void uses `POST /billpayment?operation=update&include=void` and a sparse body containing `Id`, `SyncToken`, and `sparse: true`. Voiding clears lines and amounts but retains the transaction.
- Support explicit `include=allowduplicatedocnum` on creation and full update. Respect Intuit's company-dependent rules; preserve upstream faults, use no automatic write retries, and do not make live payment mutations in tests.
- Test all operations, exact decimal handling, pagination, the void and delete request contracts, validation, and upstream faults. Live sandbox verification remains outstanding.
