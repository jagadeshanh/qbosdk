import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class EmployeeTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_and_full_update(self, opener):
        response = {"Employee": {"Id": "1", "SyncToken": "0", "GivenName": "Example", "Active": True}}
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_employee({"GivenName": "Example"}), response)
        self.client.read_employee("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/employee/1%2F2"))
        self.client.full_update_employee({**response["Employee"], "Active": False})
        body = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertEqual((body["Active"], body["sparse"]), (False, False))

    @patch("qbosdk.accounting.build_opener")
    def test_query_pages_and_fault(self, opener):
        pages = [b'{"QueryResponse":{"Employee":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_employees(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"6240"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.create_employee({"FamilyName": "Example"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "6240")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_delegation(self, opener):
        for value in ({}, {"GivenName": "x" * 101}, {"GivenName": "Bad:Name"}, {"FamilyName": "Example", "Active": "yes"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_employee(value)
        with self.assertRaises(ValidationError):
            self.client.full_update_employee({"GivenName": "Example", "Id": "1"})
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"Employee":{}}')
        AccountingClient("token", "123", validate_fields=False).create_employee({"GivenName": "x" * 101})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["GivenName"]), 101)
