# TaxService

[Intuit TaxService reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxservice)

Create a tax code with one or more existing or new tax rates using `POST /v3/company/{realmId}/taxservice/taxcode`. `TaxCode` is a required name of up to 100 characters. `TaxRateDetails` contains one or more objects.

- For existing rates, pass `TaxRateId`. Omit `RateValue` and `TaxAgencyId`. Intuit ignores `TaxRateName` when an ID is supplied. Each existing rate ID may occur once.
- To create a rate within the request, omit `TaxRateId` and supply `TaxRateName` (up to 10 characters), a string percentage `RateValue` from 0 to 100, and an existing `TaxAgencyId` as a string.
- `TaxApplicableOn` is optional and accepts `Sales` or `Purchase`.

The response contains top-level `TaxCodeId`, `TaxCode`, and `TaxRateDetails` with assigned rate IDs and formatted values. `create_tax_code` and `create_tax_service` use the same operation. The SDK sends each write once and preserves faults. Intuit enforces company and tax-model restrictions, including visibility rules for US tax agencies.
