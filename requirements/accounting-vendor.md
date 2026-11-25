# Vendor

[Intuit Vendor](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendor)

A Vendor represents a seller. Create or fully update with `DisplayName` or at least one name component (`Title`, `GivenName`, `MiddleName`, `FamilyName`, `Suffix`). QuickBooks derives a display name when omitted and enforces uniqueness across vendors, customers, and employees. Display name, components, and `PrintOnCheckName` cannot contain colons, tabs, or newlines.

The limits are 500 characters for display name, 16 for title and suffix, 100 for each other name component, company name, print name, and account number, and 20 for tax identifier. QuickBooks masks tax identifiers in responses. Preserve the server's address, contact, account, and preference fields. Currency is fixed after creation when enabled.

| Operation | Company-relative request |
| --- | --- |
| Create | `POST /vendor` |
| Read | `GET /vendor/{id}` |
| Query | `GET /query` with `SELECT … FROM Vendor` and pagination |
| Full update | `POST /vendor` with current identity, retained writable fields, and `sparse: false` |

Reads and writes return the complete `Vendor` envelope. Queries return `QueryResponse.Vendor`. Full updates require `Id` and the latest `SyncToken`.
