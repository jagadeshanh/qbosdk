import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CreditMemoTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.memo = {"CustomerRef": {"value": "1"}, "Line": [{"DetailType": "SalesItemLineDetail", "Amount": Decimal("12.34"), "SalesItemLineDetail": {"ItemRef": {"value": "2"}}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_delete_and_send(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"CreditMemo":{"Id":"7","SyncToken":"0"}}')
        self.assertEqual(self.client.create_credit_memo(self.memo)["CreditMemo"]["Id"], "7")
        self.assertIn(b'12.34', opener.return_value.open.call_args.args[0].data)
        self.client.read_credit_memo("7/8")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/creditmemo/7%2F8"))
        self.client.full_update_credit_memo({**self.memo, "Id": "7", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.delete_credit_memo({"Id": "7", "SyncToken": "1"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})
        self.client.send_credit_memo("7", send_to="user+tag@example.com")
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"sendTo": ["user+tag@example.com"]})
        self.assertEqual((request.method, request.data, request.get_header("Content-type")), ("POST", b"", "application/octet-stream"))

    @patch("qbosdk.accounting.build_opener")
    def test_pdf_query_and_pagination(self, opener):
        pages = [b'%PDF-1.4\ntest', b'{"QueryResponse":{"CreditMemo":[{"Id":"7"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(self.client.get_credit_memo_pdf("7"), b'%PDF-1.4\ntest')
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith('/creditmemo/7/pdf'))
        self.assertEqual(request.get_header('Accept'), 'application/pdf')
        self.assertEqual(list(self.client.iter_credit_memos(page_size=1)), [{"Id": "7"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_intuit_faults(self, opener):
        for value in ({"Line": [{}]}, {"CustomerRef": {"value": "1"}, "Line": []}, {**self.memo, "DocNumber": "x" * 22}, {**self.memo, "PrivateNote": "x" * 4001}, {**self.memo, "Line": [{"DetailType": "DescriptionOnly"}]}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_credit_memo(value)
        with self.assertRaises(ValidationError):
            self.client.full_update_credit_memo({**self.memo, "Id": "7"})
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "trace"}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.get_credit_memo_pdf("7")
        self.assertEqual((caught.exception.status, caught.exception.fault["Error"][0]["code"], caught.exception.intuit_tid), (400, "5010", "trace"))
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_field_validation_can_be_delegated(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"CreditMemo":{}}')
        AccountingClient("token", "123", validate_fields=False).create_credit_memo({**self.memo, "DocNumber": "x" * 22})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["DocNumber"]), 22)
