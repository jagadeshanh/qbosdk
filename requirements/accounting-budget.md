# Budget requirements

Source: [Intuit Budget reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/budget), reviewed using “Copy all for AI”.

- Create `POST /budget` with `StartDate` and `EndDate`; preserve `BudgetDetail`, period, name, type, custom extensions, and other fields. Intuit describes dates as DateTime but demonstrates date-only strings; do not coerce them or assume the user's timezone.
- Read `GET /budget/<id>` and query `GET /query?query=...`, supporting pagination and full response envelopes.
- Full update `POST /budget` requires `Id`, `SyncToken`, `StartDate`, `EndDate`, and all writable fields to retain. Omitted writable fields are set to null.
- Delete `POST /budget?operation=delete` requires `Id` and `SyncToken`; the documented successful response may contain only `time`, so do not require a Budget object.
- Preserve decimals and Intuit faults, do not retry writes automatically, and test request and response contracts offline. Live sandbox verification remains outstanding.
