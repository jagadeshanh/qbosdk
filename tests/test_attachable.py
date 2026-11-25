import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from qbosdk import AccountingClient, AccountingError, ValidationError


class AttachableTests(unittest.TestCase):
    def setUp(self):
        self.client = AccountingClient("token", "123")

    @patch("qbosdk.accounting.build_opener")
    def test_note_read_update_delete(self, opener):
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(b'{"Attachable":{"Id":"12","SyncToken":"0","Note":"hi"}}')
        self.client.create_attachable_note({"Note": "hi", "AttachableRef": [{"EntityRef": {"type": "Invoice", "value": "1"}}]})
        self.assertEqual(opener.return_value.open.call_args.args[0].get_method(), "POST")
        self.client.read_attachable("1/2")
        self.assertTrue(opener.return_value.open.call_args.args[0].full_url.endswith("/attachable/1%2F2"))
        self.client.full_update_attachable({"Id": "12", "SyncToken": "0", "Note": "hi"})
        self.assertFalse(json.loads(opener.return_value.open.call_args.args[0].data)["sparse"])
        self.client.delete_attachable({"Id": "12", "SyncToken": "1", "Note": "hi"})
        self.assertEqual(parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query), {"operation": ["delete"]})
        self.assertEqual(opener.return_value.open.call_count, 4)

    @patch("qbosdk.accounting.build_opener")
    def test_download_url_not_followed(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'"https://example.com/file?secret=redacted"')
        result = self.client.attachable_download_url("123")
        self.assertEqual(result, "https://example.com/file?secret=redacted")
        self.assertEqual(opener.return_value.open.call_count, 1)
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/download/123"))
        self.assertEqual(request.get_header("Accept"), "text/plain")

    @patch("qbosdk.accounting.build_opener")
    def test_query_pagination(self, opener):
        pages = [b'{"QueryResponse":{"Attachable":[{"Id":"1"}]}}', b'{"QueryResponse":{}}']
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(pages.pop(0))
        self.assertEqual(list(self.client.iter_attachables("select Id from attachable where AttachableRef.EntityRef.Type = 'purchase'", page_size=1)), [{"Id": "1"}])
        query = parse_qs(urlsplit(opener.return_value.open.call_args.args[0].full_url).query)["query"][0]
        self.assertIn("STARTPOSITION 2 MAXRESULTS 1", query)

    @patch("qbosdk.accounting.build_opener")
    def test_multipart_pairing_and_faults(self, opener):
        opener.return_value.open.return_value = io.BytesIO(b'{"AttachableResponse":[{"Attachable":{"Id":"1"}},{"Fault":{"Error":[{"code":"99"}]}}]}')
        result = self.client.upload_attachments([{"filename": "a.txt", "content_type": "text/plain", "content": b"abc", "metadata": {"FileName": "a.txt"}}, {"filename": "b.txt", "content_type": "text/plain", "content": b"xyz"}])
        req = opener.return_value.open.call_args.args[0]
        self.assertTrue(req.get_header("Content-type").startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="file_metadata_01"', req.data)
        self.assertIn(b'name="file_content_01"', req.data)
        self.assertIn(b'name="file_content_02"', req.data)
        self.assertIn(b"YWJj", req.data)
        self.assertEqual(result["AttachableResponse"][1]["Fault"]["Error"][0]["code"], "99")

    @patch("qbosdk.accounting.build_opener")
    def test_validation_and_remote_errors(self, opener):
        for fn in (lambda: self.client.create_attachable_note({"Note": "x" * 2001}),
                   lambda: self.client.full_update_attachable({"Id": "1", "SyncToken": "0", "sparse": True}),
                   lambda: self.client.upload_attachments([{"filename": 'a\r\nb', "content_type": "text/plain", "content": b"x"}]),
                   lambda: self.client.upload_attachments([{"filename": "a", "content_type": "text/plain\r\nX: y", "content": b"x"}])):
            with self.assertRaises((ValidationError, ValueError)):
                fn()
        opener.assert_not_called()
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'{"Fault":{"Error":[{"code":"5010"}]}}'))
        with self.assertRaises(AccountingError) as caught:
            self.client.delete_attachable({"Id": "1", "SyncToken": "0"})
        self.assertEqual(caught.exception.fault["Error"][0]["code"], "5010")
        self.assertEqual(opener.return_value.open.call_count, 1)
