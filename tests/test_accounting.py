import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class Tests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123", "sandbox")

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Account":{"Id":"42","CurrentBalance":1.23}}')
        result = self.client.create_account({"Name": "Test", "AccountType": "Bank"})
        self.assertEqual(result["Account"]["CurrentBalance"], Decimal("1.23"))
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(req.full_url, "https://sandbox-quickbooks.api.intuit.com/v3/company/123/account")
        self.assertEqual(req.get_header("Authorization"), "Bearer token")
        self.assertEqual(req.get_method(), "POST")
        self.client.read_account("a/b")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/account/a%2Fb"))
        self.client.full_update_account({"Id": "42", "SyncToken": "0", "Name": "Test", "AccountType": "Bank"})
        self.assertIs(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"], False)

    @patch("qbosdk.accounting.build_opener")
    def test_query_and_pagination(self, opener):
        pages = [b'{"QueryResponse":{"Account":[{"Id":"1"},{"Id":"2"}]}}', b'{"QueryResponse":{"Account":[{"Id":"3"}]}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual([a["Id"] for a in self.client.iter_accounts(page_size=2)], ["1", "2", "3"])
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(req.full_url).query)["query"], ["SELECT * FROM Account STARTPOSITION 3 MAXRESULTS 2"])
        opener.return_value.open.side_effect = None
        opener.return_value.open.return_value = io.BytesIO(b'{"QueryResponse":{}}')
        self.assertEqual(list(self.client.iter_accounts()), [])

    @patch("qbosdk.accounting.build_opener")
    def test_errors_and_no_retry(self, opener):
        body = b'{"Fault":{"Error":[{"code":"6240","Message":"Duplicate Name"}]}}'
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {"intuit_tid": "tid"}, io.BytesIO(body))
        with self.assertRaises(AccountingError) as caught:
            self.client.create_account({"Name": "Test", "AccountType": "Bank"})
        self.assertEqual(caught.exception.status, 400)
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "6240")
        self.assertEqual(caught.exception.intuit_tid, "tid")
        self.assertEqual(opener.return_value.open.call_count, 1)

    def test_validation(self):
        for fn in [lambda: self.client.create_account({"Name": "bad:name", "AccountType": "Bank"}),
                   lambda: self.client.full_update_account({"Id": "1", "Name": "x"}),
                   lambda: self.client.query_accounts(max_results=1001),
                   lambda: self.client.query_accounts("SELECT * FROM Account MAXRESULTS 1"),
                   lambda: AccountingClient("token", "../bad")]:
            with self.assertRaises(ValueError):
                fn()

    @patch("qbosdk.accounting.build_opener")
    def test_malformed_response(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"unexpected":true}')
        with self.assertRaises(AccountingError):
            self.client.read_account("1")

    @patch("qbosdk.accounting.build_opener")
    def test_account_name_length_boundaries_for_create_and_update(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Account":{"Id":"1"}}')
        self.client.create_account({"Name": "a" * 100, "AccountType": "Bank"})
        self.client.full_update_account({"Id": "1", "SyncToken": "0", "Name": "\u00e9" * 100})
        self.assertEqual(opener.return_value.open.call_count, 2)
        for account, update in [({"Name": "a" * 101, "AccountType": "Bank"}, False),
                                ({"Name": "\u00e9" * 101, "Id": "1", "SyncToken": "0"}, True)]:
            with self.subTest(update=update), self.assertRaisesRegex(ValueError, "100"):
                (self.client.full_update_account if update else self.client.create_account)(account)
        self.assertEqual(opener.return_value.open.call_count, 2)

    @patch("qbosdk.accounting.build_opener")
    def test_invalid_fields_do_not_reach_transport(self, opener):
        invalid = [
            {"Name": "", "AccountType": "Bank"},
            {"Name": 'bad"name', "AccountType": "Bank"},
            {"Name": "bad:name", "AccountType": "Bank"},
            {"Name": "valid", "AccountType": "Bank", "AcctNum": "1:2"},
            {"Name": "valid", "AccountType": "Bank", "AcctNum": 42},
        ]
        for body in invalid:
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.client.create_account(body)
        with self.assertRaises(ValueError):
            self.client.full_update_account({"Name": "valid", "Id": "1", "SyncToken": "0", "sparse": True})
        opener.assert_not_called()

    @patch("qbosdk.accounting.build_opener")
    def test_stale_version_fault_is_preserved_without_retry(self, opener):
        body = b'{"Fault":{"Error":[{"code":"5010","Message":"Stale Object Error"}]}}'
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(body))
        with self.assertRaises(AccountingError) as caught:
            self.client.full_update_account({"Id": "1", "SyncToken": "0", "Name": "valid"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)

    @patch("qbosdk.accounting.build_opener")
    def test_account_number_country_limits(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Account":{"Id":"1"}}')
        for country, limit in (("AU", 20), ("CA", 20), ("US", 7), ("UK", 7), ("IN", 7)):
            client = AccountingClient("token", "123", country=country)
            for update in (False, True):
                body = {"Name": "Account", "AcctNum": "a" * limit, "AccountType": "Bank"}
                if update:
                    body.update(Id="1", SyncToken="0")
                operation = client.full_update_account if update else client.create_account
                with self.subTest(country=country, update=update):
                    operation(body)
                    calls = opener.return_value.open.call_count
                    body["AcctNum"] += "a"
                    with self.assertRaises(ValueError):
                        operation(body)
                    self.assertEqual(opener.return_value.open.call_count, calls)

    def test_account_number_country_is_optional_and_explicit(self):
        with patch("qbosdk.accounting.build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(b'{"Account":{"Id":"1"}}')
            self.client.create_account({"Name": "Account", "AcctNum": "1" * 21, "AccountType": "Bank"})
        for country in ("us", "GB", "XX", 7):
            with self.subTest(country=country), self.assertRaises(ValueError):
                AccountingClient("token", "123", country=country)

    @patch("qbosdk.accounting.build_opener")
    def test_server_validation_mode_sends_invalid_fields(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Account":{"Id":"1"}}')
        client = AccountingClient("token", "123", country="US", validate_fields=False)
        client.create_account({"Name": "n" * 101, "AccountType": "Bank", "AcctNum": "1:2345678"})
        payload = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertEqual(len(payload["Name"]), 101)
        self.assertEqual(payload["AcctNum"], "1:2345678")
        with self.assertRaises(ValueError):
            client.full_update_account({"Name": "n", "Id": "1"})
        with self.assertRaises(ValueError):
            AccountingClient("token", "123", validate_fields="false")

    @patch("qbosdk.accounting.build_opener")
    def test_local_errors_identify_the_rule_and_field(self, opener):
        client = AccountingClient("token", "123", country="US")
        cases = [
            ({"Name": "a" * 101, "AccountType": "Bank"}, "Name", "max_length", 100, 101, "at most 100 characters; received 101"),
            ({"Name": 'bad"name', "AccountType": "Bank"}, "Name", "invalid_character", None, None, 'double quote'),
            ({"Name": "bad:name", "AccountType": "Bank"}, "Name", "invalid_character", None, None, "colon"),
            ({"Name": "test", "AccountType": "Bank", "AcctNum": "1" * 8}, "AcctNum", "max_length", 7, 8, "at most 7 characters for US; received 8"),
            ({"Name": "test", "AccountType": "Bank", "AcctNum": "1:2"}, "AcctNum", "invalid_character", None, None, "colon"),
        ]
        for body, field, code, limit, actual, message in cases:
            with self.subTest(field=field, code=code, message=message):
                with self.assertRaises(ValidationError) as caught:
                    client.create_account(body)
                error = caught.exception
                self.assertIsInstance(error, ValueError)
                self.assertEqual((error.field, error.code, error.limit, error.actual), (field, code, limit, actual))
                self.assertIn(message, str(error))
        opener.assert_not_called()

    def test_update_identifies_missing_field(self):
        with self.assertRaises(ValidationError) as caught:
            self.client.full_update_account({"Name": "test", "Id": "1"})
        self.assertEqual((caught.exception.field, caught.exception.code), ("SyncToken", "required"))

    @patch("qbosdk.accounting.build_opener")
    def test_complete_account_fields_preserved_and_validated(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Account":{"Id":"42","Name":"Test","SyncToken":"3","CurrencyRef":{"value":"USD","name":"US Dollar"},"MetaData":{"CreateTime":"2020-01-01T12:00:00Z"},"SubAccount":true,"Classification":"Asset","FullyQualifiedName":"Parent:Test","CurrentBalance":1.23,"CurrentBalanceWithSubAccounts":2.34,"AccountType":"Bank","AccountSubType":"Checking"}}')
        account = {"Id": "42", "SyncToken": "3", "Name": "Test", "Description": "x" * 100,
                   "Active": True, "AccountType": "Bank", "AccountSubType": "Checking",
                   "ParentRef": {"value": "12", "name": "Parent"},
                   "TaxCodeRef": {"value": "7"}, "CurrencyRef": {"value": "USD", "name": "US Dollar"}}
        result = self.client.full_update_account(account)["Account"]
        body = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertEqual(body["ParentRef"], account["ParentRef"])
        self.assertEqual(body["Description"], "x" * 100)
        self.assertEqual(result["MetaData"]["CreateTime"], "2020-01-01T12:00:00Z")
        self.assertEqual(result["CurrencyRef"]["value"], "USD")
        self.assertEqual(result["CurrentBalanceWithSubAccounts"], Decimal("2.34"))
        self.assertEqual(result["AccountSubType"], "Checking")

    @patch("qbosdk.accounting.build_opener")
    def test_account_object_validation(self, opener):
        cases = [
            ({"Description": "x" * 101}, "Description", "max_length"),
            ({"Description": 3}, "Description", "invalid_type"),
            ({"Active": 1}, "Active", "invalid_type"),
            ({"ParentRef": "12"}, "ParentRef", "invalid_type"),
            ({"ParentRef": {}}, "ParentRef.value", "required"),
            ({"TaxCodeRef": {"value": 12}}, "TaxCodeRef.value", "required"),
            ({"CurrencyRef": {"value": "US"}}, "CurrencyRef.value", "invalid_format"),
            ({"CurrencyRef": {"value": "USD", "name": 4}}, "CurrencyRef.name", "invalid_type"),
            ({"AccountType": 3}, "AccountType", "invalid_type"),
            ({"AccountSubType": []}, "AccountSubType", "invalid_type"),
        ]
        for fields, field, code in cases:
            with self.subTest(field=field), self.assertRaises(ValidationError) as caught:
                self.client.create_account({"Name": "Account", "AccountType": "Bank", **fields})
            self.assertEqual((caught.exception.field, caught.exception.code), (field, code))
        opener.assert_not_called()

    @patch("qbosdk.accounting.build_opener")
    def test_server_mode_delegates_description_length(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"Account":{"Id":"1"}}')
        client = AccountingClient("token", "123", validate_fields=False)
        client.create_account({"Name": "Account", "AccountType": "Bank", "Description": "x" * 101})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["Description"]), 101)

    def test_documented_account_type_reference(self):
        from qbosdk import ACCOUNT_TYPE_REFERENCE
        self.assertEqual(ACCOUNT_TYPE_REFERENCE["Bank"][0:2], ("Asset", "CashOnHand"))
        self.assertIn("Checking", ACCOUNT_TYPE_REFERENCE["Bank"][2])
        self.assertIn("RetainedEarnings", ACCOUNT_TYPE_REFERENCE["Equity"][2])
        self.assertEqual(len(ACCOUNT_TYPE_REFERENCE), 15)
