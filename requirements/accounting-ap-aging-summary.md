# AP Aging Summary report requirements

Source: [Intuit APAgingSummary reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingsummary), reviewed using “Copy all for AI”.

- Query `GET /v3/company/<realmId>/reports/AgedPayables` with the authenticated Accounting client and return the complete report, including nested rows, columns and header.
- Support optional string filters `customer`, `qzurl`, `vendor`, `date_macro`, `department`, `report_date`, `sort_order`, and `aging_method`.
- Locally validate `report_date` in `YYYY-MM-DD` format, `qzurl` as `true`/`false`, `sort_order` as `ascend`/`descend`, and `aging_method` as `Report_Date`/`Current`; delegate value validation to Intuit when disabled.
- Preserve upstream faults and report data, and test URL encoding, supported inputs, local and server validation, empty data and upstream errors. Live sandbox verification remains outstanding.
