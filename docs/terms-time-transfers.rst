Terms, time activities, and transfers
====================================

Payment terms
-------------

Create a standard due-date term with ``client.create_term({"Name": "Net 45", "DueDays": 45})``. For date-driven terms, provide ``DayOfMonthDue``. Use ``query_terms()`` for one page, ``iter_terms()`` for pagination, and ``read_term(term_id)`` for an individual term. Use ``full_update_term(value)`` with the current ID, sync token, and writable fields to retain.

Time activities
---------------

Record two hours of work for an existing employee::

    activity = client.create_time_activity({
        "NameOf": "Employee",
        "EmployeeRef": {"value": "4"},
        "TxnDate": "2025-03-01",
        "Hours": 2,
        "Minutes": 0,
    })["TimeActivity"]

For a vendor, use ``NameOf="Vendor"`` and ``VendorRef``. Supply the customer and hourly rate for billable work. Use ``query_time_activities()`` to get a page, ``iter_time_activities()`` for pagination, and ``read_time_activity(activity_id)`` to fetch one. A full update requires the current version and writable fields to retain. Delete with the current ID and sync token.

Transfers
---------

Record a transfer between two existing QuickBooks accounts::

    from decimal import Decimal

    result = client.create_transfer({
        "FromAccountRef": {"value": "3"},
        "ToAccountRef": {"value": "4"},
        "Amount": Decimal("12.34"),
    })
    saved = client.read_transfer(result["Transfer"]["Id"])["Transfer"]

Use ``query_transfers()`` or ``iter_transfers()`` to retrieve transfers by query. Use the latest version for full or sparse updates. To delete a transfer, pass the entire current ``Transfer`` object from the read response to ``delete_transfer(saved)``.
