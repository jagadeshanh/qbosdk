# QuickBooks Online SDK

A pure Python SDK for QuickBooks Online OAuth, webhooks, and the Accounting API. It requires Python 3.9 or later and has no runtime dependencies. See the [documentation guide](docs/index.rst) for setup and examples, the [webhook guide](docs/webhooks.rst) for receiving notifications, and the [API index](docs/api-index.rst) for supported accounting operations.

## Installation

Once the first release is available on PyPI, install it with `python -m pip install qbosdkonline`. To use the source checkout, run `python -m pip install .` in a virtual environment. Both install the `qbosdk` Python module.

## Configuration

Fill in `.env` with the client ID, client secret and exact redirect URI registered for your Intuit app. Select `sandbox` (development credentials) or `production` (production credentials). `.env` is ignored by Git. It is not loaded automatically: export its values into the process environment using your application's secret manager or, for local shell use, `set -a; source .env; set +a`. Never share this file or commit credentials.

## OAuth usage

```python
from qbosdk import OAuthClient

client = OAuthClient.from_env()
url, state = client.authorization_url()
# Store state in the current user's short-lived, single-use server session.
# Redirect the user's browser to url.

# On the registered callback, retrieve and consume that session's state:
tokens, realm_id = client.exchange_callback(callback_url, state)
# Securely persist tokens and realm_id for this connection.

# Later, serialize refreshes for this connection across all workers:
new_tokens = client.refresh(tokens.refresh_token)
# Atomically persist BOTH new tokens before using them again.
```

The host application owns sessions, callback routing, secure token persistence, and refresh synchronization. Never log callback URLs or tokens. See [OAuth requirements](requirements/oauth.md) for the complete flow, error handling, and endpoint details. `client.api_base_url` identifies the selected Accounting API host; Account operations are available as described below.

Run offline tests with `python3 -m unittest discover -s tests -v`. To validate a real connection, configure an Intuit sandbox app and implement a registered callback in the host application; offline tests do not contact Intuit.

## Local OAuth test server

For a sandbox connection, register `http://localhost:8000/qbo/callback/` with your Intuit development app and set the same value as `QBO_REDIRECT_URI` in `.env`. Intuit’s development settings allow HTTP; the SDK permits it for sandbox localhost only. Alternatively, use an HTTPS tunnel forwarding to `http://127.0.0.1:8000` and register its exact callback URL.

Export `.env` as described above, then run from the repository root:

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/python examples/oauth_server.py
```

Open **http://localhost:8000/** in your browser (or the HTTPS tunnel root if using a tunnel), select Connect, and complete Intuit's sandbox consent flow. The server reports whether the token exchange succeeded and saves the tokens and company ID to `examples/oauth_tokens.json`, a Git-ignored file created with owner-only permissions. It keeps session state only in memory. The example refuses to overwrite an existing token file; move or remove it before reconnecting. Stop it with Ctrl+C. This single-user test server binds to loopback and is not a production callback server. It needs real sandbox credentials and a registered redirect URI for an end-to-end test.

The JSON file is unencrypted and is for local sandbox testing only. Treat it as a secret. Real applications should store tokens encrypted in a secure persistent store, associate them with the correct company and environment, and atomically save the latest token pair after each refresh. Serialize refreshes per connection across workers. The SDK returns tokens to the application and does not choose or manage its storage.

## Account API

Use the connected company's access token and realm ID with the matching environment. The application owns token refresh and persistence; create a new client with the latest access token after refreshing.

```python
from qbosdk import AccountingClient, AccountingError

client = AccountingClient(access_token, realm_id, environment="sandbox")
page = client.query_accounts(start_position=1, max_results=100)
accounts = page["QueryResponse"].get("Account", [])
for account in client.iter_accounts(page_size=100):
    print(account["Name"])
