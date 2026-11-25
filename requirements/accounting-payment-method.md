# PaymentMethod

[Intuit PaymentMethod reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod)

Payment methods describe how a customer paid. `Name` is required and has a maximum length of 31 characters. `Active` is an optional boolean and supports filtering and sorting. `Type` is optional and supports `CREDIT_CARD` and `NON_CREDIT_CARD`. QuickBooks supplies metadata, string `Id`, and string `SyncToken`.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /paymentmethod` with `Name` and any applicable optional fields | PaymentMethod envelope |
| Read | `GET /paymentmethod/{id}` | PaymentMethod envelope |
| Query | `GET /query` with `SELECT … FROM PaymentMethod` and pagination | `QueryResponse.PaymentMethod` |
| Full update | `POST /paymentmethod` with latest `Id`, `SyncToken`, `Name`, and writable fields to retain | PaymentMethod envelope |

Omitted writable fields can be cleared in a full update. Set `Active` to false to disable a method. The SDK validates field shape locally and allows Intuit to enforce the name length and type values when field validation is disabled. QuickBooks faults retain their details, and writes are issued once per call.
