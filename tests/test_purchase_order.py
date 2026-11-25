import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, ValidationError


@patch("qbosdk.accounting.build_opener")
class PurchaseOrderTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.order = {"VendorRef": {"value": "5"}, "Line": [
            {"Amount": 12, "DetailType": "ItemBasedExpenseLineDetail",
             "ItemBasedExpenseLineDetail": {"ItemRef": {"value": "2"}}},
        ]}
        self.identity = {"Id": "7", "SyncToken": "3"}

    def test_create_read_full_update_and_delete(self, opener):
        send = opener.return_value.open
        send.side_effect = lambda *args, **kwargs: io.BytesIO(
            b'{"PurchaseOrder":{"Id":"7","SyncToken":"3"}}'
        )
        self.assertEqual(self.client.create_purchase_order(self.order)["PurchaseOrder"], self.identity)
        request = send.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertTrue(request.full_url.endswith("/purchaseorder"))
        self.assertEqual(json.loads(request.data), self.order)
        self.assertEqual(self.client.read_purchase_order("7/1")["PurchaseOrder"], self.identity)
        request = send.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertTrue(request.full_url.endswith("/purchaseorder/7%2F1"))
        update = {**self.order, **self.identity, "APAccountRef": {"value": "3"}, "Memo": "x" * 4000}
        self.client.full_update_purchase_order(update, allow_duplicate_doc_number=True)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.assertEqual(json.loads(request.data), {**update, "sparse": False})
        self.client.delete_purchase_order(update)
        request = send.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"operation": ["delete"]})
        self.assertEqual(json.loads(request.data), self.identity)

    def test_pdf_pagination_and_send(self, opener):
        send = opener.return_value.open
        send.side_effect = [io.BytesIO(data) for data in (
            b'%PDF-1.4', b'{"QueryResponse":{"PurchaseOrder":[{"Id":"7"}]}}',
            b'{"QueryResponse":{}}', b'{"PurchaseOrder":{}}', b'{"PurchaseOrder":{}}',
        )]
        self.assertEqual(self.client.get_purchase_order_pdf("7"), b"%PDF-1.4")
        request = send.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/purchaseorder/7/pdf"))
        self.assertEqual(request.get_header("Accept"), "application/pdf")
        self.assertEqual(list(self.client.iter_purchase_orders(page_size=1)), [{"Id": "7"}])
        for position, call in enumerate(send.call_args_list[1:3], 1):
            request = call.args[0]
            self.assertTrue(urlsplit(request.full_url).path.endswith("/query"))
            self.assertEqual(parse_qs(urlsplit(request.full_url).query)["query"],
                             [f"SELECT * FROM PurchaseOrder STARTPOSITION {position} MAXRESULTS 1"])
        for address in (None, "vendor+test@example.com"):
            self.client.send_purchase_order("7", send_to=address)
            request = send.call_args.args[0]
            url = urlsplit(request.full_url)
            self.assertTrue(url.path.endswith("/purchaseorder/7/send"))
            self.assertEqual(parse_qs(url.query), {"sendTo": [address]} if address else {})
            self.assertEqual((request.method, request.data, request.get_header("Content-type")),
                             ("POST", b"", "application/octet-stream"))

    def test_validation_and_delegation(self, opener):
        for changes, field in (
            ({"VendorRef": {}}, "VendorRef.value"),
            ({"APAccountRef": {}}, "APAccountRef.value"),
            ({"Line": []}, "Line"),
            ({"Memo": "x" * 4001}, "Memo"),
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as error:
                self.client.create_purchase_order({**self.order, **changes})
            self.assertEqual(error.exception.field, field)
        with self.assertRaises(ValidationError) as error:
            self.client.full_update_purchase_order({**self.order, **self.identity})
        self.assertEqual(error.exception.field, "APAccountRef.value")
        with self.assertRaises(ValueError):
            self.client.send_purchase_order("7", send_to=" ")
        opener.assert_not_called()
        send = opener.return_value.open
        send.return_value = io.BytesIO(b'{"PurchaseOrder":{}}')
        order = {**self.order, "Memo": "x" * 4001}
        AccountingClient("token", "123", validate_fields=False).create_purchase_order(order)
        self.assertEqual(json.loads(send.call_args.args[0].data), order)
