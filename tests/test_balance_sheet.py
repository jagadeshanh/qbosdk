import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class BalanceSheetTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_full_query_and_nested_response(self, opener):
        report = {"Header": {"ReportName": "BalanceSheet"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "42.00"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        client = AccountingClient("token", "123", "production")
        result = client.balance_sheet(customer="1,2", qzurl="true", accounting_method="Accrual", end_date="2024-12-31", date_macro="Last Fiscal Year", adjusted_gain_loss="false", class_="3,4", item="5", sort_order="ascend", summarize_column_by="Month", department="6", vendor="7", start_date="2024-01-01")
        request = opener.return_value.open.call_args.args[0]
        url = urlsplit(request.full_url)
        self.assertEqual((url.netloc, url.path), ("quickbooks.api.intuit.com", "/v3/company/123/reports/BalanceSheet"))
        params = parse_qs(url.query)
        self.assertEqual(params["class"], ["3,4"])
        self.assertEqual(len(params), 13)
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_fault_and_server_mode(self, opener):
        client = AccountingClient("token", "123")
        for values in ({"qzurl": "yes"}, {"adjusted_gain_loss": "1"}, {"start_date": "2024-02-30"}, {"start_date": "2024-01-02", "end_date": "2024-01-01"}, {"summarize_column_by": "bad"}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                client.balance_sheet(**values)
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            AccountingClient("token", "123", validate_fields=False).balance_sheet(qzurl="yes")
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["qzurl"], ["yes"])
