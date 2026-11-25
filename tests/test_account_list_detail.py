import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class AccountListDetailTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_report_request_and_response(self, opener):
        response = {"Header": {"ReportName": "AccountList", "Option": [{"Name": "NoReportData", "Value": "false"}]},
                    "Rows": {"Row": [{"ColData": [{"value": "Test"}, {"value": "Income"}], "type": "Data"}]},
                    "Columns": {"Column": [{"ColType": "account_name"}, {"ColType": "account_type"}]},
                    "extra": "preserved"}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(response).encode())
        client = AccountingClient("token", "123", "production")
        actual = client.account_list_detail(columns="account_name,account_type", account_type="Income",
                                             moddate_macro="This Week", sort_order="ascend")
        request = opener.return_value.open.call_args.args[0]
        url = urlsplit(request.full_url)
        self.assertEqual((url.scheme, url.netloc, url.path), ("https", "quickbooks.api.intuit.com", "/v3/company/123/reports/AccountList"))
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertEqual(parse_qs(url.query), {"columns": ["account_name,account_type"], "account_type": ["Income"],
                                               "moddate_macro": ["This Week"], "sort_order": ["ascend"]})
        self.assertEqual(actual, response)

    @patch("qbosdk.accounting.build_opener")
    def test_empty_report_and_sandbox_defaults(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{"ReportName":"AccountList"},"Rows":{},"Columns":{}}')
        result = AccountingClient("token", "123").account_list_detail()
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://sandbox-quickbooks.api.intuit.com/v3/company/123/reports/AccountList")
        self.assertEqual(result["Rows"], {})

    @patch("qbosdk.accounting.build_opener")
    def test_dates_sort_and_type_validation(self, opener):
        client = AccountingClient("token", "123")
        cases = [{"start_date": "2024-02-30"}, {"start_moddate": "2024-2-01"},
                 {"start_date": "2024-03-01", "end_date": "2024-03-01"},
                 {"start_createdate": "2024-03-02", "end_createdate": "2024-03-01"},
                 {"sort_order": "ascending"}, {"columns": ["account_name"]}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValidationError):
                client.account_list_detail(**case)
        opener.assert_not_called()

    @patch("qbosdk.accounting.build_opener")
    def test_server_validation_and_all_date_parameters(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{}}')
        client = AccountingClient("token", "123", validate_fields=False)
        client.account_list_detail(start_date="bad", start_moddate="bad", start_createdate="bad", sort_order="bad")
        params = parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)
        self.assertEqual(params["start_createdate"], ["bad"])
        self.assertEqual(params["sort_order"], ["bad"])

    @patch("qbosdk.accounting.build_opener")
    def test_upstream_error_and_malformed_report(self, opener):
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000","Message":"Invalid report"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            AccountingClient("token", "123").account_list_detail()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
        opener.return_value.open.side_effect = None
        opener.return_value.open.return_value = io.BytesIO(b'{"Rows":[]}')
        with self.assertRaises(AccountingError):
            AccountingClient("token", "123").account_list_detail()
