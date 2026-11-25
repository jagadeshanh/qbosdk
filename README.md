# QuickBooks Online SDK for Python

`qbosdkonline` helps Python applications connect to QuickBooks Online, work with accounting records and reports, and receive webhooks. It supports sandbox and production, requires **Python 3.9+**, and has no runtime dependencies.

[Documentation](https://qbosdk.readthedocs.io/en/latest/) · [API reference](https://qbosdk.readthedocs.io/en/latest/api-index.html) · [PyPI](https://pypi.org/project/qbosdkonline/)

## Install

```bash
python -m pip install qbosdkonline
```

Import the SDK as `qbosdk`.

## Quick start

1. Register an Intuit app and configure its OAuth redirect URI. Use development credentials for the sandbox.
2. Complete the OAuth flow to get an access token and a realm ID. The realm ID identifies the connected QuickBooks company. Your application stores the tokens and persists both values Intuit returns after each refresh. [OAuth guide](https://qbosdk.readthedocs.io/en/latest/authentication.html)
3. Use the token and realm ID to query accounts or run a report.

```python
from qbosdk import AccountingClient


def show_accounts(access_token: str, realm_id: str) -> None:
    client = AccountingClient(access_token, realm_id, environment="sandbox")

    page = client.query_accounts(max_results=10)
    for account in page["QueryResponse"].get("Account", []):
        print(account["Name"])

    report = client.account_list_detail(columns="account_name,account_type")
    print(report.get("Header", {}).get("ReportName"))
```

## What you can do

- **Connect companies.** Generate OAuth authorization URLs, validate callbacks, exchange authorization codes, and refresh tokens. [Installation and configuration](https://qbosdk.readthedocs.io/en/latest/installation.html)
- **Work with accounting data.** Query and paginate records, manage entities such as accounts, customers, and invoices, and request financial reports. [API reference](https://qbosdk.readthedocs.io/en/latest/api-index.html) · [Reports](https://qbosdk.readthedocs.io/en/latest/reports.html)
- **Receive signed webhooks.** Verify Intuit signatures using the raw request body and process CloudEvents by company. [Webhook guide](https://qbosdk.readthedocs.io/en/latest/webhooks.html)
- **Handle errors.** Inspect SDK field-validation errors and Intuit fault details, including the request ID when available. The SDK leaves retries and token refresh scheduling to your application. [Errors and validation](https://qbosdk.readthedocs.io/en/latest/errors.html)

The SDK works with Django, Flask, FastAPI, and standalone Python. Run its synchronous network calls in a worker thread when calling them from an async route.

## Develop and test

Run the offline suite from the repository root.

```bash
python -m unittest discover -s tests -v
```

The repository includes a local OAuth server for trying the sandbox connection flow. [Local sandbox setup](https://qbosdk.readthedocs.io/en/latest/testing.html#local-oauth-test-server)

## Contribute and support

Report bugs or request features on [GitHub Issues](https://github.com/jagadeshanh/qbosdk/issues). Sponsorship helps fund maintenance, sandbox testing, and integration examples. [GitHub Sponsors](https://github.com/sponsors/jagadeshanh) · [Patreon](https://www.patreon.com/c/jagadeshanh)

Released under the [MIT License](https://github.com/jagadeshanh/qbosdk/blob/main/LICENSE).
