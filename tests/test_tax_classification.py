import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class TaxClassificationTests(unittest.TestCase):
    def test_read_routes_and_envelopes(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        value = {"id": "T1", "name": "Sample", "ParentRef": {"value": "P"},
                 "applicableTo": ["Inventory"], "level": "2"}
        read = {"TaxClassification": value, "time": "sample"}
        collection = {"QueryResponse": {"TaxClassification": [value]}}
        cases = (
            (lambda: client.read_tax_classification("T/1"), "/taxclassification/T%2F1", {}, read),
            (lambda: client.read_tax_classification_children("P/1"), "/taxclassification/P%2F1/children", {}, collection),
            (client.read_all_tax_classifications, "/taxclassification", {}, collection),
            (lambda: client.read_tax_classifications_by_level(2), "/taxclassification", {"level": ["2"]}, collection),
            (lambda: client.read_tax_classifications_by_level("1"), "/taxclassification", {"level": ["1"]}, collection),
        )
        for method, suffix, query, response in cases:
            with self.subTest(suffix=suffix, query=query):
                send.return_value = io.BytesIO(json.dumps(response).encode())
                self.assertEqual(method(), response)
                request = send.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual(url.path, "/v3/company/123" + suffix)
                self.assertEqual((request.method, request.data, parse_qs(url.query)), ("GET", None, query))

    def test_validation_delegation_and_malformed_envelope(self, opener):
        client = AccountingClient("token", "123")
        for level in (True, 3, "", None):
            with self.subTest(level=level), self.assertRaises(ValidationError) as error:
                client.read_tax_classifications_by_level(level)
            self.assertEqual(error.exception.field, "level")
        with self.assertRaises(ValueError):
            client.read_tax_classification_children("..")
        opener.assert_not_called()
        send = opener.return_value.open
        send.return_value = io.BytesIO(b'{"QueryResponse":{"TaxClassification":[]}}')
        result = AccountingClient("token", "123", validate_fields=False).read_tax_classifications_by_level(3)
        self.assertEqual(result["QueryResponse"]["TaxClassification"], [])
        self.assertEqual(parse_qs(urlsplit(send.call_args.args[0].full_url).query), {"level": ["3"]})
        send.return_value = io.BytesIO(b'{"TaxClassification":[]}')
        with self.assertRaises(AccountingError):
            client.read_tax_classification("T1")
