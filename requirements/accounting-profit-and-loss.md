# ProfitAndLoss and ProfitAndLossDetail

[Intuit ProfitAndLoss reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandloss) · [Intuit ProfitAndLossDetail reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandlossdetail)

## Query a report

Both operations use GET under `/v3/company/{realmId}/reports/{reportName}`. All query parameters are optional strings. The response preserves the complete nested `Header`, `Rows`, and `Columns` objects, including section summaries, column metadata, and the no-data option when present. These reports do not use entity query pagination.

| Report name | Parameters |
| --- | --- |
| `ProfitAndLoss` | `customer`, `qzurl`, `accounting_method`, `end_date`, `date_macro`, `adjusted_gain_loss`, `class`, `item`, `sort_order`, `summarize_column_by`, `department`, `vendor`, `start_date` |
| `ProfitAndLossDetail` | `customer`, `account`, `accounting_method`, `end_date`, `date_macro`, `adjusted_gain_loss`, `class`, `sort_by`, `payment_method`, `sort_order`, `employee`, `department`, `vendor`, `account_type`, `start_date`, `columns` |

Specify dates in `YYYY-MM-DD` with the start earlier than the end, or use a predefined date macro. Accounting method is `Cash` or `Accrual`. Sort order is `ascend` or `descend`. Send the Quick Zoom and adjusted gain/loss flags as `"true"` or `"false"`. Use comma-separated IDs and column names where applicable. Intuit determines feature-dependent column availability and validates account types, payment method labels, and dates chosen by macro. The Python keyword `class_` maps to QuickBooks' `class` option. Intuit labels the detail account parameter `account` with a parenthetical `source_account_type`. The sandbox accepted a request with `account`. Its effect on returned rows still needs verification.
