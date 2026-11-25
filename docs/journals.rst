Journal entries
===============

Create a balanced journal entry::

    from decimal import Decimal

    entry = client.create_journal_entry({"Line": [
        {"Amount": Decimal("12.34"), "DetailType": "JournalEntryLineDetail",
         "JournalEntryLineDetail": {"PostingType": "Debit", "AccountRef": {"value": "1"}}},
        {"Amount": Decimal("12.34"), "DetailType": "JournalEntryLineDetail",
         "JournalEntryLineDetail": {"PostingType": "Credit", "AccountRef": {"value": "2"}}},
    ]})
    current = client.read_journal_entry(entry["JournalEntry"]["Id"])["JournalEntry"]
    for item in client.iter_journal_entries(page_size=100):
        print(item["Id"])

Full updates require the current ``Id``, ``SyncToken`` and all writable fields and lines to retain. Sparse updates leave omitted fields unchanged; delete uses the current identity. Explicit document-number options permit duplicate numbers or request automatic numbering. QuickBooks validates accounting balance, including tax rules. Writes are never automatically retried. See `Intuit's JournalEntry reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalentry>`_. Sandbox verification is pending.

Journal report
--------------

Query the Journal report with an explicit date range and columns::

    report = client.journal_report(start_date="2025-01-01", end_date="2025-06-30",
                                   columns="tx_date,credit_amt", sort_order="ascend")

The method preserves the full nested report response. The default query was verified in the sandbox. See `Intuit's JournalReport reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalreport>`_.
