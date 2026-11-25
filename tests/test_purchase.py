import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class PurchaseTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.purchase = {
            "PaymentType": "Check", "AccountRef": {"value": "1"},
            "Line": [{"Amount": Decimal("12.34"), "DetailType": "AccountBasedExpenseLineDetail",
                      "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "2"}}}],
        }

    def test_create_read_full_update_and_delete(self, opener):
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(b'{"Purchase":{"Id":"7","SyncToken":"3"}}')
        identity = self.client.create_purchase(self.purchase)["Purchase"]
        request = send.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertTrue(request.full_url.endswith("/purchase"))
        self.assertIn(b"12.34", request.data)
        self.assertEqual(self.client.read_purchase("7/1")["Purchase"], identity)
        request = send.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertTrue(request.full_url.endswith("/purchase/7%2F1"))

        full = {**self.purchase, **identity, "DocNumber": "x" * 21, "PrivateNote": "x" * 4000}
        self.client.full_update_purchase(full, allow_duplicate_doc_number=True)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.assertEqual(json.loads(request.data, parse_float=Decimal), {**full, "sparse": False})
        self.client.delete_purchase(full)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), identity)

    def test_query_and_pagination(self, opener):
        opener.return_value.open.side_effect = [
            io.BytesIO(b'{"QueryResponse":{"Purchase":[{"Id":"7"}]}}'),
            io.BytesIO(b'{"QueryResponse":{}}'),
        ]
        self.assertEqual(list(self.client.iter_purchases(page_size=1)), [{"Id": "7"}])
        for position, call in enumerate(opener.return_value.open.call_args_list, 1):
            request = call.args[0]
            self.assertEqual(request.method, "GET")
            self.assertTrue(urlsplit(request.full_url).path.endswith("/query"))
            self.assertEqual(parse_qs(urlsplit(request.full_url).query)["query"],
                             [f"SELECT * FROM Purchase STARTPOSITION {position} MAXRESULTS 1"])

    def test_validation_delegation_and_duplicate_fault(self, opener):
        for changes, field in (
            ({"PaymentType": "DebitCard"}, "PaymentType"),
            ({"AccountRef": {}}, "AccountRef.value"),
            ({"Line": []}, "Line"),
            ({"DocNumber": "x" * 22}, "DocNumber"),
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_purchase({**self.purchase, **changes})
            self.assertEqual(error.exception.field, field)
        with self.assertRaises(ValidationError):
            self.client.full_update_purchase({**self.purchase, "Id": "7"})
        opener.assert_not_called()

        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "sample"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"6140"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).create_purchase(
                {**self.purchase, "DocNumber": "x" * 22}
            )
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "sample", "6140"))
        self.assertEqual(send.call_count, 1)
