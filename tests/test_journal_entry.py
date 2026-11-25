import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class JournalEntryTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")
        self.entry = {"Line": [{"Amount": Decimal("12.34"), "DetailType": "JournalEntryLineDetail", "JournalEntryLineDetail": {"PostingType": kind, "AccountRef": {"value": account}}} for kind, account in (("Debit", "1"), ("Credit", "2"))]}

    @patch("qbosdk.accounting.build_opener")
    def test_create_read_update_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"JournalEntry":{"Id":"7","SyncToken":"0"}}')
        self.client.create_journal_entry(self.entry, allow_auto_doc_number=True)
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowautodocnum"]})
        self.assertIn(b'12.34', request.data)
        self.client.read_journal_entry("7/8")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/journalentry/7%2F8"))
        self.client.full_update_journal_entry({**self.entry, "Id": "7", "SyncToken": "0"}, allow_duplicate_doc_number=True)
        request = opener.return_value.open.call_args.args[0]
        self.assertFalse(json.loads(request.data)["sparse"])
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {"include": ["allowduplicatedocnum"]})
        self.client.sparse_update_journal_entry({"Id": "7", "SyncToken": "1", "PrivateNote": "corrected"})
        self.assertTrue(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.delete_journal_entry({"Id": "7", "SyncToken": "2"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})

    @patch("qbosdk.accounting.build_opener")
    def test_pages_validation_and_fault(self, opener):
        pages = [b'{"QueryResponse":{"JournalEntry":[{"Id":"7"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_journal_entries(page_size=1)), [{"Id": "7"}])
        with self.assertRaises(ValidationError):
            self.client.create_journal_entry({"Line": [self.entry["Line"][0]]})
        with self.assertRaises(ValidationError):
            self.client.sparse_update_journal_entry({"Id": "7"})
        with self.assertRaises(ValueError):
            self.client.create_journal_entry(self.entry, allow_auto_doc_number=True, allow_duplicate_doc_number=True)
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_journal_entry({"Id": "7", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")

    @patch("qbosdk.accounting.build_opener")
    def test_local_field_rules_can_be_delegated(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"JournalEntry":{}}')
        AccountingClient("token", "123", validate_fields=False).create_journal_entry({"Line": [self.entry["Line"][0]], "DocNumber": "x" * 22})
        self.assertEqual(len(json.loads(opener.return_value.open.call_args.args[0].data)["DocNumber"]), 22)
