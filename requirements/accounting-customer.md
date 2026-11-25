# Customer

Source: [Intuit Customer API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /customer` with `DisplayName` or at least one of `Title`, `GivenName`, `MiddleName`, `FamilyName`, and `Suffix`. Display names must be unique across customers, vendors and employees. Name fields and `PrintOnCheckName` cannot contain colon, tab or newline.
- Read `GET /customer/{id}` and query `GET /query`. The SDK provides explicit pagination and an iterator.
- Full update `POST /customer` requires current `Id` and `SyncToken` and all writable fields to retain; omitted fields are cleared. Sparse update sets `sparse: true`, supplies the versioned identity and changed fields, and leaves omitted fields unchanged. Set `Active` false to make a customer inactive.
- `DisplayName` is limited to 500 characters, `Title` and `Suffix` to 16, person-name components and `CompanyName` to 100, `PrintOnCheckName` to 110, `ResaleNum` to 16, and `Notes` to 2,000. Optional nested address, phone, email and other fields are passed through; company-specific restrictions and uniqueness are enforced by Intuit.
- Sub-customer/job creation uses `Job: true` and a `ParentRef`; the hierarchy has up to four nested levels. Currency cannot be changed once set. Preserve faults and do not retry mutations automatically.
