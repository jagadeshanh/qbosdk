Customers
=========

Create and retrieve customers with the Accounting client::

    created = client.create_customer({"GivenName": "Example", "FamilyName": "Customer"})
    customer = client.read_customer(created["Customer"]["Id"])["Customer"]
    for item in client.iter_customers(page_size=100):
        print(item["DisplayName"])
    updated = client.sparse_update_customer({
        "Id": customer["Id"], "SyncToken": customer["SyncToken"], "Notes": "Updated"
    })

``query_customers`` returns a page. Full updates require all writable fields to retain; sparse updates leave omitted fields unchanged. Set ``Active`` to false to inactivate a customer. Display names must be unique across customers, vendors and employees; Intuit enforces uniqueness. See `Intuit's Customer reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer>`_. Sandbox verification is pending.

Customer types
--------------

Use ``read_customer_type(id)``, ``query_customer_types(...)``, or ``iter_customer_types(page_size=100)`` to read the categories defined in QuickBooks. See the `CustomerType reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customertype>`_.

Departments
-----------

Create a location and retrieve it::

    result = client.create_department({"Name": "Support"})
    department = client.read_department(result["Department"]["Id"])["Department"]
    for item in client.iter_departments(page_size=100):
        print(item["Name"])

``full_update_department`` requires the current ``Id`` and ``SyncToken`` and all writable fields to retain. Set ``Active`` to false to inactivate. A subdepartment requires a ``ParentRef``. See `Intuit's Department reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department>`_. Sandbox verification is pending.
