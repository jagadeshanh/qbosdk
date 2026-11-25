Credit memos
============

Create a credit memo with a customer and a sales item or group line::

    from decimal import Decimal

    created = client.create_credit_memo({
        "CustomerRef": {"value": "1"},
        "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34"),
                  "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}],
    })
    memo = client.read_credit_memo(created["CreditMemo"]["Id"])["CreditMemo"]
    pdf = client.get_credit_memo_pdf(memo["Id"])
    for item in client.iter_credit_memos(page_size=100):
        print(item["Id"])

``query_credit_memos`` returns a page and ``iter_credit_memos`` fetches pages. ``full_update_credit_memo`` needs the current ``Id``, ``SyncToken``, and every writable field to retain. ``delete_credit_memo`` deletes the transaction; ``send_credit_memo(id, send_to=...)`` emails it and changes delivery status. These mutations are not automatically retried. Company settings may require currency, tax, project, or email fields. Refer to `Intuit's CreditMemo reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditmemo>`_. Live sandbox verification is pending.
