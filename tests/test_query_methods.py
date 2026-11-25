import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient


class QueryMethodTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_single_page_methods_route_each_entity_and_preserve_the_envelope(self, opener):
        client = AccountingClient("token", "123")
        methods = (
            ("Attachable", client.query_attachables),
            ("BillPayment", client.query_bill_payments),
            ("Bill", client.query_bills),
            ("Budget", client.query_budgets),
            ("Class", client.query_classes),
            ("CompanyCurrency", client.query_company_currencies),
            ("CreditCardPayment", client.query_credit_card_payments),
            ("CreditMemo", client.query_credit_memos),
            ("CustomerType", client.query_customer_types),
            ("Customer", client.query_customers),
            ("Deposit", client.query_deposits),
            ("Employee", client.query_employees),
            ("Estimate", client.query_estimates),
            ("ExchangeRate", client.query_exchange_rates),
            ("Invoice", client.query_invoices),
            ("JournalEntry", client.query_journal_entries),
            ("PaymentMethod", client.query_payment_methods),
            ("Payment", client.query_payments),
            ("PurchaseOrder", client.query_purchase_orders),
            ("Purchase", client.query_purchases),
            ("RecurringTransaction", client.query_recurring_transactions),
            ("RefundReceipt", client.query_refund_receipts),
            ("ReimburseCharge", client.query_reimburse_charges),
            ("SalesReceipt", client.query_sales_receipts),
            ("TaxAgency", client.query_tax_agencies),
            ("TaxCode", client.query_tax_codes),
            ("TaxPayment", client.query_tax_payments),
            ("TaxRate", client.query_tax_rates),
            ("Term", client.query_terms),
            ("TimeActivity", client.query_time_activities),
            ("Transfer", client.query_transfers),
            ("VendorCredit", client.query_vendor_credits),
            ("Vendor", client.query_vendors),
        )
        send = opener.return_value.open
        for entity, method in methods:
            with self.subTest(entity=entity):
                response_key = "CreditCardPaymentTxn" if entity == "CreditCardPayment" else entity
                response = {"QueryResponse": {"startPosition": 4, "maxResults": 1,
                                             response_key: [{"Id": "11"}]}, "time": "sample"}
                send.return_value = io.BytesIO(json.dumps(response).encode())
                self.assertEqual(method(start_position=4, max_results=1), response)
                request = send.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual((request.method, url.path), ("GET", "/v3/company/123/query"))
                self.assertEqual(parse_qs(url.query),
                                 {"query": [f"SELECT * FROM {entity} STARTPOSITION 4 MAXRESULTS 1"]})
