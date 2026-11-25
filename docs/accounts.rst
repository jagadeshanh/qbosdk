Accounts
========

Create an Accounting client with the access token and realm ID for the same company and environment:

.. code-block:: python

    from qbosdk import AccountingClient

    client = AccountingClient(access_token, realm_id, environment="sandbox", country="US")
    created = client.create_account({"Name": "Example bank", "AccountType": "Bank"})
    account = client.read_account(created["Account"]["Id"])["Account"]

Methods return Intuit's full response envelopes as dictionaries. Fractional JSON numbers are decoded as ``Decimal``. Request dictionaries may contain finite ``Decimal`` values, which are encoded as exact JSON numbers. The SDK preserves nested references and response metadata.

Query and paginate
------------------

.. code-block:: python

    page = client.query_accounts(
        "SELECT * FROM Account WHERE Active = true", start_position=1, max_results=100
    )
    accounts = page["QueryResponse"].get("Account", [])
    for account in client.iter_accounts(page_size=100):
        print(account["Name"])

The query accepts ``SELECT * FROM Account`` with optional Intuit filters and ordering. Do not include pagination clauses or semicolons. Positions start at 1; page sizes range from 1 to 1000. Pagination is not a snapshot: changes during iteration can affect results. Query text is passed to QuickBooks; escape any interpolated values according to `Intuit's query rules <https://static.developer.intuit.com/output_html/qbo/docs/learn/explore-the-quickbooks-online-api/data-queries.html>`_.

Full update
-----------

``full_update_account`` requires the current ``Id`` and ``SyncToken``. A full update clears omitted writable fields, so first read the account and include **every writable field you intend to keep**. Do not treat the partial example below as a safe replacement for an account with other writable fields::

    updated = client.full_update_account({
        "Id": account["Id"],
        "SyncToken": account["SyncToken"],
        "Name": account["Name"],
        "AccountType": account["AccountType"],
        # Include all other writable fields to retain them.
    })

QuickBooks uses ``SyncToken`` to detect stale updates. To inactivate an account, include ``Active: False`` in a full update with the other fields to retain. Inactivation does not permanently delete it. The SDK does not retry writes automatically; a timeout can leave the result unknown.

Field validation is enabled by default. Pass ``country="AU"``, ``"CA"``, ``"US"``, ``"UK"``, or ``"IN"`` to apply the documented account-number length for that country. With no country, QuickBooks validates that limit. ``ACCOUNT_TYPE_REFERENCE`` provides documented type/subtype mappings as a reference, not an exhaustive allowlist. ``CurrencyRef`` and other system-generated fields are read-only.

Batch operations
----------------

Submit up to 30 independent items with ``client.batch``::

    result = client.batch([
        {"bId": "one", "Query": "select * from Account"},
        {"bId": "two", "Query": "select * from Customer"},
    ])
    for item in result["BatchItemResponse"]:
        print(item.get("bId"), item.get("Fault"))

Items execute independently and order is not guaranteed. Inspect each result for a fault even when the HTTP request succeeds. Batch requests may include writes and are not automatically retried. Consult `Intuit's Batch reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/batch>`_ for limits and supported operations.

Change data capture
-------------------

Query changes for one or more entities::

    changes = client.change_data_capture(["Customer", "Estimate"], "2025-01-15T09:00:00-07:00")

The full ``CDCResponse`` is returned, including deleted-object status. Intuit documents a 30-day look-back and a maximum of 1,000 objects per response. The SDK does not guarantee completeness or manage synchronization checkpoints: callers must handle possible truncation, deletion, and recovery. See `Intuit's CDC guide <https://static.developer.intuit.com/output_html/qbo/docs/learn/explore-the-quickbooks-online-api/change-data-capture.html>`_.

Classes
-------

``create_class``, ``read_class``, ``query_classes``, ``iter_classes`` and ``full_update_class`` manage transaction classes. The current support is provisional pending review of the current Intuit API Explorer reference. A full update requires the current ``Id`` and ``SyncToken`` and all writable fields to retain; do not automatically retry writes.

Company profile
---------------

``read_company_info()`` reads the connected company's profile. ``query_company_info()`` queries it. ``sparse_update_company_info`` changes supplied fields while ``full_update_company_info`` may clear omitted writable fields; both require the connected company ``Id`` and the current ``SyncToken``. Intuit documents special behavior for address fields, so include the intended address details and inspect the returned address. The current API Explorer review and live sandbox verification remain outstanding.
