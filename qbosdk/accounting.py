"""QuickBooks Online Accounting API: Account operations."""

import base64
import json
import re
import secrets
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, build_opener

from ._http import NoRedirect as _NoRedirect
from ._json import dumps as _json_dumps
from .oauth import API_URLS
from .field_limits import (ACCOUNT_DESCRIPTION_MAX_LENGTH, ACCOUNT_NAME_MAX_LENGTH,
                           ACCOUNT_NUMBER_MAX_LENGTH_BY_COUNTRY, CUSTOMER_TEXT_MAX_LENGTHS,
                           DEPARTMENT_NAME_MAX_LENGTH, DEPOSIT_PRIVATE_NOTE_MAX_LENGTH,
                           EMPLOYEE_TEXT_MAX_LENGTHS, ITEM_TEXT_MAX_LENGTHS, PAYMENT_METHOD_NAME_MAX_LENGTH,
                           PURCHASE_ORDER_MEMO_MAX_LENGTH, REFUND_RECEIPT_PAYMENT_REF_MAX_LENGTH,
                           SALES_RECEIPT_PAYMENT_REF_MAX_LENGTH, TAX_CODE_NAME_MAX_LENGTH,
                           TAX_AGENCY_NAME_MAX_LENGTH, TAX_SERVICE_RATE_NAME_MAX_LENGTH,
                           TERM_NAME_MAX_LENGTH, TIME_ACTIVITY_DESCRIPTION_MAX_LENGTH,
                           TRANSACTION_DOC_NUMBER_MAX_LENGTH, TRANSACTION_PRIVATE_NOTE_MAX_LENGTH,
                           VENDOR_TEXT_MAX_LENGTHS)
from .validation import ValidationError


class AccountingError(Exception):
    """Accounting request failure; details may contain sensitive business data."""

    def __init__(self, message, *, status=None, fault=None, intuit_tid=None):
        super().__init__(message)
        self.status = status
        self.fault = fault
        self.intuit_tid = intuit_tid


