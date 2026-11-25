import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class ClassTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_preserve_fields(self, opener):
        payload = {"Class": {"Id": "1", "Name": "Example", "SyncToken": "0", "ParentRef": {"value": "2"}, "SubClass": True}}
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(payload).encode())
        self.assertEqual(self.client.create_class({"Name": "Example", "ParentRef": {"value": "2"}}), payload)
        self.client.read_class("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/class/1%2F2"))
        self.client.full_update_class({**payload["Class"], "Active": False})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])

    @patch("qbosdk.accounting.build_opener")
    def test_query_pages_and_validation(self, opener):
        pages = [b'{"QueryResponse":{"Class":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_classes(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        for value in ({"Name": "x" * 101}, {"Name": "ok", "ParentRef": {}}, {"Name": "ok", "Active": "true"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_class(value)
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.full_update_class({"Name": "ok", "Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
