import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CreditCardPaymentTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.payment = {"TxnDate": "2020-03-27", "Amount": "100", "BankAccountRef": {"value": 37}, "CreditCardAccountRef": {"value": 57}}

    @patch("qbosdk.accounting.build_opener")
    def test_operations_and_full_delete_payload(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"CreditCardPaymentTxn":{"Id":"29","SyncToken":"0"}}')
        self.client.create_credit_card_payment(self.payment)
        self.client.read_credit_card_payment("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/creditcardpayment/1%2F2"))
        record = {**self.payment, "Id": "29", "SyncToken": "0", "PrivateNote": "memo"}
        self.client.full_update_credit_card_payment(record)
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.sparse_update_credit_card_payment({"Id": "29", "SyncToken": "1", "PrivateNote": "changed"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data), {"Id": "29", "SyncToken": "1", "PrivateNote": "changed", "sparse": True})
        self.client.delete_credit_card_payment(record)
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(json.loads(request.data), record)
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_pagination_and_validation(self, opener):
        pages = [b'{"QueryResponse":{"CreditCardPaymentTxn":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_credit_card_payments(page_size=1)), [{"Id": "1"}])
        for value in ({**self.payment, "Amount": "NaN"}, {**self.payment, "PrivateNote": "x" * 4001}, {**self.payment, "BankAccountRef": {}}, {**self.payment, "TxnDate": ""}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_credit_card_payment(value)
        with self.assertRaises(ValidationError):
            self.client.delete_credit_card_payment({"Id": "1", "SyncToken": "0"})
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.sparse_update_credit_card_payment({"Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_unexpected_query_key_does_not_hide_results(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"QueryResponse":{"CreditCardPayment":[{"Id":"1"}]}}')
        with self.assertRaisesRegex(AccountingError, "unexpected"):
            list(self.client.iter_credit_card_payments())
