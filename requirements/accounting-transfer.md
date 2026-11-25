# Transfer

[Intuit Transfer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transfer)

A Transfer records funds moving between two QuickBooks accounts. Create and full update require `FromAccountRef.value`, `ToAccountRef.value`, and a decimal `Amount`. Accept both JSON numbers and decimal strings as shown in Intuit's examples. The `PrivateNote` limit is 4,000 characters. Intuit validates whether the accounts can be used in the transfer.

| Operation | Company-relative request |
| --- | --- |
| Create | `POST /transfer` |
| Read | `GET /transfer/{id}` |
| Query | `GET /query` with `SELECT … FROM Transfer` and pagination |
| Full update | `POST /transfer` with current identity, retained writable fields, and `sparse: false` |
| Sparse update | `POST /transfer` with current identity, changed fields, and `sparse: true` |
| Delete | `POST /transfer?operation=delete` with the complete latest record returned by a read |

Reads and writes return the complete `Transfer` envelope. Queries return `QueryResponse.Transfer`. Versioned requests use `Id` and the latest `SyncToken`. For deletion, pass the complete record including source and destination accounts and amount. Preserve the payload and issue the request once.
