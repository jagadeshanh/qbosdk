# CompanyInfo requirements

Source: [Intuit CompanyInfo API Reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/companyinfo), reviewed using Copy all for AI.

- Read the connected company's profile with `GET /v3/company/<realmId>/companyinfo/<realmId>` and query it using `GET /query`. Preserve full response envelopes and nested addresses and metadata.
- Full update with `POST /companyinfo` requires `Id`, `SyncToken`, `CompanyName`, and `CompanyAddr`; omitted writable fields may be cleared. Sparse update uses the same endpoint with `sparse: true`, current `Id` and `SyncToken`, and only fields to change. Check the response and Intuit's address behavior; do not assume omitted nested address components are preserved.
- Use the CompanyInfo ID returned for the connected company; the documentation does not establish that it always equals the realm ID. `CompanyName` and `LegalName` have a documented 1,024-character maximum. Preserve faults and never automatically retry mutations.
- Test both update modes, exact realm-bound URL, field validation, query, response and upstream faults offline. Read and query passed in the sandbox. Write checks use mocked transport.
