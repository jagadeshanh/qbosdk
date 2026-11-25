Accounting API index
====================

Methods are available on ``qbosdk.AccountingClient``. The entity links describe the QuickBooks
request and response fields. Query methods return a page of results unless the endpoint is
unpaginated. See :doc:`reports` for report response structure and :doc:`errors` for exceptions.
The SDK uses Intuit's default Accounting API minor version, currently 75.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Entity
     - SDK methods
   * - `Account <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account>`__
     - ``create_account()``, ``query_accounts()``, ``read_account()``, ``full_update_account()``
   * - `AccountListDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/accountlistdetail>`__
     - ``account_list_detail()``
   * - `APAgingDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingdetail>`__
     - ``ap_aging_detail()``
   * - `APAgingSummary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingsummary>`__
     - ``ap_aging_summary()``
   * - `ARAgingDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingdetail>`__
     - ``ar_aging_detail()``
   * - `ARAgingSummary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingsummary>`__
     - ``ar_aging_summary()``
   * - `Attachable <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/attachable>`__
     - ``create_attachable_note()``, ``delete_attachable()``, ``attachable_download_url()``, ``query_attachables()``, ``read_attachable()``, ``full_update_attachable()``, ``upload_attachments()``
   * - `BalanceSheet <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/balancesheet>`__
     - ``balance_sheet()``
   * - `Batch <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/batch>`__
     - ``batch()``
   * - `Bill <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill>`__
     - ``create_bill()``, ``delete_bill()``, ``query_bills()``, ``read_bill()``, ``full_update_bill()``
   * - `BillPayment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/billpayment>`__
     - ``create_bill_payment()``, ``void_bill_payment()``, ``delete_bill_payment()``, ``query_bill_payments()``, ``read_bill_payment()``, ``full_update_bill_payment()``
   * - `Budget <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/budget>`__
     - ``create_budget()``, ``delete_budget()``, ``query_budgets()``, ``read_budget()``, ``full_update_budget()``
   * - `CashFlow <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/cashflow>`__
     - ``cash_flow()``
   * - `ChangeDataCapture <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/changedatacapture>`__
     - ``change_data_capture()``
   * - `ChangeOrder <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/changeorder>`__
     - ``create_change_order()``, ``delete_change_order()``, ``read_change_order()``, ``full_update_change_order()``
   * - `Class <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/class>`__
     - ``create_class()``, ``query_classes()``, ``read_class()``, ``full_update_class()``
   * - `CompanyCurrency <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/companycurrency>`__
     - ``create_company_currency()``, ``query_company_currencies()``, ``read_company_currency()``, ``full_update_company_currency()``
   * - `CompanyInfo <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/companyinfo>`__
     - ``query_company_info()``, ``read_company_info()``, ``full_update_company_info()``, ``sparse_update_company_info()``
   * - `CreditMemo <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditmemo>`__
     - ``create_credit_memo()``, ``delete_credit_memo()``, ``get_credit_memo_pdf()``, ``query_credit_memos()``, ``read_credit_memo()``, ``send_credit_memo()``, ``full_update_credit_memo()``
   * - `CreditCardPayment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditcardpayment>`__
     - ``create_credit_card_payment()``, ``delete_credit_card_payment()``, ``query_credit_card_payments()``, ``read_credit_card_payment()``, ``full_update_credit_card_payment()``, ``sparse_update_credit_card_payment()``
   * - `Customer <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer>`__
     - ``create_customer()``, ``query_customers()``, ``read_customer()``, ``full_update_customer()``, ``sparse_update_customer()``
   * - `CustomerBalance <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalance>`__
     - ``customer_balance()``
   * - `CustomerBalanceDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalancedetail>`__
     - ``customer_balance_detail()``
   * - `CustomerIncome <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerincome>`__
     - ``customer_income()``
   * - `CustomerType <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customertype>`__
     - ``query_customer_types()``, ``read_customer_type()``
   * - `Department <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department>`__
     - ``create_department()``, ``query_departments()``, ``read_department()``, ``full_update_department()``
   * - `Deposit <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit>`__
     - ``create_deposit()``, ``delete_deposit()``, ``query_deposits()``, ``read_deposit()``, ``full_update_deposit()``, ``sparse_update_deposit()``
   * - `Employee <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee>`__
     - ``create_employee()``, ``query_employees()``, ``read_employee()``, ``full_update_employee()``
   * - `Entitlements <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/entitlements>`__
     - ``read_entitlements()``
   * - `Estimate <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/estimate>`__
     - ``create_estimate()``, ``delete_estimate()``, ``get_estimate_pdf()``, ``query_estimates()``, ``read_estimate()``, ``send_estimate()``, ``sparse_update_estimate()``, ``full_update_estimate()``
   * - `Exchangerate <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/exchangerate>`__
     - ``get_exchange_rate()``, ``query_exchange_rates()``, ``update_exchange_rate()``
   * - `GeneralLedger <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/generalledger>`__
     - ``general_ledger()``
   * - `InventoryAdjustment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryadjustment>`__
     - ``create_inventory_adjustment()``, ``delete_inventory_adjustment()``, ``read_inventory_adjustment()``, ``update_inventory_adjustment()``
   * - `InventoryValuationDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationdetail>`__
     - ``inventory_valuation_detail()``
   * - `InventoryValuationSummary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationsummary>`__
     - ``inventory_valuation_summary()``
   * - `Invoice <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice>`__
     - ``create_invoice()``, ``delete_invoice()``, ``void_invoice()``, ``get_invoice_pdf()``, ``query_invoices()``, ``read_invoice()``, ``send_invoice()``, ``sparse_update_invoice()``, ``full_update_invoice()``
   * - `Item <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item>`__
     - ``create_item()``, ``create_category()``, ``query_bundles()``, ``query_categories()``, ``query_items()``, ``read_bundle()``, ``read_category()``, ``read_item()``, ``full_update_item()``, ``update_category()``
   * - `JournalEntry <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalentry>`__
     - ``create_journal_entry()``, ``delete_journal_entry()``, ``query_journal_entries()``, ``read_journal_entry()``, ``full_update_journal_entry()``, ``sparse_update_journal_entry()``
   * - `JournalReport <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalreport>`__
     - ``journal_report()``
   * - `Payment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/payment>`__
     - ``create_payment()``, ``delete_payment()``, ``void_payment()``, ``get_payment_pdf()``, ``query_payments()``, ``read_payment()``, ``send_payment()``, ``full_update_payment()``
   * - `PaymentMethod <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod>`__
     - ``create_payment_method()``, ``query_payment_methods()``, ``read_payment_method()``, ``full_update_payment_method()``
   * - `Preferences <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/preferences>`__
     - ``query_preferences()``, ``read_preferences()``, ``full_update_preferences()``
   * - `ProfitAndLoss <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandloss>`__
     - ``profit_and_loss()``
   * - `ProfitAndLossDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandlossdetail>`__
     - ``profit_and_loss_detail()``
   * - `Purchase <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchase>`__
     - ``create_purchase()``, ``delete_purchase()``, ``query_purchases()``, ``read_purchase()``, ``full_update_purchase()``
   * - `PurchaseOrder <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder>`__
     - ``create_purchase_order()``, ``delete_purchase_order()``, ``get_purchase_order_pdf()``, ``query_purchase_orders()``, ``read_purchase_order()``, ``send_purchase_order()``, ``full_update_purchase_order()``
   * - `RecurringTransaction <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/recurringtransaction>`__
     - ``create_recurring_transaction()``, ``delete_recurring_transaction()``, ``query_recurring_transactions()``, ``read_recurring_transaction()``
   * - `RefundReceipt <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt>`__
     - ``create_refund_receipt()``, ``delete_refund_receipt()``, ``get_refund_receipt_pdf()``, ``query_refund_receipts()``, ``read_refund_receipt()``, ``send_refund_receipt()``, ``sparse_update_refund_receipt()``, ``full_update_refund_receipt()``
   * - `ReimburseCharge <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/reimbursecharge>`__
     - ``query_reimburse_charges()``, ``read_reimburse_charge()``
   * - `SalesByClassSummary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbyclasssummary>`__
     - ``sales_by_class_summary()``
   * - `SalesByCustomer <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbycustomer>`__
     - ``sales_by_customer()``
   * - `SalesByDepartment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbydepartment>`__
     - ``sales_by_department()``
   * - `SalesByProduct <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesbyproduct>`__
     - ``sales_by_product()``
   * - `SalesReceipt <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt>`__
     - ``create_sales_receipt()``, ``delete_sales_receipt()``, ``void_sales_receipt()``, ``get_sales_receipt_pdf()``, ``query_sales_receipts()``, ``read_sales_receipt()``, ``send_sales_receipt()``, ``full_update_sales_receipt()``, ``sparse_update_sales_receipt()``
   * - `TaxClassification <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxclassification>`__
     - ``read_tax_classification()``, ``read_tax_classification_children()``, ``read_all_tax_classifications()``, ``read_tax_classifications_by_level()``
   * - `TaxCode <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxcode>`__
     - ``query_tax_codes()``, ``read_tax_code()``
   * - `TaxPayment <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxpayment>`__
     - ``query_tax_payments()``, ``read_tax_payment()``
   * - `TaxRate <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxrate>`__
     - ``query_tax_rates()``, ``read_tax_rate()``
   * - `TaxService <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxservice>`__
     - ``create_tax_service()``
   * - `TaxSummary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxsummary>`__
     - ``tax_summary()``
   * - `TaxAgency <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxagency>`__
     - ``create_tax_agency()``, ``query_tax_agencies()``, ``read_tax_agency()``
   * - `Term <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/term>`__
     - ``create_term()``, ``query_terms()``, ``read_term()``, ``full_update_term()``
   * - `TimeActivity <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/timeactivity>`__
     - ``create_time_activity()``, ``delete_time_activity()``, ``query_time_activities()``, ``read_time_activity()``, ``full_update_time_activity()``
   * - `TransactionList <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlist>`__
     - ``transaction_list()``
   * - `TransactionListByVendor <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistbyvendor>`__
     - ``transaction_list_by_vendor()``
   * - `TransactionListByCustomer <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistbycustomer>`__
     - ``transaction_list_by_customer()``
   * - `TransactionListWithSplits <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlistwithsplits>`__
     - ``transaction_list_with_splits()``
   * - `Transfer <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transfer>`__
     - ``create_transfer()``, ``delete_transfer()``, ``query_transfers()``, ``read_transfer()``, ``sparse_update_transfer()``, ``full_update_transfer()``
   * - `TrialBalance <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/trialbalance>`__
     - ``trial_balance()``
   * - `Vendor <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendor>`__
     - ``create_vendor()``, ``query_vendors()``, ``read_vendor()``, ``full_update_vendor()``
   * - `VendorBalance <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorbalance>`__
     - ``vendor_balance()``
   * - `VendorBalanceDetail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorbalancedetail>`__
     - ``vendor_balance_detail()``
   * - `VendorCredit <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorcredit>`__
     - ``create_vendor_credit()``, ``delete_vendor_credit()``, ``query_vendor_credits()``, ``read_vendor_credit()``, ``full_update_vendor_credit()``
   * - `VendorExpenses <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorexpenses>`__
     - ``vendor_expenses()``

Use ``create_tax_code()`` to create a tax code through TaxService. Include a new rate in
``TaxRateDetails`` to create a tax rate as part of the same request. Most paginated entity
queries also provide an ``iter_...()`` counterpart.
