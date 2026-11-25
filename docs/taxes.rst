Taxes
=====

Tax classifications
-------------------

Browse the tax classification hierarchy before choosing a classification for an item::

    parents = client.read_tax_classifications_by_level(1)
    for parent in parents["QueryResponse"]["TaxClassification"]:
        parent_id = parent.get("Id") or parent.get("id")
        if parent_id:
            children = client.read_tax_classification_children(parent_id)

``read_all_tax_classifications()`` retrieves the full catalog. Use ``read_tax_classification(classification_id)`` for one record under the ``TaxClassification`` key. Collection reads use ``QueryResponse.TaxClassification``. The sandbox returned ``Id`` for both shapes, and Intuit's example uses ``id``. The SDK preserves the returned casing. See `Intuit's TaxClassification reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxclassification>`_.

Tax codes and rates
-------------------

List active codes to find one for a transaction::

    statement = "SELECT * FROM TaxCode WHERE Active = true"
    codes = client.query_tax_codes(statement)["QueryResponse"].get("TaxCode", [])
    current = client.read_tax_code("2")["TaxCode"]  # Use an ID for a saved tax code.

The query may also list pseudo-codes such as ``TAX`` or ``NON``. The sandbox returned an invalid-ID fault when reading a pseudo-code.

Use ``create_tax_code(value)`` to associate existing rates or create new ones where supported by the company tax model::

    result = client.create_tax_code({
        "TaxCode": "Sample code",
        "TaxRateDetails": [{"TaxRateId": "2", "TaxApplicableOn": "Sales"}],
    })
    code_id = result["TaxCodeId"]

For a new rate, supply ``TaxRateName``, ``RateValue`` as a string such as ``"8"``, and the ID of an existing agency as ``TaxAgencyId``. See Intuit's `TaxCode reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxcode>`_ and `TaxService reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxservice>`_.

Use ``query_tax_rates()`` for one page or ``iter_tax_rates()`` for multiple pages. Read an individual rate with ``read_tax_rate(rate_id)``. New rates are created when you create a tax code with new entries in its ``TaxRateDetails``. See `Intuit's TaxRate reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxrate>`_.

Tax payments
------------

In Australian, Canadian, or UK companies, use ``query_tax_payments()`` or ``iter_tax_payments()`` to list payments and refunds on filed returns::

    for payment in client.iter_tax_payments(page_size=50):
        current = client.read_tax_payment(payment["Id"])["TaxPayment"]

QuickBooks may return the refund indicator and amount as strings. Use the returned wire types when interpreting the result. See `Intuit's TaxPayment reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxpayment>`_.

Tax agencies
------------

A tax agency supplies the agency ID used when creating a new rate or reading a Tax Summary::

    agencies = client.query_tax_agencies(max_results=20)
    current = client.read_tax_agency("1")["TaxAgency"]

Use ``iter_tax_agencies()`` for multiple pages. Where company rules permit creation, call ``create_tax_agency({"DisplayName": "Example agency"})``. Intuit controls tax agency visibility and availability by tax model and locale.
