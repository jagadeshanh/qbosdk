import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class JournalReportTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_query_and_nested_report(self, opener):
        report = {"Header": {"ReportName": "JournalReport"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "12.50"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        result = AccountingClient("token", "123").journal_report(start_date="2025-01-01", end_date="2025-06-30", columns="tx_date,credit_amt", sort_by="tx_date", sort_order="ascend")
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(urlsplit(request.full_url).path.endswith("/reports/JournalReport"))
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"start_date": ["2025-01-01"], "end_date": ["2025-06-30"], "columns": ["tx_date,credit_amt"], "sort_by": ["tx_date"], "sort_order": ["ascend"]})
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        client = AccountingClient("token", "123")
        for params in ({"start_date": "2025-02-01", "end_date": "2025-01-01"}, {"sort_order": "bad"}, {"columns": ""}):
            with self.subTest(params=params), self.assertRaises(ValidationError):
                client.journal_report(**params)
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{}}')
        AccountingClient("token", "123", validate_fields=False).journal_report(sort_order="bad")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["sort_order"], ["bad"])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.journal_report()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
