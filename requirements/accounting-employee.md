# Employee

Source: [Intuit Employee API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /employee`: the operation's field descriptions require at least one of `GivenName` or `FamilyName`, while the general business rules say both are required. The SDK accepts either; Intuit determines actual enforcement. Display names must be unique across customers, vendors, and employees. Name fields and `PrintOnCheckName` cannot contain colon, tab, or newline.
- Read `GET /employee/{id}` and query `GET /query`; provide pagination. Full update `POST /employee` requires the current `Id`, `SyncToken`, and all writable fields to retain; omitted writable fields become null. Set `Active` false to inactivate.
- DisplayName is limited to 500 characters; Title and Suffix to 16; GivenName, MiddleName, FamilyName, PrintOnCheckName, SSN, and EmployeeNumber to 100. Company-specific and nested fields are passed through.
- Payroll-enabled companies require address fields and restrict Title, Suffix, PrintOnCheckName, BillRate, DisplayName, and SSN. In particular, remove a masked SSN from a read object before an update when payroll is enabled. Check CompanyInfo for `PayrollFeature`. Preserve faults and never automatically retry writes.
