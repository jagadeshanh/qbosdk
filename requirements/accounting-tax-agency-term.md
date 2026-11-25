# TaxAgency and Term

[Intuit TaxAgency](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxagency) · [Intuit Term](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/term)

| Entity | Create | Read | Query | Full update |
| --- | --- | --- | --- | --- |
| TaxAgency | `POST /taxagency` | `GET /taxagency/{id}` | `SELECT … FROM TaxAgency` | |
| Term | `POST /term` | `GET /term/{id}` | `SELECT … FROM Term` | `POST /term` with current version and `sparse: false` |

Paths are relative to the company. Read and write results preserve the full entity envelope. Queries use `GET /query`, support SDK pagination, and return the collection under `QueryResponse`.

Tax agencies identify the authority collecting tax. A create requires a `DisplayName` of at most 100 characters. Intuit limits agency visibility in US companies to system-created agencies and applies local tax configuration rules.

Terms describe due dates and optional discounts. Provide a `Name` of at most 31 characters and either `DueDays` (0–999) for standard terms or `DayOfMonthDue` (1–31) for date-driven terms. Intuit's create example encodes `DueDays` as a string, so accept integer and digit-string forms and preserve the input representation. Optional discount and next-month fields use the reference's numeric ranges. Full updates require `Id`, the current `SyncToken`, and the writable fields to retain. Set `Active: false` when disabling a term.