class AccountingClient:
    """A client for one company, environment, and caller-managed access token."""

    def __init__(self, access_token, realm_id, environment="sandbox", *, country=None, validate_fields=True):
        if not isinstance(access_token, str) or not access_token or not isinstance(realm_id, str) or not realm_id:
            raise ValueError("access token and realm ID are required strings")
        if environment not in API_URLS:
            raise ValueError("environment must be sandbox or production")
        if not realm_id.isascii() or not realm_id.isdecimal():
            raise ValueError("realm ID must contain ASCII digits")
        if country is not None and (not isinstance(country, str) or country not in ACCOUNT_NUMBER_MAX_LENGTH_BY_COUNTRY):
            raise ValueError("country must be AU, CA, US, UK, IN, or None")
        if not isinstance(validate_fields, bool):
            raise ValueError("validate_fields must be a boolean")
        self.validate_fields = validate_fields
        self._country = country
        self._access_token = access_token
        self._realm_id = realm_id
        self._api_url = API_URLS[environment]
        self._base = f"{self._api_url}/v3/company/{realm_id}"

    def _request(self, method, path, body=None, query=None, params=None, *, raw_data=None, content_type=None, text_response=False, binary_response=False, accept=None, service_root=False):
        url = (self._api_url if service_root else self._base) + path
        if query is not None:
            url += "?" + urlencode({"query": query})
        elif params:
            url += "?" + urlencode(params)
        headers = {"Authorization": "Bearer " + self._access_token, "Accept": accept or ("application/pdf" if binary_response else "text/plain" if text_response else "application/json")}
        data = raw_data
        if raw_data is not None:
            headers["Content-Type"] = content_type
        if body is not None:
            try:
                data = _json_dumps(body).encode("utf-8")
            except (TypeError, ValueError) as exc:
                raise ValueError("account must be JSON serializable with finite numbers") from exc
            headers["Content-Type"] = "application/json"
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with build_opener(_NoRedirect()).open(request, timeout=30) as response:
                if binary_response:
                    return response.read()
                if text_response:
                    value = response.read().decode("utf-8").strip()
                    if value.startswith('"'):
                        value = json.loads(value)
                    if not isinstance(value, str) or not value.startswith("https://"):
                        raise ValueError("invalid download URL")
                    return value
                payload = json.load(response, parse_float=Decimal)
        except HTTPError as exc:
            try:
                parsed = json.load(exc, parse_float=Decimal)
                fault = parsed.get("Fault") if isinstance(parsed, dict) else None
            except (ValueError, OSError):
                fault = None
            raise AccountingError("QuickBooks Accounting request failed", status=exc.code,
                                  fault=fault, intuit_tid=exc.headers.get("intuit_tid") if exc.headers else None) from None
        except (URLError, OSError, ValueError):
            raise AccountingError("QuickBooks Accounting request failed or returned invalid JSON") from None
        if not isinstance(payload, dict):
            raise AccountingError("QuickBooks returned an invalid response")
        if "Fault" in payload:
            raise AccountingError("QuickBooks Accounting request failed", fault=payload["Fault"])
        return payload

    def _account(self, body, update=False):
        if not isinstance(body, dict):
            raise ValueError("account must be a dictionary")
        name = body.get("Name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Name", "required", "Account Name is required and must be a nonempty string.")
        if self.validate_fields:
            if len(name) > ACCOUNT_NAME_MAX_LENGTH:
                raise ValidationError("Name", "max_length",
                                      f"Account Name must be at most {ACCOUNT_NAME_MAX_LENGTH} characters; received {len(name)}.",
                                      limit=ACCOUNT_NAME_MAX_LENGTH, actual=len(name))
            if '"' in name:
                raise ValidationError("Name", "invalid_character", 'Account Name cannot contain a double quote (").')
            if ':' in name:
                raise ValidationError("Name", "invalid_character", "Account Name cannot contain a colon (:).")
        number = body.get("AcctNum")
        if number is not None and not isinstance(number, str):
            raise ValidationError("AcctNum", "invalid_type", "Account AcctNum must be a string.")
        limit = ACCOUNT_NUMBER_MAX_LENGTH_BY_COUNTRY.get(self._country)
        if number is not None and self.validate_fields:
            if ':' in number:
                raise ValidationError("AcctNum", "invalid_character", "Account AcctNum cannot contain a colon (:).")
            if limit is not None and len(number) > limit:
                raise ValidationError("AcctNum", "max_length",
                                      f"Account AcctNum must be at most {limit} characters for {self._country}; received {len(number)}.",
                                      limit=limit, actual=len(number))
        description = body.get("Description")
        if description is not None and not isinstance(description, str):
            raise ValidationError("Description", "invalid_type", "Account Description must be a string.")
        if self.validate_fields and description is not None and len(description) > ACCOUNT_DESCRIPTION_MAX_LENGTH:
            raise ValidationError("Description", "max_length",
                                  f"Account Description must be at most {ACCOUNT_DESCRIPTION_MAX_LENGTH} characters; received {len(description)}.",
                                  limit=ACCOUNT_DESCRIPTION_MAX_LENGTH, actual=len(description))
        active = body.get("Active")
        if active is not None and not isinstance(active, bool):
            raise ValidationError("Active", "invalid_type", "Account Active must be a boolean.")
        for field in ("AccountType", "AccountSubType"):
            value = body.get(field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValidationError(field, "invalid_type", f"Account {field} must be a nonempty string.")
        for field in ("ParentRef", "TaxCodeRef", "CurrencyRef"):
            reference = body.get(field)
            if reference is None:
                continue
            if not isinstance(reference, dict):
                raise ValidationError(field, "invalid_type", f"Account {field} must be a reference object.")
            value = reference.get("value")
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"{field}.value", "required", f"Account {field}.value must be a nonempty string.")
            if field == "CurrencyRef" and self.validate_fields and (len(value) != 3 or not value.isascii() or not value.isalpha()):
                raise ValidationError("CurrencyRef.value", "invalid_format", "Account CurrencyRef.value must be a three-letter currency code.")
            if reference.get("name") is not None and not isinstance(reference["name"], str):
                raise ValidationError(f"{field}.name", "invalid_type", f"Account {field}.name must be a string.")
        if update:
            for field in ("Id", "SyncToken"):
                if not isinstance(body.get(field), str) or not body[field]:
                    raise ValidationError(field, "required", f"Account {field} is required for a full update and must be a nonempty string.")
            if body.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        elif not body.get("AccountType") and not body.get("AccountSubType"):
            raise ValidationError("AccountType", "required", "Account creation requires AccountType or AccountSubType.")

    def create_account(self, account):
        """Create an account; returns the complete Intuit response envelope."""
        self._account(account)
        return self._account_response(self._request("POST", "/account", account))

    def read_account(self, account_id):
        """Read an account by ID; returns the complete response envelope."""
        if not isinstance(account_id, str) or not account_id or account_id in (".", ".."):
            raise ValueError("account ID must be a nonempty string")
        return self._account_response(self._request("GET", "/account/" + quote(account_id, safe="")))

    def full_update_account(self, account):
        """Replace writable fields. Omitted writable fields are cleared by Intuit."""
        self._account(account, update=True)
        body = dict(account)
        body["sparse"] = False
        return self._account_response(self._request("POST", "/account", body))

    @staticmethod
    def _account_response(payload):
        if not isinstance(payload.get("Account"), dict):
            raise AccountingError("QuickBooks returned an invalid Account response")
        return payload

    def query_accounts(self, statement="SELECT * FROM Account", *, start_position=1, max_results=100):
        return self._query_entity("Account", statement, start_position, max_results, allow_id=False)

    def iter_accounts(self, statement="SELECT * FROM Account", *, page_size=100):
        return self._iter_entity("Account", statement, page_size, allow_id=False)

    def account_list_detail(self, *, account_type=None, start_date=None, end_date=None,
                            start_moddate=None, end_moddate=None, moddate_macro=None,
                            start_createdate=None, end_createdate=None, createdate_macro=None,
                            date_macro=None, sort_by=None, sort_order=None,
                            account_status=None, columns=None):
        """Return the AccountList report as the complete QuickBooks response."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        for key, value in params.items():
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(key, "invalid_type", f"Report parameter {key} must be a nonempty string.")
        if self.validate_fields:
            for start, end in (("start_date", "end_date"), ("start_moddate", "end_moddate"),
                               ("start_createdate", "end_createdate")):
                parsed = {}
                for field in (start, end):
                    if field in params:
                        try:
                            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", params[field]):
                                raise ValueError
                            parsed[field] = date.fromisoformat(params[field])
                        except ValueError:
                            raise ValidationError(field, "invalid_date", f"Report parameter {field} must be a valid date in YYYY-MM-DD format.") from None
                if start in parsed and end in parsed and parsed[start] >= parsed[end]:
                    raise ValidationError(start, "invalid_range", f"Report parameter {start} must be earlier than {end}.")
            if "sort_order" in params and params["sort_order"] not in ("ascend", "descend"):
                raise ValidationError("sort_order", "invalid_value", "Report sort_order must be ascend or descend.")
        return self._report("AccountList", params)

    def _report(self, name, params):
        response = self._request("GET", "/reports/" + name, params=params)
        if not any(key in response for key in ("Header", "Rows", "Columns")):
            raise AccountingError(f"QuickBooks returned an invalid {name} report response")
        if any(not isinstance(response[key], dict) for key in ("Header", "Rows", "Columns") if key in response):
            raise AccountingError(f"QuickBooks returned an invalid {name} report response")
        return response

    def _filtered_report(self, name, params):
        for field, value in params.items():
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(field, "invalid_type", f"Report parameter {field} must be a nonempty string.")
        if self.validate_fields:
            dates = {}
            pairs = (("start_date", "end_date"), ("start_duedate", "end_duedate"),
                     ("start_svcdate", "end_svcdate"), ("start_createdate", "end_createdate"),
                     ("start_moddate", "end_moddate"))
            for field in ("report_date", *(field for pair in pairs for field in pair)):
                if field in params:
                    try:
                        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", params[field]):
                            raise ValueError
                        dates[field] = date.fromisoformat(params[field])
                    except ValueError:
                        raise ValidationError(field, "invalid_date", f"Report parameter {field} must be a valid date in YYYY-MM-DD format.") from None
            for start, end in pairs:
                if start in dates and end in dates and dates[start] >= dates[end]:
                    raise ValidationError(start, "invalid_range", f"Report parameter {start} must be earlier than {end}.")
            group_values = ("Name", "Account", "Transaction Type", "Customer", "Vendor", "Employee",
                            "Location", "Payment Method", "Day", "Week", "Month", "Quarter", "Year", "None")
            if name == "TransactionListWithSplits":
                group_values = group_values[:3]
            elif name.startswith("TransactionList"):
                group_values += ("Fiscal Year", "Fiscal Quarter")
            choices = {"accounting_method": ("Cash", "Accrual"), "arpaid": ("All", "Paid", "Unpaid"),
                       "appaid": ("All", "Paid", "Unpaid"), "printed": ("Printed", "To_be_printed"),
                       "sort_order": ("ascend", "descend"), "aging_method": ("Report_Date", "Current"),
                       "qzurl": ("true", "false"), "adjusted_gain_loss": ("true", "false"),
                       "group_by": group_values,
                       "summarize_column_by": ("Total", "Month", "Week", "Days", "Quarter", "Year", "Customers", "Vendors", "Classes", "Departments", "Employees", "ProductsAndServices")}
            for field, allowed in choices.items():
                if field in params and params[field] not in allowed:
                    raise ValidationError(field, "invalid_value", f"Report parameter {field} must be one of: {', '.join(allowed)}.")
        if "class_" in params:
            params["class"] = params.pop("class_")
        return self._report(name, params)

    def customer_balance(self, *, customer=None, accounting_method=None, date_macro=None,
                         arpaid=None, report_date=None, sort_order=None,
                         summarize_column_by=None, department=None):
        """Query the CustomerBalance report, preserving its full response."""
        return self._filtered_report("CustomerBalance", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def customer_balance_detail(self, *, customer=None, shipvia=None, term=None,
                                end_duedate=None, start_duedate=None, custom1=None,
                                sort_by=None, arpaid=None, report_date=None,
                                sort_order=None, aging_method=None, department=None, columns=None):
        """Query the CustomerBalanceDetail report."""
        return self._filtered_report("CustomerBalanceDetail", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def customer_income(self, *, customer=None, term=None, accounting_method=None,
                        end_date=None, date_macro=None, class_=None, sort_order=None,
                        summarize_column_by=None, department=None, vendor=None, start_date=None):
        """Query the CustomerIncome report."""
        return self._filtered_report("CustomerIncome", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def general_ledger(self, *, customer=None, account=None, accounting_method=None,
                       source_account=None, end_date=None, date_macro=None, account_type=None,
                       source_account_type=None, sort_by=None, sort_order=None, start_date=None,
                       summarize_column_by=None, department=None, vendor=None, class_=None, columns=None):
        """Query the General Ledger report, preserving nested rows and columns."""
        params = {k: v for k, v in locals().items() if k != "self" and v is not None}
        return self._filtered_report("GeneralLedger", params)

    def inventory_valuation_detail(self, *, end_date=None, end_svcdate=None, date_macro=None,
                                   svcdate_macro=None, start_svcdate=None, group_by=None,
                                   start_date=None, columns=None):
        """Query the InventoryValuationDetail report."""
        return self._filtered_report("InventoryValuationDetail", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def inventory_valuation_summary(self, *, qzurl=None, date_macro=None, item=None,
                                    report_date=None, sort_order=None, summarize_column_by=None):
        """Query the InventoryValuationSummary report."""
        return self._filtered_report("InventoryValuationSummary", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def journal_report(self, *, end_date=None, date_macro=None, sort_by=None,
                       sort_order=None, start_date=None, columns=None):
        """Query the JournalReport and preserve its complete report structure."""
        return self._filtered_report("JournalReport", {k: v for k, v in locals().items() if k != "self" and v is not None})

    def profit_and_loss(self, *, customer=None, qzurl=None, accounting_method=None,
                        end_date=None, date_macro=None, adjusted_gain_loss=None,
                        class_=None, item=None, sort_order=None, summarize_column_by=None,
                        department=None, vendor=None, start_date=None):
        """Query the ProfitAndLoss summary and preserve its complete report structure."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("ProfitAndLoss", params)

    def profit_and_loss_detail(self, *, customer=None, account=None, accounting_method=None,
                               end_date=None, date_macro=None, adjusted_gain_loss=None,
                               class_=None, sort_by=None, payment_method=None, sort_order=None,
                               employee=None, department=None, vendor=None, account_type=None,
                               start_date=None, columns=None):
        """Query the ProfitAndLossDetail report with transaction-level filters."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("ProfitAndLossDetail", params)

    def sales_by_class_summary(self, *, customer=None, accounting_method=None,
                               start_date=None, end_date=None, date_macro=None,
                               class_=None, item=None, summarize_column_by=None, department=None):
        """Query the ClassSales report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("ClassSales", params)

    def sales_by_customer(self, *, customer=None, qzurl=None, accounting_method=None,
                          start_date=None, end_date=None, date_macro=None, class_=None,
                          item=None, sort_order=None, summarize_column_by=None, department=None):
        """Query the CustomerSales report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("CustomerSales", params)

    def sales_by_department(self, *, customer=None, accounting_method=None,
                            start_date=None, end_date=None, date_macro=None, class_=None,
                            item=None, sort_order=None, summarize_column_by=None, department=None):
        """Query the DepartmentSales report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("DepartmentSales", params)

    def sales_by_product(self, *, customer=None, start_duedate=None, end_duedate=None,
                         accounting_method=None, start_date=None, end_date=None, date_macro=None,
                         class_=None, item=None, sort_order=None, summarize_column_by=None, department=None):
        """Query the ItemSales report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("ItemSales", params)

    def tax_summary(self, *, agency_id, accounting_method=None, start_date=None, end_date=None,
                    date_macro=None, sort_order=None):
        """Query the TaxSummary report for a tax agency in a supported locale."""
        if not isinstance(agency_id, str) or not agency_id.strip():
            raise ValidationError("agency_id", "required", "Report agency_id must be a nonempty string.")
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("TaxSummary", params)

    def _transaction_list_report(self, report, filters):
        basic = {"docnum", "name", "end_date", "date_macro", "payment_method", "source_account_type",
                 "transaction_type", "group_by", "sort_by", "sort_order", "start_date", "columns"}
        allowed = basic
        if report != "TransactionListWithSplits":
            allowed |= {"duedate_macro", "arpaid", "bothamount", "start_moddate", "department",
                        "start_duedate", "end_duedate", "memo", "appaid", "moddate_macro",
                        "printed", "createdate_macro", "cleared", "qzurl", "term",
                        "end_createdate", "start_createdate", "end_moddate"}
        if report in ("TransactionList", "TransactionListByVendor"):
            allowed.add("vendor")
        if report in ("TransactionList", "TransactionListByCustomer"):
            allowed.add("customer")
        for key in filters:
            if key not in allowed:
                raise ValidationError(key, "unsupported", f"{report} does not support the {key} filter.")
        return self._filtered_report(report, {key: value for key, value in filters.items() if value is not None})

    def transaction_list(self, **filters):
        """Query the TransactionList report, with customer and vendor filters."""
        return self._transaction_list_report("TransactionList", filters)

    def transaction_list_by_vendor(self, **filters):
        """Query the TransactionListByVendor report."""
        return self._transaction_list_report("TransactionListByVendor", filters)

    def transaction_list_by_customer(self, **filters):
        """Query the TransactionListByCustomer report."""
        return self._transaction_list_report("TransactionListByCustomer", filters)

    def transaction_list_with_splits(self, **filters):
        """Query the TransactionListWithSplits report."""
        return self._transaction_list_report("TransactionListWithSplits", filters)

    def trial_balance(self, *, locale=None, accounting_method=None, start_date=None,
                      end_date=None, date_macro=None, sort_order=None, summarize_column_by=None):
        """Query TrialBalance, or TrialBalanceFR when locale is FR."""
        if locale is not None and (not isinstance(locale, str) or not re.fullmatch("[A-Z]{2}", locale)):
            raise ValidationError("locale", "invalid_format", "Trial Balance locale must be a two-letter country code.")
        params = {key: value for key, value in locals().items()
                  if key not in ("self", "locale") and value is not None}
        return self._filtered_report("TrialBalanceFR" if locale == "FR" else "TrialBalance", params)

    def vendor_balance(self, *, qzurl=None, accounting_method=None, date_macro=None, appaid=None,
                       report_date=None, sort_order=None, summarize_column_by=None, department=None, vendor=None):
        """Query the VendorBalance report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("VendorBalance", params)

    def vendor_balance_detail(self, *, term=None, start_duedate=None, end_duedate=None,
                              accounting_method=None, date_macro=None, duedate_macro=None,
                              sort_by=None, report_date=None, sort_order=None, appaid=None,
                              department=None, vendor=None, columns=None):
        """Query the VendorBalanceDetail report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("VendorBalanceDetail", params)

    def vendor_expenses(self, *, customer=None, vendor=None, start_date=None, end_date=None,
                        date_macro=None, class_=None, sort_order=None, summarize_column_by=None,
                        department=None, accounting_method=None):
        """Query the VendorExpenses report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._filtered_report("VendorExpenses", params)

    def ap_aging_detail(self, *, shipvia=None, term=None, start_duedate=None,
                        end_duedate=None, accounting_method=None, custom1=None,
                        custom2=None, custom3=None, report_date=None, num_periods=None,
                        vendor=None, past_due=None, aging_period=None, columns=None):
        """Return Intuit's AgedPayableDetail report and its nested rows."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._aging_detail("AgedPayableDetail", params)

    def ar_aging_detail(self, *, customer=None, shipvia=None, term=None, start_duedate=None,
                        end_duedate=None, custom1=None, custom2=None, custom3=None,
                        report_date=None, num_periods=None, aging_method=None, past_due=None,
                        aging_period=None, columns=None):
        """Return Intuit's AgedReceivableDetail report and its nested rows."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._aging_detail("AgedReceivableDetail", params)

    def _aging_detail(self, name, params):
        for key, value in params.items():
            if key in ("num_periods", "past_due"):
                if type(value) is not int:
                    raise ValidationError(key, "invalid_type", f"Report parameter {key} must be an integer.")
            elif key == "aging_period":
                if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                    raise ValidationError(key, "invalid_type", "Report parameter aging_period must be a number.")
                if not Decimal(str(value)).is_finite():
                    raise ValidationError(key, "invalid_value", "Report parameter aging_period must be finite.")
            elif not isinstance(value, str) or not value.strip():
                raise ValidationError(key, "invalid_type", f"Report parameter {key} must be a nonempty string.")
        if self.validate_fields:
            parsed = {}
            for field in ("report_date", "start_duedate", "end_duedate"):
                if field in params:
                    try:
                        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", params[field]):
                            raise ValueError
                        parsed[field] = date.fromisoformat(params[field])
                    except ValueError:
                        raise ValidationError(field, "invalid_date", f"Report parameter {field} must be a valid date in YYYY-MM-DD format.") from None
            if "start_duedate" in parsed and "end_duedate" in parsed and parsed["start_duedate"] >= parsed["end_duedate"]:
                raise ValidationError("start_duedate", "invalid_range", "Report parameter start_duedate must be earlier than end_duedate.")
            if "accounting_method" in params and params["accounting_method"] not in ("Cash", "Accrual"):
                raise ValidationError("accounting_method", "invalid_value", "Report accounting_method must be Cash or Accrual.")
        if self.validate_fields and "aging_method" in params and params["aging_method"] not in ("Report_Date", "Current"):
            raise ValidationError("aging_method", "invalid_value", "Report aging_method must be Report_Date or Current.")
        return self._report(name, params)

    def ap_aging_summary(self, *, customer=None, qzurl=None, vendor=None, date_macro=None,
                         department=None, report_date=None, sort_order=None, aging_method=None):
        """Return Intuit's AgedPayables summary report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._aging_summary("AgedPayables", params)

    def ar_aging_summary(self, *, customer=None, qzurl=None, date_macro=None,
                         department=None, report_date=None, sort_order=None, aging_method=None):
        """Return Intuit's AgedReceivables summary report."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._aging_summary("AgedReceivables", params)

    def _aging_summary(self, name, params):
        for field, value in params.items():
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(field, "invalid_type", f"Report parameter {field} must be a nonempty string.")
        if self.validate_fields:
            if "report_date" in params:
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", params["report_date"]):
                        raise ValueError
                    date.fromisoformat(params["report_date"])
                except ValueError:
                    raise ValidationError("report_date", "invalid_date", "Report parameter report_date must be a valid date in YYYY-MM-DD format.") from None
            for field, allowed in (("qzurl", ("true", "false")), ("sort_order", ("ascend", "descend")),
                                   ("aging_method", ("Report_Date", "Current"))):
                if field in params and params[field] not in allowed:
                    raise ValidationError(field, "invalid_value", f"Report parameter {field} must be one of: {', '.join(allowed)}.")
        return self._report(name, params)

    def _attachable(self, value, *, update=False, note=False):
        if not isinstance(value, dict):
            raise ValueError("attachable must be a dictionary")
        if note and (not isinstance(value.get("Note"), str) or not value["Note"].strip()):
            raise ValidationError("Note", "required", "Attachable Note is required and must be a nonempty string.")
        if update:
            for field in ("Id", "SyncToken"):
                if not isinstance(value.get(field), str) or not value[field]:
                    raise ValidationError(field, "required", f"Attachable {field} is required and must be a nonempty string.")
        limits = {"FileName": 1000, "Note": 2000, "Category": 100, "ContentType": 100,
                  "PlaceName": 2000, "Long": 100, "Tag": 2000, "Lat": 100}
        for field, limit in limits.items():
            item = value.get(field)
            if item is None:
                continue
            if not isinstance(item, str):
                raise ValidationError(field, "invalid_type", f"Attachable {field} must be a string.")
            if self.validate_fields and len(item) > limit:
                raise ValidationError(field, "max_length", f"Attachable {field} must be at most {limit} characters; received {len(item)}.", limit=limit, actual=len(item))

    @staticmethod
    def _attachable_result(response):
        if not isinstance(response.get("Attachable"), dict):
            raise AccountingError("QuickBooks returned an invalid Attachable response")
        return response

    def create_attachable_note(self, attachable):
        """Create a note attachment; optional AttachableRef links it to an entity."""
        self._attachable(attachable, note=True)
        return self._attachable_result(self._request("POST", "/attachable", attachable))

    def read_attachable(self, attachable_id):
        """Read attachment metadata, including the latest SyncToken."""
        if not isinstance(attachable_id, str) or not attachable_id or attachable_id in (".", ".."):
            raise ValueError("attachable ID must be a nonempty string")
        return self._attachable_result(self._request("GET", "/attachable/" + quote(attachable_id, safe="")))

    def full_update_attachable(self, attachable):
        """Full update; omitted writable fields are cleared by QuickBooks."""
        self._attachable(attachable, update=True)
        if attachable.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._attachable_result(self._request("POST", "/attachable", {**attachable, "sparse": False}))

    def delete_attachable(self, attachable):
        """Delete using the full current payload returned by read_attachable."""
        self._attachable(attachable, update=True)
        return self._attachable_result(self._request("POST", "/attachable", attachable, params={"operation": "delete"}))

    def attachable_download_url(self, attachable_id):
        """Return Intuit's temporary download URL; the caller fetches it separately."""
        if not isinstance(attachable_id, str) or not attachable_id or attachable_id in (".", ".."):
            raise ValueError("attachable ID must be a nonempty string")
        return self._request("GET", "/download/" + quote(attachable_id, safe=""), text_response=True)

    def query_attachables(self, statement="SELECT * FROM Attachable", *, start_position=1, max_results=100):
        return self._query_entity("Attachable", statement, start_position, max_results, allow_id=True)

    def iter_attachables(self, statement="SELECT * FROM Attachable", *, page_size=100):
        return self._iter_entity("Attachable", statement, page_size, allow_id=True)

    def upload_attachments(self, files):
        """Upload files as mappings with filename, content_type, content bytes, and optional metadata."""
        if not isinstance(files, (list, tuple)) or not files:
            raise ValueError("files must be a nonempty sequence")
        boundary = "qbosdk-" + secrets.token_hex(24)
        parts = []
        total = 0
        for index, item in enumerate(files, 1):
            if not isinstance(item, dict):
                raise ValueError("each file must be a dictionary")
            filename, content_type, content = item.get("filename"), item.get("content_type"), item.get("content")
            if not isinstance(filename, str) or not filename or any(c in filename for c in ('"', '\\', '/', '\r', '\n', '\0')):
                raise ValueError("filename must be a nonempty basename without quotes or control characters")
            if any(ord(c) < 32 or ord(c) == 127 for c in filename):
                raise ValueError("filename contains control characters")
            if not isinstance(content_type, str) or not re.fullmatch(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+", content_type):
                raise ValueError("content_type must be a valid MIME type")
            if not isinstance(content, bytes):
                raise ValueError("file content must be bytes")
            if self.validate_fields and len(filename) > 1000:
                raise ValidationError("FileName", "max_length", f"Attachable FileName must be at most 1000 characters; received {len(filename)}.", limit=1000, actual=len(filename))
            total += ((len(content) + 2) // 3) * 4
            if total > 100_000_000:
                raise ValueError("upload request exceeds 100 MB")
            suffix = f"{index:02d}"
            metadata = item.get("metadata")
            if metadata is not None:
                self._attachable(metadata)
                encoded = json.dumps(metadata, allow_nan=False).encode("utf-8")
                parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="file_metadata_{suffix}"; filename="attachment.json"\r\nContent-Type: application/json; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n\r\n'.encode() + encoded + b"\r\n"))
            parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="file_content_{suffix}"; filename="{filename}"\r\nContent-Type: {content_type}\r\nContent-Transfer-Encoding: base64\r\n\r\n'.encode() + base64.b64encode(content) + b"\r\n"))
        parts.append(f"--{boundary}--\r\n".encode())
        if sum(map(len, parts)) > 100_000_000:
            raise ValueError("upload request exceeds 100 MB")
        response = self._request("POST", "/upload", raw_data=b"".join(parts), content_type=f"multipart/form-data; boundary={boundary}")
        if not isinstance(response.get("AttachableResponse"), list):
            raise AccountingError("QuickBooks returned an invalid upload response")
        return response

    def balance_sheet(self, *, customer=None, qzurl=None, accounting_method=None,
                      end_date=None, date_macro=None, adjusted_gain_loss=None,
                      class_=None, item=None, sort_order=None, summarize_column_by=None,
                      department=None, vendor=None, start_date=None):
        """Query the BalanceSheet report, preserving the complete response."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._standard_report("BalanceSheet", params)

    def cash_flow(self, *, customer=None, vendor=None, end_date=None, date_macro=None,
                  class_=None, item=None, sort_order=None, summarize_column_by=None,
                  department=None, start_date=None):
        """Query the CashFlow report, preserving its complete response."""
        params = {key: value for key, value in locals().items() if key != "self" and value is not None}
        return self._standard_report("CashFlow", params)

    def _standard_report(self, name, params):
        if "class_" in params:
            params["class"] = params.pop("class_")
        for field, value in params.items():
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(field, "invalid_type", f"Report parameter {field} must be a nonempty string.")
        if self.validate_fields:
            parsed = {}
            for field in ("start_date", "end_date"):
                if field in params:
                    try:
                        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", params[field]):
                            raise ValueError
                        parsed[field] = date.fromisoformat(params[field])
                    except ValueError:
                        raise ValidationError(field, "invalid_date", f"Report parameter {field} must be a valid date in YYYY-MM-DD format.") from None
            if "start_date" in parsed and "end_date" in parsed and parsed["start_date"] >= parsed["end_date"]:
                raise ValidationError("start_date", "invalid_range", "Report parameter start_date must be earlier than end_date.")
            for field, allowed in (("qzurl", ("true", "false")), ("adjusted_gain_loss", ("true", "false")),
                                   ("accounting_method", ("Cash", "Accrual")), ("sort_order", ("ascend", "descend")),
                                   ("summarize_column_by", ("Total", "Month", "Week", "Days", "Quarter", "Year", "Customers", "Vendors", "Classes", "Departments", "Employees", "ProductsAndServices"))):
                if field in params and params[field] not in allowed:
                    raise ValidationError(field, "invalid_value", f"Report parameter {field} must be one of: {', '.join(allowed)}.")
        return self._report(name, params)

    def batch(self, items):
        """Submit independent batch items and return all per-item results and faults."""
        if not isinstance(items, (list, tuple)) or not 1 <= len(items) <= 30:
            raise ValueError("batch requires between 1 and 30 items")
        if any(not isinstance(item, dict) or not item for item in items):
            raise ValueError("each batch item must be a nonempty dictionary")
        ids = [item["bId"] for item in items if "bId" in item]
        if any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
            raise ValueError("batch item bId values must be nonempty unique strings")
        response = self._request("POST", "/batch", {"BatchItemRequest": list(items)})
        if not isinstance(response.get("BatchItemResponse"), list):
            raise AccountingError("QuickBooks returned an invalid Batch response")
        return response

    def _bill(self, bill, *, update=False):
        if not isinstance(bill, dict):
            raise ValueError("bill must be a dictionary")
        vendor = bill.get("VendorRef")
        if not isinstance(vendor, dict) or not isinstance(vendor.get("value"), str) or not vendor["value"].strip():
            raise ValidationError("VendorRef.value", "required", "Bill VendorRef.value must be a nonempty string.")
        lines = bill.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "Bill Line must be a nonempty list of line objects.")
        if update:
            self._versioned_identity(bill, "Bill")
            if bill.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        self._transaction_text_fields(bill, "Bill")

    def _transaction_text_fields(self, transaction, entity):
        self._limited_text(transaction, entity, "DocNumber", TRANSACTION_DOC_NUMBER_MAX_LENGTH)
        self._limited_text(transaction, entity, "PrivateNote", TRANSACTION_PRIVATE_NOTE_MAX_LENGTH)

    def _limited_text(self, record, entity, field, limit):
        value = record.get(field)
        if value is not None and not isinstance(value, str):
            raise ValidationError(field, "invalid_type", f"{entity} {field} must be a string.")
        if self.validate_fields and value is not None and len(value) > limit:
            raise ValidationError(field, "max_length", f"{entity} {field} must be at most {limit} characters; received {len(value)}.", limit=limit, actual=len(value))

    @staticmethod
    def _versioned_identity(value, entity):
        if not isinstance(value, dict):
            raise ValueError(f"{entity} must be a dictionary")
        for field in ("Id", "SyncToken"):
            if not isinstance(value.get(field), str) or not value[field]:
                raise ValidationError(field, "required", f"{entity} {field} is required and must be a nonempty string.")

    @staticmethod
    def _bill_result(response):
        if not isinstance(response.get("Bill"), dict):
            raise AccountingError("QuickBooks returned an invalid Bill response")
        return response

    def create_bill(self, bill, *, allow_duplicate_doc_number=False):
        """Create a Bill; duplicate document numbers require explicit opt-in."""
        self._bill(bill)
        if type(allow_duplicate_doc_number) is not bool:
            raise ValueError("allow_duplicate_doc_number must be a boolean")
        params = {"include": "allowduplicatedocnum"} if allow_duplicate_doc_number else None
        return self._bill_result(self._request("POST", "/bill", bill, params=params))

    def read_bill(self, bill_id):
        """Read one Bill by ID."""
        if not isinstance(bill_id, str) or not bill_id or bill_id in (".", ".."):
            raise ValueError("bill ID must be a nonempty string")
        return self._bill_result(self._request("GET", "/bill/" + quote(bill_id, safe="")))

    def full_update_bill(self, bill, *, allow_duplicate_doc_number=False):
        """Full update; include all writable fields that must be retained."""
        self._bill(bill, update=True)
        if type(allow_duplicate_doc_number) is not bool:
            raise ValueError("allow_duplicate_doc_number must be a boolean")
        params = {"include": "allowduplicatedocnum"} if allow_duplicate_doc_number else None
        return self._bill_result(self._request("POST", "/bill", {**bill, "sparse": False}, params=params))

    def delete_bill(self, bill):
        """Delete a Bill after the caller unlinks associated transactions."""
        self._versioned_identity(bill, "Bill")
        return self._bill_result(self._request("POST", "/bill", bill, params={"operation": "delete"}))

    def query_bills(self, statement="SELECT * FROM Bill", *, start_position=1, max_results=100):
        return self._query_entity("Bill", statement, start_position, max_results, allow_id=True)

    def iter_bills(self, statement="SELECT * FROM Bill", *, page_size=100):
        return self._iter_entity("Bill", statement, page_size, allow_id=True)

    def _bill_payment(self, payment, *, update=False):
        if not isinstance(payment, dict):
            raise ValueError("bill payment must be a dictionary")
        vendor = payment.get("VendorRef")
        if not isinstance(vendor, dict) or not isinstance(vendor.get("value"), str) or not vendor["value"].strip():
            raise ValidationError("VendorRef.value", "required", "BillPayment VendorRef.value must be a nonempty string.")
        lines = payment.get("Line")
        if not isinstance(lines, list) or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "BillPayment Line must be a list of line objects.")
        amount = payment.get("TotalAmt")
        if isinstance(amount, bool) or not isinstance(amount, (int, float, Decimal)) or not Decimal(str(amount)).is_finite():
            raise ValidationError("TotalAmt", "invalid_type", "BillPayment TotalAmt must be a finite number.")
        if self.validate_fields and amount < 0:
            raise ValidationError("TotalAmt", "invalid_value", "BillPayment TotalAmt cannot be negative.")
        pay_type = payment.get("PayType")
        if not isinstance(pay_type, str) or not pay_type:
            raise ValidationError("PayType", "required", "BillPayment PayType is required.")
        if self.validate_fields and pay_type not in ("Check", "CreditCard"):
            raise ValidationError("PayType", "invalid_value", "BillPayment PayType must be Check or CreditCard.")
        detail = {"Check": "CheckPayment", "CreditCard": "CreditCardPayment"}.get(pay_type)
        if detail and not isinstance(payment.get(detail), dict):
            raise ValidationError(detail, "required", f"BillPayment {detail} is required for {pay_type}.")
        if update:
            self._versioned_identity(payment, "BillPayment")
            if payment.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        self._transaction_text_fields(payment, "BillPayment")

    @staticmethod
    def _bill_payment_result(response):
        if not isinstance(response.get("BillPayment"), dict):
            raise AccountingError("QuickBooks returned an invalid BillPayment response")
        return response

    def create_bill_payment(self, payment, *, allow_duplicate_doc_number=False):
        """Create a BillPayment; this operation may change financial data."""
        self._bill_payment(payment)
        if type(allow_duplicate_doc_number) is not bool:
            raise ValueError("allow_duplicate_doc_number must be a boolean")
        params = {"include": "allowduplicatedocnum"} if allow_duplicate_doc_number else None
        return self._bill_payment_result(self._request("POST", "/billpayment", payment, params=params))

    def read_bill_payment(self, payment_id):
        if not isinstance(payment_id, str) or not payment_id or payment_id in (".", ".."):
            raise ValueError("bill payment ID must be a nonempty string")
        return self._bill_payment_result(self._request("GET", "/billpayment/" + quote(payment_id, safe="")))

    def full_update_bill_payment(self, payment, *, allow_duplicate_doc_number=False):
        """Full update: include all writable fields that must be retained."""
        self._bill_payment(payment, update=True)
        if type(allow_duplicate_doc_number) is not bool:
            raise ValueError("allow_duplicate_doc_number must be a boolean")
        params = {"include": "allowduplicatedocnum"} if allow_duplicate_doc_number else None
        return self._bill_payment_result(self._request("POST", "/billpayment", {**payment, "sparse": False}, params=params))

    def delete_bill_payment(self, payment):
        self._versioned_identity(payment, "BillPayment")
        return self._bill_payment_result(self._request("POST", "/billpayment", payment, params={"operation": "delete"}))

    def void_bill_payment(self, payment):
        """Void a payment using its current Id and SyncToken."""
        self._versioned_identity(payment, "BillPayment")
        body = {"Id": payment["Id"], "SyncToken": payment["SyncToken"], "sparse": True}
        return self._bill_payment_result(self._request("POST", "/billpayment", body, params={"operation": "update", "include": "void"}))

    def query_bill_payments(self, statement="SELECT * FROM BillPayment", *, start_position=1, max_results=100):
        return self._query_entity("BillPayment", statement, start_position, max_results, allow_id=True)

    def iter_bill_payments(self, statement="SELECT * FROM BillPayment", *, page_size=100):
        return self._iter_entity("BillPayment", statement, page_size, allow_id=True)

    def _budget(self, budget, *, update=False):
        if not isinstance(budget, dict):
            raise ValueError("budget must be a dictionary")
        for field in ("StartDate", "EndDate"):
            if not isinstance(budget.get(field), str) or not budget[field].strip():
                raise ValidationError(field, "required", f"Budget {field} is required and must be a nonempty string.")
        if update:
            self._versioned_identity(budget, "Budget")
            if budget.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        if budget.get("Active") is not None and not isinstance(budget["Active"], bool):
            raise ValidationError("Active", "invalid_type", "Budget Active must be a boolean.")
        if budget.get("BudgetDetail") is not None and (not isinstance(budget["BudgetDetail"], list) or any(not isinstance(item, dict) for item in budget["BudgetDetail"])):
            raise ValidationError("BudgetDetail", "invalid_type", "Budget BudgetDetail must be a list of objects.")

    @staticmethod
    def _budget_result(response):
        if not isinstance(response.get("Budget"), dict):
            raise AccountingError("QuickBooks returned an invalid Budget response")
        return response

    def create_budget(self, budget):
        self._budget(budget)
        return self._budget_result(self._request("POST", "/budget", budget))

    def read_budget(self, budget_id):
        if not isinstance(budget_id, str) or not budget_id or budget_id in (".", ".."):
            raise ValueError("budget ID must be a nonempty string")
        return self._budget_result(self._request("GET", "/budget/" + quote(budget_id, safe="")))

    def full_update_budget(self, budget):
        """Full update; include all writable fields that must be retained."""
        self._budget(budget, update=True)
        return self._budget_result(self._request("POST", "/budget", {**budget, "sparse": False}))

    def delete_budget(self, budget):
        """Delete a budget using its current Id and SyncToken."""
        self._versioned_identity(budget, "Budget")
        return self._request("POST", "/budget", budget, params={"operation": "delete"})

    def query_budgets(self, statement="SELECT * FROM Budget", *, start_position=1, max_results=100):
        return self._query_entity("Budget", statement, start_position, max_results, allow_id=True)

    def iter_budgets(self, statement="SELECT * FROM Budget", *, page_size=100):
        return self._iter_entity("Budget", statement, page_size, allow_id=True)

    @staticmethod
    def _entity_query_statement(entity, statement, *, allow_id):
        fields = r"(?:\*|id)" if allow_id else r"\*"
        if not isinstance(statement, str) or not re.match(r"^\s*select\s+" + fields + r"\s+from\s+" + re.escape(entity) + r"\b", statement, re.I):
            raise ValueError(f"statement must select {'* or Id' if allow_id else 'all fields'} from {entity}")
        if ";" in statement or re.search(r"\b(STARTPOSITION|MAXRESULTS)\b", statement, re.I):
            raise ValueError("statement must omit semicolons and pagination clauses")
        return statement.strip()

    def _query_entity(self, entity, statement, start_position, max_results, *, allow_id, response_entity=None):
        statement = self._entity_query_statement(entity, statement, allow_id=allow_id)
        if type(start_position) is not int or start_position < 1 or type(max_results) is not int or not 1 <= max_results <= 1000:
            raise ValueError("start_position must be positive and max_results must be between 1 and 1000")
        query = f"{statement} STARTPOSITION {start_position} MAXRESULTS {max_results}"
        response = self._request("GET", "/query", query=query)
        result = response.get("QueryResponse")
        if not isinstance(result, dict) or not isinstance(result.get(response_entity or entity, []), list):
            raise AccountingError(f"QuickBooks returned an invalid {entity} query response")
        if (response_entity or entity) not in result and any(isinstance(value, list) for value in result.values()):
            raise AccountingError(f"QuickBooks returned an unexpected {entity} query result key")
        return response

    def _iter_entity(self, entity, statement, page_size, *, allow_id, response_entity=None):
        position = 1
        while True:
            result = self._query_entity(entity, statement, position, page_size, allow_id=allow_id, response_entity=response_entity)["QueryResponse"]
            items = result.get(response_entity or entity, [])
            yield from items
            if len(items) < page_size:
                return
            position += len(items)

    def change_data_capture(self, entities, changed_since):
        """Return Intuit's CDC response; the caller manages synchronization checkpoints."""
        if not isinstance(entities, (list, tuple)) or not entities:
            raise ValueError("entities must be a nonempty list or tuple of entity names")
        if any(not isinstance(entity, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", entity) for entity in entities):
            raise ValidationError("entities", "invalid_value", "Each CDC entity must be a nonempty entity name.")
        if not isinstance(changed_since, str) or not changed_since.strip():
            raise ValidationError("changed_since", "required", "changed_since must be a nonempty ISO date or date-time string.")
        if self.validate_fields:
            from datetime import datetime
            try:
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", changed_since):
                    date.fromisoformat(changed_since)
                else:
                    datetime.fromisoformat(changed_since.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError("changed_since", "invalid_date", "changed_since must be a valid ISO date or date-time.") from None
        response = self._request("GET", "/cdc", params={"entities": ",".join(entities), "changedSince": changed_since})
        if not isinstance(response.get("CDCResponse"), list):
            raise AccountingError("QuickBooks returned an invalid change data capture response")
        return response

    def _class(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("class must be a dictionary")
        name = value.get("Name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Name", "required", "Class Name must be a nonempty string.")
        if self.validate_fields and len(name) > 100:
            raise ValidationError("Name", "max_length", f"Class Name must be at most 100 characters; received {len(name)}.", limit=100, actual=len(name))
        for field in ("Active", "SubClass"):
            if value.get(field) is not None and not isinstance(value[field], bool):
                raise ValidationError(field, "invalid_type", f"Class {field} must be a boolean.")
        parent = value.get("ParentRef")
        if parent is not None and (not isinstance(parent, dict) or not isinstance(parent.get("value"), str) or not parent["value"].strip()):
            raise ValidationError("ParentRef.value", "required", "Class ParentRef.value must be a nonempty string.")
        if update:
            self._versioned_identity(value, "Class")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _class_result(response):
        if not isinstance(response.get("Class"), dict):
            raise AccountingError("QuickBooks returned an invalid Class response")
        return response

    def create_class(self, value):
        """Create a class used to categorize transactions."""
        self._class(value)
        return self._class_result(self._request("POST", "/class", value))

    def read_class(self, class_id):
        if not isinstance(class_id, str) or not class_id or class_id in (".", ".."):
            raise ValueError("class ID must be a nonempty string")
        return self._class_result(self._request("GET", "/class/" + quote(class_id, safe="")))

    def full_update_class(self, value):
        """Full update; include all writable fields that must be retained."""
        self._class(value, update=True)
        return self._class_result(self._request("POST", "/class", {**value, "sparse": False}))

    def query_classes(self, statement="SELECT * FROM Class", *, start_position=1, max_results=100):
        return self._query_entity("Class", statement, start_position, max_results, allow_id=True)

    def iter_classes(self, statement="SELECT * FROM Class", *, page_size=100):
        return self._iter_entity("Class", statement, page_size, allow_id=True)

    def _company_currency(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("CompanyCurrency must be a dictionary")
        code = value.get("Code")
        if not isinstance(code, str) or not code.strip():
            raise ValidationError("Code", "required", "CompanyCurrency Code must be a nonempty string.")
        if self.validate_fields and (len(code) != 3 or not code.isascii() or not code.isalpha()):
            raise ValidationError("Code", "invalid_value", "CompanyCurrency Code must be a three-letter ISO currency code.")
        if value.get("Active") is not None and not isinstance(value["Active"], bool):
            raise ValidationError("Active", "invalid_type", "CompanyCurrency Active must be a boolean.")
        if update:
            self._versioned_identity(value, "CompanyCurrency")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _company_currency_result(response):
        if not isinstance(response.get("CompanyCurrency"), dict):
            raise AccountingError("QuickBooks returned an invalid CompanyCurrency response")
        return response

    def create_company_currency(self, value):
        """Activate a currency for a multicurrency-enabled company."""
        self._company_currency(value)
        return self._company_currency_result(self._request("POST", "/companycurrency", value))

    def read_company_currency(self, currency_id):
        if not isinstance(currency_id, str) or not currency_id or currency_id in (".", ".."):
            raise ValueError("company currency ID must be a nonempty string")
        return self._company_currency_result(self._request("GET", "/companycurrency/" + quote(currency_id, safe="")))

    def full_update_company_currency(self, value):
        """Replace writable fields; set Active to false to inactivate."""
        self._company_currency(value, update=True)
        return self._company_currency_result(self._request("POST", "/companycurrency", {**value, "sparse": False}))

    def query_company_currencies(self, statement="SELECT * FROM CompanyCurrency", *, start_position=1, max_results=100):
        return self._query_entity("CompanyCurrency", statement, start_position, max_results, allow_id=True)

    def iter_company_currencies(self, statement="SELECT * FROM CompanyCurrency", *, page_size=100):
        return self._iter_entity("CompanyCurrency", statement, page_size, allow_id=True)

    def _credit_memo(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("CreditMemo must be a dictionary")
        customer = value.get("CustomerRef")
        if not isinstance(customer, dict) or not isinstance(customer.get("value"), str) or not customer["value"].strip():
            raise ValidationError("CustomerRef.value", "required", "CreditMemo CustomerRef.value must be a nonempty string.")
        lines = value.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "CreditMemo Line must be a nonempty list of line objects.")
        if self.validate_fields and not any(line.get("DetailType") in ("SalesItemLineDetail", "GroupLineDetail") for line in lines):
            raise ValidationError("Line", "invalid_value", "CreditMemo requires at least one sales item or group line.")
        if update:
            self._versioned_identity(value, "CreditMemo")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        self._transaction_text_fields(value, "CreditMemo")

    @staticmethod
    def _credit_memo_result(response):
        if not isinstance(response.get("CreditMemo"), dict):
            raise AccountingError("QuickBooks returned an invalid CreditMemo response")
        return response

    @staticmethod
    def _credit_memo_path(memo_id):
        if not isinstance(memo_id, str) or not memo_id or memo_id in (".", ".."):
            raise ValueError("credit memo ID must be a nonempty string")
        return "/creditmemo/" + quote(memo_id, safe="")

    def create_credit_memo(self, value):
        self._credit_memo(value)
        return self._credit_memo_result(self._request("POST", "/creditmemo", value))

    def read_credit_memo(self, memo_id):
        return self._credit_memo_result(self._request("GET", self._credit_memo_path(memo_id)))

    def full_update_credit_memo(self, value):
        """Replace writable fields; include every field that must be retained."""
        self._credit_memo(value, update=True)
        return self._credit_memo_result(self._request("POST", "/creditmemo", {**value, "sparse": False}))

    def delete_credit_memo(self, value):
        """Delete a credit memo using its current Id and SyncToken."""
        self._versioned_identity(value, "CreditMemo")
        return self._credit_memo_result(self._request("POST", "/creditmemo", value, params={"operation": "delete"}))

    def query_credit_memos(self, statement="SELECT * FROM CreditMemo", *, start_position=1, max_results=100):
        return self._query_entity("CreditMemo", statement, start_position, max_results, allow_id=True)

    def iter_credit_memos(self, statement="SELECT * FROM CreditMemo", *, page_size=100):
        return self._iter_entity("CreditMemo", statement, page_size, allow_id=True)

    def get_credit_memo_pdf(self, memo_id):
        """Return the PDF response as bytes."""
        return self._request("GET", self._credit_memo_path(memo_id) + "/pdf", binary_response=True)

    def send_credit_memo(self, memo_id, *, send_to=None):
        """Ask QuickBooks to email the credit memo; this changes its delivery status."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        return self._credit_memo_result(self._request("POST", self._credit_memo_path(memo_id) + "/send", params=params, raw_data=b"", content_type="application/octet-stream"))

    def _credit_card_payment(self, value, *, sparse=False, update=False, delete=False):
        if not isinstance(value, dict):
            raise ValueError("CreditCardPayment must be a dictionary")
        if update or delete:
            self._versioned_identity(value, "CreditCardPayment")
        if not sparse:
            for field in ("BankAccountRef", "CreditCardAccountRef"):
                ref = value.get(field)
                identifier = ref.get("value") if isinstance(ref, dict) else None
                if isinstance(identifier, bool) or not isinstance(identifier, (str, int)) or not str(identifier).strip():
                    raise ValidationError(field + ".value", "required", f"CreditCardPayment {field}.value must be a nonempty identifier.")
            if not delete and (not isinstance(value.get("TxnDate"), str) or not value["TxnDate"].strip()):
                raise ValidationError("TxnDate", "required", "CreditCardPayment TxnDate is required.")
            if "Amount" not in value:
                raise ValidationError("Amount", "required", "CreditCardPayment Amount is required.")
        if "Amount" in value:
            amount = value["Amount"]
            try:
                if isinstance(amount, bool) or not isinstance(amount, (str, int, float, Decimal)) or not Decimal(str(amount)).is_finite():
                    raise ValueError
            except (ValueError, ArithmeticError):
                raise ValidationError("Amount", "invalid_type", "CreditCardPayment Amount must be a finite number.") from None
        for field in ("PrivateNote", "Memo"):
            text = value.get(field)
            if text is not None and not isinstance(text, str):
                raise ValidationError(field, "invalid_type", f"CreditCardPayment {field} must be a string.")
            if self.validate_fields and text is not None and len(text) > 4000:
                raise ValidationError(field, "max_length", f"CreditCardPayment {field} must be at most 4000 characters; received {len(text)}.", limit=4000, actual=len(text))

    @staticmethod
    def _credit_card_payment_result(response):
        if not isinstance(response.get("CreditCardPaymentTxn"), dict):
            raise AccountingError("QuickBooks returned an invalid CreditCardPayment response")
        return response

    def create_credit_card_payment(self, value):
        self._credit_card_payment(value)
        return self._credit_card_payment_result(self._request("POST", "/creditcardpayment", value))

    def read_credit_card_payment(self, payment_id):
        if not isinstance(payment_id, str) or not payment_id or payment_id in (".", ".."):
            raise ValueError("credit card payment ID must be a nonempty string")
        return self._credit_card_payment_result(self._request("GET", "/creditcardpayment/" + quote(payment_id, safe="")))

    def full_update_credit_card_payment(self, value):
        self._credit_card_payment(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._credit_card_payment_result(self._request("POST", "/creditcardpayment", {**value, "sparse": False}))

    def sparse_update_credit_card_payment(self, value):
        self._credit_card_payment(value, sparse=True, update=True)
        return self._credit_card_payment_result(self._request("POST", "/creditcardpayment", {**value, "sparse": True}))

    def delete_credit_card_payment(self, value):
        """Delete using the complete payload obtained from a read."""
        self._credit_card_payment(value, delete=True)
        return self._credit_card_payment_result(self._request("POST", "/creditcardpayment", value, params={"operation": "delete"}))

    def query_credit_card_payments(self, statement="SELECT * FROM CreditCardPayment", *, start_position=1, max_results=100):
        return self._query_entity("CreditCardPayment", statement, start_position, max_results, allow_id=True, response_entity="CreditCardPaymentTxn")

    def iter_credit_card_payments(self, statement="SELECT * FROM CreditCardPayment", *, page_size=100):
        return self._iter_entity("CreditCardPayment", statement, page_size, allow_id=True, response_entity="CreditCardPaymentTxn")

    def _customer(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Customer must be a dictionary")
        if update:
            self._versioned_identity(value, "Customer")
        names = ("DisplayName", "Title", "GivenName", "MiddleName", "FamilyName", "Suffix")
        if not sparse and not any(isinstance(value.get(field), str) and value[field].strip() for field in names):
            raise ValidationError("DisplayName", "required", "Customer requires DisplayName or at least one name component.")
        for field, limit in CUSTOMER_TEXT_MAX_LENGTHS.items():
            item = value.get(field)
            if item is not None and not isinstance(item, str):
                raise ValidationError(field, "invalid_type", f"Customer {field} must be a string.")
            if self.validate_fields and item is not None:
                if len(item) > limit:
                    raise ValidationError(field, "max_length", f"Customer {field} must be at most {limit} characters; received {len(item)}.", limit=limit, actual=len(item))
                if field in (*names, "PrintOnCheckName") and any(char in item for char in (":", "\t", "\n")):
                    raise ValidationError(field, "invalid_character", f"Customer {field} cannot contain a colon, tab, or newline.")
        if not sparse and value.get("Job") is True:
            parent = value.get("ParentRef")
            if not isinstance(parent, dict) or not isinstance(parent.get("value"), str) or not parent["value"].strip():
                raise ValidationError("ParentRef.value", "required", "Customer ParentRef.value is required for a job.")

    @staticmethod
    def _customer_result(response):
        if not isinstance(response.get("Customer"), dict):
            raise AccountingError("QuickBooks returned an invalid Customer response")
        return response

    def create_customer(self, value):
        self._customer(value)
        return self._customer_result(self._request("POST", "/customer", value))

    def read_customer(self, customer_id):
        if not isinstance(customer_id, str) or not customer_id or customer_id in (".", ".."):
            raise ValueError("customer ID must be a nonempty string")
        return self._customer_result(self._request("GET", "/customer/" + quote(customer_id, safe="")))

    def full_update_customer(self, value):
        self._customer(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._customer_result(self._request("POST", "/customer", {**value, "sparse": False}))

    def sparse_update_customer(self, value):
        self._customer(value, update=True, sparse=True)
        return self._customer_result(self._request("POST", "/customer", {**value, "sparse": True}))

    def query_customers(self, statement="SELECT * FROM Customer", *, start_position=1, max_results=100):
        return self._query_entity("Customer", statement, start_position, max_results, allow_id=True)

    def iter_customers(self, statement="SELECT * FROM Customer", *, page_size=100):
        return self._iter_entity("Customer", statement, page_size, allow_id=True)

    def read_customer_type(self, customer_type_id):
        if not isinstance(customer_type_id, str) or not customer_type_id or customer_type_id in (".", ".."):
            raise ValueError("customer type ID must be a nonempty string")
        response = self._request("GET", "/customertype/" + quote(customer_type_id, safe=""))
        if not isinstance(response.get("CustomerType"), dict):
            raise AccountingError("QuickBooks returned an invalid CustomerType response")
        return response

    def query_customer_types(self, statement="SELECT * FROM CustomerType", *, start_position=1, max_results=100):
        return self._query_entity("CustomerType", statement, start_position, max_results, allow_id=True)

    def iter_customer_types(self, statement="SELECT * FROM CustomerType", *, page_size=100):
        return self._iter_entity("CustomerType", statement, page_size, allow_id=True)

    def _department(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("Department must be a dictionary")
        name = value.get("Name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Name", "required", "Department Name must be a nonempty string.")
        if self.validate_fields and len(name) > DEPARTMENT_NAME_MAX_LENGTH:
            raise ValidationError("Name", "max_length", f"Department Name must be at most {DEPARTMENT_NAME_MAX_LENGTH} characters; received {len(name)}.", limit=DEPARTMENT_NAME_MAX_LENGTH, actual=len(name))
        if value.get("Active") is not None and not isinstance(value["Active"], bool):
            raise ValidationError("Active", "invalid_type", "Department Active must be a boolean.")
        parent = value.get("ParentRef")
        if parent is not None and (not isinstance(parent, dict) or not isinstance(parent.get("value"), str) or not parent["value"].strip()):
            raise ValidationError("ParentRef.value", "required", "Department ParentRef.value must be a nonempty string.")
        if value.get("SubDepartment") is True and parent is None:
            raise ValidationError("ParentRef.value", "required", "Department ParentRef.value is required for a subdepartment.")
        if update:
            self._versioned_identity(value, "Department")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _department_result(response):
        if not isinstance(response.get("Department"), dict):
            raise AccountingError("QuickBooks returned an invalid Department response")
        return response

    def create_department(self, value):
        self._department(value)
        return self._department_result(self._request("POST", "/department", value))

    def read_department(self, department_id):
        if not isinstance(department_id, str) or not department_id or department_id in (".", ".."):
            raise ValueError("department ID must be a nonempty string")
        return self._department_result(self._request("GET", "/department/" + quote(department_id, safe="")))

    def full_update_department(self, value):
        """Replace writable fields; set Active false to inactivate."""
        self._department(value, update=True)
        return self._department_result(self._request("POST", "/department", {**value, "sparse": False}))

    def query_departments(self, statement="SELECT * FROM Department", *, start_position=1, max_results=100):
        return self._query_entity("Department", statement, start_position, max_results, allow_id=True)

    def iter_departments(self, statement="SELECT * FROM Department", *, page_size=100):
        return self._iter_entity("Department", statement, page_size, allow_id=True)

    def _deposit(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Deposit must be a dictionary")
        if update:
            self._versioned_identity(value, "Deposit")
        if not sparse or "DepositToAccountRef" in value:
            ref = value.get("DepositToAccountRef")
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError("DepositToAccountRef.value", "required", "Deposit DepositToAccountRef.value must be a nonempty string.")
        if not sparse or "Line" in value:
            lines = value.get("Line")
            if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "required", "Deposit Line must be a nonempty list of line objects.")
        note = value.get("PrivateNote")
        if note is not None and not isinstance(note, str):
            raise ValidationError("PrivateNote", "invalid_type", "Deposit PrivateNote must be a string.")
        if self.validate_fields and note is not None and len(note) > DEPOSIT_PRIVATE_NOTE_MAX_LENGTH:
            raise ValidationError("PrivateNote", "max_length", f"Deposit PrivateNote must be at most {DEPOSIT_PRIVATE_NOTE_MAX_LENGTH} characters; received {len(note)}.", limit=DEPOSIT_PRIVATE_NOTE_MAX_LENGTH, actual=len(note))

    @staticmethod
    def _deposit_result(response):
        if not isinstance(response.get("Deposit"), dict):
            raise AccountingError("QuickBooks returned an invalid Deposit response")
        return response

    def create_deposit(self, value):
        """Record a deposit; lines can reference payments or specify direct deposits."""
        self._deposit(value)
        return self._deposit_result(self._request("POST", "/deposit", value))

    def read_deposit(self, deposit_id):
        if not isinstance(deposit_id, str) or not deposit_id or deposit_id in (".", ".."):
            raise ValueError("deposit ID must be a nonempty string")
        return self._deposit_result(self._request("GET", "/deposit/" + quote(deposit_id, safe="")))

    def full_update_deposit(self, value):
        """Replace writable fields; include every field that must be retained."""
        self._deposit(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._deposit_result(self._request("POST", "/deposit", {**value, "sparse": False}))

    def sparse_update_deposit(self, value):
        self._deposit(value, update=True, sparse=True)
        return self._deposit_result(self._request("POST", "/deposit", {**value, "sparse": True}))

    def delete_deposit(self, value):
        self._versioned_identity(value, "Deposit")
        return self._deposit_result(self._request("POST", "/deposit", value, params={"operation": "delete"}))

    def query_deposits(self, statement="SELECT * FROM Deposit", *, start_position=1, max_results=100):
        return self._query_entity("Deposit", statement, start_position, max_results, allow_id=True)

    def iter_deposits(self, statement="SELECT * FROM Deposit", *, page_size=100):
        return self._iter_entity("Deposit", statement, page_size, allow_id=True)

    def _employee(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("Employee must be a dictionary")
        if not any(isinstance(value.get(field), str) and value[field].strip() for field in ("GivenName", "FamilyName")):
            raise ValidationError("GivenName", "required", "Employee requires GivenName or FamilyName.")
        for field, limit in EMPLOYEE_TEXT_MAX_LENGTHS.items():
            item = value.get(field)
            if item is not None and not isinstance(item, str):
                raise ValidationError(field, "invalid_type", f"Employee {field} must be a string.")
            if self.validate_fields and item is not None:
                if len(item) > limit:
                    raise ValidationError(field, "max_length", f"Employee {field} must be at most {limit} characters; received {len(item)}.", limit=limit, actual=len(item))
                if field in ("DisplayName", "Title", "GivenName", "MiddleName", "FamilyName", "Suffix", "PrintOnCheckName") and any(char in item for char in (":", "\t", "\n")):
                    raise ValidationError(field, "invalid_character", f"Employee {field} cannot contain a colon, tab, or newline.")
        for field in ("Active", "BillableTime", "Organization"):
            if value.get(field) is not None and not isinstance(value[field], bool):
                raise ValidationError(field, "invalid_type", f"Employee {field} must be a boolean.")
        if update:
            self._versioned_identity(value, "Employee")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _employee_result(response):
        if not isinstance(response.get("Employee"), dict):
            raise AccountingError("QuickBooks returned an invalid Employee response")
        return response

    def create_employee(self, value):
        self._employee(value)
        return self._employee_result(self._request("POST", "/employee", value))

    def read_employee(self, employee_id):
        if not isinstance(employee_id, str) or not employee_id or employee_id in (".", ".."):
            raise ValueError("employee ID must be a nonempty string")
        return self._employee_result(self._request("GET", "/employee/" + quote(employee_id, safe="")))

    def full_update_employee(self, value):
        """Replace writable fields; omit masked SSNs for payroll-enabled companies."""
        self._employee(value, update=True)
        return self._employee_result(self._request("POST", "/employee", {**value, "sparse": False}))

    def query_employees(self, statement="SELECT * FROM Employee", *, start_position=1, max_results=100):
        return self._query_entity("Employee", statement, start_position, max_results, allow_id=True)

    def iter_employees(self, statement="SELECT * FROM Employee", *, page_size=100):
        return self._iter_entity("Employee", statement, page_size, allow_id=True)

    def read_entitlements(self):
        """Return the company's entitlement response as XML bytes."""
        return self._request("GET", "/manage/entitlements/v3/" + self._realm_id,
                             binary_response=True, accept="application/xml", service_root=True)

    def _estimate(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Estimate must be a dictionary")
        if update:
            self._versioned_identity(value, "Estimate")
        if not sparse or "CustomerRef" in value:
            customer = value.get("CustomerRef")
            if not isinstance(customer, dict) or not isinstance(customer.get("value"), str) or not customer["value"].strip():
                raise ValidationError("CustomerRef.value", "required", "Estimate CustomerRef.value must be a nonempty string.")
        if not update or "Line" in value:
            lines = value.get("Line")
            if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "required", "Estimate Line must be a nonempty list of line objects.")
            if not update and self.validate_fields and not any(line.get("DetailType") in ("SalesItemLineDetail", "GroupLineDetail") for line in lines):
                raise ValidationError("Line", "invalid_value", "Estimate requires at least one sales item or group line.")
        self._transaction_text_fields(value, "Estimate")

    @staticmethod
    def _estimate_result(response):
        if not isinstance(response.get("Estimate"), dict):
            raise AccountingError("QuickBooks returned an invalid Estimate response")
        return response

    @staticmethod
    def _estimate_path(estimate_id):
        if not isinstance(estimate_id, str) or not estimate_id or estimate_id in (".", ".."):
            raise ValueError("estimate ID must be a nonempty string")
        return "/estimate/" + quote(estimate_id, safe="")

    def create_estimate(self, value):
        self._estimate(value)
        return self._estimate_result(self._request("POST", "/estimate", value))

    def read_estimate(self, estimate_id):
        return self._estimate_result(self._request("GET", self._estimate_path(estimate_id)))

    def full_update_estimate(self, value):
        self._estimate(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._estimate_result(self._request("POST", "/estimate", {**value, "sparse": False}))

    def sparse_update_estimate(self, value):
        self._estimate(value, update=True, sparse=True)
        return self._estimate_result(self._request("POST", "/estimate", {**value, "sparse": True}))

    def delete_estimate(self, value):
        self._versioned_identity(value, "Estimate")
        return self._estimate_result(self._request("POST", "/estimate", value, params={"operation": "delete"}))

    def query_estimates(self, statement="SELECT * FROM Estimate", *, start_position=1, max_results=100):
        return self._query_entity("Estimate", statement, start_position, max_results, allow_id=True)

    def iter_estimates(self, statement="SELECT * FROM Estimate", *, page_size=100):
        return self._iter_entity("Estimate", statement, page_size, allow_id=True)

    def get_estimate_pdf(self, estimate_id):
        return self._request("GET", self._estimate_path(estimate_id) + "/pdf", binary_response=True)

    def send_estimate(self, estimate_id, *, send_to=None):
        """Ask QuickBooks to email an estimate and update its delivery status."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        return self._estimate_result(self._request("POST", self._estimate_path(estimate_id) + "/send", params=params, raw_data=b"", content_type="application/octet-stream"))

    def _exchange_currency_code(self, value, field):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(field, "required", f"ExchangeRate {field} must be a nonempty string.")
        if self.validate_fields and (len(value) != 3 or not value.isascii() or not value.isalpha()):
            raise ValidationError(field, "invalid_value", f"ExchangeRate {field} must be a three-letter ISO currency code.")

    def _exchange_date(self, value, field):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(field, "required", f"ExchangeRate {field} must be a nonempty date string.")
        if self.validate_fields:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    raise ValueError
                date.fromisoformat(value)
            except ValueError:
                raise ValidationError(field, "invalid_date", f"ExchangeRate {field} must be a valid date in YYYY-MM-DD format.") from None

    @staticmethod
    def _exchange_rate_result(response):
        if not isinstance(response.get("ExchangeRate"), dict):
            raise AccountingError("QuickBooks returned an invalid ExchangeRate response")
        return response

    def get_exchange_rate(self, source_currency_code, *, as_of_date=None):
        """Get a currency's exchange rate; the date defaults to today at Intuit."""
        self._exchange_currency_code(source_currency_code, "sourcecurrencycode")
        params = {"sourcecurrencycode": source_currency_code}
        if as_of_date is not None:
            self._exchange_date(as_of_date, "asofdate")
            params["asofdate"] = as_of_date
        return self._exchange_rate_result(self._request("GET", "/exchangerate", params=params))

    def query_exchange_rates(self, statement="SELECT * FROM ExchangeRate", *, start_position=1, max_results=100):
        return self._query_entity("ExchangeRate", statement, start_position, max_results, allow_id=False)

    def iter_exchange_rates(self, statement="SELECT * FROM ExchangeRate", *, page_size=100):
        return self._iter_entity("ExchangeRate", statement, page_size, allow_id=False)

    def update_exchange_rate(self, value):
        """Set a rate using its source currency, date, rate and current SyncToken."""
        if not isinstance(value, dict):
            raise ValueError("ExchangeRate must be a dictionary")
        if not isinstance(value.get("SyncToken"), str) or not value["SyncToken"]:
            raise ValidationError("SyncToken", "required", "ExchangeRate SyncToken must be a nonempty string.")
        self._exchange_currency_code(value.get("SourceCurrencyCode"), "SourceCurrencyCode")
        if value.get("TargetCurrencyCode") is not None:
            self._exchange_currency_code(value["TargetCurrencyCode"], "TargetCurrencyCode")
        self._exchange_date(value.get("AsOfDate"), "AsOfDate")
        rate = value.get("Rate")
        if isinstance(rate, bool) or not isinstance(rate, (int, float, Decimal)) or not Decimal(str(rate)).is_finite():
            raise ValidationError("Rate", "invalid_type", "ExchangeRate Rate must be a finite number.")
        return self._exchange_rate_result(self._request("POST", "/exchangerate", value))

    def _inventory_adjustment(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("InventoryAdjustment must be a dictionary")
        if update:
            self._versioned_identity(value, "InventoryAdjustment")
        for field in ("TxnDate", "DocNumber"):
            if (not update or field in value) and (not isinstance(value.get(field), str) or not value[field].strip()):
                raise ValidationError(field, "required", f"InventoryAdjustment {field} must be a nonempty string.")
        if not update or "AdjustAccountRef" in value:
            ref = value.get("AdjustAccountRef")
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError("AdjustAccountRef.value", "required", "InventoryAdjustment AdjustAccountRef.value must be a nonempty string.")
        if not update or "Line" in value:
            lines = value.get("Line")
            if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "required", "InventoryAdjustment Line must be a nonempty list of line objects.")
        self._transaction_text_fields(value, "InventoryAdjustment")

    @staticmethod
    def _inventory_adjustment_result(response):
        if not isinstance(response.get("InventoryAdjustment"), dict):
            raise AccountingError("QuickBooks returned an invalid InventoryAdjustment response")
        return response

    def create_inventory_adjustment(self, value):
        self._inventory_adjustment(value)
        return self._inventory_adjustment_result(self._request("POST", "/inventoryadjustment", value))

    def read_inventory_adjustment(self, adjustment_id):
        if not isinstance(adjustment_id, str) or not adjustment_id or adjustment_id in (".", ".."):
            raise ValueError("inventory adjustment ID must be a nonempty string")
        return self._inventory_adjustment_result(self._request("GET", "/inventoryadjustment/" + quote(adjustment_id, safe="")))

    def update_inventory_adjustment(self, value):
        """Update an adjustment using Intuit's required sparse mode."""
        self._inventory_adjustment(value, update=True)
        return self._inventory_adjustment_result(self._request("POST", "/inventoryadjustment", {**value, "sparse": True}))

    def delete_inventory_adjustment(self, value):
        self._versioned_identity(value, "InventoryAdjustment")
        return self._inventory_adjustment_result(self._request("POST", "/inventoryadjustment", value, params={"operation": "delete"}))

    def _invoice(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Invoice must be a dictionary")
        if update:
            self._versioned_identity(value, "Invoice")
        if not sparse or "CustomerRef" in value:
            ref = value.get("CustomerRef")
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError("CustomerRef.value", "required", "Invoice CustomerRef.value must be a nonempty string.")
        if not sparse or "Line" in value:
            lines = value.get("Line")
            if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "required", "Invoice Line must be a nonempty list of line objects.")
        self._transaction_text_fields(value, "Invoice")

    @staticmethod
    def _invoice_result(response):
        if not isinstance(response.get("Invoice"), dict):
            raise AccountingError("QuickBooks returned an invalid Invoice response")
        return response

    @staticmethod
    def _invoice_path(invoice_id):
        if not isinstance(invoice_id, str) or not invoice_id or invoice_id in (".", ".."):
            raise ValueError("invoice ID must be a nonempty string")
        return "/invoice/" + quote(invoice_id, safe="")

    @staticmethod
    def _duplicate_doc_number_params(allow_duplicate_doc_number):
        if type(allow_duplicate_doc_number) is not bool:
            raise ValueError("allow_duplicate_doc_number must be a boolean")
        return {"include": "allowduplicatedocnum"} if allow_duplicate_doc_number else None

    def create_invoice(self, value, *, allow_duplicate_doc_number=False):
        self._invoice(value)
        return self._invoice_result(self._request("POST", "/invoice", value, params=self._duplicate_doc_number_params(allow_duplicate_doc_number)))

    def read_invoice(self, invoice_id):
        return self._invoice_result(self._request("GET", self._invoice_path(invoice_id)))

    def full_update_invoice(self, value, *, allow_duplicate_doc_number=False):
        self._invoice(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._invoice_result(self._request("POST", "/invoice", {**value, "sparse": False}, params=self._duplicate_doc_number_params(allow_duplicate_doc_number)))

    def sparse_update_invoice(self, value, *, allow_duplicate_doc_number=False):
        self._invoice(value, update=True, sparse=True)
        return self._invoice_result(self._request("POST", "/invoice", {**value, "sparse": True}, params=self._duplicate_doc_number_params(allow_duplicate_doc_number)))

    def delete_invoice(self, value):
        """Delete an invoice after unlinking its linked transactions."""
        self._versioned_identity(value, "Invoice")
        return self._invoice_result(self._request("POST", "/invoice", value, params={"operation": "delete"}))

    def void_invoice(self, value):
        """Void an invoice using its current Id and SyncToken."""
        self._versioned_identity(value, "Invoice")
        return self._invoice_result(self._request("POST", "/invoice", value, params={"operation": "void"}))

    def query_invoices(self, statement="SELECT * FROM Invoice", *, start_position=1, max_results=100):
        return self._query_entity("Invoice", statement, start_position, max_results, allow_id=True)

    def iter_invoices(self, statement="SELECT * FROM Invoice", *, page_size=100):
        return self._iter_entity("Invoice", statement, page_size, allow_id=True)

    def get_invoice_pdf(self, invoice_id):
        return self._request("GET", self._invoice_path(invoice_id) + "/pdf", binary_response=True)

    def send_invoice(self, invoice_id, *, send_to=None):
        """Ask QuickBooks to email an invoice and update its delivery status."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        return self._invoice_result(self._request("POST", self._invoice_path(invoice_id) + "/send", params=params, raw_data=b"", content_type="application/octet-stream"))

    def _item(self, value, *, update=False, category=False):
        if not isinstance(value, dict):
            raise ValueError("Item must be a dictionary")
        name = value.get("Name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Name", "required", "Item Name must be a nonempty string.")
        for field, limit in ITEM_TEXT_MAX_LENGTHS.items():
            item = value.get(field)
            if item is not None and not isinstance(item, str):
                raise ValidationError(field, "invalid_type", f"Item {field} must be a string.")
            if self.validate_fields and item is not None and len(item) > limit:
                raise ValidationError(field, "max_length", f"Item {field} must be at most {limit} characters; received {len(item)}.", limit=limit, actual=len(item))
        if self.validate_fields and any(char in name for char in (":", "\t", "\n")):
            raise ValidationError("Name", "invalid_character", "Item Name cannot contain a colon, tab, or newline.")
        for field in ("Active", "SubItem", "TrackQtyOnHand"):
            if value.get(field) is not None and not isinstance(value[field], bool):
                raise ValidationError(field, "invalid_type", f"Item {field} must be a boolean.")
        if value.get("SubItem") is True:
            parent = value.get("ParentRef")
            if not isinstance(parent, dict) or not isinstance(parent.get("value"), str) or not parent["value"].strip():
                raise ValidationError("ParentRef.value", "required", "Item ParentRef.value is required for a subitem.")
        if category and value.get("Type") != "Category":
            raise ValidationError("Type", "invalid_value", "Category Type must be Category.")
        if update:
            self._versioned_identity(value, "Item")
            if not category and value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _item_result(response):
        if not isinstance(response.get("Item"), dict):
            raise AccountingError("QuickBooks returned an invalid Item response")
        return response

    def create_item(self, value):
        self._item(value)
        return self._item_result(self._request("POST", "/item", value))

    def create_category(self, value):
        self._item(value, category=True)
        return self._item_result(self._request("POST", "/item", value))

    def read_item(self, item_id):
        if not isinstance(item_id, str) or not item_id or item_id in (".", ".."):
            raise ValueError("item ID must be a nonempty string")
        return self._item_result(self._request("GET", "/item/" + quote(item_id, safe="")))

    def read_category(self, item_id):
        return self.read_item(item_id)

    def read_bundle(self, item_id):
        return self.read_item(item_id)

    def full_update_item(self, value, *, do_not_update_account_on_transactions=False):
        self._item(value, update=True)
        if type(do_not_update_account_on_transactions) is not bool:
            raise ValueError("do_not_update_account_on_transactions must be a boolean")
        params = {"include": "donotupdateaccountontxns"} if do_not_update_account_on_transactions else None
        return self._item_result(self._request("POST", "/item", {**value, "sparse": False}, params=params))

    def update_category(self, value):
        self._item(value, update=True, category=True)
        return self._item_result(self._request("POST", "/item", value))

    def query_items(self, statement="SELECT * FROM Item", *, start_position=1, max_results=100):
        return self._query_entity("Item", statement, start_position, max_results, allow_id=True)

    def iter_items(self, statement="SELECT * FROM Item", *, page_size=100):
        return self._iter_entity("Item", statement, page_size, allow_id=True)

    def query_categories(self, statement="SELECT * FROM Item WHERE Type='Category'", *, start_position=1, max_results=100):
        return self.query_items(statement, start_position=start_position, max_results=max_results)

    def query_bundles(self, statement="SELECT * FROM Item WHERE Type='Group'", *, start_position=1, max_results=100):
        return self.query_items(statement, start_position=start_position, max_results=max_results)

    def _journal_entry(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("JournalEntry must be a dictionary")
        if update:
            self._versioned_identity(value, "JournalEntry")
        if not sparse or "Line" in value:
            lines = value.get("Line")
            if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "required", "JournalEntry Line must be a nonempty list of line objects.")
            if not sparse and self.validate_fields:
                posting_types = [line["JournalEntryLineDetail"].get("PostingType") for line in lines if isinstance(line.get("JournalEntryLineDetail"), dict)]
                if not all(kind in posting_types for kind in ("Debit", "Credit")):
                    raise ValidationError("Line", "invalid_value", "JournalEntry requires at least one debit line and one credit line.")
        self._transaction_text_fields(value, "JournalEntry")

    @staticmethod
    def _journal_entry_result(response):
        if not isinstance(response.get("JournalEntry"), dict):
            raise AccountingError("QuickBooks returned an invalid JournalEntry response")
        return response

    @staticmethod
    def _journal_entry_params(allow_duplicate_doc_number, allow_auto_doc_number):
        if type(allow_duplicate_doc_number) is not bool or type(allow_auto_doc_number) is not bool:
            raise ValueError("document number options must be boolean")
        if allow_duplicate_doc_number and allow_auto_doc_number:
            raise ValueError("document number options cannot be combined")
        if allow_duplicate_doc_number:
            return {"include": "allowduplicatedocnum"}
        if allow_auto_doc_number:
            return {"include": "allowautodocnum"}
        return None

    def create_journal_entry(self, value, *, allow_duplicate_doc_number=False, allow_auto_doc_number=False):
        self._journal_entry(value)
        params = self._journal_entry_params(allow_duplicate_doc_number, allow_auto_doc_number)
        return self._journal_entry_result(self._request("POST", "/journalentry", value, params=params))

    def read_journal_entry(self, entry_id):
        if not isinstance(entry_id, str) or not entry_id or entry_id in (".", ".."):
            raise ValueError("journal entry ID must be a nonempty string")
        return self._journal_entry_result(self._request("GET", "/journalentry/" + quote(entry_id, safe="")))

    def full_update_journal_entry(self, value, *, allow_duplicate_doc_number=False, allow_auto_doc_number=False):
        self._journal_entry(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        params = self._journal_entry_params(allow_duplicate_doc_number, allow_auto_doc_number)
        return self._journal_entry_result(self._request("POST", "/journalentry", {**value, "sparse": False}, params=params))

    def sparse_update_journal_entry(self, value, *, allow_duplicate_doc_number=False, allow_auto_doc_number=False):
        self._journal_entry(value, update=True, sparse=True)
        params = self._journal_entry_params(allow_duplicate_doc_number, allow_auto_doc_number)
        return self._journal_entry_result(self._request("POST", "/journalentry", {**value, "sparse": True}, params=params))

    def delete_journal_entry(self, value):
        self._versioned_identity(value, "JournalEntry")
        return self._journal_entry_result(self._request("POST", "/journalentry", value, params={"operation": "delete"}))

    def query_journal_entries(self, statement="SELECT * FROM JournalEntry", *, start_position=1, max_results=100):
        return self._query_entity("JournalEntry", statement, start_position, max_results, allow_id=True)

    def iter_journal_entries(self, statement="SELECT * FROM JournalEntry", *, page_size=100):
        return self._iter_entity("JournalEntry", statement, page_size, allow_id=True)

    def _payment(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Payment must be a dictionary")
        if update:
            self._versioned_identity(value, "Payment")
        if not sparse or "TotalAmt" in value:
            amount = value.get("TotalAmt")
            if isinstance(amount, bool) or not isinstance(amount, (int, float, Decimal)):
                raise ValidationError("TotalAmt", "invalid_type", "Payment TotalAmt is required and must be a number.")
        if not sparse or "CustomerRef" in value:
            customer = value.get("CustomerRef")
            if not isinstance(customer, dict) or not isinstance(customer.get("value"), str) or not customer["value"].strip():
                raise ValidationError("CustomerRef.value", "required", "Payment CustomerRef.value must be a nonempty string.")
        if "Line" in value:
            lines = value["Line"]
            if not isinstance(lines, list) or any(not isinstance(line, dict) for line in lines):
                raise ValidationError("Line", "invalid_type", "Payment Line must be a list of line objects.")
        self._limited_text(value, "Payment", "PrivateNote", TRANSACTION_PRIVATE_NOTE_MAX_LENGTH)

    @staticmethod
    def _payment_result(response):
        if not isinstance(response.get("Payment"), dict):
            raise AccountingError("QuickBooks returned an invalid Payment response")
        return response

    @staticmethod
    def _payment_path(payment_id):
        if not isinstance(payment_id, str) or not payment_id.strip() or payment_id in (".", ".."):
            raise ValueError("payment ID must be a nonempty string")
        return "/payment/" + quote(payment_id, safe="")

    def create_payment(self, value):
        """Record a received payment; omit Line to leave it unapplied."""
        self._payment(value)
        return self._payment_result(self._request("POST", "/payment", value))

    def read_payment(self, payment_id):
        return self._payment_result(self._request("GET", self._payment_path(payment_id)))

    def full_update_payment(self, value):
        """Replace writable payment fields using the current Id and SyncToken."""
        self._payment(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._payment_result(self._request("POST", "/payment", {**value, "sparse": False}))

    def sparse_update_payment(self, value):
        """Update selected fields; if Line is present it replaces all payment lines."""
        self._payment(value, update=True, sparse=True)
        return self._payment_result(self._request("POST", "/payment", {**value, "sparse": True}))

    def delete_payment(self, value):
        self._versioned_identity(value, "Payment")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._payment_result(self._request("POST", "/payment", identity, params={"operation": "delete"}))

    def void_payment(self, value):
        """Zero a payment. Remove any associated deposit separately before voiding."""
        self._versioned_identity(value, "Payment")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"], "sparse": True}
        return self._payment_result(self._request("POST", "/payment", identity,
                                                  params={"operation": "update", "include": "void"}))

    def query_payments(self, statement="SELECT * FROM Payment", *, start_position=1, max_results=100):
        return self._query_entity("Payment", statement, start_position, max_results, allow_id=True)

    def iter_payments(self, statement="SELECT * FROM Payment", *, page_size=100):
        return self._iter_entity("Payment", statement, page_size, allow_id=True)

    def get_payment_pdf(self, payment_id):
        return self._request("GET", self._payment_path(payment_id) + "/pdf", binary_response=True)

    def send_payment(self, payment_id, *, send_to):
        """Ask QuickBooks to send the payment receipt to an explicit recipient."""
        if not isinstance(send_to, str) or not send_to.strip():
            raise ValueError("send_to must be a nonempty email address string")
        response = self._request("POST", self._payment_path(payment_id) + "/send",
                                 params={"sendTo": send_to}, raw_data=b"",
                                 content_type="application/octet-stream")
        return self._payment_result(response)

    def _payment_method(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("PaymentMethod must be a dictionary")
        if not isinstance(value.get("Name"), str) or not value["Name"].strip():
            raise ValidationError("Name", "required", "PaymentMethod Name must be a nonempty string.")
        self._limited_text(value, "PaymentMethod", "Name", PAYMENT_METHOD_NAME_MAX_LENGTH)
        if value.get("Active") is not None and not isinstance(value["Active"], bool):
            raise ValidationError("Active", "invalid_type", "PaymentMethod Active must be a boolean.")
        method_type = value.get("Type")
        if method_type is not None and not isinstance(method_type, str):
            raise ValidationError("Type", "invalid_type", "PaymentMethod Type must be a string.")
        if self.validate_fields and method_type is not None and method_type not in ("CREDIT_CARD", "NON_CREDIT_CARD"):
            raise ValidationError("Type", "invalid_value", "PaymentMethod Type must be CREDIT_CARD or NON_CREDIT_CARD.")
        if update:
            self._versioned_identity(value, "PaymentMethod")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _payment_method_result(response):
        if not isinstance(response.get("PaymentMethod"), dict):
            raise AccountingError("QuickBooks returned an invalid PaymentMethod response")
        return response

    def create_payment_method(self, value):
        self._payment_method(value)
        return self._payment_method_result(self._request("POST", "/paymentmethod", value))

    def read_payment_method(self, method_id):
        if not isinstance(method_id, str) or not method_id.strip() or method_id in (".", ".."):
            raise ValueError("payment method ID must be a nonempty string")
        return self._payment_method_result(self._request("GET", "/paymentmethod/" + quote(method_id, safe="")))

    def full_update_payment_method(self, value):
        """Replace writable fields; set Active false to disable the payment method."""
        self._payment_method(value, update=True)
        return self._payment_method_result(self._request("POST", "/paymentmethod", {**value, "sparse": False}))

    def query_payment_methods(self, statement="SELECT * FROM PaymentMethod", *, start_position=1, max_results=100):
        return self._query_entity("PaymentMethod", statement, start_position, max_results, allow_id=True)

    def iter_payment_methods(self, statement="SELECT * FROM PaymentMethod", *, page_size=100):
        return self._iter_entity("PaymentMethod", statement, page_size, allow_id=True)

    @staticmethod
    def _preferences_result(response):
        if not isinstance(response.get("Preferences"), dict):
            raise AccountingError("QuickBooks returned an invalid Preferences response")
        return response

    def read_preferences(self):
        """Read the connected company's preferences."""
        return self._preferences_result(self._request("GET", "/preferences"))

    def query_preferences(self, statement="SELECT * FROM Preferences"):
        """Query company preferences without pagination."""
        statement = self._entity_query_statement("Preferences", statement, allow_id=False)
        response = self._request("GET", "/query", query=statement)
        if not isinstance(response.get("QueryResponse"), dict):
            raise AccountingError("QuickBooks returned an invalid Preferences query response")
        return response

    def full_update_preferences(self, value):
        """Replace writable preferences using the current Id and SyncToken."""
        self._versioned_identity(value, "Preferences")
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._preferences_result(self._request("POST", "/preferences", {**value, "sparse": False}))

    def _purchase(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("Purchase must be a dictionary")
        if update:
            self._versioned_identity(value, "Purchase")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        payment_type = value.get("PaymentType")
        if not isinstance(payment_type, str) or not payment_type.strip():
            raise ValidationError("PaymentType", "required", "Purchase PaymentType must be a nonempty string.")
        if self.validate_fields and payment_type not in ("Cash", "Check", "CreditCard"):
            raise ValidationError("PaymentType", "invalid_value", "Purchase PaymentType must be Cash, Check, or CreditCard.")
        account = value.get("AccountRef")
        if not isinstance(account, dict) or not isinstance(account.get("value"), str) or not account["value"].strip():
            raise ValidationError("AccountRef.value", "required", "Purchase AccountRef.value must be a nonempty string.")
        lines = value.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "Purchase Line must be a nonempty list of line objects.")
        self._transaction_text_fields(value, "Purchase")

    @staticmethod
    def _purchase_result(response):
        if not isinstance(response.get("Purchase"), dict):
            raise AccountingError("QuickBooks returned an invalid Purchase response")
        return response

    def create_purchase(self, value, *, allow_duplicate_doc_number=False):
        """Record an expense funded by cash, check, or credit card."""
        self._purchase(value)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._purchase_result(self._request("POST", "/purchase", value, params=params))

    def read_purchase(self, purchase_id):
        if not isinstance(purchase_id, str) or not purchase_id.strip() or purchase_id in (".", ".."):
            raise ValueError("purchase ID must be a nonempty string")
        return self._purchase_result(self._request("GET", "/purchase/" + quote(purchase_id, safe="")))

    def full_update_purchase(self, value, *, allow_duplicate_doc_number=False):
        self._purchase(value, update=True)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._purchase_result(self._request("POST", "/purchase", {**value, "sparse": False}, params=params))

    def delete_purchase(self, value):
        self._versioned_identity(value, "Purchase")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._purchase_result(self._request("POST", "/purchase", identity, params={"operation": "delete"}))

    def query_purchases(self, statement="SELECT * FROM Purchase", *, start_position=1, max_results=100):
        return self._query_entity("Purchase", statement, start_position, max_results, allow_id=True)

    def iter_purchases(self, statement="SELECT * FROM Purchase", *, page_size=100):
        return self._iter_entity("Purchase", statement, page_size, allow_id=True)

    def _purchase_order(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("PurchaseOrder must be a dictionary")
        if update:
            self._versioned_identity(value, "PurchaseOrder")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        for field in ("VendorRef", "APAccountRef"):
            if field == "APAccountRef" and not update and field not in value:
                continue
            ref = value.get(field)
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError(f"{field}.value", "required", f"PurchaseOrder {field}.value must be a nonempty string.")
        lines = value.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "PurchaseOrder Line must be a nonempty list of line objects.")
        self._transaction_text_fields(value, "PurchaseOrder")
        self._limited_text(value, "PurchaseOrder", "Memo", PURCHASE_ORDER_MEMO_MAX_LENGTH)

    @staticmethod
    def _purchase_order_result(response):
        if not isinstance(response.get("PurchaseOrder"), dict):
            raise AccountingError("QuickBooks returned an invalid PurchaseOrder response")
        return response

    @staticmethod
    def _purchase_order_path(order_id):
        if not isinstance(order_id, str) or not order_id.strip() or order_id in (".", ".."):
            raise ValueError("purchase order ID must be a nonempty string")
        return "/purchaseorder/" + quote(order_id, safe="")

    def create_purchase_order(self, value, *, allow_duplicate_doc_number=False):
        self._purchase_order(value)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._purchase_order_result(self._request("POST", "/purchaseorder", value, params=params))

    def read_purchase_order(self, order_id):
        return self._purchase_order_result(self._request("GET", self._purchase_order_path(order_id)))

    def full_update_purchase_order(self, value, *, allow_duplicate_doc_number=False):
        self._purchase_order(value, update=True)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._purchase_order_result(self._request("POST", "/purchaseorder", {**value, "sparse": False}, params=params))

    def delete_purchase_order(self, value):
        """Delete an order after unlinking its associated transactions."""
        self._versioned_identity(value, "PurchaseOrder")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._purchase_order_result(self._request("POST", "/purchaseorder", identity, params={"operation": "delete"}))

    def query_purchase_orders(self, statement="SELECT * FROM PurchaseOrder", *, start_position=1, max_results=100):
        return self._query_entity("PurchaseOrder", statement, start_position, max_results, allow_id=True)

    def iter_purchase_orders(self, statement="SELECT * FROM PurchaseOrder", *, page_size=100):
        return self._iter_entity("PurchaseOrder", statement, page_size, allow_id=True)

    def get_purchase_order_pdf(self, order_id):
        return self._request("GET", self._purchase_order_path(order_id) + "/pdf", binary_response=True)

    def send_purchase_order(self, order_id, *, send_to=None):
        """Ask QuickBooks to email the order using POEmail or an explicit recipient."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        response = self._request("POST", self._purchase_order_path(order_id) + "/send",
                                 params=params, raw_data=b"", content_type="application/octet-stream")
        return self._purchase_order_result(response)

    @staticmethod
    def _recurring_template(value):
        if not isinstance(value, dict) or len(value) != 1:
            raise ValueError("RecurringTransaction requires one transaction-type key")
        entity, template = next(iter(value.items()))
        supported = ("Bill", "Purchase", "CreditMemo", "Deposit", "Estimate",
                     "Invoice", "JournalEntry", "RefundReceipt", "SalesReceipt",
                     "Transfer", "VendorCredit", "PurchaseOrder")
        if entity not in supported or not isinstance(template, dict):
            raise ValueError("RecurringTransaction requires a supported transaction type and template object")
        return entity, template

    @staticmethod
    def _recurring_transaction_result(response):
        if not isinstance(response.get("RecurringTransaction"), dict):
            raise AccountingError("QuickBooks returned an invalid RecurringTransaction response")
        return response

    def create_recurring_transaction(self, value):
        """Create a template with its RecurringInfo nested under the transaction type."""
        entity, template = self._recurring_template(value)
        if not isinstance(template.get("RecurringInfo"), dict) or not template["RecurringInfo"]:
            field = f"{entity}.RecurringInfo"
            raise ValidationError(field, "required", f"{field} must be a nonempty object.")
        return self._recurring_transaction_result(self._request("POST", "/recurringtransaction", value))

    def delete_recurring_transaction(self, value):
        """Delete an unlinked template using the nested Id and current SyncToken."""
        entity, template = self._recurring_template(value)
        self._versioned_identity(template, entity)
        body = {entity: {"Id": template["Id"], "SyncToken": template["SyncToken"]}}
        response = self._request("POST", "/recurringtransaction", body, params={"operation": "delete"})
        return self._recurring_transaction_result(response)

    def read_recurring_transaction(self, transaction_id):
        if not isinstance(transaction_id, str) or not transaction_id.strip() or transaction_id in (".", ".."):
            raise ValueError("recurring transaction ID must be a nonempty string")
        path = "/recurringtransaction/" + quote(transaction_id, safe="")
        return self._recurring_transaction_result(self._request("GET", path))

    def query_recurring_transactions(self, statement="SELECT * FROM RecurringTransaction",
                                     *, start_position=1, max_results=100):
        return self._query_entity("RecurringTransaction", statement, start_position, max_results, allow_id=False)

    def iter_recurring_transactions(self, statement="SELECT * FROM RecurringTransaction", *, page_size=100):
        return self._iter_entity("RecurringTransaction", statement, page_size, allow_id=False)

    def _refund_receipt(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("RefundReceipt must be a dictionary")
        if update:
            self._versioned_identity(value, "RefundReceipt")
        if not sparse or "DepositToAccountRef" in value:
            ref = value.get("DepositToAccountRef")
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError("DepositToAccountRef.value", "required",
                                      "RefundReceipt DepositToAccountRef.value must be a nonempty string.")
        if not sparse or "Line" in value:
            self._receipt_lines(value.get("Line"), "RefundReceipt", sparse=sparse)
        self._transaction_text_fields(value, "RefundReceipt")
        self._limited_text(value, "RefundReceipt", "PaymentRefNum", REFUND_RECEIPT_PAYMENT_REF_MAX_LENGTH)
        payment_type = value.get("PaymentType")
        if payment_type is not None and not isinstance(payment_type, str):
            raise ValidationError("PaymentType", "invalid_type", "RefundReceipt PaymentType must be a string.")
        if self.validate_fields and payment_type is not None and payment_type not in ("Cash", "Check", "CreditCard", "Other"):
            raise ValidationError("PaymentType", "invalid_value",
                                  "RefundReceipt PaymentType must be Cash, Check, CreditCard, or Other.")

    @staticmethod
    def _refund_receipt_result(response):
        if not isinstance(response.get("RefundReceipt"), dict):
            raise AccountingError("QuickBooks returned an invalid RefundReceipt response")
        return response

    @staticmethod
    def _refund_receipt_path(receipt_id):
        if not isinstance(receipt_id, str) or not receipt_id.strip() or receipt_id in (".", ".."):
            raise ValueError("refund receipt ID must be a nonempty string")
        return "/refundreceipt/" + quote(receipt_id, safe="")

    def create_refund_receipt(self, value, *, allow_duplicate_doc_number=False):
        self._refund_receipt(value)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._refund_receipt_result(self._request("POST", "/refundreceipt", value, params=params))

    def read_refund_receipt(self, receipt_id):
        return self._refund_receipt_result(self._request("GET", self._refund_receipt_path(receipt_id)))

    def full_update_refund_receipt(self, value, *, allow_duplicate_doc_number=False):
        self._refund_receipt(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._refund_receipt_result(self._request("POST", "/refundreceipt", {**value, "sparse": False}, params=params))

    def sparse_update_refund_receipt(self, value, *, allow_duplicate_doc_number=False):
        self._refund_receipt(value, update=True, sparse=True)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._refund_receipt_result(self._request("POST", "/refundreceipt", {**value, "sparse": True}, params=params))

    def delete_refund_receipt(self, value):
        """Delete the receipt after unlinking its associated transactions."""
        self._versioned_identity(value, "RefundReceipt")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._refund_receipt_result(self._request("POST", "/refundreceipt", identity, params={"operation": "delete"}))

    def query_refund_receipts(self, statement="SELECT * FROM RefundReceipt", *, start_position=1, max_results=100):
        return self._query_entity("RefundReceipt", statement, start_position, max_results, allow_id=True)

    def iter_refund_receipts(self, statement="SELECT * FROM RefundReceipt", *, page_size=100):
        return self._iter_entity("RefundReceipt", statement, page_size, allow_id=True)

    def get_refund_receipt_pdf(self, receipt_id):
        return self._request("GET", self._refund_receipt_path(receipt_id) + "/pdf", binary_response=True)

    def send_refund_receipt(self, receipt_id, *, send_to=None):
        """Ask QuickBooks to email a refund receipt and record its delivery information."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        response = self._request("POST", self._refund_receipt_path(receipt_id) + "/send",
                                 params=params, raw_data=b"", content_type="application/octet-stream")
        return self._refund_receipt_result(response)

    def read_reimburse_charge(self, charge_id):
        """Retrieve a billable expense charge by its ReimburseCharge ID."""
        if not isinstance(charge_id, str) or not charge_id.strip() or charge_id in (".", ".."):
            raise ValueError("reimburse charge ID must be a nonempty string")
        response = self._request("GET", "/reimbursecharge/" + quote(charge_id, safe=""))
        if not isinstance(response.get("ReimburseCharge"), dict):
            raise AccountingError("QuickBooks returned an invalid ReimburseCharge response")
        return response

    def query_reimburse_charges(self, statement="SELECT * FROM ReimburseCharge", *, start_position=1, max_results=100):
        return self._query_entity("ReimburseCharge", statement, start_position, max_results, allow_id=True)

    def iter_reimburse_charges(self, statement="SELECT * FROM ReimburseCharge", *, page_size=100):
        return self._iter_entity("ReimburseCharge", statement, page_size, allow_id=True)

    def _receipt_lines(self, lines, entity, *, sparse):
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", f"{entity} Line must be a nonempty list of line objects.")
        if not sparse and self.validate_fields and not any(
            line.get("DetailType") in ("SalesItemLineDetail", "GroupLineDetail") for line in lines
        ):
            raise ValidationError("Line", "invalid_value", f"{entity} requires a sales item or group line.")

    def _sales_receipt(self, value, *, update=False, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("SalesReceipt must be a dictionary")
        if update:
            self._versioned_identity(value, "SalesReceipt")
        if (update and not sparse) or "CustomerRef" in value:
            ref = value.get("CustomerRef")
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError("CustomerRef.value", "required",
                                      "SalesReceipt CustomerRef.value must be a nonempty string.")
        if not sparse or "Line" in value:
            self._receipt_lines(value.get("Line"), "SalesReceipt", sparse=sparse)
        self._transaction_text_fields(value, "SalesReceipt")
        self._limited_text(value, "SalesReceipt", "PaymentRefNum", SALES_RECEIPT_PAYMENT_REF_MAX_LENGTH)

    @staticmethod
    def _sales_receipt_result(response):
        if not isinstance(response.get("SalesReceipt"), dict):
            raise AccountingError("QuickBooks returned an invalid SalesReceipt response")
        return response

    @staticmethod
    def _sales_receipt_path(receipt_id):
        if not isinstance(receipt_id, str) or not receipt_id.strip() or receipt_id in (".", ".."):
            raise ValueError("sales receipt ID must be a nonempty string")
        return "/salesreceipt/" + quote(receipt_id, safe="")

    def create_sales_receipt(self, value):
        self._sales_receipt(value)
        return self._sales_receipt_result(self._request("POST", "/salesreceipt", value))

    def read_sales_receipt(self, receipt_id):
        return self._sales_receipt_result(self._request("GET", self._sales_receipt_path(receipt_id)))

    def full_update_sales_receipt(self, value):
        self._sales_receipt(value, update=True)
        if value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._sales_receipt_result(self._request("POST", "/salesreceipt", {**value, "sparse": False}))

    def sparse_update_sales_receipt(self, value):
        self._sales_receipt(value, update=True, sparse=True)
        return self._sales_receipt_result(self._request("POST", "/salesreceipt", {**value, "sparse": True}))

    def delete_sales_receipt(self, value):
        self._versioned_identity(value, "SalesReceipt")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._sales_receipt_result(self._request("POST", "/salesreceipt", identity, params={"operation": "delete"}))

    def void_sales_receipt(self, value):
        """Zero an existing receipt. Remove any associated deposit separately."""
        self._versioned_identity(value, "SalesReceipt")
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"], "sparse": True}
        response = self._request("POST", "/salesreceipt", identity, params={"operation": "update", "include": "void"})
        return self._sales_receipt_result(response)

    def query_sales_receipts(self, statement="SELECT * FROM SalesReceipt", *, start_position=1, max_results=100):
        return self._query_entity("SalesReceipt", statement, start_position, max_results, allow_id=True)

    def iter_sales_receipts(self, statement="SELECT * FROM SalesReceipt", *, page_size=100):
        return self._iter_entity("SalesReceipt", statement, page_size, allow_id=True)

    def get_sales_receipt_pdf(self, receipt_id):
        return self._request("GET", self._sales_receipt_path(receipt_id) + "/pdf", binary_response=True)

    def send_sales_receipt(self, receipt_id, *, send_to=None):
        """Ask QuickBooks to email a receipt using its billing address or a supplied recipient."""
        if send_to is not None and (not isinstance(send_to, str) or not send_to.strip()):
            raise ValueError("send_to must be a nonempty email address string")
        params = {"sendTo": send_to} if send_to is not None else None
        response = self._request("POST", self._sales_receipt_path(receipt_id) + "/send",
                                 params=params, raw_data=b"", content_type="application/octet-stream")
        return self._sales_receipt_result(response)

    @staticmethod
    def _tax_classification_path(classification_id):
        if (not isinstance(classification_id, str) or not classification_id.strip()
                or classification_id in (".", "..")):
            raise ValueError("tax classification ID must be a nonempty string")
        return "/taxclassification/" + quote(classification_id, safe="")

    def read_tax_classification(self, classification_id):
        """Retrieve one classification and preserve QuickBooks' field casing."""
        response = self._request("GET", self._tax_classification_path(classification_id))
        if not isinstance(response.get("TaxClassification"), dict):
            raise AccountingError("QuickBooks returned an invalid TaxClassification response")
        return response

    def _tax_classification_collection(self, path, params=None):
        response = self._request("GET", path, params=params)
        result = response.get("QueryResponse")
        if not isinstance(result, dict) or not isinstance(result.get("TaxClassification"), list):
            raise AccountingError("QuickBooks returned an invalid TaxClassification collection")
        return response

    def read_tax_classification_children(self, parent_id):
        """Retrieve the classifications directly under a parent."""
        path = self._tax_classification_path(parent_id) + "/children"
        return self._tax_classification_collection(path)

    def read_all_tax_classifications(self):
        """Retrieve the full classification catalog."""
        return self._tax_classification_collection("/taxclassification")

    def read_tax_classifications_by_level(self, level):
        """Retrieve parent classifications at level 1 or child classifications at level 2."""
        if type(level) not in (int, str) or not str(level).strip():
            raise ValidationError("level", "invalid_type", "TaxClassification level must be an integer or nonempty string.")
        level = str(level)
        if self.validate_fields and level not in ("1", "2"):
            raise ValidationError("level", "invalid_value", "TaxClassification level must be 1 or 2.")
        return self._tax_classification_collection("/taxclassification", {"level": level})

    def read_tax_code(self, tax_code_id):
        if not isinstance(tax_code_id, str) or not tax_code_id.strip() or tax_code_id in (".", ".."):
            raise ValueError("tax code ID must be a nonempty string")
        response = self._request("GET", "/taxcode/" + quote(tax_code_id, safe=""))
        if not isinstance(response.get("TaxCode"), dict):
            raise AccountingError("QuickBooks returned an invalid TaxCode response")
        return response

    def query_tax_codes(self, statement="SELECT * FROM TaxCode", *, start_position=1, max_results=100):
        return self._query_entity("TaxCode", statement, start_position, max_results, allow_id=True)

    def iter_tax_codes(self, statement="SELECT * FROM TaxCode", *, page_size=100):
        return self._iter_entity("TaxCode", statement, page_size, allow_id=True)

    def _tax_service_rate(self, rate, path):
        rate_id = rate.get("TaxRateId")
        if "TaxRateId" in rate:
            if not isinstance(rate_id, str) or not rate_id.strip():
                raise ValidationError(path + ".TaxRateId", "required", f"{path}.TaxRateId must be a nonempty string.")
            if self.validate_fields and ("RateValue" in rate or "TaxAgencyId" in rate):
                raise ValidationError(path, "invalid_value", f"{path} must omit RateValue and TaxAgencyId for an existing rate.")
        else:
            for name in ("TaxRateName", "TaxAgencyId", "RateValue"):
                field = path + "." + name
                if not isinstance(rate.get(name), str) or not rate[name].strip():
                    raise ValidationError(field, "required", f"{field} must be a nonempty string for a new rate.")
            rate_name = rate["TaxRateName"]
            if self.validate_fields and len(rate_name) > TAX_SERVICE_RATE_NAME_MAX_LENGTH:
                field = path + ".TaxRateName"
                limit = TAX_SERVICE_RATE_NAME_MAX_LENGTH
                raise ValidationError(field, "max_length", f"{field} must be at most {limit} characters; received {len(rate_name)}.",
                                      limit=limit, actual=len(rate_name))
            if self.validate_fields:
                try:
                    percentage = Decimal(rate["RateValue"].removesuffix("%"))
                    valid = percentage.is_finite() and 0 <= percentage <= 100
                except InvalidOperation:
                    valid = False
                if not valid:
                    field = path + ".RateValue"
                    raise ValidationError(field, "invalid_value", f"{field} must be a percentage from 0 to 100.")
        applicable = rate.get("TaxApplicableOn")
        if applicable is not None and not isinstance(applicable, str):
            raise ValidationError(path + ".TaxApplicableOn", "invalid_type", f"{path}.TaxApplicableOn must be a string.")
        if self.validate_fields and applicable is not None and applicable not in ("Sales", "Purchase"):
            raise ValidationError(path + ".TaxApplicableOn", "invalid_value", f"{path}.TaxApplicableOn must be Sales or Purchase.")
        return rate_id

    def create_tax_code(self, value):
        """Create a tax code through TaxService, optionally creating associated tax rates."""
        if not isinstance(value, dict):
            raise ValueError("TaxService payload must be a dictionary")
        if not isinstance(value.get("TaxCode"), str) or not value["TaxCode"].strip():
            raise ValidationError("TaxCode", "required", "TaxService TaxCode must be a nonempty string.")
        self._limited_text(value, "TaxService", "TaxCode", TAX_CODE_NAME_MAX_LENGTH)
        rates = value.get("TaxRateDetails")
        if not isinstance(rates, list) or not rates or any(not isinstance(rate, dict) for rate in rates):
            raise ValidationError("TaxRateDetails", "required", "TaxService TaxRateDetails must be a nonempty list of objects.")
        seen = set()
        for index, rate in enumerate(rates):
            path = f"TaxRateDetails[{index}]"
            rate_id = self._tax_service_rate(rate, path)
            if rate_id is not None:
                if self.validate_fields and rate_id in seen:
                    raise ValidationError(path + ".TaxRateId", "duplicate", f"{path}.TaxRateId duplicates an earlier rate.")
                seen.add(rate_id)
        response = self._request("POST", "/taxservice/taxcode", value)
        if not isinstance(response.get("TaxCodeId"), str) or not isinstance(response.get("TaxRateDetails"), list):
            raise AccountingError("QuickBooks returned an invalid TaxService response")
        return response

    def create_tax_service(self, value):
        """Create a tax code and its rate associations using the TaxService endpoint."""
        return self.create_tax_code(value)

    def read_tax_payment(self, payment_id):
        """Read a tax payment or refund in an AU, CA, or UK company."""
        if not isinstance(payment_id, str) or not payment_id.strip() or payment_id in (".", ".."):
            raise ValueError("tax payment ID must be a nonempty string")
        response = self._request("GET", "/taxpayment/" + quote(payment_id, safe=""))
        if not isinstance(response.get("TaxPayment"), dict):
            raise AccountingError("QuickBooks returned an invalid TaxPayment response")
        return response

    def query_tax_payments(self, statement="SELECT * FROM TaxPayment", *, start_position=1, max_results=100):
        return self._query_entity("TaxPayment", statement, start_position, max_results, allow_id=True)

    def iter_tax_payments(self, statement="SELECT * FROM TaxPayment", *, page_size=100):
        return self._iter_entity("TaxPayment", statement, page_size, allow_id=True)

    def read_tax_rate(self, tax_rate_id):
        if not isinstance(tax_rate_id, str) or not tax_rate_id.strip() or tax_rate_id in (".", ".."):
            raise ValueError("tax rate ID must be a nonempty string")
        response = self._request("GET", "/taxrate/" + quote(tax_rate_id, safe=""))
        if not isinstance(response.get("TaxRate"), dict):
            raise AccountingError("QuickBooks returned an invalid TaxRate response")
        return response

    def query_tax_rates(self, statement="SELECT * FROM TaxRate", *, start_position=1, max_results=100):
        return self._query_entity("TaxRate", statement, start_position, max_results, allow_id=True)

    def iter_tax_rates(self, statement="SELECT * FROM TaxRate", *, page_size=100):
        return self._iter_entity("TaxRate", statement, page_size, allow_id=True)

    @staticmethod
    def _entity_envelope(response, entity):
        if not isinstance(response.get(entity), dict):
            raise AccountingError(f"QuickBooks returned an invalid {entity} response")
        return response

    def _read_entity_record(self, entity, record_id):
        if not isinstance(record_id, str) or not record_id.strip() or record_id in (".", ".."):
            raise ValueError(f"{entity} ID must be a nonempty string")
        path = f"/{entity.lower()}/" + quote(record_id, safe="")
        return self._entity_envelope(self._request("GET", path), entity)

    def _post_entity_record(self, entity, value, *, params=None):
        response = self._request("POST", f"/{entity.lower()}", value, params=params)
        return self._entity_envelope(response, entity)

    def _update_entity_record(self, entity, value, *, sparse=False, params=None):
        self._versioned_identity(value, entity)
        if not sparse and value.get("sparse", False) is not False:
            raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")
        return self._post_entity_record(entity, {**value, "sparse": sparse}, params=params)

    def _delete_entity_record(self, entity, value):
        self._versioned_identity(value, entity)
        identity = {"Id": value["Id"], "SyncToken": value["SyncToken"]}
        return self._post_entity_record(entity, identity, params={"operation": "delete"})

    @staticmethod
    def _required_reference(record, entity, field):
        reference = record.get(field)
        if (not isinstance(reference, dict) or not isinstance(reference.get("value"), str)
                or not reference["value"].strip()):
            raise ValidationError(f"{field}.value", "required", f"{entity} {field}.value must be a nonempty string.")

    def create_tax_agency(self, value):
        if not isinstance(value, dict):
            raise ValueError("TaxAgency must be a dictionary")
        if not isinstance(value.get("DisplayName"), str) or not value["DisplayName"].strip():
            raise ValidationError("DisplayName", "required", "TaxAgency DisplayName must be a nonempty string.")
        self._limited_text(value, "TaxAgency", "DisplayName", TAX_AGENCY_NAME_MAX_LENGTH)
        return self._post_entity_record("TaxAgency", value)

    def read_tax_agency(self, agency_id):
        return self._read_entity_record("TaxAgency", agency_id)

    def query_tax_agencies(self, statement="SELECT * FROM TaxAgency", *, start_position=1, max_results=100):
        return self._query_entity("TaxAgency", statement, start_position, max_results, allow_id=True)

    def iter_tax_agencies(self, statement="SELECT * FROM TaxAgency", *, page_size=100):
        return self._iter_entity("TaxAgency", statement, page_size, allow_id=True)

    def _term(self, value):
        if not isinstance(value, dict):
            raise ValueError("Term must be a dictionary")
        if not isinstance(value.get("Name"), str) or not value["Name"].strip():
            raise ValidationError("Name", "required", "Term Name must be a nonempty string.")
        self._limited_text(value, "Term", "Name", TERM_NAME_MAX_LENGTH)
        if value.get("DueDays") is None and value.get("DayOfMonthDue") is None:
            raise ValidationError("DueDays", "required", "Term requires DueDays or DayOfMonthDue.")
        if self.validate_fields:
            limits = {"DayOfMonthDue": (1, 31), "DiscountDayOfMonth": (0, 31),
                      "DueDays": (0, 999), "DiscountDays": (0, 999), "DueNextMonthDays": (0, 999)}
            for field, (low, high) in limits.items():
                number = value.get(field)
                if number is None:
                    continue
                if type(number) is not int and not (isinstance(number, str) and re.fullmatch(r"[0-9]{1,3}", number)):
                    raise ValidationError(field, "invalid_type", f"Term {field} must be an integer.")
                if not low <= int(number) <= high:
                    raise ValidationError(field, "invalid_value", f"Term {field} must be between {low} and {high}.")
            if value.get("DiscountPercent") is not None:
                self._validate_decimal_range(value["DiscountPercent"], "DiscountPercent", 0, 100)

    def create_term(self, value):
        self._term(value)
        return self._post_entity_record("Term", value)

    def read_term(self, term_id):
        return self._read_entity_record("Term", term_id)

    def full_update_term(self, value):
        self._term(value)
        return self._update_entity_record("Term", value)

    def query_terms(self, statement="SELECT * FROM Term", *, start_position=1, max_results=100):
        return self._query_entity("Term", statement, start_position, max_results, allow_id=True)

    def iter_terms(self, statement="SELECT * FROM Term", *, page_size=100):
        return self._iter_entity("Term", statement, page_size, allow_id=True)

    @staticmethod
    def _validate_decimal_range(value, field, minimum=None, maximum=None):
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            raise ValidationError(field, "invalid_type", f"{field} must be a finite number.") from None
        if not number.is_finite():
            raise ValidationError(field, "invalid_type", f"{field} must be a finite number.")
        if minimum is not None and maximum is not None and not minimum <= number <= maximum:
            raise ValidationError(field, "invalid_value", f"{field} must be between {minimum} and {maximum}.")

    def _time_activity(self, value):
        if not isinstance(value, dict):
            raise ValueError("TimeActivity must be a dictionary")
        name_of = value.get("NameOf")
        if not isinstance(name_of, str) or not name_of.strip():
            raise ValidationError("NameOf", "required", "TimeActivity NameOf must be a nonempty string.")
        if name_of in ("Employee", "Vendor"):
            self._required_reference(value, "TimeActivity", name_of + "Ref")
        elif self.validate_fields:
            raise ValidationError("NameOf", "invalid_value", "TimeActivity NameOf must be Employee or Vendor.")
        hours_given = value.get("Hours") is not None or value.get("Minutes") is not None
        timestamps = (value.get("StartTime"), value.get("EndTime"))
        if not hours_given or any(timestamp is not None for timestamp in timestamps):
            for field, timestamp in zip(("StartTime", "EndTime"), timestamps):
                if not isinstance(timestamp, str) or not timestamp.strip():
                    raise ValidationError(field, "required", f"TimeActivity {field} must be a nonempty string when using timestamps.")
        if self.validate_fields:
            for hour_field, minute_field in (("Hours", "Minutes"), ("BreakHours", "BreakMinutes")):
                hours = 0 if value.get(hour_field) is None else value[hour_field]
                minutes = 0 if value.get(minute_field) is None else value[minute_field]
                if type(hours) is not int or not 0 <= hours <= 8760:
                    raise ValidationError(hour_field, "invalid_value", f"TimeActivity {hour_field} must be an integer from 0 to 8760.")
                minute_limit = 0 if hours == 8760 else 59
                if type(minutes) is not int or not 0 <= minutes <= minute_limit:
                    raise ValidationError(minute_field, "invalid_value", f"TimeActivity {minute_field} must be an integer from 0 to {minute_limit}.")
        if value.get("BillableStatus") == "Billable":
            self._required_reference(value, "TimeActivity", "CustomerRef")
            if value.get("HourlyRate") is None:
                raise ValidationError("HourlyRate", "required", "TimeActivity HourlyRate is required for billable work.")
        if self.validate_fields and value.get("HourlyRate") is not None:
            self._validate_decimal_range(value["HourlyRate"], "HourlyRate", 0, 99999999999)
        self._limited_text(value, "TimeActivity", "Description", TIME_ACTIVITY_DESCRIPTION_MAX_LENGTH)

    def create_time_activity(self, value):
        self._time_activity(value)
        return self._post_entity_record("TimeActivity", value)

    def read_time_activity(self, activity_id):
        return self._read_entity_record("TimeActivity", activity_id)

    def full_update_time_activity(self, value):
        self._time_activity(value)
        return self._update_entity_record("TimeActivity", value)

    def delete_time_activity(self, value):
        return self._delete_entity_record("TimeActivity", value)

    def query_time_activities(self, statement="SELECT * FROM TimeActivity", *, start_position=1, max_results=100):
        return self._query_entity("TimeActivity", statement, start_position, max_results, allow_id=True)

    def iter_time_activities(self, statement="SELECT * FROM TimeActivity", *, page_size=100):
        return self._iter_entity("TimeActivity", statement, page_size, allow_id=True)

    def _transfer(self, value, *, sparse=False):
        if not isinstance(value, dict):
            raise ValueError("Transfer must be a dictionary")
        for field in ("FromAccountRef", "ToAccountRef"):
            if not sparse or field in value:
                self._required_reference(value, "Transfer", field)
        if not sparse or "Amount" in value:
            amount = value.get("Amount")
            if isinstance(amount, bool) or not isinstance(amount, (int, float, Decimal, str)):
                raise ValidationError("Amount", "required", "Transfer Amount must be a number or decimal string.")
            if self.validate_fields:
                self._validate_decimal_range(amount, "Amount")
        self._limited_text(value, "Transfer", "PrivateNote", TRANSACTION_PRIVATE_NOTE_MAX_LENGTH)

    def create_transfer(self, value):
        self._transfer(value)
        return self._post_entity_record("Transfer", value)

    def read_transfer(self, transfer_id):
        return self._read_entity_record("Transfer", transfer_id)

    def full_update_transfer(self, value):
        self._transfer(value)
        return self._update_entity_record("Transfer", value)

    def sparse_update_transfer(self, value):
        self._transfer(value, sparse=True)
        return self._update_entity_record("Transfer", value, sparse=True)

    def delete_transfer(self, value):
        """Delete a transfer using the complete current record returned by a read."""
        self._versioned_identity(value, "Transfer")
        self._transfer(value)
        return self._post_entity_record("Transfer", value, params={"operation": "delete"})

    def query_transfers(self, statement="SELECT * FROM Transfer", *, start_position=1, max_results=100):
        return self._query_entity("Transfer", statement, start_position, max_results, allow_id=True)

    def iter_transfers(self, statement="SELECT * FROM Transfer", *, page_size=100):
        return self._iter_entity("Transfer", statement, page_size, allow_id=True)

    def _vendor(self, value):
        if not isinstance(value, dict):
            raise ValueError("Vendor must be a dictionary")
        names = ("DisplayName", "Title", "GivenName", "MiddleName", "FamilyName", "Suffix")
        if not any(isinstance(value.get(field), str) and value[field].strip() for field in names):
            raise ValidationError("DisplayName", "required", "Vendor requires DisplayName or at least one name component.")
        for field, limit in VENDOR_TEXT_MAX_LENGTHS.items():
            self._limited_text(value, "Vendor", field, limit)
            text = value.get(field)
            if (self.validate_fields and text is not None and field in (*names, "PrintOnCheckName")
                    and any(character in text for character in (":", "\t", "\n"))):
                raise ValidationError(field, "invalid_character", f"Vendor {field} cannot contain a colon, tab, or newline.")

    def create_vendor(self, value):
        self._vendor(value)
        return self._post_entity_record("Vendor", value)

    def read_vendor(self, vendor_id):
        return self._read_entity_record("Vendor", vendor_id)

    def full_update_vendor(self, value):
        self._vendor(value)
        return self._update_entity_record("Vendor", value)

    def query_vendors(self, statement="SELECT * FROM Vendor", *, start_position=1, max_results=100):
        return self._query_entity("Vendor", statement, start_position, max_results, allow_id=True)

    def iter_vendors(self, statement="SELECT * FROM Vendor", *, page_size=100):
        return self._iter_entity("Vendor", statement, page_size, allow_id=True)

    def _vendor_credit(self, value):
        if not isinstance(value, dict):
            raise ValueError("VendorCredit must be a dictionary")
        self._required_reference(value, "VendorCredit", "VendorRef")
        lines = value.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "VendorCredit Line must be a nonempty list of line objects.")
        if self.validate_fields and not any(line.get("Amount") is not None for line in lines):
            raise ValidationError("Line.Amount", "required", "VendorCredit requires at least one line with an Amount.")
        self._transaction_text_fields(value, "VendorCredit")

    def create_vendor_credit(self, value, *, allow_duplicate_doc_number=False):
        self._vendor_credit(value)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._post_entity_record("VendorCredit", value, params=params)

    def read_vendor_credit(self, credit_id):
        return self._read_entity_record("VendorCredit", credit_id)

    def full_update_vendor_credit(self, value, *, allow_duplicate_doc_number=False):
        self._vendor_credit(value)
        params = self._duplicate_doc_number_params(allow_duplicate_doc_number)
        return self._update_entity_record("VendorCredit", value, params=params)

    def delete_vendor_credit(self, value):
        return self._delete_entity_record("VendorCredit", value)

    def query_vendor_credits(self, statement="SELECT * FROM VendorCredit", *, start_position=1, max_results=100):
        return self._query_entity("VendorCredit", statement, start_position, max_results, allow_id=True)

    def iter_vendor_credits(self, statement="SELECT * FROM VendorCredit", *, page_size=100):
        return self._iter_entity("VendorCredit", statement, page_size, allow_id=True)

    def _change_order(self, value, *, update=False):
        if not isinstance(value, dict):
            raise ValueError("change order must be a dictionary")
        for field in ("ProjectRef", "CustomerRef"):
            ref = value.get(field)
            if not isinstance(ref, dict) or not isinstance(ref.get("value"), str) or not ref["value"].strip():
                raise ValidationError(field + ".value", "required", f"ChangeOrder {field}.value must be a nonempty string.")
        lines = value.get("Line")
        if not isinstance(lines, list) or not lines or any(not isinstance(line, dict) for line in lines):
            raise ValidationError("Line", "required", "ChangeOrder Line must be a nonempty list of line objects.")
        if self.validate_fields:
            if not any(line.get("DetailType") == "SalesItemLineDetail" for line in lines):
                raise ValidationError("Line", "invalid_value", "ChangeOrder requires at least one SalesItemLineDetail line.")
            parent = None
            for line in lines:
                links = line.get("LinkedTxn")
                if not isinstance(links, list) or not links:
                    raise ValidationError("Line.LinkedTxn", "required", "Each ChangeOrder line must reference its parent estimate.")
                estimates = [link.get("TxnId") for link in links if isinstance(link, dict) and link.get("TxnType") == "Estimate" and isinstance(link.get("TxnId"), str) and link["TxnId"]]
                if len(estimates) != 1:
                    raise ValidationError("Line.LinkedTxn", "invalid_value", "Each ChangeOrder line must identify one parent Estimate.")
                if parent is not None and parent != estimates[0]:
                    raise ValidationError("Line.LinkedTxn", "invalid_value", "All ChangeOrder lines must reference the same Estimate.")
                parent = estimates[0]
            if update or "LinkedTxn" in value:
                header_links = value.get("LinkedTxn")
                if not isinstance(header_links, list) or not header_links:
                    raise ValidationError("LinkedTxn", "required", "ChangeOrder LinkedTxn must reference the parent Estimate.")
                if any(not isinstance(link, dict) or link.get("TxnType") != "Estimate"
                       or link.get("TxnId") != parent for link in header_links):
                    raise ValidationError("LinkedTxn", "invalid_value",
                                          "ChangeOrder LinkedTxn must reference the same Estimate as its lines.")
        self._transaction_text_fields(value, "ChangeOrder")
        if update:
            self._versioned_identity(value, "ChangeOrder")
            if value.get("sparse", False) is not False:
                raise ValidationError("sparse", "invalid_value", "A full update cannot be sparse.")

    @staticmethod
    def _change_order_result(response):
        if not isinstance(response.get("ChangeOrder"), dict):
            raise AccountingError("QuickBooks returned an invalid ChangeOrder response")
        return response

    def create_change_order(self, value):
        self._change_order(value)
        return self._change_order_result(self._request("POST", "/changeorder", value))

    def read_change_order(self, change_order_id):
        if not isinstance(change_order_id, str) or not change_order_id or change_order_id in (".", ".."):
            raise ValueError("change order ID must be a nonempty string")
        return self._change_order_result(self._request("GET", "/changeorder/" + quote(change_order_id, safe="")))

    def full_update_change_order(self, value):
        """Full update: include all writable fields and lines that must be retained."""
        self._change_order(value, update=True)
        return self._change_order_result(self._request("POST", "/changeorder", {**value, "sparse": False}))

    def delete_change_order(self, value):
        """Delete a change order; Intuit describes this action as irreversible."""
        self._versioned_identity(value, "ChangeOrder")
        return self._change_order_result(self._request("POST", "/changeorder", value, params={"operation": "delete"}))

    @staticmethod
    def _company_info_result(response):
        if not isinstance(response.get("CompanyInfo"), dict):
            raise AccountingError("QuickBooks returned an invalid CompanyInfo response")
        return response

    def read_company_info(self):
        """Read the CompanyInfo for the client's connected realm."""
        return self._company_info_result(self._request("GET", "/companyinfo/" + self._realm_id))

    def query_company_info(self, statement="SELECT * FROM CompanyInfo", *, start_position=1, max_results=100):
        return self._query_entity("CompanyInfo", statement, start_position, max_results, allow_id=True)

    def _company_info(self, value, *, sparse):
        self._versioned_identity(value, "CompanyInfo")
        if "sparse" in value and value["sparse"] is not sparse:
            raise ValidationError("sparse", "invalid_value", f"CompanyInfo sparse must be {sparse} for this operation.")
        for field in ("CompanyName", "LegalName"):
            item = value.get(field)
            if not sparse and field == "CompanyName" and (not isinstance(item, str) or not item.strip()):
                raise ValidationError(field, "required", "CompanyInfo CompanyName must be a nonempty string for a full update.")
            if item is not None and not isinstance(item, str):
                raise ValidationError(field, "invalid_type", f"CompanyInfo {field} must be a string.")
            if self.validate_fields and isinstance(item, str) and len(item) > 1024:
                raise ValidationError(field, "max_length", f"CompanyInfo {field} must be at most 1024 characters; received {len(item)}.", limit=1024, actual=len(item))
        address = value.get("CompanyAddr")
        if (not sparse and not isinstance(address, dict)) or (address is not None and not isinstance(address, dict)):
            raise ValidationError("CompanyAddr", "invalid_type", "CompanyInfo CompanyAddr must be an address object.")

    def full_update_company_info(self, value):
        """Full update: omitted writable fields may be cleared by Intuit."""
        self._company_info(value, sparse=False)
        return self._company_info_result(self._request("POST", "/companyinfo", {**value, "sparse": False}))

    def sparse_update_company_info(self, value):
        """Update supplied fields only; use the latest Id and SyncToken."""
        self._company_info(value, sparse=True)
        return self._company_info_result(self._request("POST", "/companyinfo", {**value, "sparse": True}))
