import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CustomerTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_and_updates(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Customer":{"Id":"1","SyncToken":"0"}}')
        self.client.create_customer({"GivenName": "Example"})
        self.client.read_customer("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/customer/1%2F2"))
        self.client.full_update_customer({"Id": "1", "SyncToken": "0", "DisplayName": "Example", "Active": False})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.sparse_update_customer({"Id": "1", "SyncToken": "1", "Notes": "updated"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data), {"Id": "1", "SyncToken": "1", "Notes": "updated", "sparse": True})

    @patch("qbosdk.accounting.build_opener")
    def test_pagination_and_fault(self, opener):
        pages = [b'{"QueryResponse":{"Customer":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_customers(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"6240"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.create_customer({"DisplayName": "Duplicate"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "6240")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_delegation(self, opener):
        for value in ({}, {"DisplayName": "a:b"}, {"DisplayName": "x" * 501}, {"GivenName": "A", "Job": True}, {"DisplayName": "A", "Notes": "x" * 2001}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_customer(value)
        with self.assertRaises(ValidationError):
            self.client.sparse_update_customer({"Id": "1"})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Customer":{}}')
        AccountingClient("token", "123", validate_fields=False).create_customer({"DisplayName": "x" * 501})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["DisplayName"]), 501)
