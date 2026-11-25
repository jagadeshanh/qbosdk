Deposits
========

Record a direct deposit into an account::

    from decimal import Decimal

    response = client.create_deposit({
        "DepositToAccountRef": {"value": "35"},
        "Line": [{"Amount": Decimal("20.00"), "DetailType": "DepositLineDetail",
                  "DepositLineDetail": {"AccountRef": {"value": "87"}}}],
    })
    deposit = client.read_deposit(response["Deposit"]["Id"])["Deposit"]
    for item in client.iter_deposits(page_size=100):
        print(item["Id"])

Lines may also reference eligible transactions through ``LinkedTxn``. Use ``full_update_deposit`` with all writable fields to retain or ``sparse_update_deposit`` with changed fields; both require the current ``Id`` and ``SyncToken``. ``delete_deposit`` deletes the record using its current identity. These writes are not automatically retried. See `Intuit's Deposit reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit>`_. Sandbox verification is pending.
