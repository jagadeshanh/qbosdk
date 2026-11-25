import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class ChangeOrderTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.order = {"ProjectRef": {"value": "1"}, "CustomerRef": {"value": "2"}, "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34001"), "LinkedTxn": [{"TxnType": "Estimate", "TxnId": "3"}]}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"ChangeOrder":{"Id":"4","SyncToken":"0"}}')
        self.assertEqual(self.client.create_change_order(self.order)["ChangeOrder"]["Id"], "4")
        self.assertIn(b'12.34001', opener.return_value.open.call_args.args[0].data)
        self.client.read_change_order("4/5")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/changeorder/4%2F5"))
        links = self.order["Line"][0]["LinkedTxn"]
        self.client.full_update_change_order({**self.order, "Id": "4", "SyncToken": "0", "LinkedTxn": links})
        body = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertFalse(body["sparse"])
        self.assertEqual(body["LinkedTxn"], links)
        self.client.delete_change_order({"Id": "4", "SyncToken": "1"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_upstream_fault(self, opener):
        for order in ({**self.order, "ProjectRef": {}}, {**self.order, "Line": []}, {**self.order, "Line": [{"DetailType": "SalesItemLineDetail"}]}, {**self.order, "Line": self.order["Line"] + [{"DetailType": "SalesItemLineDetail", "LinkedTxn": [{"TxnType": "Estimate", "TxnId": "different"}]}]}):
            with self.subTest(order=order), self.assertRaises(ValidationError):
                self.client.create_change_order(order)
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_change_order({"Id": "4", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_header_estimate_link_and_text_limits(self, opener):
        current = {**self.order, "Id": "4", "SyncToken": "0"}
        for payload in (current, {**current, "LinkedTxn": [{"TxnType": "Estimate", "TxnId": "5"}]}):
            with self.subTest(payload=payload), self.assertRaises(ValidationError) as error:
                self.client.full_update_change_order(payload)
            self.assertEqual(error.exception.field, "LinkedTxn")
        with self.assertRaises(ValidationError) as error:
            self.client.create_change_order({**self.order, "DocNumber": "x" * 22})
        self.assertEqual((error.exception.field, error.exception.limit), ("DocNumber", 21))
        opener.assert_not_called()
