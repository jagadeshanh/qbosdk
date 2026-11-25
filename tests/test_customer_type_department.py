import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class CustomerTypeDepartmentTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_customer_type_read_and_pages(self, opener):
        pages = [b'{"CustomerType":{"Id":"1","Name":"Retail"}}', b'{"QueryResponse":{"CustomerType":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(self.client.read_customer_type("1/2")["CustomerType"]["Name"], "Retail")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/customertype/1%2F2"))
        self.assertEqual(list(self.client.iter_customer_types(page_size=1)), [{"Id": "1"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])

    @patch("qbosdk.accounting.build_opener")
    def test_department_create_read_update_and_query(self, opener):
        response = {"Department": {"Id": "2", "SyncToken": "0", "Name": "Support", "Active": True}}
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(json.dumps(response).encode())
        self.assertEqual(self.client.create_department({"Name": "Support"}), response)
        self.client.read_department("2/3")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/department/2%2F3"))
        self.client.full_update_department({**response["Department"], "Active": False})
        self.assertEqual(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"], False)
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"QueryResponse":{"Department":[{"Id":"2"}]}}')
        self.assertEqual(self.client.query_departments(max_results=1)["QueryResponse"]["Department"][0]["Id"], "2")

    @patch("qbosdk.accounting.build_opener")
    def test_department_validation_and_server_fault(self, opener):
        for value in ({"Name": "x" * 101}, {"Name": "x", "ParentRef": {}}, {"Name": "x", "SubDepartment": True}, {"Name": "x", "Active": "yes"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.create_department(value)
        with self.assertRaises(ValidationError):
            self.client.full_update_department({"Name": "x", "Id": "2"})
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.full_update_department({"Name": "x", "Id": "2", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_department_field_validation_delegation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Department":{}}')
        AccountingClient("token", "123", validate_fields=False).create_department({"Name": "x" * 101})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["Name"]), 101)
