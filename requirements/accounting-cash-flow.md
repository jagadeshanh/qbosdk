# Cash Flow report requirements

Intuit's [CashFlow API Reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/cashflow) documents the Statement of Cash Flows endpoint. The browser Copy all for AI review and a sandbox query using a date macro verified the request contract.

- Query `GET /v3/company/<realmId>/reports/CashFlow` and preserve the complete report envelope and nested rows. Surface errors and malformed responses.
- Support optional string filters `customer`, `vendor`, `end_date`, `date_macro`, `class`, `item`, `sort_order`, `summarize_column_by`, `department`, and `start_date`; the Python parameter `class_` is encoded as `class`.
- With local validation enabled, dates must be valid `YYYY-MM-DD` values with the start earlier than the end; validate sort order and documented grouping values. With validation disabled, send values to Intuit after structural type checks.
- Test parameter encoding, authorization, nested and empty report results, local validation and upstream faults. Live verification and the requested API Explorer review remain outstanding.
