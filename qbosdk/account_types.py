"""Account type reference from the documented QuickBooks Account object.

Values vary by company locale and Intuit may update them. This reference is not
used as a validation allowlist; QuickBooks remains authoritative.
"""

# Account type -> (classification, default subtype, documented subtypes).
ACCOUNT_TYPE_REFERENCE = {
    'Bank': ('Asset', 'CashOnHand', (
        'CashAndCashEquivalents', 'CashOnHand', 'Checking', 'MoneyMarket',
        'OtherEarMarkedBankAccounts', 'RentsHeldInTrust', 'Savings', 'TrustAccounts',
    )),
    'Other Current Asset': ('Asset', 'EmployeeCashAdvances', (
        'AllowanceForBadDebts', 'AssetsAvailableForSale', 'BalWithGovtAuthorities', 'CalledUpShareCapitalNotPaid',
        'DevelopmentCosts', 'EmployeeCashAdvances', 'ExpenditureAuthorisationsAndLettersOfCredit', 'GlobalTaxDeferred',
        'GlobalTaxRefund', 'InternalTransfers', 'Inventory', 'Investment_MortgageRealEstateLoans',
        'Investment_Other', 'Investment_TaxExemptSecurities', 'Investment_USGovernmentObligations', 'LoansToOfficers',
        'LoansToOthers', 'LoansToStockholders', 'OtherConsumables', 'OtherCurrentAssets',
        'PrepaidExpenses', 'ProvisionsCurrentAssets', 'ShortTermInvestmentsInRelatedParties', 'ShortTermLoansAndAdvancesToRelatedParties',
        'TradeAndOtherReceivables', 'Retainage', 'UndepositedFunds',
    )),
    'Fixed Asset': ('Asset', 'FurnitureAndFixtures', (
        'AccumulatedAmortization', 'AccumulatedDepletion', 'AccumulatedDepreciation', 'AssetsInCourseOfConstruction',
        'Buildings', 'CapitalWip', 'CumulativeDepreciationOnIntangibleAssets', 'DepletableAssets',
        'FixedAssetComputers', 'FixedAssetCopiers', 'FixedAssetFurniture', 'FixedAssetPhone',
        'FixedAssetPhotoVideo', 'FixedAssetSoftware', 'FixedAssetOtherToolsEquipment', 'FurnitureAndFixtures',
        'IntangibleAssets', 'IntangibleAssetsUnderDevelopment', 'Land', 'LandAsset',
        'LeaseholdImprovements', 'MachineryAndEquipment', 'NonCurrentAssets', 'OtherFixedAssets',
        'ParticipatingInterests', 'ProvisionsFixedAssets', 'Vehicles',
    )),
    'Other Asset': ('Asset', 'Licenses', (
        'AccumulatedAmortizationOfOtherAssets', 'AssetsHeldForSale', 'AvailableForSaleFinancialAssets', 'DeferredTax',
        'Goodwill', 'Investments', 'LeaseBuyout', 'Licenses',
        'LongTermInvestments', 'LongTermLoansAndAdvancesToRelatedParties', 'OrganizationalCosts', 'OtherIntangibleAssets',
        'OtherLongTermAssets', 'OtherLongTermInvestments', 'OtherLongTermLoansAndAdvances', 'PrepaymentsAndAccruedIncome',
        'ProvisionsNonCurrentAssets', 'SecurityDeposits',
    )),
    'Accounts Receivable': ('Asset', 'Accounts Receivable', (
        'Accounts Receivable',
    )),
    'Equity': ('Equity', 'OpeningBalanceEquity', (
        'AccumulatedAdjustment', 'AccumulatedOtherComprehensiveIncome', 'CalledUpShareCapital', 'CapitalReserves',
        'CommonStock', 'DividendDisbursed', 'EquityInEarningsOfSubsiduaries', 'EstimatedTaxes',
        'Funds', 'Healthcare', 'InvestmentGrants', 'MoneyReceivedAgainstShareWarrants',
        'OtherFreeReserves', 'OpeningBalanceEquity', 'OwnersEquity', 'PaidInCapitalOrSurplus',
        'PartnerContributions', 'PartnerDistributions', 'PersonalIncome', 'PersonalExpense',
        'PartnersEquity', 'PreferredStock', 'RetainedEarnings', 'ShareApplicationMoneyPendingAllotment',
        'ShareCapital', 'TreasuryStock',
    )),
    'Expense': ('Expense', 'Travel', (
        'AdvertisingPromotional', 'AmortizationExpense', 'AppropriationsToDepreciation', 'Auto',
        'BadDebts', 'BankCharges', 'BorrowingCost', 'CharitableContributions',
        'CommissionsAndFees', 'CostOfLabor', 'DistributionCosts', 'DuesSubscriptions',
        'Entertainment', 'EntertainmentMeals', 'EquipmentRental', 'ExternalServices',
        'ExtraordinaryCharges', 'FinanceCosts', 'GlobalTaxExpense', 'IncomeTaxExpense',
        'Insurance', 'InterestPaid', 'LegalProfessionalFees', 'LossOnDiscontinuedOperationsNetOfTax',
        'ManagementCompensation', 'OfficeExpenses', 'OfficeGeneralAdministrativeExpenses', 'OtherBusinessExpenses',
        'OtherCurrentOperatingCharges', 'OtherExternalServices', 'OtherMiscellaneousServiceCost', 'OtherRentalCosts',
        'OtherSellingExpenses', 'PayrollExpenses', 'ProjectStudiesSurveysAssessments', 'PromotionalMeals',
        'PurchasesRebates', 'RentOrLeaseOfBuildings', 'RepairMaintenance', 'ShippingAndDeliveryExpense',
        'ShippingFreightDelivery', 'StaffCosts', 'Sundry', 'SuppliesMaterials',
        'Travel', 'TravelExpensesGeneralAndAdminExpenses', 'TravelExpensesSellingExpense', 'TravelMeals',
        'Utilities', 'TaxesPaid', 'UnappliedCashBillPaymentExpense',
    )),
    'Other Expense': ('Expense', 'Depreciation', (
        'Amortization', 'DeferredTaxExpense', 'Depletion', 'Depreciation',
        'ExceptionalItems', 'ExchangeGainOrLoss', 'ExtraordinaryItems', 'GasAndFuel',
        'HomeOffice', 'HomeOwnerRentalInsurance', 'IncomeTaxOtherExpense', 'MatCredit',
        'MortgageInterest', 'OtherHomeOfficeExpenses', 'OtherVehicleExpenses', 'OtherMiscellaneousExpense',
        'ParkingAndTolls', 'PenaltiesSettlements', 'PriorPeriodItems', 'RentAndLease',
        'RepairsAndMaintenance', 'TaxRoundoffGainOrLoss', 'Utilities', 'Vehicle',
        'VehicleInsurance', 'VehicleLease', 'VehicleLoanInterest', 'VehicleLoan',
        'VehicleRegistration', 'VehicleRepairs', 'WashAndRoadServices',
    )),
    'Cost of Goods Sold': ('Expense', 'CostOfLaborCos', (
        'CostOfLaborCos', 'CostOfSales', 'EquipmentRentalCos', 'FreightAndDeliveryCost',
        'OtherCostsOfServiceCos', 'ShippingFreightDeliveryCos', 'SuppliesMaterialsCogs',
    )),
    'Accounts Payable': ('Liability', 'Accounts Payable', (
        'Accounts Payable', 'OutstandingDuesMicroSmallEnterprise', 'OutstandingDuesOtherThanMicroSmallEnterprise',
    )),
    'Credit Card': ('Liability', 'Credit Card', (
        'Credit Card',
    )),
    'Long Term Liability': ('Liability', 'NotesPayable', (
        'AccrualsAndDeferredIncome', 'AccruedLongLermLiabilities', 'AccruedVacationPayable', 'BankLoans',
        'DebtsRelatedToParticipatingInterests', 'DeferredTaxLiabilities', 'GovernmentAndOtherPublicAuthorities', 'GroupAndAssociates',
        'LiabilitiesRelatedToAssetsHeldForSale', 'LongTermBorrowings', 'LongTermDebit', 'LongTermEmployeeBenefitObligations',
        'NotesPayable', 'ObligationsUnderFinanceLeases', 'OtherLongTermLiabilities', 'OtherLongTermProvisions',
        'ProvisionForLiabilities', 'ProvisionsNonCurrentLiabilities', 'ShareholderNotesPayable', 'StaffAndRelatedLongTermLiabilityAccounts',
    )),
    'Other Current Liability': ('Liability', 'OtherCurrentLiabilities', (
        'AccruedLiabilities', 'CurrentLiabilities', 'CurrentPortionEmployeeBenefitsObligations', 'CurrentPortionOfObligationsUnderFinanceLeases',
        'CurrentTaxLiability', 'DirectDepositPayable', 'DividendsPayable', 'DutiesAndTaxes',
        'FederalIncomeTaxPayable', 'GlobalTaxPayable', 'GlobalTaxSuspense', 'InsurancePayable',
        'InterestPayables', 'LineOfCredit', 'LoanPayable', 'OtherCurrentLiabilities',
        'PayrollClearing', 'PayrollTaxPayable', 'PrepaidExpensesPayable', 'ProvisionForWarrantyObligations',
        'ProvisionsCurrentLiabilities', 'RentsInTrustLiability', 'TrustAccountsLiabilities', 'SalesTaxPayable',
        'ShortTermBorrowings', 'SocialSecurityAgencies', 'StaffAndRelatedLiabilityAccounts', 'StateLocalIncomeTaxPayable',
        'SundryDebtorsAndCreditors', 'TradeAndOtherPayables',
    )),
    'Income': ('Revenue', 'OtherPrimaryIncome', (
        'CashReceiptIncome', 'DiscountsRefundsGiven', 'NonProfitIncome', 'OperatingGrants',
        'OtherCurrentOperatingIncome', 'OtherPrimaryIncome', 'OwnWorkCapitalized', 'RevenueGeneral',
        'SalesOfProductIncome', 'SalesRetail', 'SalesWholesale', 'SavingsByTaxScheme',
        'ServiceFeeIncome', 'UnappliedCashPaymentIncome',
    )),
    'Other Income': ('Revenue', 'OtherInvestmentIncome', (
        'DividendIncome', 'GainLossOnSaleOfFixedAssets', 'GainLossOnSaleOfInvestments', 'InterestEarned',
        'LossOnDisposalOfAssets', 'OtherOperatingIncome', 'OtherInvestmentIncome', 'OtherMiscellaneousIncome',
        'TaxExemptInterest', 'UnrealisedLossOnSecuritiesNetOfTax',
    )),
}
