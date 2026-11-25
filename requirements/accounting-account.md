# Accounting API: Account requirements

## Scope and connection

Implement the QuickBooks Online Account object and create, query, read, and full-update operations described below. The SDK implements these operations; live sandbox verification remains outstanding. The SDK must use the connected company's `realmId`, an accounting-scoped access token, and the matching environment: `https://sandbox-quickbooks.api.intuit.com` for sandbox and `https://quickbooks.api.intuit.com` for production. Requests use HTTPS and must not expose tokens in URLs, logs, or errors. The host application owns token storage and refresh; an expired or rejected token must be reported to the caller.

The [Intuit Account reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account) is the authority for current fields, locale-specific rules, supported values, and version behavior. The contracts below are based on the supplied reference; verify the current documentation before implementation.

## Account object

An account represents an entry in a company's chart of accounts. Preserve documented fields and nested references in responses, including fields not needed for a particular operation. Monetary balances must retain their decimal precision. The response may include an `Account` object and a `time` field.

| Field | Contract |
| --- | --- |
| `Id` | String identifier; required for update. |
| `Name` | Required user-visible name; unique, at most 100 characters, with no double quote or colon. |
| `SyncToken` | String version; required for update. A stale token causes an update failure. |
| `AcctNum` | Conditionally required account number; no colon. Maximum length: 20 for AU and CA; 7 for US, UK, and IN. By default the SDK enforces the applicable length when the company country is supplied; callers may explicitly delegate field validation to Intuit. Without a country Intuit validates the length. |
| `CurrencyRef`, `ParentRef`, `TaxCodeRef` | Reference objects; `TaxCodeRef` applies to global locales and may be conditionally required. |
| `Description`, `Active` | Optional description and active status. |
| `AccountType`, `AccountSubType` | Account classification and subtype; at least one is required for creation according to the supplied contract. |
| `MetaData` | Server-managed modification metadata; read-only. |
| `SubAccount`, `Classification`, `FullyQualifiedName` | Read-only hierarchy and classification information. The fully qualified name is system generated and limited to five levels. |
| `CurrentBalance`, `CurrentBalanceWithSubAccounts` | Read-only decimal balances; `CurrentBalance` applies to balance-sheet accounts. |

Some account types cannot be parents or subaccounts; verify the current Intuit rules before enforcing them. Inactivation uses an update with `Active: false`; it does not permanently delete the account or remove existing references.

## Operations

### Create

- `POST /v3/company/<realmId>/account`, with a JSON account object. At minimum, require `Name` and either `AccountType` or `AccountSubType`; apply documented conditional fields and name/account-number rules.
- Return the created `Account` response, including its `Id` and `SyncToken` when supplied. Surface duplicate-name and other Intuit validation failures to the caller.
- Do not automatically retry an ambiguous create: the original request may have succeeded.

### Query

- `GET /v3/company/<realmId>/query?query=<selectStatement>`; correctly encode the query as a URL parameter. Support an Account select statement such as `select * from Account where Metadata.CreateTime > '2014-12-31'`.
- Return the `QueryResponse` and its account list and pagination metadata when present. An empty result must be distinguishable from an error. Preserve the response's other documented metadata.
- Document query syntax, supported filtering and pagination against Intuit's current query documentation; do not interpolate untrusted values into query text without appropriate escaping.

### Read

- `GET /v3/company/<realmId>/account/<accountId>` retrieves an existing account. Encode identifiers safely as path segments.
- Return the `Account` response, including its current `SyncToken`, and surface not-found and authorization failures.

### Full update

- `POST /v3/company/<realmId>/account` with the account `Id`, current `SyncToken`, and all writable fields to retain. Return the updated `Account` response and its new version when supplied.
- **Omitted writable fields are set to null.** Make full-replacement semantics explicit in the public interface and documentation; do not silently turn a partial object into a full update. A caller should read the current account first and include all writable fields it needs to preserve.
- Surface stale `SyncToken` conflicts; do not automatically overwrite newer changes. Do not automatically retry an ambiguous update.

## Errors, safety, and verification

