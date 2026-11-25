Bills
=====

Bills are accounts-payable transactions. Create, query, read, fully update, and delete them with the Accounting client::

    from decimal import Decimal

    created = client.create_bill({
        "VendorRef": {"value": "56"},
        "Line": [{"Amount": Decimal("12.34"),
                  "DetailType": "AccountBasedExpenseLineDetail",
                  "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "7"}}}],
    })
    bill = client.read_bill(created["Bill"]["Id"])["Bill"]
    for item in client.iter_bills(page_size=100):
        print(item["Id"])

``full_update_bill`` requires the current ``Id`` and ``SyncToken``, and all writable fields to retain; omitted fields are cleared. ``delete_bill`` requires ``Id`` and ``SyncToken``; unlink related transactions before deleting. These operations change accounting data and are not automatically retried. ``allow_duplicate_doc_number=True`` explicitly opts in to Intuit's duplicate-document-number parameter. See `Intuit's Bill reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill>`_.

Bill payments
-------------

``create_bill_payment``, ``read_bill_payment``, ``query_bill_payments``, ``iter_bill_payments``, and ``full_update_bill_payment`` support the corresponding BillPayment operations. Supply the vendor, payment type, total amount, lines, and matching check or credit-card payment details. The client preserves decimal amounts. ``delete_bill_payment`` deletes a payment; ``void_bill_payment`` submits the documented sparse void using its current ``Id`` and ``SyncToken``. These methods change financial records and are never retried automatically. See `Intuit's BillPayment reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/billpayment>`_.

Budgets
-------

``create_budget``, ``read_budget``, ``query_budgets``, ``iter_budgets``, ``full_update_budget``, and ``delete_budget`` expose Intuit's Budget operations. Create and full update require ``StartDate`` and ``EndDate``; full update also requires the current ``Id`` and ``SyncToken`` and all writable fields to retain. The delete response may contain only a timestamp. Mutations are not automatically retried. See `Intuit's Budget reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/budget>`_.

Change orders
-------------

The provisional ``create_change_order``, ``read_change_order``, ``full_update_change_order``, and ``delete_change_order`` methods implement the documented ChangeOrder operations. Change orders require supported US company plans and an active project. Full updates must retain all desired fields and lines; deletion is irreversible. The contract still needs review against Intuit's current API Explorer and live sandbox verification.
