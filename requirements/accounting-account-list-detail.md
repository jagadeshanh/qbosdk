# Accounting API: Account List Detail report

## Scope

Provide the read-only Account List Detail report at `GET /v3/company/<realmId>/reports/AccountList`. Use the connected company's access token, realm ID, and selected sandbox or production host. Return the full report response, including `Header`, `Rows`, `Columns`, and any additional fields provided by Intuit; preserve nested rows and column order. Empty or omitted row containers are valid. Report requests must surface Intuit faults, network errors, and malformed responses without exposing credentials.

## Parameters

Support optional string parameters `account_type`, `start_date`, `end_date`, `start_moddate`, `end_moddate`, `moddate_macro`, `createdate_macro`, `sort_by`, `sort_order`, `account_status`, and `columns`. The Intuit reference also mentions `date_macro`, `start_createdate`, and `end_createdate` in parameter descriptions. Sandbox requests containing those options returned reports. Their effect on the reported rows or period still needs verification. Encode values as query parameters, including spaces and comma-separated columns.

When local field validation is enabled, date values must be valid `YYYY-MM-DD` strings; if both ends of a date range are supplied, the start must precede the end. `sort_order` accepts `ascend` or `descend`. Intuit remains authoritative for parameter combinations, account types, status values, columns, date macros, locale, and version support. With local field validation disabled, send parameter values to Intuit after basic type checks.

## Verification

Test both environments, authorization, URL and parameter encoding, defaults, date and sort validation, response structure, empty reports, and upstream errors. Exercise a read-only sandbox request when available; do not log report contents or credentials by default. Reference: [Intuit AccountListDetail](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/accountlistdetail).
