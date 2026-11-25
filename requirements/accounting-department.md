# Department

Source: [Intuit Department API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /department` with `Name` (maximum 100 characters) and `ParentRef` when creating a subdepartment. Read `GET /department/{id}` and query `GET /query` with pagination.
- Full update `POST /department` needs the current `Id`, `SyncToken`, `Name`, and all writable fields to retain. Omitted writable fields are set to null. Setting `Active` false inactivates the entity while retaining references.
- The system-defined fully qualified name expresses the hierarchy, limited to five levels. Preserve response and fault envelopes; do not automatically retry writes.
