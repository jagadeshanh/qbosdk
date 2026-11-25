import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class RemainingEntityTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.identity = {"Id": "9", "SyncToken": "2"}
        self.transfer = {"FromAccountRef": {"value": "1"}, "ToAccountRef": {"value": "2"},
                         "Amount": Decimal("12.340")}
        self.time = {"NameOf": "Employee", "EmployeeRef": {"value": "4"}, "Hours": 3}
        self.credit = {"VendorRef": {"value": "2"}, "Line": [{"Amount": 10}]}

    def test_create_read_and_query_each_entity(self, opener):
        cases = (
            ("TaxAgency", {"DisplayName": "x" * 100}, self.client.create_tax_agency,
             self.client.read_tax_agency, self.client.iter_tax_agencies),
            ("Term", {"Name": "x" * 31, "DueDays": "999"}, self.client.create_term,
             self.client.read_term, self.client.iter_terms),
            ("TimeActivity", self.time, self.client.create_time_activity,
             self.client.read_time_activity, self.client.iter_time_activities),
            ("Transfer", {**self.transfer, "Amount": "12.340"}, self.client.create_transfer,
             self.client.read_transfer, self.client.iter_transfers),
            ("Vendor", {"GivenName": "x" * 100}, self.client.create_vendor,
             self.client.read_vendor, self.client.iter_vendors),
            ("VendorCredit", self.credit, self.client.create_vendor_credit,
             self.client.read_vendor_credit, self.client.iter_vendor_credits),
        )
        send = opener.return_value.open
        for entity, value, create, read, iterate in cases:
            with self.subTest(entity=entity):
                send.reset_mock()
                result = {entity: self.identity, "time": "sample"}
                page = {"QueryResponse": {entity: [self.identity]}}
                send.side_effect = [io.BytesIO(json.dumps(response).encode()) for response in
                                    (result, result, page, {"QueryResponse": {}})]
                self.assertEqual(create(value), result)
                self.assertEqual(read("9/a"), result)
                self.assertEqual(list(iterate(page_size=1)), [self.identity])
                requests = [call.args[0] for call in send.call_args_list]
                path = "/v3/company/123/" + entity.lower()
                self.assertEqual((requests[0].method, urlsplit(requests[0].full_url).path,
                                  json.loads(requests[0].data)), ("POST", path, value))
                self.assertEqual((requests[1].method, urlsplit(requests[1].full_url).path),
                                 ("GET", path + "/9%2Fa"))
                for position, request in enumerate(requests[2:], 1):
                    url = urlsplit(request.full_url)
                    self.assertEqual((request.method, url.path), ("GET", "/v3/company/123/query"))
                    self.assertEqual(parse_qs(url.query),
                                     {"query": [f"SELECT * FROM {entity} STARTPOSITION {position} MAXRESULTS 1"]})

    def test_full_and_sparse_updates(self, opener):
        send = opener.return_value.open
        cases = (
            ("Term", {"Name": "Date driven", "DayOfMonthDue": 31}, self.client.full_update_term, {}, False),
            ("TimeActivity", {**self.time, "Hours": 8760, "Minutes": 0}, self.client.full_update_time_activity, {}, False),
            ("Transfer", self.transfer, self.client.full_update_transfer, {}, False),
            ("Transfer", {"PrivateNote": "New note"}, self.client.sparse_update_transfer, {}, True),
            ("Vendor", {"DisplayName": "Example", "Active": False}, self.client.full_update_vendor, {}, False),
            ("VendorCredit", self.credit, self.client.full_update_vendor_credit, {"allow_duplicate_doc_number": True}, False),
        )
        for entity, value, method, kwargs, sparse in cases:
            with self.subTest(entity=entity, sparse=sparse):
                send.return_value = io.BytesIO(json.dumps({entity: self.identity}).encode())
                payload = {**self.identity, **value}
                self.assertEqual(method(payload, **kwargs)[entity], self.identity)
                request = send.call_args.args[0]
                self.assertEqual((request.method, urlsplit(request.full_url).path),
                                 ("POST", "/v3/company/123/" + entity.lower()))
                self.assertEqual(json.loads(request.data, parse_float=Decimal), {**payload, "sparse": sparse})
                self.assertNotIn("sparse", payload)
                self.assertEqual(parse_qs(urlsplit(request.full_url).query),
                                 {"include": ["allowduplicatedocnum"]} if kwargs else {})

    def test_deletes_use_the_documented_payload(self, opener):
        send = opener.return_value.open
        cases = (
            ("TimeActivity", self.client.delete_time_activity, {**self.identity, **self.time}, self.identity),
            ("VendorCredit", self.client.delete_vendor_credit, {**self.identity, **self.credit}, self.identity),
            ("Transfer", self.client.delete_transfer,
             {**self.identity, **self.transfer, "MetaData": {"CreateTime": "sample"}, "TxnDate": "2025-01-01"},
             None),
        )
        for entity, method, payload, expected in cases:
            with self.subTest(entity=entity):
                send.return_value = io.BytesIO(json.dumps({entity: {"status": "Deleted"}}).encode())
                self.assertEqual(method(payload)[entity]["status"], "Deleted")
                request = send.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual((request.method, url.path, parse_qs(url.query)),
                                 ("POST", "/v3/company/123/" + entity.lower(), {"operation": ["delete"]}))
                self.assertEqual(json.loads(request.data, parse_float=Decimal), expected or payload)

    def test_time_activity_timestamp_format_and_billable_ref(self, opener):
        send = opener.return_value.open
        value = {"NameOf": "Vendor", "VendorRef": {"value": "5"}, "TxnDate": "2025-01-02",
                 "StartTime": "08:00:00-08:00", "EndTime": "09:00:00-08:00",
                 "BillableStatus": "Billable", "CustomerRef": {"value": "6"}, "HourlyRate": 25}
        send.return_value = io.BytesIO(b'{"TimeActivity":{}}')
        self.client.create_time_activity(value)
        self.assertEqual(json.loads(send.call_args.args[0].data), value)

    def test_validation_and_upstream_fault_delegation(self, opener):
        cases = (
            (self.client.create_tax_agency, {"DisplayName": "x" * 101}, "DisplayName"),
            (self.client.create_term, {"Name": "Term"}, "DueDays"),
            (self.client.create_term, {"Name": "Term", "DayOfMonthDue": 32}, "DayOfMonthDue"),
            (self.client.create_time_activity, {**self.time, "Hours": 8760, "Minutes": 1}, "Minutes"),
            (self.client.create_time_activity, {"NameOf": "Vendor", "Hours": 2}, "VendorRef.value"),
            (self.client.create_time_activity, {**self.time, "BillableStatus": "Billable"}, "CustomerRef.value"),
            (self.client.create_transfer, {**self.transfer, "Amount": "NaN"}, "Amount"),
            (self.client.delete_transfer, self.identity, "FromAccountRef.value"),
            (self.client.create_vendor, {"DisplayName": "Vendor:Test"}, "DisplayName"),
            (self.client.create_vendor, {"DisplayName": "Vendor", "TaxIdentifier": "x" * 21}, "TaxIdentifier"),
            (self.client.create_vendor_credit, {**self.credit, "Line": [{}]}, "Line.Amount"),
        )
        for method, payload, field in cases:
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                method(payload)
            self.assertEqual(error.exception.field, field)
        opener.assert_not_called()

        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "sample"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"2050"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).create_tax_agency({"DisplayName": "x" * 101})
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "sample", "2050"))
        self.assertEqual(send.call_count, 1)
