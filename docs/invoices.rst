Invoices
========

Create and read an invoice::

    from decimal import Decimal

    created = client.create_invoice({
        "CustomerRef": {"value": "1"},
        "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34"),
                  "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}],
    })
    invoice = client.read_invoice(created["Invoice"]["Id"])["Invoice"]
    pdf = client.get_invoice_pdf(invoice["Id"])
    for item in client.iter_invoices(page_size=100):
        print(item["Id"])

``query_invoices`` returns a page. Full updates require the current ``Id``, ``SyncToken``, and all writable fields to retain; sparse updates leave omitted fields unchanged. ``void_invoice`` zeroes amounts and quantities, while ``delete_invoice`` requires linked transactions to be unlinked first. ``send_invoice(id, send_to=...)`` emails the invoice. Writes and sends are not automatically retried. To allow duplicate document numbers, explicitly pass ``allow_duplicate_doc_number=True`` to create or update. See `Intuit's Invoice reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice>`_. Sandbox verification is pending.
