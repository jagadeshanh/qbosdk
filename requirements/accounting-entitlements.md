# Entitlements

Source: [Intuit Entitlements API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/entitlements), reviewed with Copy all for AI. Sandbox verification is pending.

- Read `GET /manage/entitlements/v3/{realmId}` on the sandbox or production QuickBooks API host, with `Accept: application/xml`. This endpoint does not accept JSON as its requested response format.
- Return the XML response as bytes to preserve all fields and repeated `Entitlement` elements. It can include plan, user counts, feature terms, and company details. Preserve HTTP error status and Intuit trace ID; the existing JSON fault parser does not decode XML fault bodies.
- Entitlements represent available company features; enabled preferences and user permissions are separate. Treat company information as sensitive.
