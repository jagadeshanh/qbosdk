import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class BillTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.bill = {"VendorRef": {"value": "56"}, "Line": [{"Amount": Decimal("12.340000000000000001"), "DetailType": "AccountBasedExpenseLineDetail", "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "7"}}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_delete_and_decimal_precision(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Bill":{"Id":"42","SyncToken":"0","TotalAmt":12.34}}')
        self.assertEqual(self.client.create_bill(self.bill, allow_duplicate_doc_number=True)["Bill"]["TotalAmt"], Decimal("12.34"))
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(req.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.assertIn(b'12.340000000000000001', req.data)
        self.client.read_bill("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/bill/1%2F2"))
        self.client.full_update_bill({**self.bill, "Id": "42", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.delete_bill({"Id": "42", "SyncToken": "1"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_query_and_empty_results(self, opener):
        pages = [b'{"QueryResponse":{"Bill":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_bills(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2 MAXRESULTS 1", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_fault(self, opener):
        for body in ({"Line": [{}]}, {"VendorRef": {"value": "1"}, "Line": []}, {**self.bill, "DocNumber": "x" * 22}, {**self.bill, "PrivateNote": "x" * 4001}):
            with self.subTest(body=body), self.assertRaises(ValidationError):
                self.client.create_bill(body)
        with self.assertRaises(ValueError):
            self.client.create_bill({**self.bill, "Line": [{"Amount": Decimal("NaN")}]})
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_bill({"Id": "42", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)
