# CompanyCurrency

Source: [Intuit CompanyCurrency API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/companycurrency), reviewed with Copy all for AI. Applies to companies with multicurrency enabled. Live sandbox behavior has not been verified.

- Create: `POST /companycurrency` with required three-letter ISO `Code`; `Active` is optional.
- Read: `GET /companycurrency/{id}`. Query: `GET /query` with a CompanyCurrency select statement; SDK pagination uses `STARTPOSITION` and `MAXRESULTS`.
- Update: `POST /companycurrency` with `Id`, `SyncToken`, `Code`, and all writable fields to retain. This is a full update: omitted writable fields become null. Set `Active` false to inactivate; references remain intact.
- `Name` and `MetaData` are system-defined; `CustomField` and `Active` may be returned. Preserve the response envelope and Intuit fault details.
- Local field-value validation can be disabled with `validate_fields=False`; structural requirements remain. Do not automatically retry mutations. Currency availability and company configuration are determined by Intuit.
