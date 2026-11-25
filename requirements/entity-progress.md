# QuickBooks entity implementation progress

Source: `qbo-entities-anchors.json`. Each entity was reviewed using Intuit’s API Reference Copy all for AI control. Contract checks also used Intuit’s [public entity definitions](https://static.developer.intuit.com/JSONObjects/EntityJsonObject_v1.json) and [reference models and examples](https://static.developer.intuit.com/JSONObjects/CodesModelsJsonObjects_v2.json). The [API index](../docs/api-index.rst) maps the named operations to SDK methods. Offline tests use mocked transport.

| Entity | Status |
| --- | --- |
| Account | Copy all for AI reviewed; create, paginated query, read, and full update implemented and offline tested; first query page and read verified in the sandbox. Prior sandbox Account lifecycle tests cover create, full update, and inactivation. |
| AccountListDetail | Copy all for AI reviewed; report query implemented and offline tested; default request and requests with date macro and creation-date filters accepted in the sandbox. Effects of the extra filters remain unverified. |
| APAgingDetail | Copy all for AI used; implemented ap_aging_detail, offline tested; default report query verified in the sandbox. |
| APAgingSummary | Copy all for AI used; implemented ap_aging_summary, offline tested; default report query verified in the sandbox. |
| ARAgingDetail | Copy all for AI used; implemented ar_aging_detail, offline tested; default report query verified in the sandbox. |
| ARAgingSummary | Copy all for AI used; implemented ar_aging_summary, offline tested; default report query verified in the sandbox. |
| Attachable | Copy all for AI used; note, query, read, update, delete, download URL and upload implemented and offline tested; live verification pending. |
| BalanceSheet | Copy all for AI used; implemented balance_sheet, offline tested; default report query verified in the sandbox. |
| Batch | Copy all for AI used; implemented batch, offline tested; live verification pending. |
| Bill | Copy all for AI used; create, delete, query, read, full update implemented and offline tested; live verification pending. |
| BillPayment | Copy all for AI used; create, void, delete, query, read and full update implemented and offline tested; live verification pending. |
| Budget | Copy all for AI used; create, delete, query, read and full update implemented and offline tested; live verification pending. |
| CashFlow | Copy all for AI reviewed; report query implemented, offline tested, and verified in the sandbox with a date macro. |
| ChangeDataCapture | Copy all for AI reviewed; CDC implemented and offline tested; recent Account and Customer CDC query verified in the sandbox. |
| ChangeOrder | Copy all for AI reviewed; create, delete, read, and full update implemented and offline tested; live verification requires a project-enabled company and test records. |
| Class | Copy all for AI reviewed; create, paginated query, read, and full update implemented and offline tested; sandbox query returned no records to read. |
| CompanyCurrency | Intuit API Explorer Copy all for AI reviewed; create, query, read and full update implemented and offline tested; live verification pending. |
| CompanyInfo | Copy all for AI reviewed; read, query, full update, and sparse update implemented and offline tested; query and read verified in the sandbox. |
| CreditMemo | Intuit API Explorer Copy all for AI reviewed; create, delete, PDF, query, read, send and full update implemented and offline tested; live verification pending. |
| CreditCardPayment | Copy all for AI reviewed; create, delete, read, paginated query, and full and sparse update implemented and offline tested. The current Intuit sample uses CreditCardPaymentTxn in QueryResponse. Sandbox query returned no records to read. |
| Customer | Copy all for AI reviewed; create, query, read, full and sparse update implemented and offline tested; live verification pending. |
| CustomerBalance | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| CustomerBalanceDetail | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| CustomerIncome | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| CustomerType | Copy all for AI reviewed; read and paginated query implemented and offline tested; live verification pending. |
| Department | Copy all for AI reviewed; create, read, paginated query and full update implemented and offline tested; live verification pending. |
| Deposit | Copy all for AI reviewed; create, delete, query, read, full and sparse update implemented and offline tested; live verification pending. |
| Employee | Copy all for AI reviewed; create, query, read and full update implemented and offline tested; conflicting name requirements and payroll rules need live verification. |
| Entitlements | Copy all for AI reviewed; XML read implemented and offline tested; XML fault details and live verification pending. |
| Estimate | Copy all for AI reviewed; create, delete, PDF, query, read, send, sparse and full update implemented and offline tested; live verification pending. |
| Exchangerate | Copy all for AI reviewed; get, paginated query and update implemented and offline tested; live verification pending. |
| GeneralLedger | Copy all for AI reviewed; report query implemented and offline tested; account-type spelling and default report query verified in the sandbox. |
| InventoryAdjustment | Copy all for AI reviewed; create, delete, read and sparse update implemented and offline tested; date and sparse requirements need live verification. |
| InventoryValuationDetail | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| InventoryValuationSummary | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| Invoice | Copy all for AI reviewed; create, delete, void, PDF, query, read, send, sparse and full update implemented and offline tested; live verification pending. |
| Item | Copy all for AI reviewed; item and category create/update and item/category/bundle read/query implemented and offline tested; live verification pending. |
| JournalEntry | Copy all for AI reviewed; create, delete, query, read, full and sparse update implemented and offline tested; live verification pending. |
| JournalReport | Copy all for AI reviewed; report query implemented and offline tested; default report query verified in the sandbox. |
| Payment | Copy all for AI reviewed; create, read, paginated query, full and sparse update, delete, void, PDF and email implemented and offline tested; read, first query page and PDF verified in the sandbox. |
| PaymentMethod | Copy all for AI reviewed; create, read, paginated query and full update implemented and offline tested; read and first query page verified in the sandbox. |
| Preferences | Copy all for AI reviewed; read, unpaginated query and full update implemented and offline tested; read and unfiltered query verified in the sandbox. |
| ProfitAndLoss | Copy all for AI reviewed; report query implemented and offline tested; date-macro query verified in the sandbox. |
| ProfitAndLossDetail | Copy all for AI reviewed; report query implemented and offline tested; date-macro query with and without the account parameter accepted in the sandbox; filter semantics pending. |
| Purchase | Copy all for AI reviewed; create, read, paginate, full update and delete implemented and offline tested; read and first query page verified in the sandbox. |
| PurchaseOrder | Copy all for AI reviewed; create, read, paginated query, full update, delete, PDF and email implemented and offline tested; read, first query page and PDF verified in the sandbox. |
| RecurringTransaction | Copy all for AI reviewed; create, delete, read, and paginated query implemented and offline tested; read and first query page verified in the sandbox. |
| RefundReceipt | Copy all for AI reviewed; create, delete, PDF, read, paginated query, email, and full and sparse update implemented and offline tested; read, first query page, and PDF verified in the sandbox. |
| ReimburseCharge | Copy all for AI reviewed; read and paginated query implemented and offline tested; read and first query page verified in the sandbox. |
| SalesByClassSummary | Copy all for AI reviewed; report query implemented, offline tested, and verified in the sandbox with a date macro. |
| SalesByCustomer | Copy all for AI reviewed; report query implemented, offline tested, and verified in the sandbox with a date macro and Quick Zoom option. |
| SalesByDepartment | Copy all for AI reviewed; report query implemented, offline tested, and verified in the sandbox with a date macro. |
| SalesByProduct | Copy all for AI reviewed; report query implemented, offline tested, and verified in the sandbox with an explicit due-date range. |
| SalesReceipt | Copy all for AI reviewed; create, delete, void, read, paginated query, PDF, email, and full and sparse update implemented and offline tested; read, first query page, and PDF verified in the sandbox. |
| TaxClassification | Copy all for AI reviewed; all four read modes implemented, offline tested, and verified in the sandbox. |
| TaxCode | Copy all for AI reviewed; create via TaxService, read, and paginated query implemented and offline tested; first query page and read by numeric TaxCode ID verified in the sandbox. |
| TaxPayment | Copy all for AI reviewed; read and paginated query implemented and offline tested; live verification needs an AU, CA, or UK sandbox. |
| TaxRate | Copy all for AI reviewed; create via TaxService, read, and paginated query implemented and offline tested; read and first query page verified in the sandbox. |
| TaxService | Copy all for AI reviewed; tax code and rate creation implemented and offline tested; live write verification pending. |
| TaxSummary | Copy all for AI and Intuit reference data reviewed; report query implemented and offline tested; live verification needs a compatible sandbox. |
| TaxAgency | Copy all for AI and Intuit reference data reviewed; create, read, and paginated query implemented and offline tested; read and first query page verified in the sandbox. |
| Term | Copy all for AI and Intuit reference data reviewed; create, read, paginated query, and full update implemented and offline tested; read and first query page verified in the sandbox. |
| TimeActivity | Copy all for AI and Intuit reference data reviewed; create, read, paginated query, full update, and delete implemented and offline tested; read and first query page verified in the sandbox. |
| TransactionList | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| TransactionListByVendor | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| TransactionListByCustomer | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| TransactionListWithSplits | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| Transfer | Copy all for AI and Intuit reference data reviewed; create, read, paginated query, full and sparse update, and delete implemented and offline tested; sandbox query returned no records to read. |
| TrialBalance | Copy all for AI and Intuit reference data reviewed; standard and French report endpoints implemented and offline tested; standard endpoint verified using a date macro in the sandbox. |
| Vendor | Copy all for AI and Intuit reference data reviewed; create, read, paginated query, and full update implemented and offline tested; read and first query page verified in the sandbox. |
| VendorBalance | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| VendorBalanceDetail | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
| VendorCredit | Copy all for AI and Intuit reference data reviewed; create, read, paginated query, full update, and delete implemented and offline tested; sandbox query returned no records to read. |
| VendorExpenses | Copy all for AI and Intuit reference data reviewed; report query implemented, offline tested, and verified using a date macro in the sandbox. |
