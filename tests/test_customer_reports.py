import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CustomerReportTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_report_paths_parameters_and_nested_rows(self, opener):
        report = {"Header": {"ReportName": "Example"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "12.50"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(report).encode())
        client = AccountingClient("token", "123")
        cases = [(client.customer_balance, {"customer": "1,2", "arpaid": "Unpaid", "report_date": "2025-01-01"}, "CustomerBalance"),
                 (client.customer_balance_detail, {"start_duedate": "2025-01-01", "end_duedate": "2025-02-01", "columns": "tx_date,due_date"}, "CustomerBalanceDetail"),
                 (client.customer_income, {"class_": "2", "start_date": "2025-01-01", "end_date": "2025-02-01", "accounting_method": "Accrual"}, "CustomerIncome")]
        for operation, params, name in cases:
            with self.subTest(name=name):
                self.assertEqual(operation(**params), report)
                request = opener.return_value.open.call_args.args[0]
                self.assertTrue(urlsplit(request.full_url).path.endswith("/reports/" + name))
                expected = {("class" if k == "class_" else k): [v] for k, v in params.items()}
                self.assertEqual(parse_qs(urlsplit(request.full_url).query), expected)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        client = AccountingClient("token", "123")
        for operation, args in ((client.customer_balance, {"arpaid": "bad"}), (client.customer_balance_detail, {"report_date": "2025-02-30"}), (client.customer_income, {"start_date": "2025-02-01", "end_date": "2025-01-01"})):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                operation(**args)
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{}}')
        AccountingClient("token", "123", validate_fields=False).customer_balance(arpaid="bad")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["arpaid"], ["bad"])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.customer_income()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
