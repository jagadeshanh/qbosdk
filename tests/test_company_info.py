import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class CompanyInfoTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123", "production")

    @patch("qbosdk.accounting.build_opener")
    def test_read_and_update_modes(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"CompanyInfo":{"Id":"123","SyncToken":"1","CompanyName":"Example","CompanyAddr":{"City":"Test"}}}')
        self.assertEqual(self.client.read_company_info()["CompanyInfo"]["Id"], "123")
        self.assertEqual(urlsplit(opener.return_value.open.call_args.args[0].full_url).path, "/v3/company/123/companyinfo/123")
        self.client.sparse_update_company_info({"Id": "123", "SyncToken": "1", "LegalName": "New"})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data), {"Id": "123", "SyncToken": "1", "LegalName": "New", "sparse": True})
        self.client.full_update_company_info({"Id": "123", "SyncToken": "1", "CompanyName": "Example", "CompanyAddr": {"City": "Test"}})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])

    @patch("qbosdk.accounting.build_opener")
    def test_query_and_invalid_inputs(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"QueryResponse":{"CompanyInfo":[{"Id":"123"}]}}')
        self.assertEqual(self.client.query_company_info()["QueryResponse"]["CompanyInfo"][0]["Id"], "123")
        self.assertIn("SELECT * FROM CompanyInfo", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        for payload, sparse in [({"Id": "", "SyncToken": "0"}, True), ({"Id": "123", "SyncToken": "0", "CompanyName": "x" * 1025}, True), ({"Id": "123", "SyncToken": "0"}, False), ({"Id": "123", "SyncToken": "0", "sparse": False}, True)]:
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                (self.client.sparse_update_company_info if sparse else self.client.full_update_company_info)(payload)
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_upstream_fault_and_no_retry(self, opener):
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.sparse_update_company_info({"Id": "123", "SyncToken": "0", "LegalName": "New"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)
