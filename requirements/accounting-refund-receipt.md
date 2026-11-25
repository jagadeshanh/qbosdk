# RefundReceipt

[Intuit RefundReceipt reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt)

A refund receipt records money returned to a customer. Create and full update require `DepositToAccountRef.value` for an appropriate Bank or Other Current Asset account and a `Line` list containing a sales item or group. Description and discount lines can accompany them. Subtotal and calculated amounts are read-only. Supply `CurrencyRef` for multicurrency companies. Intuit documents `PaymentRefNum` for bank-account refunds and requires it when `PrintStatus=PrintComplete`. `BillEmail` is required when `EmailStatus=NeedToSend`. Supply credit card details only for transactions processed through Intuit Payments. `CustomSalesTax` is reserved and cannot be used as the transaction tax code.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /refundreceipt` with required fields | RefundReceipt envelope |
| Read | `GET /refundreceipt/{id}` | RefundReceipt envelope |
| Query | `GET /query` with `SELECT … FROM RefundReceipt` and pagination | `QueryResponse.RefundReceipt` |
| Full update | `POST /refundreceipt` with current identity, required and retained writable fields, and `sparse: false` | RefundReceipt envelope |
| Sparse update | `POST /refundreceipt` with current identity, changed fields, and `sparse: true` | RefundReceipt envelope |
| Delete | `POST /refundreceipt?operation=delete` with current identity | RefundReceipt deletion envelope |
| PDF | `GET /refundreceipt/{id}/pdf` accepting `application/pdf` | PDF bytes |
| Send | `POST /refundreceipt/{id}/send` with empty octet-stream body and optional `sendTo` | RefundReceipt envelope with delivery information |

Updates and delete require `Id` and the latest `SyncToken`. Unlink transactions before deleting. A full update can clear omitted writable fields. A sparse update leaves omitted fields untouched. Sending uses the stored email unless an explicit recipient is supplied. An explicit recipient updates `BillEmail.Address`.

Limit `PaymentRefNum` to 100, `DocNumber` to 21, and `PrivateNote` to 4,000 characters. Supported payment types are Cash, Check, CreditCard, and Other. Locale-specific document numbering and company-dependent constraints are validated by Intuit. Use `allow_duplicate_doc_number=True` only for intentional duplicate document numbers. The SDK preserves fault details and issues writes and sends once per call.
