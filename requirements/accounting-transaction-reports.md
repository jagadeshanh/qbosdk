# Transaction list reports

[Intuit TransactionList](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlist) · [By Vendor](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistbyvendor) · [By Customer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistbycustomer) · [With Splits](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistwithsplits)

Each report uses GET under `/v3/company/{realmId}/reports/{reportName}`, with the report name matching the entity name. Preserve the complete nested header, rows, columns, and optional summary data. All filters accept strings.

All four reports accept `docnum`, `name`, `start_date`, `end_date`, `date_macro`, `payment_method`, `source_account_type`, `transaction_type`, `group_by`, `sort_by`, `sort_order`, and `columns`.

The first three reports also accept `duedate_macro`, `arpaid`, `bothamount`, `start_moddate`, `department`, `start_duedate`, `end_duedate`, `memo`, `appaid`, `moddate_macro`, `printed`, `createdate_macro`, `cleared`, `qzurl`, `term`, `end_createdate`, `start_createdate`, and `end_moddate`. `TransactionList` accepts both `vendor` and `customer`. Its vendor and customer variants accept only their respective filter.

Use `YYYY-MM-DD` for explicit dates with starts before their ends, and comma-separated IDs or columns where applicable. Report grouping with splits supports `Name`, `Account`, and `Transaction Type`. Grouping in the other variants also supports time periods, including fiscal year and fiscal quarter. Validate documented filter names for the chosen report and preserve upstream faults.