- Report local field validation failures with an actionable message, field and rule code; include the allowed and received lengths for length failures. Preserve `ValueError` compatibility and do not expose field values.
- Preserve useful Intuit fault details such as status, error code, and message for callers, including duplicate, validation, authorization, and concurrency errors, without exposing credentials. Distinguish network failures and malformed responses; never report failure as an empty result.
- Keep sandbox and production credentials, company IDs, and hosts separate. Do not log token values or sensitive account data by default.
- Add offline tests for request methods, URL encoding, authorization headers, body and response contracts, decimal values, empty queries, upstream errors, stale versions, and no unsafe write retries. Use sanitized fixtures.
- Verify the read/query path against the connected sandbox. Test mutations only in the sandbox using explicitly identifiable test data, and document the outcome and any cleanup or inactivation. No production writes are required for verification.

## Open decisions

- Public Python representation of accounts and raw responses, decimal serialization, query interface, and error types.
- Supported API minor version, locale-specific validation, pagination ergonomics, and retry policy for safe reads.
- How the sandbox example presents Account operations and obtains a fresh token without losing rotated credentials.

---
## Complete Object
# QuickBooks Online: Account Object Attributes

## Id
- **Type:** String, filterable
- **Flags:** Required for update, read only, system defined
- **Description:** Unique identifier for this object.

## Name
- **Type:** String, filterable, sortable
- **Flags:** Required. Max 100 characters.
- **Description:** User recognizable name for the Account. `Account.Name` must not contain double quotes (`"`) or colon (`:`).

## SyncToken
- **Type:** String
- **Flags:** Required for update, read only, system defined
- **Description:** Version number of the object. It is used to lock an object for use by one app at a time. As soon as an application modifies an object, its `SyncToken` is incremented. Attempts to modify an object specifying an older `SyncToken` fails. Only the latest version of the object is maintained by QuickBooks Online.

## AcctNum
- **Type:** String
- **Flags:** Conditionally required
- **Description:** User-defined account number to help the user in identifying the account within the chart-of-accounts and in deciding what should be posted to the account. `Account.AcctNum` must not contain colon (`:`).
  - Name must be unique.
  - Max length for `Account.AcctNum`:
    - AU & CA: 20 characters
    - US, UK & IN: 7 characters

## CurrencyRef
- **Type:** CurrencyRef
- **Flags:** Optional, read only
- **Description:** Reference to the currency in which this account holds amounts.

| Attribute | Type | Required | Description |
|---|---|---|---|
| `value` | String | Required | A three letter string representing the ISO 4217 code for the currency. For example, `USD`, `AUD`, `EUR`, and so on. |
| `name` | String | Optional | The full name of the currency. |

## ParentRef
- **Type:** ReferenceType, filterable, sortable
- **Flags:** Optional
- **Description:** Specifies the Parent AccountId if this represents a SubAccount.

| Attribute | Type | Required | Description |
|---|---|---|---|
| `value` | string | Required | The ID for the referenced object as found in the Id field of the object payload. The context is set by the type of reference and is specific to the QuickBooks company file. |
| `name` | string | Optional | An identifying name for the object being referenced by `value` and is derived from the field that holds the common name of that object. This varies by context and specific type of object referenced. For example, references to a Customer object use `Customer.DisplayName` to populate this field. Optionally returned in responses, implementation dependent. |

## Description
- **Type:** String, filterable, sortable
- **Flags:** Optional. Max 100 characters.
- **Description:** User entered description for the account, which may include user entered information to guide bookkeepers/accountants in deciding what journal entries to post to the account.

## Active
- **Type:** Boolean, filterable
- **Flags:** Optional
- **Description:** Whether or not active inactive accounts may be hidden from most display purposes and may not be posted to.

## MetaData
- **Type:** ModificationMetaData
- **Flags:** Optional
- **Description:** Descriptive information about the object. The MetaData values are set by Data Services and are read only for all applications.

| Attribute | Type | Flags | Description |
|---|---|---|---|
| `CreateTime` | DateTime, filterable, sortable | read only, system defined | Time the entity was created in the source domain. |
| `LastUpdatedTime` | DateTime, filterable, sortable | read only, system defined | Time the entity was last updated in the source domain. |

Both `CreateTime` and `LastUpdatedTime` contain a `dateTime` (string) child attribute, in one of these formats:

- Local time zone: `YYYY-MM-DDTHH:MM:SS`
- UTC: `YYYY-MM-DDTHH:MM:SSZ`
- Specific time zone: `YYYY-MM-DDTHH:MM:SS+/-HH:MM`

