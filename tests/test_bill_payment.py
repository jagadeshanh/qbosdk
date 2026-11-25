import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class BillPaymentTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.payment = {"VendorRef": {"value": "56"}, "TotalAmt": Decimal("200.00001"), "PayType": "Check", "Line": [{"Amount": Decimal("200.00001"), "LinkedTxn": [{"TxnId": "234", "TxnType": "Bill"}]}], "CheckPayment": {"BankAccountRef": {"value": "35"}}}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_void_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"BillPayment":{"Id":"42","SyncToken":"0","TotalAmt":200.01}}')
        self.assertEqual(self.client.create_bill_payment(self.payment, allow_duplicate_doc_number=True)["BillPayment"]["TotalAmt"], Decimal("200.01"))
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(req.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.assertIn(b'200.00001', req.data)
        self.client.read_bill_payment("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/billpayment/1%2F2"))
        self.client.full_update_bill_payment({**self.payment, "Id": "42", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.void_bill_payment({"Id": "42", "SyncToken": "1", "PrivateNote": "do not copy"})
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(req.full_url).query), {"operation": ["update"], "include": ["void"]})
        self.assertEqual(json.loads(req.data), {"Id": "42", "SyncToken": "1", "sparse": True})
        self.client.delete_bill_payment({"Id": "42", "SyncToken": "2"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_query_and_empty_page(self, opener):
        pages = [b'{"QueryResponse":{"BillPayment":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_bill_payments(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])

    @patch("qbosdk.accounting.build_opener")
    def test_validation_fault_and_server_mode(self, opener):
        invalid = [{**self.payment, "TotalAmt": -1}, {**self.payment, "TotalAmt": True}, {**self.payment, "PayType": "Unknown"}, {**self.payment, "CheckPayment": None}]
        for body in invalid:
            with self.subTest(body=body), self.assertRaises(ValidationError):
                self.client.create_bill_payment(body)
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.void_bill_payment({"Id": "42", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)
