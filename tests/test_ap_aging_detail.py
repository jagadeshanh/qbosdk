import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class APAgingDetailTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_report_and_all_filters(self, opener):
        report = {"Header": {"ReportName": "AgedPayableDetail"}, "Rows": {"Row": [{"Header": {"ColData": [{"value": "Past due"}]}, "Rows": {"Row": [{"ColData": [{"value": "12.34"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        client = AccountingClient("token", "123", "sandbox")
        result = client.ap_aging_detail(shipvia="Delivery", term="1,2", start_duedate="2024-01-01", end_duedate="2024-06-30", accounting_method="Accrual", custom1="a", custom2="b", custom3="c", report_date="2024-06-30", num_periods=4, vendor="1,2", past_due=30, aging_period=Decimal("30.5"), columns="due_date,vend_name")
        request = opener.return_value.open.call_args.args[0]
        url = urlsplit(request.full_url)
        self.assertEqual(url.path, "/v3/company/123/reports/AgedPayableDetail")
        self.assertEqual(url.netloc, "sandbox-quickbooks.api.intuit.com")
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertEqual(parse_qs(url.query)["aging_period"], ["30.5"])
        self.assertEqual(parse_qs(url.query)["columns"], ["due_date,vend_name"])
        self.assertEqual(len(parse_qs(url.query)), 14)
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_invalid_inputs_never_send(self, opener):
        client = AccountingClient("token", "123")
        for kwargs in ({"report_date": "2024-02-30"}, {"start_duedate": "2024-03-01", "end_duedate": "2024-03-01"}, {"num_periods": True}, {"aging_period": float("nan")}, {"accounting_method": "bad"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                client.ap_aging_detail(**kwargs)
        opener.assert_not_called()

    @patch("qbosdk.accounting.build_opener")
    def test_empty_report_and_server_validation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{},"Rows":{}}')
        result = AccountingClient("token", "123", "production", validate_fields=False).ap_aging_detail(report_date="bad", accounting_method="bad")
        self.assertEqual(result["Rows"], {})
        self.assertEqual(urlsplit(opener.return_value.open.call_args.args[0].full_url).netloc, "quickbooks.api.intuit.com")

    @patch("qbosdk.accounting.build_opener")
    def test_fault_propagates(self, opener):
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"123"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            AccountingClient("token", "123").ap_aging_detail()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "123")

    @patch("qbosdk.accounting.build_opener")
    def test_ap_summary_endpoint_parameters_and_validation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{"ReportName":"AgedPayables"},"Rows":{}}')
        client = AccountingClient("token", "123", "production")
        self.assertEqual(client.ap_aging_summary(customer="1,2", qzurl="true", vendor="3", date_macro="This Week", department="4", report_date="2024-06-30", sort_order="descend", aging_method="Report_Date")["Rows"], {})
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(urlsplit(request.full_url).path, "/v3/company/123/reports/AgedPayables")
        self.assertEqual(len(parse_qs(urlsplit(request.full_url).query)), 8)
        for args in ({"qzurl": "yes"}, {"report_date": "2024-02-30"}, {"aging_method": "wrong"}, {"sort_order": "up"}):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                client.ap_aging_summary(**args)
