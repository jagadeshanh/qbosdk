# Tax Summary and Trial Balance

[Intuit TaxSummary](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxsummary) · [Intuit TrialBalance](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/trialbalance) · [Reports workflow](https://developer.intuit.com/app/developer/qbo/docs/workflows/run-reports)

Both reports use GET under `/v3/company/{realmId}/reports/{reportName}` and return the full report envelope. Dates are `YYYY-MM-DD` with start before end. Accounting method is `Cash` or `Accrual` and sort order is `ascend` or `descend`.

- **TaxSummary** requires `agency_id`, the QuickBooks TaxAgency ID. Optional filters are `accounting_method`, `start_date`, `end_date`, `date_macro`, and `sort_order`. The entity reference describes non-US availability. The reports workflow identifies France specifically. Live verification requires a compatible sandbox.
- **TrialBalance** accepts `accounting_method`, `start_date`, `end_date`, `date_macro`, `sort_order`, and `summarize_column_by`. Use `TrialBalanceFR` for French companies, selected through the SDK argument `locale="FR"`. The locale argument controls the endpoint and is omitted from the HTTP query parameters.
