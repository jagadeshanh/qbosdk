import io
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError


class ReimburseChargeTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_read_preserves_amount_and_invoice_link(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        send.side_effect = [
            io.BytesIO(b'{"ReimburseCharge":{"Amount":100.25,"LinkedTxn":[{"TxnId":"1","TxnType":"Invoice"}]}}'),
            io.BytesIO(b'{"ReimburseCharge":[]}'),
        ]
        charge = client.read_reimburse_charge("4/7")["ReimburseCharge"]
        self.assertEqual(charge["Amount"], Decimal("100.25"))
        self.assertEqual(charge["LinkedTxn"], [{"TxnId": "1", "TxnType": "Invoice"}])
        request = send.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertTrue(request.full_url.endswith("/reimbursecharge/4%2F7"))
        with self.assertRaises(AccountingError):
            client.read_reimburse_charge("4")

    @patch("qbosdk.accounting.build_opener")
    def test_filtered_pagination(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        send.side_effect = [
            io.BytesIO(b'{"QueryResponse":{"ReimburseCharge":[{"Id":"4","HasBeenInvoiced":false}]}}'),
            io.BytesIO(b'{"QueryResponse":{}}'),
        ]
        statement = "SELECT * FROM ReimburseCharge WHERE HasBeenInvoiced = false"
        self.assertEqual(list(client.iter_reimburse_charges(statement, page_size=1)),
                         [{"Id": "4", "HasBeenInvoiced": False}])
        for position, call in enumerate(send.call_args_list, 1):
            request = call.args[0]
            self.assertTrue(urlsplit(request.full_url).path.endswith("/query"))
            self.assertEqual(parse_qs(urlsplit(request.full_url).query)["query"],
                             [f"{statement} STARTPOSITION {position} MAXRESULTS 1"])
