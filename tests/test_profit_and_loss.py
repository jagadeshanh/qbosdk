import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


@patch("qbosdk.accounting.build_opener")
class ProfitAndLossTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.report = {"Header": {"Currency": "USD"}, "Columns": {"Column": []},
                       "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "9.50"}]}]}}]}}

    def test_summary_passes_all_filters_and_preserves_response(self, opener):
        send = opener.return_value.open
        send.return_value = io.BytesIO(json.dumps(self.report).encode())
        params = {"customer": "1,2", "qzurl": "true", "accounting_method": "Cash",
                  "end_date": "2025-06-30", "date_macro": "This Month", "adjusted_gain_loss": "false",
                  "class_": "3", "item": "6", "sort_order": "descend", "summarize_column_by": "Month",
                  "department": "9", "vendor": "10", "start_date": "2025-06-01"}
        self.assertEqual(self.client.profit_and_loss(**params), self.report)
        self.assert_request(send.call_args.args[0], "ProfitAndLoss", params)

    def test_detail_passes_all_filters_and_preserves_response(self, opener):
        send = opener.return_value.open
        send.return_value = io.BytesIO(json.dumps(self.report).encode())
        params = {"customer": "1", "account": "2,3", "accounting_method": "Accrual",
                  "end_date": "2025-06-30", "date_macro": "This Month", "adjusted_gain_loss": "true",
                  "class_": "3", "sort_by": "tx_date", "payment_method": "Check", "sort_order": "ascend",
                  "employee": "4", "department": "9", "vendor": "10", "account_type": "Income",
                  "start_date": "2025-06-01", "columns": "tx_date,name,subt_nat_amount"}
        self.assertEqual(self.client.profit_and_loss_detail(**params), self.report)
        self.assert_request(send.call_args.args[0], "ProfitAndLossDetail", params)

    def assert_request(self, request, report_name, params):
        url = urlsplit(request.full_url)
        self.assertTrue(url.path.endswith("/reports/" + report_name))
        self.assertEqual((request.method, request.data), ("GET", None))
        expected = {("class" if key == "class_" else key): [value] for key, value in params.items()}
        self.assertEqual(parse_qs(url.query), expected)

    def test_validation_delegation_and_fault(self, opener):
        for params, field in (
            ({"start_date": "2025-02-29"}, "start_date"),
            ({"start_date": "2025-01-01", "end_date": "2025-01-01"}, "start_date"),
            ({"accounting_method": "Both"}, "accounting_method"),
            ({"adjusted_gain_loss": "yes"}, "adjusted_gain_loss"),
        ):
            with self.subTest(params=params), self.assertRaises(ValidationError) as error:
                self.client.profit_and_loss_detail(**params)
            self.assertEqual(error.exception.field, field)
        opener.assert_not_called()
        send = opener.return_value.open
        send.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "sample"},
                                     io.BytesIO(b'{"Fault":{"Error":[{"code":"4000"}]}}'))
        with self.assertRaises(AccountingError) as error:
            AccountingClient("token", "123", validate_fields=False).profit_and_loss(adjusted_gain_loss="yes")
        self.assertEqual((error.exception.status, error.exception.intuit_tid,
                          error.exception.fault["Error"][0]["code"]), (400, "sample", "4000"))
        self.assert_request(send.call_args.args[0], "ProfitAndLoss", {"adjusted_gain_loss": "yes"})
