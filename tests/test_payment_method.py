import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class PaymentMethodTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    def test_create_read_and_full_update(self, opener):
        request = opener.return_value.open
        request.side_effect = lambda *args, **kwargs: io.BytesIO(
            b'{"PaymentMethod":{"Id":"8","SyncToken":"1"},"time":"sample"}'
        )
        method = {"Name": "x" * 31, "Type": "CREDIT_CARD"}
        result = self.client.create_payment_method(method)
        sent = request.call_args.args[0]
        self.assertTrue(sent.full_url.endswith("/paymentmethod"))
        self.assertEqual((sent.method, json.loads(sent.data)), ("POST", method))
        self.assertEqual(self.client.read_payment_method("8/1"), result)
        sent = request.call_args.args[0]
        self.assertTrue(sent.full_url.endswith("/paymentmethod/8%2F1"))
        self.assertEqual(sent.method, "GET")
        update = {**method, **result["PaymentMethod"], "Active": False}
        self.client.full_update_payment_method(update)
        self.assertEqual(json.loads(request.call_args.args[0].data), {**update, "sparse": False})
        self.assertNotIn("sparse", update)

    def test_query_and_pagination(self, opener):
        request = opener.return_value.open
        request.side_effect = [io.BytesIO(data) for data in (
            b'{"QueryResponse":{"PaymentMethod":[{"Id":"1"}]}}',
            b'{"QueryResponse":{"PaymentMethod":[{"Id":"2"}]}}',
            b'{"QueryResponse":{}}',
        )]
        self.assertEqual(list(self.client.iter_payment_methods(page_size=1)),
                         [{"Id": "1"}, {"Id": "2"}])
        for position, call in enumerate(request.call_args_list, 1):
            sent = call.args[0]
            self.assertEqual(sent.method, "GET")
            self.assertTrue(urlsplit(sent.full_url).path.endswith("/query"))
            self.assertEqual(parse_qs(urlsplit(sent.full_url).query)["query"],
                             [f"SELECT * FROM PaymentMethod STARTPOSITION {position} MAXRESULTS 1"])

    def test_validation_delegation_and_response_shape(self, opener):
        for payload, field in (
            ({}, "Name"), ({"Name": "x" * 32}, "Name"),
            ({"Name": "check", "Type": "UNKNOWN"}, "Type"),
            ({"Name": "check", "Active": "false"}, "Active"),
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_payment_method(payload)
            self.assertEqual(error.exception.field, field)
        with self.assertRaises(ValidationError) as error:
            self.client.create_payment_method({"Name": "x" * 32})
        self.assertEqual((error.exception.code, error.exception.limit, error.exception.actual),
                         ("max_length", 31, 32))
        with self.assertRaises(ValidationError):
            self.client.full_update_payment_method({"Name": "check", "Id": "8"})
        opener.assert_not_called()

        request = opener.return_value.open
        request.return_value = io.BytesIO(b'{"PaymentMethod":[]}')
        delegated = {"Name": "x" * 32, "Type": "UNKNOWN"}
        with self.assertRaises(AccountingError):
            AccountingClient("token", "123", validate_fields=False).create_payment_method(delegated)
        self.assertEqual(json.loads(request.call_args.args[0].data), delegated)
