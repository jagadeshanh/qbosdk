Recurring transactions
======================

Recurring templates are available for supported QuickBooks Online Essentials and Plus companies. Query a page, then read an individual template using its ID::

    response = client.query_recurring_transactions(max_results=10)
    templates = response["QueryResponse"].get("RecurringTransaction", [])
    for entry in client.iter_recurring_transactions():
        for transaction_type, template in entry.items():
            if isinstance(template, dict) and "Id" in template:
                current = client.read_recurring_transaction(template["Id"])

To create a template, pass a dictionary with one supported transaction-type key. Include that transaction's required fields and place the template settings under its ``RecurringInfo`` key. The schedule depends on the recurrence mode. An active automated template can generate transactions in QuickBooks.

To delete an unlinked template, use the current version. For example, ``client.delete_recurring_transaction({"Invoice": {"Id": "20", "SyncToken": "1"}})`` deletes an invoice template. See `Intuit's RecurringTransaction reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/recurringtransaction>`_.
