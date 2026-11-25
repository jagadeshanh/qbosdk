# General Ledger report

Source: [Intuit GeneralLedger API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/generalledger), reviewed with Copy all for AI. Live sandbox verification is pending.

- Query `GET /reports/GeneralLedger` with optional `customer`, `account`, `accounting_method`, `source_account`, `end_date`, `date_macro`, `account_type`, `sort_by`, `sort_order`, `start_date`, `summarize_column_by`, `department`, `vendor`, `class`, and `columns`.
- The parameter table names `account_type` and describes `source_account_type`; the sample uses `source_account_type`. The SDK exposes both spellings pending live confirmation. Python uses `class_` for the wire parameter `class`.
- Explicit dates use `YYYY-MM-DD`, and the start precedes the end. Preserve complete header, columns, and nested rows and Intuit faults. Intuit warns that the report hierarchy can be incorrect in some circumstances when subaccounts are configured.
