import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class TaxCodeTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.rate = {"TaxRateName": "SampleRate", "TaxAgencyId": "1", "RateValue": "8",
                     "TaxApplicableOn": "Sales"}

    def test_create_with_existing_and_new_rates_uses_taxservice(self, opener):
        send = opener.return_value.open
        payload = {"TaxCode": "x" * 100, "TaxRateDetails": [
            self.rate, {"TaxRateId": "2", "TaxApplicableOn": "Purchase"},
        ]}
        result = {**payload, "TaxCodeId": "4", "TaxRateDetails": [
            {**self.rate, "TaxRateId": "3", "RateValue": "8%"}, {"TaxRateId": "2"},
        ]}
        send.side_effect = lambda *args, **kwargs: io.BytesIO(json.dumps(result).encode())
        for create in (self.client.create_tax_code, self.client.create_tax_service):
            self.assertEqual(create(payload), result)
            request = send.call_args.args[0]
            self.assertTrue(request.full_url.endswith("/taxservice/taxcode"))
            self.assertEqual((request.method, json.loads(request.data)), ("POST", payload))

    def test_read_and_paginate(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'{"TaxCode":{"Id":"4","TaxGroup":true}}',
            b'{"QueryResponse":{"TaxCode":[{"Id":"4"}]}}', b'{"QueryResponse":{}}',
        )]
        self.assertEqual(self.client.read_tax_code("4/a")["TaxCode"], {"Id": "4", "TaxGroup": True})
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/taxcode/4%2Fa"))
        self.assertEqual(request.method, "GET")
        self.assertEqual(list(self.client.iter_tax_codes(page_size=1)), [{"Id": "4"}])
        for position, call in enumerate(send.call_args_list[1:], 1):
            self.assertEqual(parse_qs(urlsplit(call.args[0].full_url).query)["query"],
                             [f"SELECT * FROM TaxCode STARTPOSITION {position} MAXRESULTS 1"])

    def test_validation_delegation_and_fault(self, opener):
        for rates, field in (
            ([], "TaxRateDetails"),
            ([{"TaxRateId": "2"}, {"TaxRateId": "2"}], "TaxRateDetails[1].TaxRateId"),
            ([{"TaxRateId": "2", "RateValue": "8"}], "TaxRateDetails[0]"),
            ([{**self.rate, "RateValue": "101"}], "TaxRateDetails[0].RateValue"),
            ([{**self.rate, "RateValue": "nan"}], "TaxRateDetails[0].RateValue"),
            ([{**self.rate, "TaxRateName": "x" * 11}], "TaxRateDetails[0].TaxRateName"),
            ([{**self.rate, "TaxApplicableOn": "Other"}], "TaxRateDetails[0].TaxApplicableOn"),
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_tax_code({"TaxCode": "Sample", "TaxRateDetails": rates})
            self.assertEqual(error.exception.field, field)
        with self.assertRaises(ValidationError) as error:
            self.client.create_tax_code({"TaxCode": "x" * 101, "TaxRateDetails": [self.rate]})
        self.assertEqual((error.exception.field, error.exception.limit), ("TaxCode", 100))
        opener.assert_not_called()

        payload = {"TaxCode": "Sample", "TaxRateDetails": [{**self.rate, "RateValue": "101"}]}
        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "sample"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"2050"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).create_tax_service(payload)
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "sample", "2050"))
        self.assertEqual(json.loads(send.call_args.args[0].data), payload)
        self.assertEqual(send.call_count, 1)
