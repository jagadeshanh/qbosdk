# TaxPayment

[Intuit TaxPayment reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxpayment)

A tax payment or refund is associated with a filed return in Australia, Canada, or the United Kingdom. Preserve the complete result including `Refund`, `PaymentAccountRef`, `PaymentAmount`, dates, and metadata. The field table describes boolean and decimal values while the sample encodes `Refund` and `PaymentAmount` as strings. The table labels the date `TxnDate`, and the sample returns `PaymentDate`. Preserve both the wire field names and value types.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Query | `GET /query` with `SELECT … FROM TaxPayment` and pagination | `QueryResponse.TaxPayment` |
| Read | `GET /taxpayment/{id}` | TaxPayment envelope |

There are no write operations in the reference. Live verification requires a compatible sandbox company.
