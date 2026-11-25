import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class InvoiceTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.invoice = {"CustomerRef": {"value": "1"}, "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34"), "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_delete_void_send(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Invoice":{"Id":"7","SyncToken":"0"}}')
        self.client.create_invoice(self.invoice, allow_duplicate_doc_number=True)
        request = opener.return_value.open.call_args.args[0]
        self.assertIn(b'12.34', request.data)
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.client.read_invoice("7/8")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/invoice/7%2F8"))
        self.client.full_update_invoice({**self.invoice, "Id": "7", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.sparse_update_invoice({"Id": "7", "SyncToken": "1", "PrivateNote": "updated"})
        self.assertTrue(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        for operation, name in ((self.client.delete_invoice, "delete"), (self.client.void_invoice, "void")):
            operation({"Id": "7", "SyncToken": "2"})
            self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": [name]})
        self.client.send_invoice("7", send_to="user+tag@example.com")
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"sendTo": ["user+tag@example.com"]})
        self.assertEqual((request.method, request.data, request.get_header("Content-type")), ("POST", b"", "application/octet-stream"))

    @patch("qbosdk.accounting.build_opener")
    def test_pdf_pagination_and_fault(self, opener):
        pages = [b'%PDF-1.4\ntest', b'{"QueryResponse":{"Invoice":[{"Id":"7"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(self.client.get_invoice_pdf("7"), b'%PDF-1.4\ntest')
        self.assertEqual(opener.return_value.open.call_args.args[0].get_header("Accept"), "application/pdf")
        self.assertEqual(list(self.client.iter_invoices(page_size=1)), [{"Id": "7"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.void_invoice({"Id": "7", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_delegation(self, opener):
        for value in ({"Line": [{}]}, {"CustomerRef": {"value": "1"}, "Line": []}, {**self.invoice, "DocNumber": "x" * 22}, {**self.invoice, "PrivateNote": "x" * 4001}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_invoice(value)
        with self.assertRaises(ValidationError):
            self.client.sparse_update_invoice({"Id": "7"})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Invoice":{}}')
        AccountingClient("token", "123", validate_fields=False).create_invoice({**self.invoice, "DocNumber": "x" * 22})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["DocNumber"]), 22)
