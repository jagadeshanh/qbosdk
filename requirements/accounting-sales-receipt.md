# SalesReceipt

[Intuit SalesReceipt reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt)

Sales receipts record a sale paid at the time of purchase. Create requires at least one sales item or group line. The create operation's minimum payload allows omitting `CustomerRef`. The full update contract requires the customer reference. Send `CurrencyRef` for multicurrency companies and `ProjectRef` when applicable. QuickBooks uses Undeposited Funds when `DepositToAccountRef` is omitted. The documented line limit for taxable receipts is 750. QuickBooks determines whether a receipt is taxable and validates the relevant company, tax, currency, and product rules.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /salesreceipt` with required fields | SalesReceipt envelope |
| Delete | `POST /salesreceipt?operation=delete` with current identity | SalesReceipt deletion envelope |
| Void | `POST /salesreceipt?operation=update&include=void` with current identity and `sparse: true` | Voided SalesReceipt envelope |
| PDF | `GET /salesreceipt/{id}/pdf` accepting `application/pdf` | PDF bytes |
| Query | `GET /query` with `SELECT … FROM SalesReceipt` and pagination | `QueryResponse.SalesReceipt` |
| Read | `GET /salesreceipt/{id}` | SalesReceipt envelope |
| Send | `POST /salesreceipt/{id}/send` with empty octet-stream body and optional `sendTo` | SalesReceipt envelope including delivery information |
| Full update | `POST /salesreceipt` with current identity, required and retained writable fields, and `sparse: false` | SalesReceipt envelope |
| Sparse update | `POST /salesreceipt` with current identity, changed fields, and `sparse: true` | SalesReceipt envelope |

Versioned writes require the latest `Id` and `SyncToken`. A void keeps the transaction, zeroes all amounts and quantities, and prepends `Voided` to the private note. Remove an associated deposit separately before voiding a deposited receipt. A send uses the stored billing email unless a recipient is supplied. Intuit saves an explicit recipient to `BillEmail.Address`, sets `EmailStatus` to `EmailSent`, and records `DeliveryInfo`.

Limit `PaymentRefNum` and `DocNumber` to 21 and `PrivateNote` to 4,000 characters. Document numbering follows company preferences and locale. The SDK preserves QuickBooks faults and issues writes once per call.
