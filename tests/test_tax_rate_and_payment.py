import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError


class TaxRateAndPaymentTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_reads_preserve_wire_types_and_encode_ids(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        cases = (
            (client.read_tax_rate, "TaxRate", '{"RateValue":2.25}', {"RateValue": Decimal("2.25")}),
            (client.read_tax_payment, "TaxPayment", '{"PaymentAmount":"10.00","Refund":"false"}',
             {"PaymentAmount": "10.00", "Refund": "false"}),
        )
        for method, entity, data, expected in cases:
            with self.subTest(entity=entity):
                send.return_value = io.BytesIO(('{"' + entity + '":' + data + '}').encode())
                self.assertEqual(method("8/1")[entity], expected)
                request = send.call_args.args[0]
                self.assertTrue(request.full_url.endswith(f"/{entity.lower()}/8%2F1"))
                self.assertEqual(request.method, "GET")
                send.return_value = io.BytesIO(b'{}')
                with self.assertRaises(AccountingError):
                    method("8")

    @patch("qbosdk.accounting.build_opener")
    def test_query_paginates_both_entities(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        for method, entity in ((client.iter_tax_rates, "TaxRate"),
                               (client.iter_tax_payments, "TaxPayment")):
            with self.subTest(entity=entity):
                send.reset_mock()
                send.side_effect = [
                    io.BytesIO(json.dumps({"QueryResponse": {entity: [{"Id": "1"}]}}).encode()),
                    io.BytesIO(b'{"QueryResponse":{}}'),
                ]
                self.assertEqual(list(method(page_size=1)), [{"Id": "1"}])
                for position, call in enumerate(send.call_args_list, 1):
                    request = call.args[0]
                    url = urlsplit(request.full_url)
                    self.assertTrue(url.path.endswith("/query"))
                    self.assertEqual(parse_qs(url.query)["query"],
                                     [f"SELECT * FROM {entity} STARTPOSITION {position} MAXRESULTS 1"])
