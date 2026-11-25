import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CompanyCurrencyTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_and_full_update(self, opener):
        response = {"CompanyCurrency": {"Id": "7", "SyncToken": "0", "Code": "GBP", "Active": True}}
        opener.return_value.open.side_effect = lambda *args, **kwargs: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_company_currency({"Code": "GBP"}), response)
        self.client.read_company_currency("7/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/companycurrency/7%2F2"))
        self.client.full_update_company_currency({**response["CompanyCurrency"], "Active": False})
        body = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertEqual((body["Active"], body["sparse"]), (False, False))

    @patch("qbosdk.accounting.build_opener")
    def test_pagination_and_fault(self, opener):
        pages = [b'{"QueryResponse":{"CompanyCurrency":[{"Id":"7"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *args, **kwargs: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_company_currencies(page_size=1)), [{"Id": "7"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.full_update_company_currency({"Code": "GBP", "Id": "7", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_delegation(self, opener):
        for body in ({"Code": "GB"}, {"Code": "GBP", "Active": "false"}):
            with self.subTest(body=body), self.assertRaises(ValidationError):
                self.client.create_company_currency(body)
        with self.assertRaises(ValidationError):
            self.client.full_update_company_currency({"Code": "GBP", "Id": "7"})
        opener.return_value.open.return_value = io.BytesIO(b'{"CompanyCurrency":{"Code":"GB"}}')
        AccountingClient("token", "123", validate_fields=False).create_company_currency({"Code": "GB"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data)["Code"], "GB")
