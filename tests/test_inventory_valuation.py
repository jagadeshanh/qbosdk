import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class InventoryValuationTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_detail_and_summary_preserve_reports(self, opener):
        report = {"Header": {"ReportName": "Example"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "12.50"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(report).encode())
        client = AccountingClient("token", "123")
        cases = [(client.inventory_valuation_detail, {"start_svcdate": "2025-01-01", "end_svcdate": "2025-06-30", "group_by": "Transaction Type", "columns": "tx_date,qty_on_hand"}, "InventoryValuationDetail"),
                 (client.inventory_valuation_summary, {"item": "1,2", "qzurl": "true", "report_date": "2025-06-30", "sort_order": "ascend"}, "InventoryValuationSummary")]
        for operation, params, name in cases:
            with self.subTest(name=name):
                self.assertEqual(operation(**params), report)
                request = opener.return_value.open.call_args.args[0]
                self.assertTrue(urlsplit(request.full_url).path.endswith("/reports/" + name))
                self.assertEqual(parse_qs(urlsplit(request.full_url).query), {key: [value] for key, value in params.items()})

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        client = AccountingClient("token", "123")
        for operation, args in ((client.inventory_valuation_detail, {"start_svcdate": "2025-02-01", "end_svcdate": "2025-01-01"}), (client.inventory_valuation_detail, {"group_by": "bad"}), (client.inventory_valuation_summary, {"qzurl": "yes"}), (client.inventory_valuation_summary, {"report_date": "2025-02-30"})):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                operation(**args)
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{}}')
        AccountingClient("token", "123", validate_fields=False).inventory_valuation_summary(qzurl="bad")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["qzurl"], ["bad"])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.inventory_valuation_detail()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
