# TaxClassification

[Intuit TaxClassification reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxclassification)

Tax classifications group products for jurisdiction-specific taxation. Returned fields include an ID, code, name, description, level, parent reference, and applicable item types. Intuit's sample uses `id`; sandbox singular and collection reads returned `Id`. Preserve the original casing and content. Level `1` represents parent classifications and level `2` represents child classifications.

| Operation | Request relative to company | Result |
| --- | --- | --- |
| Read by ID | `GET /taxclassification/{classificationId}` | `TaxClassification` object in the response envelope |
| Read children | `GET /taxclassification/{parentId}/children` | `QueryResponse.TaxClassification` list |
| Read all | `GET /taxclassification` | `QueryResponse.TaxClassification` list |
| Read by level | `GET /taxclassification?level=1` or `level=2` | `QueryResponse.TaxClassification` list |

The level option accepts an integer or its string representation. With field validation disabled, other nonempty level values are delegated to Intuit. The endpoint uses dedicated paths for collection reads. A sandbox check verified the list envelope for all, level, and children, and the singular envelope for read by ID.
