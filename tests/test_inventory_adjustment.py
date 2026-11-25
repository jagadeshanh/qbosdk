import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class InventoryAdjustmentTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.adjustment = {"DocNumber": "27", "TxnDate": "2024-05-02", "AdjustAccountRef": {"value": "91"}, "Line": [{"ItemAdjustmentLineDetail": {"ItemRef": {"value": "101"}, "QtyDiff": Decimal("-2.25")}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_sparse_update_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"InventoryAdjustment":{"Id":"1","SyncToken":"0"}}')
        self.client.create_inventory_adjustment(self.adjustment)
        self.assertIn(b'-2.25', opener.return_value.open.call_args.args[0].data)
        self.client.read_inventory_adjustment("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/inventoryadjustment/1%2F2"))
        self.client.update_inventory_adjustment({"Id": "1", "SyncToken": "0", "PrivateNote": "corrected"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data), {"Id": "1", "SyncToken": "0", "PrivateNote": "corrected", "sparse": True})
        self.client.delete_inventory_adjustment({"Id": "1", "SyncToken": "1"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        for value in ({**self.adjustment, "DocNumber": "x" * 22}, {**self.adjustment, "Line": []}, {**self.adjustment, "AdjustAccountRef": {}}, {**self.adjustment, "TxnDate": ""}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_inventory_adjustment(value)
        with self.assertRaises(ValidationError):
            self.client.update_inventory_adjustment({"Id": "1"})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"InventoryAdjustment":{}}')
        AccountingClient("token", "123", validate_fields=False).create_inventory_adjustment({**self.adjustment, "DocNumber": "x" * 22})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["DocNumber"]), 22)
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_inventory_adjustment({"Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
