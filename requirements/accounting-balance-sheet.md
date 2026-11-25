# Balance Sheet report requirements

Source: [Intuit BalanceSheet](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/balancesheet), reviewed using “Copy all for AI”.

- Query `GET /v3/company/<realmId>/reports/BalanceSheet` with an authenticated Accounting client; preserve the complete nested report response and upstream faults.
- Support optional string parameters `customer`, `qzurl`, `accounting_method`, `end_date`, `date_macro`, `adjusted_gain_loss`, `class`, `item`, `sort_order`, `summarize_column_by`, `department`, `vendor`, and `start_date`. Python callers use `class_` for the `class` parameter.
- Locally validate dates and ordering, boolean-like string options, accounting method, sort order, and documented column grouping values. With field validation disabled, send values to Intuit while retaining structural checks.
- Test defaults, all encoded parameters, nested and empty report responses, invalid inputs, faults, and both environments. Live sandbox verification is outstanding.
