Estimates
=========

Create an estimate for a customer and retrieve its PDF::

    from decimal import Decimal

    result = client.create_estimate({
        "CustomerRef": {"value": "1"},
        "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34"),
                  "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}],
    })
    estimate = client.read_estimate(result["Estimate"]["Id"])["Estimate"]
    pdf_bytes = client.get_estimate_pdf(estimate["Id"])
    for item in client.iter_estimates(page_size=100):
        print(item["Id"])

``query_estimates`` returns a page. Full updates require the current ``Id``, ``SyncToken``, and all writable fields to retain; sparse updates leave omitted fields untouched. ``delete_estimate`` deletes an estimate, and ``send_estimate(id, send_to=...)`` asks QuickBooks to email it. These writes are never automatically retried. See `Intuit's Estimate reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/estimate>`_. Live sandbox verification is pending.
