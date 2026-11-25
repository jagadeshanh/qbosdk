import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class PreferencesTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    def test_read_and_full_update_preserve_grouped_preferences(self, opener):
        values = {"Id": "1", "SyncToken": "2", "SalesFormsPrefs": {"AllowEstimates": True},
                  "ProductAndServicesPrefs": {"ForPurchase": True}}
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(json.dumps({"Preferences": values}).encode())
        self.assertEqual(self.client.read_preferences()["Preferences"], values)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/preferences"))
        self.assertEqual(request.method, "GET")
        self.assertEqual(self.client.full_update_preferences(values)["Preferences"], values)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/preferences"))
        self.assertEqual(request.method, "POST")
        self.assertEqual(json.loads(request.data), {**values, "sparse": False})
        self.assertNotIn("sparse", values)

    def test_query_with_metadata_filter_omits_pagination(self, opener):
        send = opener.return_value.open
        send.return_value = io.BytesIO(b'{"QueryResponse":{"Preferences":[{"Id":"1"}]}}')
        statement = "SELECT * FROM Preferences WHERE MetaData.LastUpdatedTime > '2025-01-01'"
        self.assertEqual(self.client.query_preferences(statement)["QueryResponse"]["Preferences"], [{"Id": "1"}])
        request = send.call_args.args[0]
        self.assertTrue(urlsplit(request.full_url).path.endswith("/query"))
        self.assertEqual(request.method, "GET")
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"query": [statement]})

    def test_rejects_pagination_and_invalid_update_identity(self, opener):
        for statement in ("SELECT * FROM Preferences MAXRESULTS 1", "SELECT * FROM Account"):
            with self.subTest(statement=statement), self.assertRaises(ValueError):
                self.client.query_preferences(statement)
        with self.assertRaises(ValidationError):
            self.client.full_update_preferences({"Id": "1"})
        with self.assertRaises(ValidationError):
            self.client.full_update_preferences({"Id": "1", "SyncToken": "2", "sparse": True})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"QueryResponse":[]}')
        with self.assertRaises(AccountingError):
            self.client.query_preferences()
