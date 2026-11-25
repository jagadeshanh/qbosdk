# ExchangeRate

Source: [Intuit Exchangerate API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/exchangerate), reviewed with Copy all for AI. Applies to multicurrency-enabled companies; sandbox verification is pending.

- Get `GET /exchangerate?sourcecurrencycode={code}[&asofdate={date}]`; the date defaults to today. Currency codes are three-letter ISO 4217 codes and dates use `YYYY-MM-DD`.
- Query `GET /query` for `ExchangeRate`, using pagination. Return the complete response and preserve exact decimal rates.
- Update `POST /exchangerate` with `SyncToken`, `AsOfDate`, `SourceCurrencyCode`, and `Rate`; `TargetCurrencyCode` defaults to home currency. Intuit documents that updating the home currency fails and that equal source and target currencies use a rate of one. Preserve Intuit faults and do not automatically retry updates.
