Account List Detail report
==========================

``account_list_detail`` queries the Account List Detail report from ``GET /v3/company/<realmId>/reports/AccountList``. It returns the entire report dictionary, including its header, nested rows, columns, and any other response fields.

.. code-block:: python

    from qbosdk import AccountingClient

    client = AccountingClient(access_token, realm_id, environment="sandbox")
    report = client.account_list_detail(
        account_type="Income",
        columns="account_name,account_type",
        sort_order="ascend",
    )
    for row in report.get("Rows", {}).get("Row", []):
        print(row.get("ColData", []))

Optional string keyword parameters are ``account_type``, ``start_date``, ``end_date``, ``start_moddate``, ``end_moddate``, ``moddate_macro``, ``start_createdate``, ``end_createdate``, ``createdate_macro``, ``date_macro``, ``sort_by``, ``sort_order``, ``account_status``, and ``columns``. Date values use ``YYYY-MM-DD``. When both ends of a range are provided, the start must precede the end. Sort order is ``ascend`` or ``descend``. With ``validate_fields=False``, date and sort values are sent to QuickBooks for validation.

The supplied Intuit reference mentions ``date_macro``, ``start_createdate``, and ``end_createdate`` in descriptions without listing them consistently; their live support has not been verified. The SDK does not flatten report rows or promise that optional containers are present. See the `Intuit AccountListDetail reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/accountlistdetail>`_.

AP Aging Detail report
======================

``ap_aging_detail`` queries Intuit's ``AgedPayableDetail`` endpoint and returns the full report, including nested rows::

    report = client.ap_aging_detail(
        report_date="2025-06-30", start_duedate="2025-01-01",
        end_duedate="2025-06-30", columns="due_date,vend_name"
    )

Optional parameters also include ``shipvia``, ``term``, ``accounting_method``, ``custom1``, ``custom2``, ``custom3``, ``num_periods``, ``vendor``, ``past_due``, and ``aging_period``. The due-date start must precede the end. The latter three numeric fields are supplied as numbers, while the other parameters are strings. Refer to the `Intuit APAgingDetail reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingdetail>`_.

AP Aging Summary report
=======================

``ap_aging_summary`` queries the ``AgedPayables`` report::

    report = client.ap_aging_summary(report_date="2025-06-30", aging_method="Report_Date")

Optional filters include ``customer``, ``qzurl`` (the strings ``"true"`` or ``"false"``), ``vendor``, ``date_macro``, ``department``, ``sort_order``, and ``aging_method``. See `Intuit's APAgingSummary reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/apagingsummary>`_.

AR Aging reports
================

Query receivables detail or summary with the same authenticated client::

    detail = client.ar_aging_detail(customer="1,2", report_date="2025-06-30", columns="due_date,cust_name")
    summary = client.ar_aging_summary(customer="1", date_macro="Last Fiscal Year")

Detail also supports ``shipvia``, ``term``, due dates, custom fields, ``num_periods``, ``aging_method``, ``past_due``, and ``aging_period``. Summary supports ``qzurl``, ``department``, ``report_date``, ``sort_order``, and ``aging_method``. Both return complete report envelopes. See Intuit's `detail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingdetail>`_ and `summary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/aragingsummary>`_ references.

Balance Sheet report
====================

Query the complete report and optional filters::

    report = client.balance_sheet(date_macro="Last Fiscal Year-to-date", class_="1,2", accounting_method="Accrual")

