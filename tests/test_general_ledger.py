import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class GeneralLedgerTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_report_query_and_nested_results(self, opener):
        report = {"Header": {"ReportName": "GeneralLedger"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "12.50"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        result = AccountingClient("token", "123").general_ledger(start_date="2025-01-01", end_date="2025-06-30", source_account_type="Bank", account="1,2", class_="3", columns="account_name,tx_date")
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(urlsplit(request.full_url).path.endswith("/reports/GeneralLedger"))
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"start_date": ["2025-01-01"], "end_date": ["2025-06-30"], "source_account_type": ["Bank"], "account": ["1,2"], "class": ["3"], "columns": ["account_name,tx_date"]})
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        client = AccountingClient("token", "123")
        for args in ({"start_date": "2025-02-01", "end_date": "2025-01-01"}, {"accounting_method": "bad"}, {"sort_order": "bad"}, {"account": ""}):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                client.general_ledger(**args)
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{}}')
        AccountingClient("token", "123", validate_fields=False).general_ledger(accounting_method="bad", account_type="Bank")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["account_type"], ["Bank"])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.general_ledger()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
