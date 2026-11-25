import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class RecurringTransactionTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    def test_create_read_and_delete_wrapped_template(self, opener):
        value = {"Invoice": {"CustomerRef": {"value": "2"}, "Line": [{"Amount": 5}],
                             "RecurringInfo": {"Name": "Reusable invoice", "Active": False}}}
        response = {"RecurringTransaction": {"Invoice": {"Id": "9", "SyncToken": "2"}}}
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_recurring_transaction(value), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/recurringtransaction"))
        self.assertEqual((request.method, json.loads(request.data)), ("POST", value))
        self.assertEqual(self.client.read_recurring_transaction("9/a"), response)
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/recurringtransaction/9%2Fa"))
        self.assertEqual(request.method, "GET")
        self.client.delete_recurring_transaction({"Invoice": {**value["Invoice"], "Id": "9", "SyncToken": "2"}})
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), response["RecurringTransaction"])

    def test_query_preserves_wrappers_and_paginates(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'{"QueryResponse":{"RecurringTransaction":[{"Bill":{"Id":"2"}}]}}',
            b'{"QueryResponse":{"RecurringTransaction":[{"Invoice":{"Id":"9"}}]}}',
            b'{"QueryResponse":{}}',
        )]
        self.assertEqual(list(self.client.iter_recurring_transactions(page_size=1)),
                         [{"Bill": {"Id": "2"}}, {"Invoice": {"Id": "9"}}])
        for position, call in enumerate(send.call_args_list, 1):
            request = call.args[0]
            self.assertEqual(parse_qs(urlsplit(request.full_url).query)["query"],
                             [f"SELECT * FROM RecurringTransaction STARTPOSITION {position} MAXRESULTS 1"])

    def test_validation_and_fault_preservation(self, opener):
        for payload in ({}, {"Invoice": {}, "Bill": {}}, {"Account": {}}, {"Invoice": []}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.client.create_recurring_transaction(payload)
        with self.assertRaises(ValidationError) as error:
            self.client.create_recurring_transaction({"Invoice": {}})
        self.assertEqual(error.exception.field, "Invoice.RecurringInfo")
        with self.assertRaises(ValidationError):
            self.client.delete_recurring_transaction({"Invoice": {"Id": "9"}})
        opener.assert_not_called()

        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "sample"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as error:
            self.client.delete_recurring_transaction({"Invoice": {"Id": "9", "SyncToken": "1"}})
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "sample", "5010"))
        self.assertEqual(send.call_count, 1)
