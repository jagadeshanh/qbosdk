"""Local OAuth demonstration for sandbox callbacks."""

import html
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
import time
from urllib.parse import urlsplit

from qbosdk import OAuthClient, OAuthError

HERE = Path(__file__).resolve().parent
TOKEN_FILE = HERE / "oauth_tokens.json"


def save_tokens(tokens, realm_id, environment):
    """Create a private, single-connection sandbox file without overwriting it."""
    data = {"environment": environment, "realm_id": realm_id,
            "obtained_at": datetime.now(timezone.utc).isoformat(), **asdict(tokens)}
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
    except Exception:
        TOKEN_FILE.unlink(missing_ok=True)
        raise


class OAuthTestServer(HTTPServer):
    def __init__(self, address, client):
        super().__init__(address, Handler)
        self.client = client
        self.sessions = {}
        self.callback_path = urlsplit(client.redirect_uri).path or "/"
        if self.callback_path in ("/", "/connect", "/success"):
            self.server_close()
            raise ValueError("redirect URI needs a distinct callback path, such as /callback")


class Handler(BaseHTTPRequestHandler):
    def session_cookie(self, value, max_age):
        secure = "; Secure" if urlsplit(self.server.client.redirect_uri).scheme == "https" else ""
        return f"qbo_test_session={value}; Path=/; Max-Age={max_age}{secure}; HttpOnly; SameSite=Lax"

    def log_message(self, format, *args):
        # Requests can contain OAuth codes; do not log URLs.
        pass

    def reply(self, status, body, headers=()):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; form-action 'self' https://appcenter.intuit.com; base-uri 'none'")
        for key, value in headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == "/":
            self.reply(200, (HERE / "index.html").read_text(encoding="utf-8"))
        elif request.path == "/success":
            self.reply(200, "<h1>Connected</h1><p>Token exchange succeeded. Tokens were saved in the local sandbox token file.</p>")
        elif request.path == self.server.callback_path:
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get("Cookie", ""))
                session = cookie.get("qbo_test_session")
                stored = self.server.sessions.pop(session.value, None) if session else None
            except Exception:
                stored = None
            if not stored or time.monotonic() > stored[1]:
                self.reply(400, "<h1>OAuth session missing or expired</h1><p>Start again from the test page.</p>")
                return
            callback = self.server.client.redirect_uri + ("?" + request.query if request.query else "")
            try:
                if TOKEN_FILE.exists():
                    self.reply(409, "<h1>Token file already exists</h1><p>Move or remove it before connecting another company.</p>")
                    return
                tokens, realm_id = self.server.client.exchange_callback(callback, stored[0])
                save_tokens(tokens, realm_id, self.server.client.environment)
            except OSError:
                self.reply(500, "<h1>Could not save tokens</h1><p>The connection must be authorized again.</p>")
                return
            except OAuthError as exc:
                self.reply(400, "<h1>OAuth failed</h1><p>" + html.escape(str(exc)) + "</p>")
                return
            self.reply(303, "", [("Location", "/success"), ("Set-Cookie", self.session_cookie("", 0))])
        else:
            self.reply(404, "<h1>Not found</h1>")

    def do_POST(self):
        if self.path != "/connect":
            self.reply(404, "<h1>Not found</h1>")
            return
        now = time.monotonic()
        self.server.sessions = {key: value for key, value in self.server.sessions.items() if value[1] > now}
        url, state = self.server.client.authorization_url()
        session = secrets.token_urlsafe(32)
        self.server.sessions[session] = (state, now + 600)
        self.reply(303, "", [("Location", url), ("Set-Cookie", self.session_cookie(session, 600))])


def main():
    client = OAuthClient.from_env()
    if client.environment != "sandbox":
        raise SystemExit("This test server only supports sandbox credentials.")
    server = OAuthTestServer(("127.0.0.1", 8000), client)
    print("Listening on 127.0.0.1:8000. Open http://localhost:8000/ to start, or use your HTTPS tunnel.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
