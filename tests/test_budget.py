import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from qbosdk import AccountingClient, AccountingError, ValidationError


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.budget = {"StartDate": "2024-01-01", "EndDate": "2024-12-31", "BudgetDetail": [{"Amount": Decimal("12.345"), "AccountRef": {"value": "5"}}]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_and_delete(self, opener):
        payloads = [b'{"Budget":{"Id":"1","SyncToken":"0","BudgetDetail":[{"Amount":12.345}]}}', b'{"Budget":{"Id":"1","SyncToken":"0"}}', b'{"Budget":{"Id":"1","SyncToken":"1"}}', b'{"time":"2021-08-05T15:17:32-07:00"}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(payloads.pop(0))
        self.assertEqual(self.client.create_budget(self.budget)["Budget"]["BudgetDetail"][0]["Amount"], Decimal("12.345"))
        self.assertIn(b'12.345', opener.return_value.open.call_args.args[0].data)
        self.client.read_budget("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/budget/1%2F2"))
        self.client.full_update_budget({**self.budget, "Id": "1", "SyncToken": "0"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.assertIn("time", self.client.delete_budget({"Id": "1", "SyncToken": "1"}))
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_query_and_validation(self, opener):
        pages = [b'{"QueryResponse":{"Budget":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_budgets(page_size=1)), [{"Id": "1"}])
        with self.assertRaises(ValidationError):
            self.client.create_budget({"StartDate": "2024-01-01"})
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_budget({"Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
