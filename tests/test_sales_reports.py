import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, ValidationError


@patch("qbosdk.accounting.build_opener")
class SalesReportTests(unittest.TestCase):
    def test_reports_preserve_nested_rows_and_pass_filters(self, opener):
        client = AccountingClient("token", "123")
        send = opener.return_value.open
        common = {"customer": "1,2", "accounting_method": "Accrual", "start_date": "2025-01-01",
                  "end_date": "2025-03-31", "date_macro": "This Fiscal Year", "class_": "2",
                  "item": "3", "summarize_column_by": "Month", "department": "4"}
        cases = (
            (client.sales_by_class_summary, "ClassSales", {}),
            (client.sales_by_customer, "CustomerSales", {"qzurl": "true", "sort_order": "descend"}),
            (client.sales_by_department, "DepartmentSales", {"sort_order": "ascend"}),
            (client.sales_by_product, "ItemSales", {"start_duedate": "2025-01-01",
                                                   "end_duedate": "2025-02-01", "sort_order": "descend"}),
        )
        for method, name, extras in cases:
            with self.subTest(report=name):
                report = {"Header": {"ReportName": name}, "Columns": {"Column": [{"ColType": "Money"}]},
                          "Rows": {"Row": [{"Rows": {"Row": [{"ColData": [{"value": "2", "id": "1"}]}]}}]}}
                send.return_value = io.BytesIO(json.dumps(report).encode())
                self.assertEqual(method(**common, **extras), report)
                request = send.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual(url.path, "/v3/company/123/reports/" + name)
                self.assertEqual((request.method, request.data), ("GET", None))
                self.assertEqual(parse_qs(url.query), {
                    ("class" if key == "class_" else key): [value]
                    for key, value in {**common, **extras}.items()
                })

    def test_due_date_validation_and_delegation(self, opener):
        invalid = {"start_duedate": "2025-03-01", "end_duedate": "2025-02-01"}
        with self.assertRaises(ValidationError) as error:
            AccountingClient("token", "123").sales_by_product(**invalid)
        self.assertEqual((error.exception.field, error.exception.code), ("start_duedate", "invalid_range"))
        opener.assert_not_called()
        send = opener.return_value.open
        send.return_value = io.BytesIO(b'{"Header":{"Option":[{"Name":"NoReportData","Value":"true"}]}}')
        response = AccountingClient("token", "123", validate_fields=False).sales_by_product(**invalid)
        self.assertEqual(response["Header"]["Option"][0]["Value"], "true")
        self.assertEqual(parse_qs(urlsplit(send.call_args.args[0].full_url).query),
                         {key: [value] for key, value in invalid.items()})
