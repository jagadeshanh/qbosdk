# AR Aging Detail report requirements

Source: [Intuit ARAgingDetail](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingdetail), reviewed using “Copy all for AI”.

- Query `GET /v3/company/<realmId>/reports/AgedReceivableDetail` through the authenticated Accounting client and return the complete report, including nested rows, columns and header.
- Optional string filters: `customer`, `shipvia`, `term`, `start_duedate`, `end_duedate`, `custom1`, `custom2`, `custom3`, `report_date`, `aging_method`, and `columns`. `num_periods` and `past_due` are integers; `aging_period` is numeric.
- When local validation is enabled, dates use `YYYY-MM-DD`, due-date start precedes end, and `aging_method` is `Report_Date` or `Current`. Delegate value checks to Intuit when disabled, retaining structural type checks.
- Encode filters, preserve faults and financial report data, and test parameters, validation, no-data reports and failures. Live sandbox verification is outstanding.