``class_`` is sent as QuickBooks' ``class`` parameter. See `Intuit's BalanceSheet reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/balancesheet>`_ for the available filters and values.

Cash Flow report
================

``client.cash_flow`` retrieves the full Statement of Cash Flows report::

    report = client.cash_flow(start_date="2025-01-01", end_date="2025-06-30", class_="1,2")

Supported filters include ``customer``, ``vendor``, ``date_macro``, ``item``, ``sort_order``, ``summarize_column_by``, and ``department``. The filter list is provisional pending review of the current `Intuit CashFlow reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/cashflow>`_.

Customer reports
================

Query balances, balance details, and income with the same authenticated client::

    balance = client.customer_balance(customer="1,2", arpaid="Unpaid")
    detail = client.customer_balance_detail(customer="1", columns="tx_date,due_date")
    income = client.customer_income(start_date="2025-01-01", end_date="2025-06-30", class_="2")

The methods return the complete report, including nested rows. ``class_`` is sent as ``class``. See the Intuit references for `balance <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalance>`_, `balance detail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerbalancedetail>`_, and `income <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customerincome>`_. Live verification is pending.

General Ledger report
=====================

Query account activity for a date range::

    report = client.general_ledger(
        start_date="2025-01-01", end_date="2025-06-30",
        source_account_type="Bank", columns="account_name,tx_date"
    )

The complete report is returned. Intuit warns that its hierarchy can be incorrect in some circumstances with subaccounts. The reference table and example differ on ``account_type`` versus ``source_account_type``; both are exposed until live behavior is verified. See `Intuit's GeneralLedger reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/generalledger>`_.

Profit and Loss
---------------

Use ``profit_and_loss()`` for totals and ``profit_and_loss_detail()`` for transaction-level rows::

    summary = client.profit_and_loss(date_macro="This Fiscal Year",
                                     accounting_method="Accrual",
                                     summarize_column_by="Month")
    detail = client.profit_and_loss_detail(start_date="2025-01-01", end_date="2025-03-31",
                                           account="12", columns="tx_date,name,subt_nat_amount",
                                           sort_by="tx_date", sort_order="ascend")

Both methods preserve the complete report, including nested rows, headers and columns. Use comma-separated IDs for report filters and ``class_`` for the QuickBooks class filter. The detail report's available columns depend on company settings. See Intuit's `ProfitAndLoss reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandloss>`_ and `ProfitAndLossDetail reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/profitandlossdetail>`_.

Sales reports
-------------

Query sales grouped by class, customer, department, or product::

    by_class = client.sales_by_class_summary(date_macro="This Fiscal Year")
    by_customer = client.sales_by_customer(customer="5,6", qzurl="false")
    by_department = client.sales_by_department(department="3", sort_order="descend")
    by_product = client.sales_by_product(
        start_duedate="2025-01-01", end_duedate="2025-03-31", item="12",
    )

Each method returns the full report with its header, rows, and columns. Pass comma-separated IDs for entity filters. Use ``class_`` for the class filter. Class and department results depend on the company's tracking settings.

Transaction lists
-----------------

Use ``transaction_list()`` for a general transaction report. For grouped or split views, use the corresponding method::

    purchases = client.transaction_list_by_vendor(vendor="15", appaid="Unpaid")
    sales = client.transaction_list_by_customer(customer="7", group_by="Fiscal Quarter")
    splits = client.transaction_list_with_splits(group_by="Account", date_macro="This Month")

The customer and vendor variants accept their corresponding ID filter. The splits variant supports the Name, Account, and Transaction Type groups. See the `Intuit TransactionList reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transactionlist>`_.

Tax Summary and Trial Balance
-----------------------------

Use the tax agency ID to query a Tax Summary in a supported company. Specify ``locale="FR"`` to select the French Trial Balance endpoint::

    tax = client.tax_summary(agency_id="2", date_macro="This Fiscal Year")
    trial = client.trial_balance(locale="FR", accounting_method="Accrual")

Vendor reports
--------------

Query outstanding balances, vendor transactions, or vendor expenses::

    balance = client.vendor_balance(vendor="12,15", appaid="Unpaid")
    bills = client.vendor_balance_detail(vendor="12", columns="tx_date,doc_num")
    expenses = client.vendor_expenses(date_macro="This Month", vendor="15")

Report methods return the full QuickBooks report. Use ``class_`` when filtering vendor expenses by class.
