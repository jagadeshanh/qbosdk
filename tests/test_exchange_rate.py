import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class ExchangeRateTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.rate = {"SyncToken": "0", "SourceCurrencyCode": "EUR", "TargetCurrencyCode": "USD", "AsOfDate": "2025-01-02", "Rate": Decimal("1.234567890123")}

    @patch("qbosdk.accounting.build_opener")
    def test_get_and_update(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"ExchangeRate":{"Rate":1.234567890123,"SyncToken":"0"}}')
        result = self.client.get_exchange_rate("EUR", as_of_date="2025-01-02")
        self.assertEqual(result["ExchangeRate"]["Rate"], Decimal("1.234567890123"))
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"sourcecurrencycode": ["EUR"], "asofdate": ["2025-01-02"]})
        self.client.update_exchange_rate(self.rate)
        self.assertIn(b'1.234567890123', opener.return_value.open.call_args.args[0].data)

    @patch("qbosdk.accounting.build_opener")
    def test_pages_and_fault(self, opener):
        pages = [b'{"QueryResponse":{"ExchangeRate":[{"SourceCurrencyCode":"EUR"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_exchange_rates(page_size=1)), [{"SourceCurrencyCode": "EUR"}])
        self.assertIn("STARTPOSITION 2", parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0])
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.update_exchange_rate(self.rate)
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_delegation(self, opener):
        for value in ({**self.rate, "SourceCurrencyCode": "EU"}, {**self.rate, "AsOfDate": "2025-02-30"}, {**self.rate, "Rate": Decimal("NaN")}, {**self.rate, "SyncToken": ""}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.client.update_exchange_rate(value)
        opener.assert_not_called()
        opener.return_value.open.return_value = io.BytesIO(b'{"ExchangeRate":{}}')
        AccountingClient("token", "123", validate_fields=False).get_exchange_rate("EU", as_of_date="bad")
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"sourcecurrencycode": ["EU"], "asofdate": ["bad"]})
