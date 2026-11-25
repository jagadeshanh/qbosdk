# InventoryAdjustment

Source: [Intuit InventoryAdjustment API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/inventoryadjustment), reviewed with Copy all for AI. Available for US QuickBooks Online Plus and Advanced plans. Live sandbox verification is pending.

- Create `POST /inventoryadjustment` with `DocNumber`, `TxnDate`, `AdjustAccountRef`, and at least one `Line`; item adjustment details include `ItemRef` and `QtyDiff`. `DocNumber` is limited to 21 characters and `PrivateNote` to 4,000.
- Read `GET /inventoryadjustment/{id}`. Update `POST /inventoryadjustment` with `Id`, `SyncToken`, and `sparse: true`; the text describes identity as the minimum while the field table marks additional fields required. Delete uses `POST /inventoryadjustment?operation=delete` with current `Id` and `SyncToken`.
- The date text says `yyyy/MM/dd` while examples use `yyyy-MM-dd`; the SDK passes a nonempty date string to Intuit without choosing between them. Preserve complete responses and faults; do not retry writes automatically. Adjustment changes inventory quantity and valuation.
