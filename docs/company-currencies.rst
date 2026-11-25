Company currencies
==================

For a multicurrency-enabled company, create, query, read, and update currencies with the authenticated client::

    created = client.create_company_currency({"Code": "GBP"})
    currency = client.read_company_currency(created["CompanyCurrency"]["Id"])["CompanyCurrency"]
    currencies = list(client.iter_company_currencies(page_size=100))
    currency["Active"] = False
    result = client.full_update_company_currency(currency)

The update is a full replacement: include all writable fields to retain and the latest ``Id`` and ``SyncToken``. Setting ``Active`` to false inactivates the currency. QuickBooks determines which currencies can be used; local field validation may be delegated to QuickBooks with ``validate_fields=False``. See the `Intuit reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/companycurrency>`_. Live sandbox behavior remains unverified.

Exchange rates
--------------

Use a multicurrency-enabled company to look up, query, or set rates::

    from decimal import Decimal

    current = client.get_exchange_rate("EUR", as_of_date="2025-01-02")
    for rate in client.iter_exchange_rates(page_size=100):
        print(rate["SourceCurrencyCode"], rate["Rate"])
    result = client.update_exchange_rate({
        "SyncToken": current["ExchangeRate"]["SyncToken"],
        "SourceCurrencyCode": "EUR", "AsOfDate": "2025-01-02",
        "Rate": Decimal("1.2345"),
    })

``TargetCurrencyCode`` defaults to the home currency. Updates change company data and are not automatically retried. See `Intuit's Exchangerate reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/exchangerate>`_; live sandbox verification is pending.
