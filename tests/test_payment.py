import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class PaymentTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.payment = {"CustomerRef": {"value": "5"}, "TotalAmt": Decimal("12.34")}
        self.identity = {"Id": "7", "SyncToken": "0"}

    def test_create_and_updates_preserve_payment_lines(self, opener):
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(
            b'{"Payment":{"Id":"7","UnappliedAmt":12.34},"time":"sample"}'
        )
        response = self.client.create_payment(self.payment)
        self.assertEqual(response["Payment"]["UnappliedAmt"], Decimal("12.34"))
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/payment"))
        self.assertEqual(request.method, "POST")
        self.assertNotIn("Line", json.loads(request.data))
        self.assertIn(b"12.34", request.data)

        lines = [{"Amount": 10, "LinkedTxn": [{"TxnId": "9", "TxnType": "Invoice"}]},
                 {"Amount": 2.34, "LinkedTxn": [{"TxnId": "10", "TxnType": "CreditMemo"}]}]
        self.client.full_update_payment({**self.payment, **self.identity, "Line": lines})
        self.assertEqual(json.loads(send.call_args.args[0].data),
                         {**self.payment, **self.identity, "TotalAmt": 12.34, "Line": lines, "sparse": False})
        self.client.sparse_update_payment({**self.identity, "PrivateNote": "x" * 4000})
        self.assertNotIn("Line", json.loads(send.call_args.args[0].data))
        self.client.sparse_update_payment({**self.identity, "Line": []})
        self.assertEqual(json.loads(send.call_args.args[0].data),
                         {**self.identity, "Line": [], "sparse": True})

    def test_read_delete_void_and_send_routes(self, opener):
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(b'{"Payment":{"Id":"7"}}')
        self.assertEqual(self.client.read_payment("7/8")["Payment"]["Id"], "7")
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/payment/7%2F8"))
        self.assertEqual(request.method, "GET")
        self.client.delete_payment({**self.identity, **self.payment})
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), self.identity)
        self.client.void_payment(self.identity)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query),
                         {"operation": ["update"], "include": ["void"]})
        self.assertEqual(json.loads(request.data), {**self.identity, "sparse": True})
        self.client.send_payment("7", send_to="user+test@example.com")
        request = send.call_args.args[0]
        self.assertTrue(urlsplit(request.full_url).path.endswith("/payment/7/send"))
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"sendTo": ["user+test@example.com"]})
        self.assertEqual((request.method, request.data, request.get_header("Content-type")),
                         ("POST", b"", "application/octet-stream"))

    def test_pdf_query_and_pagination(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'%PDF-1.4', b'{"QueryResponse":{"Payment":[{"Id":"7"}]}}', b'{"QueryResponse":{}}'
        )]
        self.assertEqual(self.client.get_payment_pdf("7"), b"%PDF-1.4")
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/payment/7/pdf"))
        self.assertEqual(request.get_header("Accept"), "application/pdf")
        self.assertEqual(list(self.client.iter_payments(page_size=1)), [{"Id": "7"}])
        for position, call in enumerate(send.call_args_list[1:], 1):
            statement = parse_qs(urlsplit(call.args[0].full_url).query)["query"][0]
            self.assertEqual(statement, f"SELECT * FROM Payment STARTPOSITION {position} MAXRESULTS 1")

    def test_validation_delegation_and_stale_fault(self, opener):
        for payment, field in (
            ({}, "TotalAmt"), ({**self.payment, "TotalAmt": True}, "TotalAmt"),
            ({**self.payment, "CustomerRef": {}}, "CustomerRef.value"),
            ({**self.payment, "Line": [None]}, "Line"),
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_payment(payment)
            self.assertEqual(error.exception.field, field)
        overlong = {**self.payment, "PrivateNote": "x" * 4001}
        with self.assertRaises(ValidationError) as error:
            self.client.create_payment(overlong)
        self.assertEqual((error.exception.field, error.exception.limit, error.exception.actual),
                         ("PrivateNote", 4000, 4001))
        with self.assertRaises(ValidationError):
            self.client.full_update_payment({**self.payment, **self.identity, "sparse": True})
        with self.assertRaises(ValidationError):
            self.client.void_payment({"Id": "7"})
        with self.assertRaises(ValueError):
            self.client.send_payment("7", send_to="")
        opener.assert_not_called()

        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "example"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).create_payment(overlong)
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "example", "5010"))
        self.assertEqual(send.call_count, 1)
        self.assertEqual(len(json.loads(send.call_args.args[0].data)["PrivateNote"]), 4001)
