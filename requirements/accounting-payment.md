# Payment

[Intuit Payment reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/payment)

Payment records amounts received from customers in QuickBooks Online. A payment can be unapplied and recorded as a credit, or applied to one or more transactions through ordered `Line` entries. Each link identifies its destination with `TxnId` and `TxnType`. Documented types include Invoice, CreditMemo, JournalEntry, Expense, Check, and CreditCardCredit.

## Object and validation

- Create requires numeric `TotalAmt` and a `CustomerRef.value` string. Supply `CurrencyRef` when multicurrency is enabled and `ProjectRef` when applicable.
- Optional fields include `TxnDate`, `PaymentMethodRef`, `DepositToAccountRef`, `ExchangeRate`, `PaymentRefNum`, and `PrivateNote` (maximum 4,000 characters). QuickBooks defaults the deposit account to Undeposited Funds when omitted. Supply credit card details only for payments transacted through Intuit Payments.
- Preserve response fields such as `UnappliedAmt`, `MetaData`, and `TaxExemptionRef`. Use the latest `Id` and `SyncToken` for changes to an existing payment.

## Operations

Paths are relative to `/v3/company/{realmId}`.

| Operation | Request | Result |
| --- | --- | --- |
| Create | `POST /payment` | Payment envelope |
| Read | `GET /payment/{id}` | Payment envelope |
| Query | `GET /query` with `SELECT … FROM Payment` | Paginated `QueryResponse.Payment` |
| Full update | `POST /payment` with current identity, required and retained writable fields, and `sparse: false` | Payment envelope |
| Sparse update | `POST /payment` with current identity, changes, and `sparse: true` | Payment envelope |
| Delete | `POST /payment?operation=delete` with current identity | Payment deletion envelope |
| Void | `POST /payment?operation=update&include=void` with current identity and `sparse: true` | Voided Payment envelope |
| PDF | `GET /payment/{id}/pdf` accepting `application/pdf` | PDF bytes |
| Send | `POST /payment/{id}/send?sendTo={email}` with an empty `application/octet-stream` body | Payment envelope |

Include every line to retain when changing any line in either update mode. Send an empty `Line` list to remove all lines. Full updates can clear omitted writable fields. Intuit's full-update field table marks `TotalAmt` required while its example omits it. The SDK follows the field table.

Voiding retains the transaction, zeroes its amounts and quantities, and prepends `Voided` to `PrivateNote`. Intuit requires deleting the associated deposit before voiding a deposited payment. The caller manages that separate operation. Writes and email sends are issued once per SDK call. API faults retain their HTTP status, details, and Intuit request ID where available.
