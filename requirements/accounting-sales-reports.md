# Sales reports

[Intuit SalesByClassSummary](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbyclasssummary) · [SalesByCustomer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbycustomer) · [SalesByDepartment](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbydepartment) · [SalesByProduct](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbyproduct)

## Query a report

Use `GET /v3/company/{realmId}/reports/{reportName}`. All options are optional strings. Each report returns its original `Header`, `Rows`, and `Columns` structure. Preserve nested rows, summaries, cell IDs, column metadata, and empty reports.

| Entity | Report name | Options in addition to the common parameters |
| --- | --- | --- |
| SalesByClassSummary | `ClassSales` | None |
| SalesByCustomer | `CustomerSales` | `qzurl`, `sort_order` |
| SalesByDepartment | `DepartmentSales` | `sort_order` |
| SalesByProduct | `ItemSales` | `sort_order`, `start_duedate`, `end_duedate` |

All four reports accept `customer`, `accounting_method`, `start_date`, `end_date`, `date_macro`, `class`, `item`, `summarize_column_by`, and `department`. Use comma-separated QuickBooks IDs for the four entity filters. Python uses `class_` for the wire parameter `class`.

Report dates and due dates use `YYYY-MM-DD`. Start must precede end in each explicit pair. `date_macro` selects a predefined period. The accounting method is `Cash` or `Accrual`, sort order is `ascend` or `descend`, and Quick Zoom uses `"true"` or `"false"`. Class and department data depend on company configuration.
