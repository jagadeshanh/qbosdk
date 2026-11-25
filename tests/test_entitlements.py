import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlsplit
from xml.etree import ElementTree

from qbosdk import AccountingClient, AccountingError


class EntitlementsTests(unittest.TestCase):
    @patch("qbosdk.accounting.build_opener")
    def test_xml_and_environment_paths(self, opener):
        payload = b'<EntitlementsResponse><PlanName>Example</PlanName><Entitlement id="1"><name>Class Tracking</name><term>On</term></Entitlement></EntitlementsResponse>'
        opener.return_value.open.side_effect = lambda *a, **kw: io.BytesIO(payload)
        for environment, host in (("sandbox", "sandbox-quickbooks.api.intuit.com"), ("production", "quickbooks.api.intuit.com")):
            with self.subTest(environment=environment):
                result = AccountingClient("token", "123", environment).read_entitlements()
                request = opener.return_value.open.call_args.args[0]
                self.assertEqual((urlsplit(request.full_url).hostname, urlsplit(request.full_url).path), (host, "/manage/entitlements/v3/123"))
                self.assertEqual(request.get_header("Accept"), "application/xml")
                self.assertEqual(ElementTree.fromstring(result).findtext("Entitlement/name"), "Class Tracking")

    @patch("qbosdk.accounting.build_opener")
    def test_http_failure_is_reported(self, opener):
        opener.return_value.open.side_effect = HTTPError("url", 403, "bad", {"intuit_tid": "trace"}, io.BytesIO(b'<Fault/>'))
        with self.assertRaises(AccountingError) as caught:
            AccountingClient("token", "123").read_entitlements()
        self.assertEqual((caught.exception.status, caught.exception.intuit_tid), (403, "trace"))
