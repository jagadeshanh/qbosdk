# Item, category and bundle

Source: [Intuit Item API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item), reviewed with Copy all for AI. Sandbox verification is pending.

- Create `POST /item` with a unique `Name` (maximum 100 characters; no colon, tab or newline). Item type and account references depend on inventory, service, noninventory and locale; inventory items require quantity, inventory start date and asset account. Name, SKU, description and purchase description limits are 100, 100, 4,000 and 1,000 respectively.
- Create categories as Item objects with `Type: Category`; subcategories require `SubItem` and `ParentRef`. Category hierarchy has at most three levels below the root. Bundles are `Type: Group` and cannot be created through this API.
- Read item, category or bundle through `GET /item/{id}`; query them through `GET /query`, with `Type='Category'` or `Type='Group'` filters for the latter two. Preserve response envelopes and pagination.
- Full item update `POST /item` needs current `Id`, `SyncToken` and all writable fields to retain. Omitted writable fields become null. Opt in to `include=donotupdateaccountontxns` to prevent historical transaction account updates. Category update uses the same endpoint and `Type: Category`. Items can be inactivated with `Active: false`; Intuit says this is not valid for categories. Do not automatically retry mutations.
