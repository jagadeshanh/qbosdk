# Preferences

[Intuit Preferences reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/preferences)

Preferences holds company-wide settings. QuickBooks returns grouped settings such as accounting, sales forms, purchases, products and services, reports, email, taxes, time tracking, and currency. `OtherPrefs` holds extension name/value pairs. Most settings are read-only and some vary by company edition or affect only the QuickBooks UI. The caller selects writable fields according to the reference.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Read | `GET /preferences` without an ID | Preferences envelope |
| Query | `GET /query` with `SELECT * FROM Preferences` and optional metadata timestamp filters or sort clauses | QueryResponse envelope |
| Full update | `POST /preferences` with the current `Id` and `SyncToken`, all writable fields to retain, and `sparse: false` | Preferences envelope |

Intuit documents no pagination, create, or delete for Preferences. A full update can clear omitted writable settings or revert them to defaults. Preserve grouped response data and Intuit faults. Do not retry updates automatically.
