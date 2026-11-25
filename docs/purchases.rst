Purchases
=========

Record an expense using an existing funding account and expense account::

    from decimal import Decimal

    purchase = client.create_purchase({
        "PaymentType": "Check",
        "AccountRef": {"value": "1"},
        "Line": [{
            "Amount": Decimal("12.34"),
            "DetailType": "AccountBasedExpenseLineDetail",
            "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "2"}},
        }],
    })["Purchase"]

Use ``read_purchase(purchase_id)`` to retrieve a purchase. Use ``query_purchases()`` for one page or ``iter_purchases()`` for all pages. Full updates require the latest ``Id`` and ``SyncToken``, the required creation fields, and any writable fields you want to keep. Deletion also requires the current version.

QuickBooks computes the total from the transaction. The top-level funding account must match the payment type. Use ``allow_duplicate_doc_number=True`` only when intentionally reusing a document number. See `Intuit's Purchase reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchase>`_.

Purchase orders
---------------

Create a purchase order using an existing vendor, accounts payable account, and item linked to an expense account::

    from decimal import Decimal

    order = client.create_purchase_order({
        "VendorRef": {"value": "5"},
        "APAccountRef": {"value": "3"},
        "Line": [{
            "Amount": Decimal("12.34"),
            "DetailType": "ItemBasedExpenseLineDetail",
            "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "2"}},
        }],
    })["PurchaseOrder"]
    pdf = client.get_purchase_order_pdf(order["Id"])

Use ``read_purchase_order(order_id)`` to retrieve an order and ``query_purchase_orders()`` or ``iter_purchase_orders()`` to list orders. A full update uses the current ``Id`` and ``SyncToken``, required references and lines, and any writable fields you want to keep. Unlink associated transactions before deleting.

``send_purchase_order(order_id)`` emails the order to its stored address. Supply ``send_to=address`` to choose the recipient. ``Memo`` appears on the vendor's copy. ``PrivateNote`` stays internal. See `Intuit's PurchaseOrder reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder>`_.

Reimbursable charges
--------------------

List billable expenses that have yet to be invoiced::

    statement = "SELECT * FROM ReimburseCharge WHERE HasBeenInvoiced = false"
    for charge in client.iter_reimburse_charges(statement, page_size=100):
        current = client.read_reimburse_charge(charge["Id"])["ReimburseCharge"]

``query_reimburse_charges()`` returns a single page. QuickBooks generates these charges from billable expense lines and links them to invoices. See `Intuit's ReimburseCharge reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/reimbursecharge>`_.

Vendors and vendor credits
--------------------------

Create or retrieve a vendor::

    vendor = client.create_vendor({"DisplayName": "Example Vendor"})["Vendor"]
    current = client.read_vendor(vendor["Id"])["Vendor"]

Use ``query_vendors()`` or ``iter_vendors()`` to retrieve vendors by query. Full updates require the latest version, a name, and any writable fields you intend to keep.

Create a vendor credit with ``create_vendor_credit(value)`` using ``VendorRef`` and expense lines carrying amounts. Use ``read_vendor_credit(credit_id)`` for one credit, ``query_vendor_credits()`` for a page, or ``iter_vendor_credits()`` to traverse pages. Full updates and deletion require the current ID and sync token. Pass ``allow_duplicate_doc_number=True`` on create or update only when deliberately reusing a document number.
