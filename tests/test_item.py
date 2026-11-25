import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class ItemTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_item_and_category_operations(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Item":{"Id":"1","SyncToken":"0","Name":"Example"}}')
        self.client.create_item({"Name": "Example", "Type": "Service"})
        self.client.create_category({"Name": "Category", "Type": "Category"})
        for method in (self.client.read_item, self.client.read_category, self.client.read_bundle):
            method("1/2")
            self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/item/1%2F2"))
        self.client.full_update_item({"Name": "Example", "Id": "1", "SyncToken": "0"}, do_not_update_account_on_transactions=True)
        request = opener.return_value.open.call_args.args[0]
        self.assertFalse(json.loads(request.data)["sparse"])
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["donotupdateaccountontxns"]})
        self.client.update_category({"Name": "Category", "Type": "Category", "Id": "1", "SyncToken": "0"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data)["Type"], "Category")

    @patch("qbosdk.accounting.build_opener")
    def test_type_queries_and_pagination(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"QueryResponse":{"Item":[{"Id":"1"}]}}')
        for method, expected in ((self.client.query_categories, "Type='Category'"), (self.client.query_bundles, "Type='Group'")):
            method(max_results=1)
            query = parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0]
            self.assertIn(expected, query)
        pages = [b'{"QueryResponse":{"Item":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_items(page_size=1)), [{"Id": "1"}])

    @patch("qbosdk.accounting.build_opener")
    def test_validation_delegation_and_fault(self, opener):
        for value in ({"Name": "x" * 101}, {"Name": "bad:name"}, {"Name": "x", "SubItem": True}, {"Name": "x", "Active": "yes"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_item(value)
        with self.assertRaises(ValidationError):
            self.client.create_category({"Name": "x", "Type": "Service"})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Item":{}}')
        AccountingClient("token", "123", validate_fields=False).create_item({"Name": "x" * 101})
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.update_category({"Name": "x", "Type": "Category", "Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
