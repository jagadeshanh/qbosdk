# PurchaseOrder

[Intuit PurchaseOrder reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder)

A PurchaseOrder is a non-posting request for a vendor to provide goods or services. Create requires `VendorRef.value` and a nonempty `Line` list. Supply an accounts payable liability account as `APAccountRef.value`, especially when more than one exists. The API reference allows the company default to supply the account on create. An item-based expense line references an item with an expense account. The object also describes account-based expense lines. Intuit enforces line and company rules. Supply `CurrencyRef` when the company uses multicurrency.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /purchaseorder` | PurchaseOrder envelope |
| Delete | `POST /purchaseorder?operation=delete` with current identity | PurchaseOrder deletion envelope |
| PDF | `GET /purchaseorder/{id}/pdf` accepting `application/pdf` | PDF bytes |
| Query | `GET /query` using `SELECT … FROM PurchaseOrder` and pagination | `QueryResponse.PurchaseOrder` |
| Read | `GET /purchaseorder/{id}` | PurchaseOrder envelope |
| Send | `POST /purchaseorder/{id}/send` with empty octet-stream body and optional `sendTo` | PurchaseOrder envelope |
| Full update | `POST /purchaseorder` with current `Id` and `SyncToken`, required fields, retained writable fields, and `sparse: false` | PurchaseOrder envelope |

Unlink associated transactions before deleting. Include `APAccountRef` in full updates. Omitted writable fields may be cleared in full updates. Sending uses the stored `POEmail.Address` unless a recipient is supplied. Intuit documents that sending sets `EmailStatus` to `EmailSent` and an explicit recipient updates the saved address at minor version 17 or later.

`DocNumber` is limited to 21 characters. `Memo` (shown to the vendor) and `PrivateNote` (internal) are each limited to 4,000 characters. Duplicate document numbers require explicit opt-in with `include=allowduplicatedocnum`. Preserve fault details and issue each write or send once per SDK call.
