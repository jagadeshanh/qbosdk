# TaxCode

[Intuit TaxCode reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxcode)

Tax codes mark sales as taxable or non-taxable and can group tax rates used for sales and purchases. The SDK preserves the complete response, including the grouping details, status, metadata, and system-generated flags.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Query | `GET /query` with `SELECT … FROM TaxCode` and pagination | `QueryResponse.TaxCode` |
| Read | `GET /taxcode/{id}` | TaxCode envelope |
| Create | `POST /taxservice/taxcode` | TaxService response with the newly created code ID and rates |

Use the [TaxService contract](accounting-tax-service.md) for the create request. Intuit does not document an independent write route under `/taxcode`.