response = client.read_account("42")
created = client.create_account({"Name": "Example bank", "AccountType": "Bank"})
# Full update clears omitted writable fields. Include ALL writable fields to retain.
updated = client.full_update_account({
    "Id": "42", "SyncToken": "0", "Name": "Example bank", "AccountType": "Bank"
})
```

The methods return Intuit's response envelope as dictionaries. JSON fractional numbers are returned as `Decimal`; request input accepts finite `Decimal` values without binary rounding. Query accepts a `SELECT * FROM Account` statement with optional Intuit filters and ordering, but without pagination clauses or semicolons. Use `start_position` (one-based) and `max_results` (1–1000) for a single page or `iter_accounts` to fetch successive pages. The iterator does not provide a snapshot if accounts change while paging. Queries use Intuit's default active-account behavior unless filtered otherwise; see the [Intuit query documentation](https://static.developer.intuit.com/output_html/qbo/docs/learn/explore-the-quickbooks-online-api/data-queries.html). Query statements are raw Intuit query text: escape values according to Intuit's rules before inserting them.

`AccountingError` exposes `status`, `fault`, and `intuit_tid` when available. Fault details may contain customer data; handle them accordingly. Requests are not automatically retried or refreshed. A timeout on a write can leave its outcome unknown; check QuickBooks before trying again. Full update requires a current `Id` and `SyncToken` and explicitly sets `sparse` to false. It cannot determine whether the supplied object contains every field that the caller intends to retain.

### Live sandbox Account test

The sandbox scripts described below are local development files. These commands apply to checkouts that already have the scripts.

With a fresh sandbox connection saved by the OAuth test server, run `.venv/bin/python examples/test_account_sandbox.py`. It checks the account-number limits for AU, CA, US, UK, and IN locally without sending those cases to Intuit, then queries and checks that a 101-character name is rejected locally, then creates a uniquely named Bank account with a 100-character name, reads and fully updates it, and finally sets `Active` to false and verifies the result. This changes the sandbox chart of accounts; QuickBooks retains the inactive account. The script prints the test name and ID for manual recovery if a request or cleanup has an uncertain outcome. It does not refresh or modify the token file; reconnect if the access token has expired.

For client-side `AcctNum` length validation, pass the QuickBooks company country to `AccountingClient`, for example `AccountingClient(access_token, realm_id, country="US")`. Supported values are `AU`, `CA`, `US`, `UK`, and `IN`. Without a country, the SDK does not assume a locale or enforce a length; QuickBooks applies its own validation. Account names must be unique within the company and are validated by QuickBooks.

### Capture sandbox validation errors

Run `.venv/bin/python examples/test_account_sandbox.py` to send invalid Account creates through the SDK to Intuit before the normal lifecycle test. This test explicitly disables local validation for those negative cases, regardless of `QBO_VALIDATE_FIELDS`; normal SDK operations still use the configured setting. Set `QBO_COUNTRY=US` (or `AU`, `CA`, `UK`, `IN`) only when that is the actual sandbox company’s country to include its account-number length case. With the default `true`, the SDK rejects invalid fields locally. The script writes separate owner-readable `examples/qbo_faults_*.jsonl` files with test names, status, Intuit fault codes, messages, details, and request IDs. These files are Git-ignored and may contain sensitive business data; handle them as secrets. It records each test name before sending, stops on uncertain outcomes, and attempts to inactivate any account that unexpectedly gets created. Inspect the file and sandbox if cleanup is uncertain. These probes change sandbox data if Intuit accepts an invalid request; they must never use production credentials.

The library setting is explicit: `AccountingClient(access_token, realm_id, country="US", validate_fields=False)` delegates Account name and account-number format and length checks to Intuit. The default is `True`. The SDK still validates structural requirements, including field types and update identifiers. Environment variables configure the example scripts; applications pass the setting to the client themselves.

If you used the earlier `validate_account_fields` argument or `QBO_VALIDATE_ACCOUNT_FIELDS` environment variable, replace them with `validate_fields` and `QBO_VALIDATE_FIELDS` respectively; the earlier names are no longer read. Reinstall the SDK and re-export `.env` after changing the setting.

### Local validation errors

Account field validation raises `ValidationError`, a subclass of `ValueError`, before sending a request. The message identifies the failed rule; `field` and `code` identify it programmatically. Length errors also expose `limit` and `actual` (character counts). The SDK reports the first detected failure and does not include the field value in the error.

```python
from qbosdk import ValidationError

try:
    client.create_account({"Name": "x" * 101, "AccountType": "Bank"})
except ValidationError as error:
    print(error)          # Account Name must be at most 100 characters; received 101.
    print(error.field)    # Name
    print(error.code)     # max_length
    print(error.limit, error.actual)  # 100 101
```

These are SDK validation codes, not Intuit error codes. For a request rejected by Intuit, catch `AccountingError` and inspect its `fault` for Intuit's original code, message, detail, and field when supplied. Existing `except ValueError` handlers continue to catch local validation errors.

The Account API accepts account dictionaries and preserves response fields and nested reference objects. `Description` is limited to 100 characters when field validation is enabled. `Active` must be a boolean; provided `ParentRef`, `TaxCodeRef`, and `CurrencyRef` objects need a nonempty string `value`. `CurrencyRef` is documented by Intuit as read-only; treat it and other system-generated fields as response data. Full updates must include the writable fields the application intends to retain.

`from qbosdk import ACCOUNT_TYPE_REFERENCE` provides the documented type-to-classification, default subtype, and subtype mapping; for example, `ACCOUNT_TYPE_REFERENCE["Bank"]` returns `(classification, default_subtype, subtypes)`. It is a reference, not an allowlist: available values and type/subtype combinations depend on the QuickBooks company and locale, and QuickBooks validates them. The SDK does not infer parent account types or hierarchy depth; verify those constraints with QuickBooks when creating or updating subaccounts.

### Account List Detail report

```python
report = client.account_list_detail(
    account_type="Income", columns="account_name,account_type", sort_order="ascend"
)
rows = report.get("Rows", {}).get("Row", [])
```

The method returns the complete report, preserving nested rows, columns and header. Its optional keyword parameters follow the [AccountListDetail reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/accountlistdetail). Dates use `YYYY-MM-DD` and an explicit start must precede its end. The reference mentions `date_macro`, `start_createdate`, and `end_createdate` in descriptions without listing them consistently; their support needs live verification. With `validate_fields=False`, date and sort values are sent to Intuit for validation. If you have the local read-only sandbox script, `.venv/bin/python examples/test_account_list_detail_sandbox.py` prints the row count.
