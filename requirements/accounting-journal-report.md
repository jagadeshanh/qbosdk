# Journal report

Source: [Intuit JournalReport API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalreport), reviewed with Copy all for AI. Live sandbox verification is pending.

- Query `GET /reports/JournalReport` with optional `end_date`, `date_macro`, `sort_by`, `sort_order`, `start_date`, and `columns`.
- Explicit dates use `YYYY-MM-DD`; the start must precede the end. Sort order is `ascend` or `descend`. Preserve the complete report, including nested rows and columns, and Intuit faults.
