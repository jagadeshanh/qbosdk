import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, ValidationError


@patch("qbosdk.accounting.build_opener")
class SalesReceiptTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.identity = {"Id": "7", "SyncToken": "2"}
        self.receipt = {"Line": [{"DetailType": "SalesItemLineDetail", "Amount": 12,
                                  "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}]}

    def test_create_read_and_update_modes(self, opener):
        send = opener.return_value.open
        response = {"SalesReceipt": self.identity}
        send.side_effect = lambda *args, **kwargs: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_sales_receipt(self.receipt), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/salesreceipt"))
        self.assertEqual((request.method, json.loads(request.data)), ("POST", self.receipt))
        self.assertEqual(self.client.read_sales_receipt("7/a"), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/salesreceipt/7%2Fa"))
        self.assertEqual(request.method, "GET")
        full = {**self.identity, **self.receipt, "CustomerRef": {"value": "2"}, "PaymentRefNum": "x" * 21}
        self.client.full_update_sales_receipt(full)
        self.assertEqual(json.loads(send.call_args.args[0].data), {**full, "sparse": False})
        sparse = {**self.identity, "PrivateNote": "New note"}
        self.client.sparse_update_sales_receipt(sparse)
        self.assertEqual(json.loads(send.call_args.args[0].data), {**sparse, "sparse": True})

    def test_delete_void_pdf_and_email(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'{"SalesReceipt":{"status":"Deleted"}}', b'{"SalesReceipt":{"TotalAmt":0}}',
            b'%PDF-1.4', b'{"SalesReceipt":{}}', b'{"SalesReceipt":{}}',
        )]
        self.client.delete_sales_receipt(self.identity)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), self.identity)
        self.client.void_sales_receipt(self.identity)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query),
                         {"operation": ["update"], "include": ["void"]})
        self.assertEqual(json.loads(request.data), {**self.identity, "sparse": True})
        self.assertEqual(self.client.get_sales_receipt_pdf("7"), b"%PDF-1.4")
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/salesreceipt/7/pdf"))
        self.assertEqual(request.get_header("Accept"), "application/pdf")
        for email in (None, "sandbox+test@example.com"):
            self.client.send_sales_receipt("7", send_to=email)
            request = send.call_args.args[0]
            url = urlsplit(request.full_url)
            self.assertTrue(url.path.endswith("/salesreceipt/7/send"))
            self.assertEqual(parse_qs(url.query), {"sendTo": [email]} if email else {})
            self.assertEqual((request.method, request.data, request.get_header("Content-type")),
                             ("POST", b"", "application/octet-stream"))

    def test_pagination_validation_and_delegation(self, opener):
        too_long = {**self.receipt, "PaymentRefNum": "x" * 22}
        with self.assertRaises(ValidationError) as error:
            self.client.create_sales_receipt(too_long)
        self.assertEqual((error.exception.field, error.exception.limit), ("PaymentRefNum", 21))
        with self.assertRaises(ValidationError):
            self.client.full_update_sales_receipt({**self.identity, **self.receipt})
        with self.assertRaises(ValidationError):
            self.client.void_sales_receipt({"Id": "7"})
        opener.assert_not_called()
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'{"SalesReceipt":{}}', b'{"QueryResponse":{"SalesReceipt":[{"Id":"7"}]}}',
            b'{"QueryResponse":{}}',
        )]
        AccountingClient("token", "123", validate_fields=False).create_sales_receipt(too_long)
        self.assertEqual(json.loads(send.call_args.args[0].data), too_long)
        self.assertEqual(list(self.client.iter_sales_receipts(page_size=1)), [{"Id": "7"}])
        for position, call in enumerate(send.call_args_list[1:], 1):
            self.assertEqual(parse_qs(urlsplit(call.args[0].full_url).query)["query"],
                             [f"SELECT * FROM SalesReceipt STARTPOSITION {position} MAXRESULTS 1"])
