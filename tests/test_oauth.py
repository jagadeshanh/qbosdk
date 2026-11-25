import base64
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

from qbosdk import OAuthClient, OAuthError


class Response(io.BytesIO):
    pass


class OAuthTests(unittest.TestCase):
    def setUp(self):
        self.client = OAuthClient("client", "secret", "https://example.com/callback")
        self.payload = {"access_token": "access", "refresh_token": "refresh", "token_type": "bearer", "expires_in": 3600, "x_refresh_token_expires_in": 100}

    def test_authorization_url_and_environments(self):
        url, state = self.client.authorization_url()
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["state"], [state])
        self.assertEqual(query["scope"], ["com.intuit.quickbooks.accounting"])
        self.assertEqual(query["response_type"], ["code"])
        self.assertNotEqual(state, self.client.authorization_url()[1])
        self.assertEqual(self.client.api_base_url, "https://sandbox-quickbooks.api.intuit.com")
        self.assertEqual(OAuthClient("x", "y", "https://example.com/c", "production").api_base_url, "https://quickbooks.api.intuit.com")
        with self.assertRaises(ValueError):
            OAuthClient("x", "y", "https://example.com/c", "other")

    @patch("qbosdk.oauth.build_opener")
    def test_exchange_and_refresh(self, opener):
        opener.return_value.open.side_effect = lambda *a, **k: Response(json.dumps(self.payload).encode())
        tokens, realm = self.client.exchange_callback("https://example.com/callback?code=abc&realmId=42&state=xyz", "xyz")
        self.assertEqual((tokens.access_token, tokens.refresh_token, realm), ("access", "refresh", "42"))
        self.assertNotIn("access", repr(tokens))
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(req.data.decode()), {"grant_type": ["authorization_code"], "code": ["abc"], "redirect_uri": ["https://example.com/callback"]})
        self.assertEqual(req.get_header("Authorization"), "Basic " + base64.b64encode(b"client:secret").decode())
        self.client.refresh("refresh")
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(parse_qs(req.data.decode()), {"grant_type": ["refresh_token"], "refresh_token": ["refresh"]})

    @patch("qbosdk.oauth.build_opener")
    def test_reject_bad_callbacks_without_network(self, opener):
        for url, state in [
            ("https://example.com/callback?code=a&realmId=1&state=x", "wrong"),
            ("https://evil.com/callback?code=a&realmId=1&state=x", "x"),
            ("https://example.com/callback?code=a&code=b&realmId=1&state=x", "x"),
            ("https://example.com/callback?error=access_denied&state=x", "x"),
            ("https://example.com/callback?code=a&state=x", "x"),
        ]:
            with self.subTest(url=url), self.assertRaises(OAuthError):
                self.client.exchange_callback(url, state)
        opener.assert_not_called()

    @patch("qbosdk.oauth.build_opener")
    def test_failure_does_not_expose_secret_or_retry(self, opener):
        opener.return_value.open.side_effect = HTTPError("url", 400, "bad", {}, io.BytesIO(b'secret'))
        with self.assertRaises(OAuthError) as error:
            self.client.refresh("secret")
        self.assertNotIn("secret", str(error.exception))
        self.assertEqual(opener.return_value.open.call_count, 1)
        opener.return_value.open.side_effect = URLError("secret")
        with self.assertRaises(OAuthError) as error:
            self.client.refresh("secret")
        self.assertNotIn("secret", str(error.exception))

    @patch("qbosdk.oauth.build_opener")
    def test_malformed_token_response(self, opener):
        opener.return_value.open.return_value = Response(b'{"access_token": "x"}')
        with self.assertRaises(OAuthError):
            self.client.refresh("refresh")

    def test_local_sandbox_redirect(self):
        client = OAuthClient("client", "secret", "http://localhost:8000/qbo/callback/", "sandbox")
        self.assertEqual(parse_qs(urlsplit(client.authorization_url()[0]).query)["redirect_uri"], ["http://localhost:8000/qbo/callback/"])
        with self.assertRaises(ValueError):
            OAuthClient("client", "secret", "http://localhost:8000/qbo/callback/", "production")

    def test_configuration_validation(self):
        for uri in ("http://example.com/callback", "https://example.com/callback?x=1", "https://user@example.com/callback"):
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                OAuthClient("client", "secret", uri)


if __name__ == "__main__":
    unittest.main()
