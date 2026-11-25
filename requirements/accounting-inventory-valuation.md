# Inventory valuation reports

Sources: [InventoryValuationDetail](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationdetail) and [InventoryValuationSummary](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationsummary), reviewed using Copy all for AI. Sandbox verification is pending.

- Detail: `GET /reports/InventoryValuationDetail` accepts `end_date`, `end_svcdate`, `date_macro`, `svcdate_macro`, `start_svcdate`, `group_by`, `start_date`, and `columns`.
- Summary: `GET /reports/InventoryValuationSummary` accepts `qzurl`, `date_macro`, `item`, `report_date`, `sort_order`, and `summarize_column_by`.
- Dates use `YYYY-MM-DD`. Start dates must precede corresponding end dates. Validate documented enum values when local validation is enabled. Preserve nested report rows, columns, headers and Intuit faults.
