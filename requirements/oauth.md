# OAuth 2.0 requirements and flow

## Scope and configuration

The SDK is pure Python and uses the standard library. It supports Intuit's authorization-code flow for the QuickBooks Online accounting scope. The host application supplies the environment (`sandbox` or `production`), the corresponding Intuit client ID and secret, and an exactly matching registered redirect URI. Production requires HTTPS; sandbox also accepts HTTP on localhost for local testing. Sandbox uses development credentials; production uses production credentials. The Accounting API base URL differs by environment; the documented authorization and token URLs used here are shared. API requests are outside this phase.

## Flow

1. The host calls `authorization_url()`, stores the generated unpredictable state in the initiating user's server-side session, and redirects the user's browser to the returned URL. The URL requests the accounting scope and an authorization code.
2. Intuit asks the user to sign in, select a company, and consent. Intuit redirects to the registered URI with `state` and either `code` and `realmId` or an error. The host passes the full callback URL and the original session state to `exchange_callback()`. State must be single-use, session-bound, expire promptly, and be removed by the host even on failure. Reject unsolicited or replayed callbacks.
3. The SDK checks the callback target, rejects missing or duplicate parameters and mismatched state, then exchanges the code once using client authentication over HTTPS. It returns tokens and the company realm ID. The host must immediately store them securely, associated with the correct user, environment, and company. Redirect the browser to a clean URL without the code; do not log callback URLs.
4. Use the access token for authorized API requests. Before or after expiry, the host may call `refresh()` with the latest refresh token. Persist both returned tokens atomically before subsequent use. Serialize refreshes per connection across processes; the SDK does not provide storage or locking. If the refresh token expires or is revoked, start a new authorization flow.

The token endpoint receives form-encoded requests with HTTP Basic client authentication. Token calls are not automatically retried: a timeout can leave the outcome unknown, and a code is single-use or a refresh token may have rotated. The host must handle this uncertainty and reauthorize if necessary. The SDK does not follow token endpoint redirects or include sensitive response bodies in exceptions. It does not implement a web server, token persistence, OpenID Connect, or token revocation.

## Security and verification

Keep the client secret and tokens on a trusted backend, encrypted at rest where persisted. Never include them in URLs, logs, fixtures, or source control. Validate Intuit's current security requirements for deployment. Tests must cover authorization parameters, callback validation, exchange and refresh requests, token responses, and failure paths without real credentials. A live sandbox authorization remains necessary to verify an app's registered redirect and credentials.

Sources: [Intuit OAuth 2.0 guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0), [authorization FAQ](https://static.developer.intuit.com/output_html/qbo/docs/develop/authentication-and-authorization/faq.html), and [Account API reference](https://developer.intuit.com/docs/api/accounting/account).
