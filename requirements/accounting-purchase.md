# Purchase

[Intuit Purchase reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchase)

Purchase records a cash, check, or credit-card expense. Creates and full updates require `PaymentType` (`Cash`, `Check`, or `CreditCard`), `AccountRef.value`, and expense lines. The funding account must be active and match the payment type. A multicurrency company also requires `CurrencyRef`. QuickBooks calculates `TotalAmt` from the transaction. The object lists account-based and item-based expense lines, with item-based lines dependent on purchase settings. The create table only lists account-based lines. The SDK forwards both structures and leaves company-specific line validation to Intuit.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Create | `POST /purchase` | Purchase envelope |
| Delete | `POST /purchase?operation=delete` with `Id` and `SyncToken` | Purchase deletion envelope |
| Query | `GET /query` with `SELECT … FROM Purchase` and pagination | `QueryResponse.Purchase` |
| Read | `GET /purchase/{id}` | Purchase envelope |
| Full update | `POST /purchase` with current `Id` and `SyncToken`, retained writable fields, and `sparse: false` | Purchase envelope |

Limit `DocNumber` to 21 characters and `PrivateNote` to 4,000 characters. Duplicate handling varies according to company preferences and payment type. Pass `allow_duplicate_doc_number=True` on an intentional duplicate to add `include=allowduplicatedocnum`. The SDK preserves QuickBooks faults and issues writes once per call. Omitted writable fields can be cleared by full updates.
