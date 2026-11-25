import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class ChangeDataCaptureTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_request_and_deleted_response(self, opener):
        response = {"CDCResponse": [{"QueryResponse": [{"Customer": [{"Id": "1", "status": "Deleted"}]}]}], "time": "2025-01-01T12:00:00Z"}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(response).encode())
        result = AccountingClient("token", "123", "production").change_data_capture(["Customer", "Estimate"], "2025-01-01T09:00:00-07:00")
        request = opener.return_value.open.call_args.args[0]
        url = urlsplit(request.full_url)
        self.assertEqual((url.netloc, url.path), ("quickbooks.api.intuit.com", "/v3/company/123/cdc"))
        self.assertEqual(parse_qs(url.query), {"entities": ["Customer,Estimate"], "changedSince": ["2025-01-01T09:00:00-07:00"]})
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertEqual(result, response)

    @patch("qbosdk.accounting.build_opener")
    def test_empty_result_and_local_validation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"CDCResponse":[{"QueryResponse":[{}]}]}')
        client = AccountingClient("token", "123")
        self.assertEqual(client.change_data_capture(["Account"], "2025-01-01")["CDCResponse"][0]["QueryResponse"], [{}])
        for entities, since in (([], "2025-01-01"), (["Account,Invoice"], "2025-01-01"), (["Account"], "2025-02-30")):
            with self.subTest(entities=entities, since=since), self.assertRaises((ValueError, ValidationError)):
                client.change_data_capture(entities, since)
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_fault_and_malformed_response(self, opener):
        client = AccountingClient("token", "123", validate_fields=False)
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.change_data_capture(["Account"], "bad")
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
        opener.return_value.open.side_effect = None
        opener.return_value.open.return_value = io.BytesIO(b'{"CDCResponse":{}}')
        with self.assertRaises(AccountingError):
            client.change_data_capture(["Account"], "bad")
