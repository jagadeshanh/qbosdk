# Customer reports

Sources: Intuit's [CustomerBalance](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalance), [CustomerBalanceDetail](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalancedetail), and [CustomerIncome](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerincome) API Explorer pages, each reviewed with Copy all for AI. Live sandbox verification is pending.

- `GET /reports/CustomerBalance`: optional `customer`, `accounting_method`, `date_macro`, `arpaid`, `report_date`, `sort_order`, `summarize_column_by`, `department`.
- `GET /reports/CustomerBalanceDetail`: optional `customer`, `shipvia`, `term`, `end_duedate`, `start_duedate`, `custom1`, `sort_by`, `arpaid`, `report_date`, `sort_order`, `aging_method`, `department`, `columns`.
- `GET /reports/CustomerIncome`: optional `customer`, `term`, `accounting_method`, `end_date`, `date_macro`, `class`, `sort_order`, `summarize_column_by`, `department`, `vendor`, `start_date`. Python uses `class_` for `class`.
- Dates use `YYYY-MM-DD`; when both range endpoints are supplied the start must precede the end. Validate documented enumerations when local field validation is enabled. Return full `Header`, `Rows`, and `Columns` structures without flattening, and preserve faults.
