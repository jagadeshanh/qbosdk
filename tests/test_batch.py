import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from qbosdk import AccountingClient, AccountingError


class BatchTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_request_and_partial_faults(self, opener):
        response = {"BatchItemResponse": [{"bId": "a", "QueryResponse": {}}, {"bId": "b", "Fault": {"Error": [{"code": "6240"}]}}]}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(response).encode())
        items = [{"bId": "a", "Query": "SELECT * FROM Account"}, {"bId": "b", "operation": "create", "Account": {"Name": "test"}}]
        self.assertEqual(AccountingClient("token", "123").batch(items), response)
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/v3/company/123/batch"))
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data), {"BatchItemRequest": items})
        self.assertEqual(request.get_header("Authorization"), "Bearer token")

    @patch("qbosdk.accounting.build_opener")
    def test_invalid_batch_never_sent(self, opener):
        client = AccountingClient("token", "123")
        for items in ([], [{}], [{"bId": "x"}] * 31, [{"bId": "x"}, {"bId": "x"}], [{"bId": []}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                client.batch(items)
        opener.assert_not_called()

    @patch("qbosdk.accounting.build_opener")
    def test_malformed_response_and_no_retry(self, opener):
        client = AccountingClient("token", "123")
        opener.return_value.open.return_value = io.BytesIO(b'{"BatchItemResponse":{}}')
        with self.assertRaises(AccountingError):
            client.batch([{"bId": "a", "Query": "SELECT * FROM Account"}])
        opener.return_value.open.side_effect = HTTPError("url", 429, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"throttle"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.batch([{"bId": "a", "Query": "SELECT * FROM Account"}])
        self.assertEqual(caught.exception.status, 429)
        self.assertEqual(opener.return_value.open.call_count, 2)
