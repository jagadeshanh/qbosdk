# ReimburseCharge

[Intuit ReimburseCharge reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/reimbursecharge)

QuickBooks creates a reimbursable charge when a bill or expense line is made billable to a customer. The returned object can include the charge amount, customer, lines, currency, and the linked invoice. `HasBeenInvoiced` indicates whether an invoice is linked. The SDK preserves the entire object and decodes fractional JSON amounts as Decimal.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Query | `GET /query` with `SELECT … FROM ReimburseCharge`, optional filters such as `HasBeenInvoiced = false`, and pagination | `QueryResponse.ReimburseCharge` |
| Read | `GET /reimbursecharge/{chargeId}` | ReimburseCharge envelope |

The read URL in the reference labels the generic path placeholder `taxrateId`. Use the reimbursable charge's ID. The reference defines read and query for this entity.
