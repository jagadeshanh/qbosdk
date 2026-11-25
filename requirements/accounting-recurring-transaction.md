# RecurringTransaction

[Intuit RecurringTransaction reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/recurringtransaction)

Recurring transactions define schedules, reminders, and reusable transaction templates in supported QuickBooks Essentials and Plus companies. The request identifies one transaction type as the top-level key. Supported types are Bill, Purchase, CreditMemo, Deposit, Estimate, Invoice, JournalEntry, RefundReceipt, SalesReceipt, Transfer, VendorCredit, and PurchaseOrder.

Create includes the relevant transaction's minimum payload and nested `RecurringInfo`. The latter carries the template settings, such as `Name`, `RecurType`, `Active`, and `ScheduleInfo` when applicable. The underlying transaction determines which fields apply. Intuit's create notes mention item lines and `DepositToAccountRef`; the SDK leaves these checks to Intuit because the supported transaction types have different underlying fields. Intuit does not allow using `CustomSalesTax` as `TxnTaxCodeRef`.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /recurringtransaction` with one transaction object and its nested `RecurringInfo` | RecurringTransaction envelope |
| Delete | `POST /recurringtransaction?operation=delete` with `Id` and current `SyncToken` nested under the template type | RecurringTransaction deletion envelope |
| Query | `GET /query` with `SELECT * FROM RecurringTransaction` and optional filter and pagination clauses | `QueryResponse.RecurringTransaction` list of wrapped templates |
| Read | `GET /recurringtransaction/{id}` | RecurringTransaction envelope |

Unlink associated transactions before deleting the template. The reference lists create, delete, query, and read. Writes preserve upstream faults and are issued once per SDK call.
