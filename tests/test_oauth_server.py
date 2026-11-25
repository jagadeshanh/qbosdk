import time
import unittest
from unittest.mock import Mock, patch
import tempfile
import json
import os
from pathlib import Path

from qbosdk import OAuthTokens

from examples.oauth_server import Handler


class TestServer(unittest.TestCase):
    def test_form_policy_allows_intuit_redirect(self):
        handler = Handler.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.reply(200, "page")
        handler.send_header.assert_any_call(
            "Content-Security-Policy",
            "default-src 'none'; form-action 'self' https://appcenter.intuit.com; base-uri 'none'",
        )

    def test_connect_callback_and_replay(self):
        handler = Handler.__new__(Handler)
        handler.server = Mock()
        handler.server.sessions = {}
        handler.server.callback_path = "/callback"
        handler.server.client.redirect_uri = "https://tunnel.example/callback"
        handler.server.client.authorization_url.return_value = ("https://intuit.example/authorize", "state")
        handler.server.client.exchange_callback.return_value = (OAuthTokens("access", "refresh", "bearer", 3600), "company")
        handler.server.client.environment = "sandbox"
        handler.reply = Mock()
        handler.path = "/connect"
        handler.do_POST()
        self.assertEqual(handler.reply.call_args.args[0], 303)
        session = next(iter(handler.server.sessions))
        handler.headers = {"Cookie": "qbo_test_session=" + session}
        handler.path = "/callback?code=code&realmId=company&state=state"
        with tempfile.TemporaryDirectory() as directory, patch("examples.oauth_server.TOKEN_FILE", Path(directory) / "tokens.json"):
            handler.do_GET()
            stored = json.loads((Path(directory) / "tokens.json").read_text())
            self.assertEqual(stored["realm_id"], "company")
            self.assertEqual(stored["refresh_token"], "refresh")
            self.assertEqual(os.stat(Path(directory) / "tokens.json").st_mode & 0o777, 0o600)
        handler.server.client.exchange_callback.assert_called_once_with("https://tunnel.example" + handler.path, "state")
        self.assertEqual(handler.reply.call_args.args[0], 303)
        handler.do_GET()
        self.assertEqual(handler.reply.call_args.args[0], 400)
        handler.server.client.exchange_callback.assert_called_once()

    def test_local_http_cookie(self):
        handler = Handler.__new__(Handler)
        handler.server = Mock()
        handler.server.client.redirect_uri = "http://localhost:8000/qbo/callback/"
        cookie = handler.session_cookie("session", 600)
        self.assertNotIn("; Secure", cookie)
        self.assertIn("HttpOnly", cookie)
        handler.server.client.redirect_uri = "https://tunnel.example/redirect"
        self.assertIn("; Secure", handler.session_cookie("session", 600))

    def test_expired_session(self):
        handler = Handler.__new__(Handler)
        handler.server = Mock()
        handler.server.callback_path = "/callback"
        handler.server.sessions = {"session": ("state", time.monotonic() - 1)}
        handler.headers = {"Cookie": "qbo_test_session=session"}
        handler.path = "/callback?state=state"
        handler.reply = Mock()
        handler.do_GET()
        self.assertEqual(handler.reply.call_args.args[0], 400)
        handler.server.client.exchange_callback.assert_not_called()
