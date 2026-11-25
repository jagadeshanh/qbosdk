# AR Aging Summary report requirements

Source: [Intuit ARAgingSummary](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingsummary), reviewed using “Copy all for AI”.

- Query `GET /v3/company/<realmId>/reports/AgedReceivables` through the authenticated Accounting client and return the full report, including nested rows, columns and header.
- Optional string filters: `customer`, `qzurl`, `date_macro`, `aging_method`, `report_date`, `sort_order`, and `department`.
- With local validation enabled, `report_date` uses `YYYY-MM-DD`, `qzurl` is `true` or `false`, `aging_method` is `Report_Date` or `Current`, and `sort_order` is `ascend` or `descend`. Delegate value checks to Intuit when disabled.
- Encode filters, preserve faults and report data, and test parameters, validation, no-data reports and failures. Live sandbox verification is outstanding.
