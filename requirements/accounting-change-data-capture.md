# Change Data Capture requirements

Sources: [Intuit's ChangeDataCapture API Reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/changedatacapture) and [CDC guide](https://static.developer.intuit.com/output_html/qbo/docs/learn/explore-the-quickbooks-online-api/change-data-capture.html). A recent Account and Customer CDC request passed in the sandbox.

- Query `GET /v3/company/<realmId>/cdc` with comma-separated `entities` and an ISO `changedSince` date or date-time. Use the configured environment and authentication, URL-encode parameters, and return the complete response including nested query responses, deleted-object status and response time.
- Validate nonempty entity names and date syntax; allow Intuit to validate supported entities and temporal limits. No local clock-based cutoff is imposed. With field validation disabled, forward the date to Intuit.
- Intuit documents a 30-day look-back and a maximum of 1,000 returned objects. This SDK must not claim a complete synchronization or silently advance a checkpoint; callers must handle potential truncation, deletions, recovery, and persistence.
- Test encoded parameters, no-change responses, deleted records, malformed responses and faults without credentials. Live verification and the API Explorer review are outstanding.
