# AP Aging Detail report requirements

Source: [Intuit APAgingDetail reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingdetail), reviewed using “Copy all for AI”.

- Query `GET /v3/company/<realmId>/reports/AgedPayableDetail` using the authenticated sandbox or production Accounting client. This is a read-only report.
- Return Intuit's entire report object, including optional `Header`, `Rows`, `Columns`, and nested rows and metadata; propagate faults and reject malformed reports.
- Support optional string parameters `shipvia`, `term`, `start_duedate`, `end_duedate`, `accounting_method`, `custom1`, `custom2`, `custom3`, `report_date`, `vendor`, and `columns`; `num_periods` and `past_due` are integers, and `aging_period` is numeric.
- Locally validate dates as `YYYY-MM-DD`, require the start due date to precede the end, and validate `accounting_method` as `Cash` or `Accrual` when field validation is enabled. Forward strings to Intuit when disabled; preserve structural type checks.
- URL-encode query values. Preserve financial values and upstream error details. Do not log credentials or report contents by default.
- Test the endpoint, supported parameters, report structure, no-data results, invalid dates, numeric types, and upstream errors offline. Live sandbox verification remains outstanding.
