import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class CashFlowTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_full_query_and_nested_report(self, opener):
        report = {"Header": {"ReportName": "CashFlow"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "100.00"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        client = AccountingClient("token", "123", "production")
        result = client.cash_flow(customer="1", vendor="2", end_date="2024-12-31", date_macro="This Year", class_="3,4", item="5", sort_order="ascend", summarize_column_by="Month", department="6", start_date="2024-01-01")
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual((urlsplit(req.full_url).netloc, urlsplit(req.full_url).path), ("quickbooks.api.intuit.com", "/v3/company/123/reports/CashFlow"))
        params = parse_qs(urlsplit(req.full_url).query)
        self.assertEqual(params["class"], ["3,4"])
        self.assertEqual(len(params), 10)
        self.assertEqual(req.get_header("Authorization"), "Bearer token")
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_faults(self, opener):
        client = AccountingClient("token", "123")
        for args in ({"start_date": "2024-02-30"}, {"start_date": "2024-02-01", "end_date": "2024-01-01"}, {"sort_order": "wrong"}, {"summarize_column_by": "bad"}):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                client.cash_flow(**args)
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            AccountingClient("token", "123", validate_fields=False).cash_flow(sort_order="wrong")
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
