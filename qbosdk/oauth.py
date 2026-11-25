"""OAuth 2.0 authorization-code flow for QuickBooks Online."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import hmac
import json
import os
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, build_opener

from ._http import NoRedirect as _NoRedirect

AUTHORIZATION_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
ACCOUNTING_SCOPE = "com.intuit.quickbooks.accounting"
API_URLS = {
    "sandbox": "https://sandbox-quickbooks.api.intuit.com",
    "production": "https://quickbooks.api.intuit.com",
}


class OAuthError(Exception):
    """An OAuth operation failed. Sensitive response bodies are not exposed."""


@dataclass(frozen=True)
class OAuthTokens:
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    token_type: str
    expires_in: int
    x_refresh_token_expires_in: int | None = None
    x_refresh_token_hard_expires_in: int | None = None


class OAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, environment: str = "sandbox"):
        if not all((client_id, client_secret, redirect_uri)):
            raise ValueError("client ID, client secret, and redirect URI are required")
        if environment not in API_URLS:
            raise ValueError("environment must be sandbox or production")
        uri = urlsplit(redirect_uri)
        local_http = environment == "sandbox" and uri.scheme == "http" and uri.hostname == "localhost"
        if (uri.scheme != "https" and not local_http) or not uri.netloc or uri.query or uri.fragment or uri.username or uri.password:
            raise ValueError("redirect URI must use HTTPS, or HTTP localhost in sandbox, without credentials, query, or fragment")
        self.client_id = client_id
        self._client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.environment = environment
        self.api_base_url = API_URLS[environment]

    @classmethod
    def from_env(cls):
        """Read credentials from the process environment; does not load .env files."""
        return cls(os.getenv("QBO_CLIENT_ID", ""), os.getenv("QBO_CLIENT_SECRET", ""),
                   os.getenv("QBO_REDIRECT_URI", ""), os.getenv("QBO_ENVIRONMENT", "sandbox"))

    def authorization_url(self):
        """Return (URL, state); store state in the initiating user's session."""
        state = secrets.token_urlsafe(32)
        query = urlencode({"client_id": self.client_id, "response_type": "code",
                           "scope": ACCOUNTING_SCOPE, "redirect_uri": self.redirect_uri,
                           "state": state})
        return f"{AUTHORIZATION_URL}?{query}", state

    def exchange_callback(self, callback_url: str, expected_state: str):
        """Validate the callback and exchange its one-use code; return (tokens, realm ID)."""
        actual, registered = urlsplit(callback_url), urlsplit(self.redirect_uri)
        if (actual.scheme, actual.netloc, actual.path) != (registered.scheme, registered.netloc, registered.path) or actual.fragment:
            raise OAuthError("callback URL does not match the registered redirect URI")
        params = parse_qs(actual.query, keep_blank_values=True)
        def one(name):
            values = params.get(name, [])
            if len(values) != 1 or not values[0]:
                raise OAuthError(f"callback requires exactly one {name}")
            return values[0]
        state = one("state")
        if not expected_state or not hmac.compare_digest(state.encode(), expected_state.encode()):
            raise OAuthError("OAuth state mismatch")
        if "error" in params:
            one("error")
            raise OAuthError("authorization was rejected by Intuit")
        code, realm_id = one("code"), one("realmId")
        return self._token_request({"grant_type": "authorization_code", "code": code,
                                    "redirect_uri": self.redirect_uri}), realm_id

    def refresh(self, refresh_token: str):
        """Exchange the latest refresh token; callers must persist the returned pair."""
        if not refresh_token:
            raise ValueError("refresh token is required")
        return self._token_request({"grant_type": "refresh_token", "refresh_token": refresh_token})

    def _token_request(self, data):
        credentials = base64.b64encode(f"{self.client_id}:{self._client_secret}".encode()).decode("ascii")
        request = Request(TOKEN_URL, data=urlencode(data).encode(), method="POST", headers={
            "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}",
        })
        try:
            with build_opener(_NoRedirect()).open(request, timeout=30) as response:
                payload = json.load(response)
        except HTTPError as exc:
            raise OAuthError(f"Intuit token request failed (HTTP {exc.code})") from None
        except (URLError, OSError, ValueError) as exc:
            raise OAuthError("Intuit token request failed or returned invalid JSON") from None
        try:
            if not isinstance(payload, dict):
                raise ValueError
            access, refresh, token_type, expires = (payload[k] for k in ("access_token", "refresh_token", "token_type", "expires_in"))
            if not all(isinstance(x, str) and x for x in (access, refresh, token_type)) or type(expires) is not int or expires <= 0:
                raise ValueError
            optional = [payload.get(k) for k in ("x_refresh_token_expires_in", "x_refresh_token_hard_expires_in")]
            if any(x is not None and (type(x) is not int or x < 0) for x in optional):
                raise ValueError
            return OAuthTokens(access, refresh, token_type, expires, *optional)
        except (KeyError, ValueError, TypeError):
            raise OAuthError("Intuit returned an invalid token response") from None