## SubAccount
- **Type:** Boolean, filterable, sortable
- **Flags:** read only, system defined
- **Description:** Specifies whether this object represents a parent (false) or subaccount (true). Accounts of these types cannot have a sub account and cannot be a sub account of another account: `OpeningBalanceEquity`, `UndepositedFunds`, `RetainedEarnings`, `CashReceiptIncome`, `CashExpenditureExpense`, `ExchangeGainOrLoss`.

## Classification
- **Type:** String, filterable
- **Flags:** read only, system defined
- **Description:** The classification of an account. Not supported for non-posting accounts.
- **Valid values:** `Asset`, `Equity`, `Expense`, `Liability`, `Revenue`

## FullyQualifiedName
- **Type:** String, filterable, sortable
- **Flags:** read only, system defined
- **Description:** Fully qualified name of the object; derived from `Name` and `ParentRef`. The fully qualified name prepends the topmost parent, followed by each subaccount separated by colons and takes the form of `Parent:Account1:SubAccount1:SubAccount2`. System generated. Limited to 5 levels.

## AccountType
- **Type:** AccountTypeEnum, filterable
- **Description:** A detailed account classification that specifies the use of this account. The type is based on the Classification.

See [Account Type and Account Sub Type mapping](#account-type-and-account-sub-type-mapping) below.

## CurrentBalanceWithSubAccounts
- **Type:** Decimal, filterable, sortable
- **Flags:** read only
- **Description:** Specifies the cumulative balance amount for the current Account and all its sub-accounts.

## TaxCodeRef
- **Type:** ReferenceType
- **Applies to:** Global locales only
- **Description:** Reference to the default tax code used by this account. Tax codes are referenced by the `TaxCode.Id` in the TaxCode object.

| Attribute | Type | Required | Description |
|---|---|---|---|
| `value` | string | Required | The ID for the referenced object as found in the Id field of the object payload. The context is set by the type of reference and is specific to the QuickBooks company file. |
| `name` | string | Optional | An identifying name for the object being referenced by `value` and is derived from the field that holds the common name of that object. This varies by context and specific type of object referenced. For example, references to a Customer object use `Customer.DisplayName` to populate this field. Optionally returned in responses, implementation dependent. |

## AccountSubType
- **Type:** String, filterable
- **Description:** The account sub-type classification and is based on the `AccountType` value.

Valid values are the same as in the mapping below.

## CurrentBalance
- **Type:** Decimal, filterable, sortable
- **Flags:** read only
- **Description:** Specifies the balance amount for the current Account. Valid for Balance Sheet accounts.

---

# Account Type and Account Sub Type mapping

The default sub type for each account type is marked **(default)**.

## Asset

| Account Type | Account Sub Types |
|---|---|
| **Bank** | `CashAndCashEquivalents`, `CashOnHand` **(default)**, `Checking`, `MoneyMarket`, `OtherEarMarkedBankAccounts`, `RentsHeldInTrust`, `Savings`, `TrustAccounts` |
| **Other Current Asset** | `AllowanceForBadDebts`, `AssetsAvailableForSale`, `BalWithGovtAuthorities`, `CalledUpShareCapitalNotPaid`, `DevelopmentCosts`, `EmployeeCashAdvances` **(default)**, `ExpenditureAuthorisationsAndLettersOfCredit`, `GlobalTaxDeferred`, `GlobalTaxRefund`, `InternalTransfers`, `Inventory`, `Investment_MortgageRealEstateLoans`, `Investment_Other`, `Investment_TaxExemptSecurities`, `Investment_USGovernmentObligations`, `LoansToOfficers`, `LoansToOthers`, `LoansToStockholders`, `OtherConsumables`, `OtherCurrentAssets`, `PrepaidExpenses`, `ProvisionsCurrentAssets`, `ShortTermInvestmentsInRelatedParties`, `ShortTermLoansAndAdvancesToRelatedParties`, `TradeAndOtherReceivables`, `Retainage`, `UndepositedFunds` |
| **Fixed Asset** | `AccumulatedAmortization`, `AccumulatedDepletion`, `AccumulatedDepreciation`, `AssetsInCourseOfConstruction`, `Buildings`, `CapitalWip`, `CumulativeDepreciationOnIntangibleAssets`, `DepletableAssets`, `FixedAssetComputers`, `FixedAssetCopiers`, `FixedAssetFurniture`, `FixedAssetPhone`, `FixedAssetPhotoVideo`, `FixedAssetSoftware`, `FixedAssetOtherToolsEquipment`, `FurnitureAndFixtures` **(default)**, `IntangibleAssets`, `IntangibleAssetsUnderDevelopment`, `Land`, `LandAsset`, `LeaseholdImprovements`, `MachineryAndEquipment`, `NonCurrentAssets`, `OtherFixedAssets`, `ParticipatingInterests`, `ProvisionsFixedAssets`, `Vehicles` |
| **Other Asset** | `AccumulatedAmortizationOfOtherAssets`, `AssetsHeldForSale`, `AvailableForSaleFinancialAssets`, `DeferredTax`, `Goodwill`, `Investments`, `LeaseBuyout`, `Licenses` **(default)**, `LongTermInvestments`, `LongTermLoansAndAdvancesToRelatedParties`, `OrganizationalCosts`, `OtherIntangibleAssets`, `OtherLongTermAssets`, `OtherLongTermInvestments`, `OtherLongTermLoansAndAdvances`, `PrepaymentsAndAccruedIncome`, `ProvisionsNonCurrentAssets`, `SecurityDeposits` |
| **Accounts Receivable** | `Accounts Receivable` **(default)** |

## Equity

| Account Type | Account Sub Types |
|---|---|
| **Equity** | `AccumulatedAdjustment`, `AccumulatedOtherComprehensiveIncome`, `CalledUpShareCapital`, `CapitalReserves`, `CommonStock`, `DividendDisbursed`, `EquityInEarningsOfSubsiduaries`, `EstimatedTaxes`, `Funds`, `Healthcare`, `InvestmentGrants`, `MoneyReceivedAgainstShareWarrants`, `OtherFreeReserves`, `OpeningBalanceEquity` **(default)**, `OwnersEquity`, `PaidInCapitalOrSurplus`, `PartnerContributions`, `PartnerDistributions`, `PersonalIncome`, `PersonalExpense`, `PartnersEquity`, `PreferredStock`, `RetainedEarnings`, `ShareApplicationMoneyPendingAllotment`, `ShareCapital`, `TreasuryStock` |

## Expense

| Account Type | Account Sub Types |
|---|---|
| **Expense** | `AdvertisingPromotional`, `AmortizationExpense`, `AppropriationsToDepreciation`, `Auto`, `BadDebts`, `BankCharges`, `BorrowingCost`, `CharitableContributions`, `CommissionsAndFees`, `CostOfLabor`, `DistributionCosts`, `DuesSubscriptions`, `Entertainment`, `EntertainmentMeals`, `EquipmentRental`, `ExternalServices`, `ExtraordinaryCharges`, `FinanceCosts`, `GlobalTaxExpense`, `IncomeTaxExpense`, `Insurance`, `InterestPaid`, `LegalProfessionalFees`, `LossOnDiscontinuedOperationsNetOfTax`, `ManagementCompensation`, `OfficeExpenses`, `OfficeGeneralAdministrativeExpenses`, `OtherBusinessExpenses`, `OtherCurrentOperatingCharges`, `OtherExternalServices`, `OtherMiscellaneousServiceCost`, `OtherRentalCosts`, `OtherSellingExpenses`, `PayrollExpenses`, `ProjectStudiesSurveysAssessments`, `PromotionalMeals`, `PurchasesRebates`, `RentOrLeaseOfBuildings`, `RepairMaintenance`, `ShippingAndDeliveryExpense`, `ShippingFreightDelivery`, `StaffCosts`, `Sundry`, `SuppliesMaterials`, `Travel` **(default)**, `TravelExpensesGeneralAndAdminExpenses`, `TravelExpensesSellingExpense`, `TravelMeals`, `Utilities`, `TaxesPaid`, `UnappliedCashBillPaymentExpense` |
| **Other Expense** | `Amortization`, `DeferredTaxExpense`, `Depletion`, `Depreciation` **(default)**, `ExceptionalItems`, `ExchangeGainOrLoss`, `ExtraordinaryItems`, `GasAndFuel`, `HomeOffice`, `HomeOwnerRentalInsurance`, `IncomeTaxOtherExpense`, `MatCredit`, `MortgageInterest`, `OtherHomeOfficeExpenses`, `OtherVehicleExpenses`, `OtherMiscellaneousExpense`, `ParkingAndTolls`, `PenaltiesSettlements`, `PriorPeriodItems`, `RentAndLease`, `RepairsAndMaintenance`, `TaxRoundoffGainOrLoss`, `Utilities`, `Vehicle`, `VehicleInsurance`, `VehicleLease`, `VehicleLoanInterest`, `VehicleLoan`, `VehicleRegistration`, `VehicleRepairs`, `WashAndRoadServices` |
| **Cost of Goods Sold** | `CostOfLaborCos` **(default)**, `CostOfSales`, `EquipmentRentalCos`, `FreightAndDeliveryCost`, `OtherCostsOfServiceCos`, `ShippingFreightDeliveryCos`, `SuppliesMaterialsCogs` |

## Liability

| Account Type | Account Sub Types |
|---|---|
| **Accounts Payable** | `Accounts Payable` **(default)**, `OutstandingDuesMicroSmallEnterprise`, `OutstandingDuesOtherThanMicroSmallEnterprise` |
| **Credit Card** | `Credit Card` **(default)** |
| **Long Term Liability** | `AccrualsAndDeferredIncome`, `AccruedLongLermLiabilities`, `AccruedVacationPayable`, `BankLoans`, `DebtsRelatedToParticipatingInterests`, `DeferredTaxLiabilities`, `GovernmentAndOtherPublicAuthorities`, `GroupAndAssociates`, `LiabilitiesRelatedToAssetsHeldForSale`, `LongTermBorrowings`, `LongTermDebit`, `LongTermEmployeeBenefitObligations`, `NotesPayable` **(default)**, `ObligationsUnderFinanceLeases`, `OtherLongTermLiabilities`, `OtherLongTermProvisions`, `ProvisionForLiabilities`, `ProvisionsNonCurrentLiabilities`, `ShareholderNotesPayable`, `StaffAndRelatedLongTermLiabilityAccounts` |
| **Other Current Liability** | `AccruedLiabilities`, `CurrentLiabilities`, `CurrentPortionEmployeeBenefitsObligations`, `CurrentPortionOfObligationsUnderFinanceLeases`, `CurrentTaxLiability`, `DirectDepositPayable`, `DividendsPayable`, `DutiesAndTaxes`, `FederalIncomeTaxPayable`, `GlobalTaxPayable`, `GlobalTaxSuspense`, `InsurancePayable`, `InterestPayables`, `LineOfCredit`, `LoanPayable`, `OtherCurrentLiabilities` **(default)**, `PayrollClearing`, `PayrollTaxPayable`, `PrepaidExpensesPayable`, `ProvisionForWarrantyObligations`, `ProvisionsCurrentLiabilities`, `RentsInTrustLiability`, `TrustAccountsLiabilities`, `SalesTaxPayable`, `ShortTermBorrowings`, `SocialSecurityAgencies`, `StaffAndRelatedLiabilityAccounts`, `StateLocalIncomeTaxPayable`, `SundryDebtorsAndCreditors`, `TradeAndOtherPayables` |

## Revenue

| Account Type | Account Sub Types |
|---|---|
| **Income** | `CashReceiptIncome`, `DiscountsRefundsGiven`, `NonProfitIncome`, `OperatingGrants`, `OtherCurrentOperatingIncome`, `OtherPrimaryIncome` **(default)**, `OwnWorkCapitalized`, `RevenueGeneral`, `SalesOfProductIncome`, `SalesRetail`, `SalesWholesale`, `SavingsByTaxScheme`, `ServiceFeeIncome`, `UnappliedCashPaymentIncome` |
| **Other Income** | `DividendIncome`, `GainLossOnSaleOfFixedAssets`, `GainLossOnSaleOfInvestments`, `InterestEarned`, `LossOnDisposalOfAssets`, `OtherOperatingIncome`, `OtherInvestmentIncome` **(default)**, `OtherMiscellaneousIncome`, `TaxExemptInterest`, `UnrealisedLossOnSecuritiesNetOfTax` |