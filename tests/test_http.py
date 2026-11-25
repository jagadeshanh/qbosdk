import unittest

from qbosdk._http import NoRedirect


class HttpSafeguardTests(unittest.TestCase):
    def test_redirect_is_not_followed(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://example.com"))
