Credit card payments
====================

Record a payment between home-currency bank and credit-card accounts::

    from decimal import Decimal

    response = client.create_credit_card_payment({
        "TxnDate": "2025-01-02", "Amount": Decimal("100.00"),
        "BankAccountRef": {"value": "37"},
        "CreditCardAccountRef": {"value": "57"},
    })
    payment = client.read_credit_card_payment(response["CreditCardPaymentTxn"]["Id"])["CreditCardPaymentTxn"]
    page = client.query_credit_card_payments(max_results=100)

``iter_credit_card_payments`` fetches pages. Full updates require all writable fields to retain; sparse updates send only the requested changes with the current ``Id`` and ``SyncToken``. To delete, pass the complete current read object to ``delete_credit_card_payment``. Intuit's sparse-update documentation lists required fields even though it describes partial updates, and its query response key is not illustrated; both require live verification. Mutations are never automatically retried. See `Intuit's reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditcardpayment>`_.
