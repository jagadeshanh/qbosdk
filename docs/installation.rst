Installation and configuration
==============================

The SDK has no third-party runtime dependencies. Install a local checkout in a virtual environment::

    python3 -m venv .venv
    .venv/bin/python -m pip install .

A PyPI release is planned but is not available yet. The installed SDK is imported as ``qbosdk``.

Register an Intuit app, then provide its client ID, client secret, environment and registered redirect URI to the application. The example scripts can read these environment variables:

.. code-block:: text

    QBO_ENVIRONMENT=sandbox
    QBO_CLIENT_ID=your-client-id
    QBO_CLIENT_SECRET=your-client-secret
    QBO_REDIRECT_URI=http://localhost:8000/qbo/callback/

Use development credentials for sandbox and production credentials for production. Production redirects require HTTPS; the SDK also permits HTTP localhost redirects in sandbox. The SDK reads process environment variables; it does not load ``.env`` automatically. Keep secrets out of source control and logs.

``QBO_VALIDATE_FIELDS`` and ``QBO_COUNTRY`` configure the sandbox examples; applications instantiate ``AccountingClient`` with explicit options instead.
