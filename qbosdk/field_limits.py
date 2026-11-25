"""Documented QuickBooks field limits, organized by entity and field."""

TRANSACTION_DOC_NUMBER_MAX_LENGTH = 21
TRANSACTION_PRIVATE_NOTE_MAX_LENGTH = 4000

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account
ACCOUNT_NAME_MAX_LENGTH = 100
ACCOUNT_DESCRIPTION_MAX_LENGTH = 100
ACCOUNT_NUMBER_MAX_LENGTH_BY_COUNTRY = {"AU": 20, "CA": 20, "US": 7, "UK": 7, "IN": 7}

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer
CUSTOMER_TEXT_MAX_LENGTHS = {
    "DisplayName": 500, "Title": 16, "GivenName": 100, "MiddleName": 100,
    "FamilyName": 100, "Suffix": 16, "PrintOnCheckName": 110,
    "CompanyName": 100, "ResaleNum": 16, "Notes": 2000,
}

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department
DEPARTMENT_NAME_MAX_LENGTH = 100

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit
DEPOSIT_PRIVATE_NOTE_MAX_LENGTH = 4000

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee
EMPLOYEE_TEXT_MAX_LENGTHS = {
    "DisplayName": 500, "Title": 16, "GivenName": 100, "MiddleName": 100,
    "FamilyName": 100, "Suffix": 16, "PrintOnCheckName": 100,
    "SSN": 100, "EmployeeNumber": 100,
}

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item
ITEM_TEXT_MAX_LENGTHS = {"Name": 100, "Sku": 100, "Description": 4000, "PurchaseDesc": 1000}

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod
PAYMENT_METHOD_NAME_MAX_LENGTH = 31

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder
PURCHASE_ORDER_MEMO_MAX_LENGTH = 4000

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt
REFUND_RECEIPT_PAYMENT_REF_MAX_LENGTH = 100

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt
SALES_RECEIPT_PAYMENT_REF_MAX_LENGTH = 21

# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxservice
TAX_CODE_NAME_MAX_LENGTH = 100
TAX_SERVICE_RATE_NAME_MAX_LENGTH = 10

TAX_AGENCY_NAME_MAX_LENGTH = 100
TERM_NAME_MAX_LENGTH = 31
TIME_ACTIVITY_DESCRIPTION_MAX_LENGTH = 4000
VENDOR_TEXT_MAX_LENGTHS = {
    "DisplayName": 500, "Title": 16, "GivenName": 100, "MiddleName": 100,
    "FamilyName": 100, "Suffix": 16, "CompanyName": 100, "TaxIdentifier": 20,
    "AcctNum": 100, "PrintOnCheckName": 100,
}
