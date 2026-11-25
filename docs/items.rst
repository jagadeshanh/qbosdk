Items, categories and bundles
=============================

Create and retrieve an item or category::

    item = client.create_item({"Name": "Consulting", "Type": "Service",
                               "IncomeAccountRef": {"value": "1"},
                               "ExpenseAccountRef": {"value": "2"}})
    category = client.create_category({"Name": "Services", "Type": "Category"})
    categories = client.query_categories()
    bundles = client.query_bundles()
    for entry in client.iter_items(page_size=100):
        print(entry["Name"])

``read_item``, ``read_category``, and ``read_bundle`` read the same Item resource. Bundles cannot be created through the API. Inventory items require additional fields and account references; category hierarchies have their own rules. Full updates require the current ``Id`` and ``SyncToken`` and all writable fields to retain. Use ``do_not_update_account_on_transactions=True`` to request Intuit's historical-account update exclusion. See `Intuit's Item reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item>`_. Sandbox verification is pending.
