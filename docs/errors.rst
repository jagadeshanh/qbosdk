Errors and validation
=====================

Local Account field failures raise ``ValidationError``, a ``ValueError`` subclass. It identifies the field and rule without exposing the field value:

.. code-block:: python

    from qbosdk import ValidationError

    try:
        client.create_account({"Name": "x" * 101, "AccountType": "Bank"})
    except ValidationError as error:
        print(error)                 # Account Name must be at most 100 characters; received 101.
        print(error.field, error.code)  # Name max_length
        print(error.limit, error.actual)  # 100 101

The SDK reports the first local failure. These codes are SDK codes, not Intuit fault codes. To delegate supported field rules to QuickBooks, construct the client with ``validate_fields=False``; structural checks still apply.

For Intuit and transport failures, catch ``AccountingError``. Its ``status``, ``fault``, and ``intuit_tid`` attributes carry upstream details when available. The fault can contain sensitive business data, so handle and log it carefully. No error is converted into an empty report or account list.
