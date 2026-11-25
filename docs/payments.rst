Customer payments
=================

Create an unapplied payment for an existing sandbox customer::

    from decimal import Decimal

    result = client.create_payment({
        "CustomerRef": {"value": "5"},
        "TotalAmt": Decimal("12.34"),
    })
    payment = result["Payment"]
    current = client.read_payment(payment["Id"])["Payment"]
    identity = {"Id": current["Id"], "SyncToken": current["SyncToken"]}
    updated = client.sparse_update_payment({**identity, "PrivateNote": "Received by check"})

Add a ``Line`` entry with an ``Amount`` and a ``LinkedTxn`` list to apply a payment. Each link identifies the transaction by ``TxnId`` and ``TxnType``, such as ``Invoice``. Include every line to keep when editing lines, or pass ``Line=[]`` to remove them all. For a full update, include all writable fields to retain and the current version from QuickBooks.

Use ``query_payments()`` for a single page or ``iter_payments()`` to iterate across pages. ``get_payment_pdf(payment_id)`` returns bytes. ``send_payment(payment_id, send_to=address)`` asks QuickBooks to email the receipt to the specified address.

Both ``delete_payment(identity)`` and ``void_payment(identity)`` require the latest version. Voiding keeps the record and zeroes its amounts. For a deposited payment, Intuit requires you to remove the associated deposit first. A Payment query was verified in the sandbox. See `Intuit's Payment reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/payment>`_.

Payment methods
---------------

Create a payment method and use its ID in ``PaymentMethodRef.value`` when recording a payment::

    method = client.create_payment_method({
        "Name": "Business Check",
        "Type": "NON_CREDIT_CARD",
    })["PaymentMethod"]
    current = client.read_payment_method(method["Id"])["PaymentMethod"]
    methods = list(client.iter_payment_methods(page_size=100))

``query_payment_methods()`` returns one page. Use ``full_update_payment_method(value)`` with the current ``Id``, ``SyncToken``, ``Name``, and any writable fields you want to keep. Set ``Active`` to false to disable a method. Names are limited to 31 characters. See `Intuit's PaymentMethod reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod>`_.

Refund receipts
---------------

Read an existing refund receipt or retrieve receipts one page at a time::

    response = client.query_refund_receipts(max_results=20)
    for receipt in response["QueryResponse"].get("RefundReceipt", []):
        current = client.read_refund_receipt(receipt["Id"])["RefundReceipt"]

Use ``iter_refund_receipts()`` to iterate across pages. To create a receipt, supply the account used to refund the money as ``DepositToAccountRef.value`` and at least one sales item or group line. A full update also requires the current ``Id`` and ``SyncToken`` and the writable fields to retain. A sparse update applies the fields you supply. Unlink associated transactions before deleting a receipt.

``get_refund_receipt_pdf(receipt_id)`` returns PDF bytes. ``send_refund_receipt(receipt_id)`` uses the saved recipient. Supply ``send_to=address`` to send to a specific address and update the stored billing email. See `Intuit's RefundReceipt reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt>`_.

Sales receipts
--------------

Record a sale paid at purchase using an existing sales item::

    receipt = client.create_sales_receipt({
        "Line": [{
            "Amount": 35,
            "DetailType": "SalesItemLineDetail",
            "SalesItemLineDetail": {"ItemRef": {"value": "10"}},
        }],
    })["SalesReceipt"]
    current = client.read_sales_receipt(receipt["Id"])["SalesReceipt"]

Use ``query_sales_receipts()`` for one page and ``iter_sales_receipts()`` to traverse pages. Full updates require the current version, customer reference, sales lines, and other writable fields to retain. Sparse updates use the current version and only the fields to change. Deletion and voiding also require the latest ``Id`` and ``SyncToken``. Remove any associated deposit before voiding.

``get_sales_receipt_pdf(receipt_id)`` returns PDF bytes. Use ``send_sales_receipt(receipt_id)`` to email the stored address or supply ``send_to=address`` to send to a specific recipient and update the saved billing email. See `Intuit's SalesReceipt reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt>`_.
