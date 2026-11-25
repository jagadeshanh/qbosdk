# VendorCredit

[Intuit VendorCredit](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorcredit)

Vendor credits record accounts-payable credit for goods or services. Supply `VendorRef.value` and at least one line with an `Amount`. Intuit supports item-based and account-based expense lines, uses `CurrencyRef` for multicurrency companies, and calculates `TotalAmt` and the remaining credit balance. A credit can have links to reimbursable charges.

| Operation | Company-relative request |
| --- | --- |
| Create | `POST /vendorcredit` |
| Read | `GET /vendorcredit/{id}` |
| Query | `GET /query` with `SELECT … FROM VendorCredit` and pagination |
| Full update | `POST /vendorcredit` with current identity, required and retained writable fields, and `sparse: false` |
| Delete | `POST /vendorcredit?operation=delete` with current identity |

Reads and writes return the complete `VendorCredit` envelope. Queries return `QueryResponse.VendorCredit`. Versioned operations use `Id` and current `SyncToken`. Limit document number to 21 characters and private note to 4,000. For an intentional duplicate document number, `allow_duplicate_doc_number=True` sets `include=allowduplicatedocnum`.
