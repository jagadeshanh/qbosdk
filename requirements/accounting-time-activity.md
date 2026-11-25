# TimeActivity

[Intuit TimeActivity](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/timeactivity)

Time activities record employee or vendor work. Supply `NameOf` as `Employee` or `Vendor` with the matching reference. Send `Hours` and/or `Minutes`, or use `StartTime` and `EndTime`. Intuit accepts full times and documents time-of-day forms with a `TxnDate`. When recording historical or future activity with offset-free time-of-day values, provide the posting date. The maximum duration or break is 8,760 hours, with 0–59 minutes and only zero minutes at 8,760 hours.

Supply `CustomerRef` and `HourlyRate` for billable work. `HourlyRate` is 0–99,999,999,999. `Description` allows up to 4,000 characters. Intuit validates locale, project, payroll, and accounting requirements. QuickBooks sets the billed status through invoice processing.

| Operation | Company-relative request |
| --- | --- |
| Create | `POST /timeactivity` |
| Read | `GET /timeactivity/{id}` |
| Query | `GET /query` with `SELECT … FROM TimeActivity` and pagination |
| Full update | `POST /timeactivity` with current identity, retained writable fields, and `sparse: false` |
| Delete | `POST /timeactivity?operation=delete` with current identity |

Reads and writes return the complete `TimeActivity` envelope. Queries return `QueryResponse.TimeActivity`. Versioned writes require `Id` and the current `SyncToken`.
