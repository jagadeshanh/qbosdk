import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, ValidationError


class ReportRoutesTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_report_filters_and_envelope(self, opener):
        client = AccountingClient("token", "123")
        cases = (
            (client.tax_summary, "TaxSummary", {"agency_id": "3", "sort_order": "ascend"}),
            (client.trial_balance, "TrialBalance", {"date_macro": "This Month"}),
            (client.trial_balance, "TrialBalanceFR", {"locale": "FR", "accounting_method": "Cash"}),
            (client.transaction_list, "TransactionList", {"vendor": "5", "customer": "3", "printed": "Printed"}),
            (client.transaction_list_by_vendor, "TransactionListByVendor", {"vendor": "5", "appaid": "Unpaid"}),
            (client.transaction_list_by_customer, "TransactionListByCustomer", {"customer": "3", "group_by": "Fiscal Quarter"}),
            (client.transaction_list_with_splits, "TransactionListWithSplits", {"group_by": "Account", "columns": "tx_date,name"}),
            (client.vendor_balance, "VendorBalance", {"qzurl": "true", "vendor": "3,5"}),
            (client.vendor_balance_detail, "VendorBalanceDetail", {"start_duedate": "2025-01-01", "end_duedate": "2025-01-31"}),
            (client.vendor_expenses, "VendorExpenses", {"vendor": "5", "class_": "12"}),
        )
        send = opener.return_value.open
        for method, name, params in cases:
            with self.subTest(name=name):
                report = {"Header": {"ReportName": name}, "Columns": {"Column": []},
                          "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "8"}]}]}}]}}
                send.return_value = io.BytesIO(json.dumps(report).encode())
                self.assertEqual(method(**params), report)
                request = send.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual((request.method, url.path), ("GET", "/v3/company/123/reports/" + name))
                self.assertEqual(parse_qs(url.query), {
                    ("class" if key == "class_" else key): [value]
                    for key, value in params.items() if key != "locale"
                })

    @patch("qbosdk.accounting.build_opener")
    def test_report_specific_validation_and_delegation(self, opener):
        client = AccountingClient("token", "123")
        cases = (
            (client.tax_summary, {"agency_id": ""}, "agency_id"),
            (client.transaction_list_by_vendor, {"customer": "4"}, "customer"),
            (client.transaction_list_by_customer, {"vendor": "4"}, "vendor"),
            (client.transaction_list, {"start_moddate": "2025-06-01", "end_moddate": "2025-04-01"}, "start_moddate"),
            (client.transaction_list, {"start_createdate": "2025-02-29"}, "start_createdate"),
            (client.transaction_list_with_splits, {"group_by": "Fiscal Quarter"}, "group_by"),
            (client.vendor_balance_detail, {"appaid": "Other"}, "appaid"),
        )
        for method, params, field in cases:
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                method(**params)
            self.assertEqual(error.exception.field, field)
        opener.assert_not_called()
        send = opener.return_value.open
        send.return_value = io.BytesIO(b'{"Header":{}}')
        AccountingClient("token", "123", validate_fields=False).vendor_balance(appaid="Other")
        self.assertEqual(parse_qs(urlsplit(send.call_args.args[0].full_url).query), {"appaid": ["Other"]})
