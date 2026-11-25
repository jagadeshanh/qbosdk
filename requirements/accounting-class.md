# Class requirements

Source: [Intuit Class API Reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/class), reviewed using Copy all for AI.

- Provide create (`POST /class`), read (`GET /class/<id>`), query (`GET /query`), and full update (`POST /class`) for a class. Preserve complete response envelopes, references and metadata.
- `Name` is a string with a documented 100-character QuickBooks Online limit. Support optional `Active`, `SubClass`, and `ParentRef`; full update requires `Id`, `SyncToken`, and the writable fields the caller wants to retain. Preserve local validation opt-out for field-length checks.
- Full update must be explicitly non-sparse and not automatically retried. Query supports caller-supplied filters and pagination; no result must not be confused with a failure.
- The sandbox accepted a Class query and returned an empty page.
