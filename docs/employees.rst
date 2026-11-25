Employees
=========

Create and read an employee using the authenticated client::

    created = client.create_employee({"GivenName": "Example", "FamilyName": "Employee"})
    employee = client.read_employee(created["Employee"]["Id"])["Employee"]
    for item in client.iter_employees(page_size=100):
        print(item["Id"])

``full_update_employee`` requires the current ``Id`` and ``SyncToken`` and all writable fields to retain. Set ``Active`` false to inactivate. Payroll-enabled companies impose additional field and address rules: in particular, remove masked SSNs from update requests. Read `Intuit's Employee reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee>`_ and check the company's payroll settings before submitting. Intuit's business rules say both given and family names are required, while the create field descriptions say either is sufficient; live enforcement remains unverified.

Company entitlements
--------------------

``read_entitlements()`` returns the company's Entitlements response as XML bytes::

    from xml.etree import ElementTree

    root = ElementTree.fromstring(client.read_entitlements())
    print(root.findtext("PlanName"))

The endpoint uses a separate QuickBooks ``/manage`` path and XML response format. Its features describe what is available to the company; preferences and user permissions may further restrict use. XML fault bodies are not yet decoded into ``AccountingError.fault``. See `Intuit's Entitlements reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/entitlements>`_. Sandbox verification is pending.
