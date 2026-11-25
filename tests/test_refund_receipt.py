import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class RefundReceiptTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.receipt = {
            "DepositToAccountRef": {"value": "2"}, "PaymentType": "Cash",
            "Line": [{"Amount": 10, "DetailType": "SalesItemLineDetail",
                      "SalesItemLineDetail": {"ItemRef": {"value": "3"}}}],
        }
        self.identity = {"Id": "7", "SyncToken": "1"}

    def test_create_read_full_sparse_and_delete(self, opener):
        send = opener.return_value.open
        response = {"RefundReceipt": self.identity, "time": "sample"}
        send.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_refund_receipt(self.receipt), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/refundreceipt"))
        self.assertEqual((request.method, json.loads(request.data)), ("POST", self.receipt))
        self.assertEqual(self.client.read_refund_receipt("7/a"), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/refundreceipt/7%2Fa"))
        self.assertEqual(request.method, "GET")

        full = {**self.receipt, **self.identity, "PaymentRefNum": "x" * 100}
        self.client.full_update_refund_receipt(full, allow_duplicate_doc_number=True)
        request = send.call_args.args[0]
        self.assertEqual(json.loads(request.data), {**full, "sparse": False})
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowduplicatedocnum"]})

        sparse = {**self.identity, "PrivateNote": "Updated"}
        self.client.sparse_update_refund_receipt(sparse)
        self.assertEqual(json.loads(send.call_args.args[0].data), {**sparse, "sparse": True})
        self.client.delete_refund_receipt(full)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), self.identity)

    def test_query_pagination_pdf_and_email(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(payload) for payload in (
            b'{"QueryResponse":{"RefundReceipt":[{"Id":"7"}]}}',
            b'{"QueryResponse":{}}', b'%PDF-1.4',
            b'{"RefundReceipt":{}}', b'{"RefundReceipt":{}}',
        )]
        self.assertEqual(list(self.client.iter_refund_receipts(page_size=1)), [{"Id": "7"}])
        for position, call in enumerate(send.call_args_list, 1):
            self.assertEqual(parse_qs(urlsplit(call.args[0].full_url).query)["query"],
                             [f"SELECT * FROM RefundReceipt STARTPOSITION {position} MAXRESULTS 1"])
        self.assertEqual(self.client.get_refund_receipt_pdf("7"), b"%PDF-1.4")
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/refundreceipt/7/pdf"))
        self.assertEqual(request.get_header("Accept"), "application/pdf")
        for recipient in (None, "sample+test@example.com"):
            self.client.send_refund_receipt("7", send_to=recipient)
            request = send.call_args.args[0]
            url = urlsplit(request.full_url)
            self.assertTrue(url.path.endswith("/refundreceipt/7/send"))
            self.assertEqual(parse_qs(url.query), {"sendTo": [recipient]} if recipient else {})
            self.assertEqual((request.method, request.data, request.get_header("Content-type")),
                             ("POST", b"", "application/octet-stream"))

    def test_validation_delegation_and_fault(self, opener):
        for payload, field in (({"DepositToAccountRef": {}}, "DepositToAccountRef.value"),
                               ({"Line": [{"DetailType": "DiscountLineDetail"}]}, "Line"),
                               ({"PaymentRefNum": "x" * 101}, "PaymentRefNum"),
                               ({"PaymentType": "Unknown"}, "PaymentType")):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_refund_receipt({**self.receipt, **payload})
            self.assertEqual(error.exception.field, field)
        with self.assertRaises(ValidationError):
            self.client.full_update_refund_receipt({**self.receipt, **self.identity, "sparse": True})
        opener.assert_not_called()

        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "example"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"2050"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).create_refund_receipt(
                {**self.receipt, "PaymentRefNum": "x" * 101}
            )
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "example", "2050"))
        self.assertEqual(send.call_count, 1)
