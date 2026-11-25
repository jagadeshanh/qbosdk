Inventory adjustments
=====================

Create an inventory quantity adjustment::

    from decimal import Decimal

    created = client.create_inventory_adjustment({
        "DocNumber": "27", "TxnDate": "2025-01-02",
        "AdjustAccountRef": {"value": "91"},
        "Line": [{"ItemAdjustmentLineDetail": {
            "ItemRef": {"value": "101"}, "QtyDiff": Decimal("-2")
        }}],
    })
    adjustment = client.read_inventory_adjustment(created["InventoryAdjustment"]["Id"])["InventoryAdjustment"]

``update_inventory_adjustment`` sends a sparse update with the current ``Id`` and ``SyncToken``; ``delete_inventory_adjustment`` deletes it with that identity. These operations affect inventory and valuation and are not automatically retried. Intuit's date-format and sparse-field descriptions have inconsistencies; see the `InventoryAdjustment reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryadjustment>`_ and verify against the company before use. Live sandbox verification is pending.

Inventory valuation reports
---------------------------

Query detailed or summary inventory valuation reports::

    detail = client.inventory_valuation_detail(date_macro="This Fiscal Year-to-date", columns="tx_date,qty_on_hand")
    summary = client.inventory_valuation_summary(report_date="2025-06-30", item="1,2")

Both methods return the complete report with nested rows. See the Intuit references for `detail <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationdetail>`_ and `summary <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryvaluationsummary>`_. Live verification is pending.
