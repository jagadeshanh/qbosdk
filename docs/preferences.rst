Company preferences
===================

Read settings for the company associated with the accounting client::

    preferences = client.read_preferences()["Preferences"]
    currency_preferences = preferences.get("CurrencyPrefs", {})

Use ``query_preferences()`` to issue a Preferences query. It accepts optional filters and sorting on metadata timestamps. The endpoint does not paginate.

``full_update_preferences(value)`` changes company-wide settings. Read the current preferences first, then submit the latest ``Id`` and ``SyncToken`` along with any writable settings you want to keep. QuickBooks can clear omitted settings or restore their defaults. See the writable fields and edition restrictions in `Intuit's Preferences reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/preferences>`_.
