# CreditCardPayment

Source: [Intuit CreditCardPayment API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditcardpayment), reviewed using Copy all for AI. Only home-currency bank and credit-card accounts are supported. Sandbox verification remains pending.

- Create `POST /creditcardpayment` with `TxnDate`, `Amount`, `BankAccountRef`, and `CreditCardAccountRef`. `PrivateNote` and `Memo` each have a 4,000-character limit.
- Query with `GET /query` and `SELECT ... FROM CreditCardPayment`; read with `GET /creditcardpayment/{id}`. Intuit's object and delete examples use the `CreditCardPaymentTxn` response key. The query response key is not shown in the explorer and requires live verification.
- Full update `POST /creditcardpayment` requires `Id`, `SyncToken`, and all writable fields to retain; omitted writable fields are cleared.
- Sparse update uses `sparse: true`, `Id`, `SyncToken`, and changed fields. The reference says omitted fields remain unchanged but also lists the create fields as required; actual enforcement needs sandbox verification.
- Delete `POST /creditcardpayment?operation=delete` requires the complete object returned by read, including its current `Id` and `SyncToken`. No mutation is automatically retried.
