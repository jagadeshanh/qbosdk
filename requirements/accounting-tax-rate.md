# TaxRate

[Intuit TaxRate reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxrate)

A tax rate records the percentage applied in tax calculations. The API returns the rate, agency, applicable dates, active state, and related information. Preserve the returned fields and decode fractional JSON numbers as Decimal.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Query | `GET /query` with `SELECT … FROM TaxRate` and pagination | `QueryResponse.TaxRate` |
| Read | `GET /taxrate/{id}` | TaxRate envelope |
| Create | `POST /taxservice/taxcode` with at least one new rate in `TaxRateDetails` | TaxService result including the new code and associated rate IDs |

Use the [TaxService contract](accounting-tax-service.md) to create a rate. The TaxRate read schema allows longer names than the TaxService create schema. Enforce the TaxService limit only on its new-rate payloads.
