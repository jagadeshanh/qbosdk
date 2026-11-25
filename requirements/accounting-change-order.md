# ChangeOrder requirements

Source: [Intuit ChangeOrder API Reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/changeorder), reviewed using Copy all for AI.

- Change orders are project estimate changes, available only for supported US company plans and project configurations. Create and full update use `POST /v3/company/<realmId>/changeorder`; read uses `GET /changeorder/<id>`; deletion uses `POST /changeorder?operation=delete` with `Id` and `SyncToken`. The anchor list does not specify a query operation.
- A change order needs `ProjectRef`, `CustomerRef` and at least one line. Include at least one `SalesItemLineDetail` line. Every line must have a `LinkedTxn` referring to the same parent `Estimate`. Limit `DocNumber` to 21 characters and `PrivateNote` to 4,000 characters. Intuit validates the project and customer against the company.
- Full update requires `Id`, `SyncToken`, the header `LinkedTxn` for the same parent estimate, and all writable fields and lines to retain; omitted fields and lines may be cleared or deleted. Delete is irreversible. No write is automatically retried.
- Return the complete response envelope and preserve decimal amounts and faults. Test request contracts and errors offline. Live verification requires a project-enabled sandbox and suitable test records.
