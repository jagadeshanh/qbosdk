import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class DepositTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.deposit = {"DepositToAccountRef": {"value": "35"}, "Line": [{"Amount": Decimal("20.01"), "DetailType": "DepositLineDetail", "DepositLineDetail": {"AccountRef": {"value": "87"}}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_and_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Deposit":{"Id":"1","SyncToken":"0"}}')
        self.client.create_deposit(self.deposit)
        self.assertIn(b'20.01', opener.return_value.open.call_args.args[0].data)
        self.client.read_deposit("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/deposit/1%2F2"))
        self.client.full_update_deposit({**self.deposit, "Id": "1", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.sparse_update_deposit({"Id": "1", "SyncToken": "1", "PrivateNote": "corrected"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data), {"Id": "1", "SyncToken": "1", "PrivateNote": "corrected", "sparse": True})
        self.client.delete_deposit({"Id": "1", "SyncToken": "2"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_pagination_and_linked_transaction(self, opener):
        pages = [b'{"Deposit":{"Id":"1"}}', b'{"QueryResponse":{"Deposit":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.client.create_deposit({"DepositToAccountRef": {"value": "35"}, "Line": [{"LinkedTxn": [{"TxnId": "120", "TxnType": "Payment"}]}]})
        self.assertEqual(list(self.client.iter_deposits(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_faults(self, opener):
        for value in ({"Line": [{}]}, {"DepositToAccountRef": {"value": "35"}, "Line": []}, {**self.deposit, "PrivateNote": "x" * 4001}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_deposit(value)
        with self.assertRaises(ValidationError):
            self.client.sparse_update_deposit({"Id": "1"})
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_deposit({"Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_field_validation_delegation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Deposit":{}}')
        AccountingClient("token", "123", validate_fields=False).create_deposit({**self.deposit, "PrivateNote": "x" * 4001})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["PrivateNote"]), 4001)
