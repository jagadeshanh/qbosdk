import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class ARAgingTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_detail_full_query_and_nested_response(self, opener):
        report = {"Header": {"ReportName": "AgedReceivableDetail"}, "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "12.50"}]}]}}]}, "Columns": {"Column": []}}
        opener.return_value.open.return_value = io.BytesIO(json.dumps(report).encode())
        result = AccountingClient("token", "123").ar_aging_detail(customer="1,2", shipvia="Post", term="3", start_duedate="2024-01-01", end_duedate="2024-06-30", custom1="a", custom2="b", custom3="c", report_date="2024-06-30", num_periods=4, aging_method="Current", past_due=30, aging_period=Decimal("30.5"), columns="due_date,cust_name")
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(urlsplit(req.full_url).path, "/v3/company/123/reports/AgedReceivableDetail")
        self.assertEqual(len(parse_qs(urlsplit(req.full_url).query)), 14)
        self.assertEqual(result, report)

    @patch("qbosdk.accounting.build_opener")
    def test_summary_and_server_validation(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Header":{},"Rows":{}}')
        client = AccountingClient("token", "123", "production", validate_fields=False)
        client.ar_aging_summary(customer="4", qzurl="true", date_macro="Last Fiscal Year", aging_method="bad", report_date="bad", sort_order="ascend", department="1")
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(urlsplit(req.full_url).path, "/v3/company/123/reports/AgedReceivables")
        self.assertEqual(len(parse_qs(urlsplit(req.full_url).query)), 7)

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_faults(self, opener):
        client = AccountingClient("token", "123")
        for operation, kwargs in [(client.ar_aging_detail, {"aging_method": "bad"}), (client.ar_aging_detail, {"num_periods": True}), (client.ar_aging_detail, {"start_duedate": "2024-01-02", "end_duedate": "2024-01-01"}), (client.ar_aging_summary, {"qzurl": "yes"})]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                operation(**kwargs)
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            client.ar_aging_summary()
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "4000")
