# Vendor reports

[Intuit VendorBalance](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorbalance) · [Intuit VendorBalanceDetail](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorbalancedetail) · [Intuit VendorExpenses](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorexpenses)

Each report uses GET under `/v3/company/{realmId}/reports/{reportName}` with the entity name as the report name. Preserve nested headers, rows, summaries, and columns.

| Report | Optional string parameters |
| --- | --- |
| VendorBalance | `qzurl`, `accounting_method`, `date_macro`, `appaid`, `report_date`, `sort_order`, `summarize_column_by`, `department`, `vendor` |
| VendorBalanceDetail | `term`, `start_duedate`, `end_duedate`, `accounting_method`, `date_macro`, `duedate_macro`, `sort_by`, `report_date`, `sort_order`, `appaid`, `department`, `vendor`, `columns` |
| VendorExpenses | `customer`, `vendor`, `start_date`, `end_date`, `date_macro`, `class`, `sort_order`, `summarize_column_by`, `department`, `accounting_method` |

Use `YYYY-MM-DD` dates and an earlier start date in any explicit pair. `appaid` accepts `All`, `Paid`, or `Unpaid`. `qzurl` accepts `"true"` or `"false"`. Use comma-separated IDs and column names where applicable. Pass `class_` for the QuickBooks `class` filter.
