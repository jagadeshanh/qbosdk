Testing and development
=======================

Run the offline suite from the repository root::

    python3 -m unittest discover -s tests -v

Local OAuth test server
-----------------------

Register ``http://localhost:8000/qbo/callback/`` with your Intuit development app. In a local ``.env`` file, set the same value for ``QBO_REDIRECT_URI``, set ``QBO_ENVIRONMENT=sandbox``, and add the client ID and client secret. From the repository root, run::

    python3 -m venv .venv
    .venv/bin/python -m pip install .
    set -a
    source .env
    set +a
    .venv/bin/python examples/oauth_server.py

Open ``http://localhost:8000/`` and select **Connect**. The server keeps OAuth session state in memory and saves the connection to the Git-ignored ``examples/oauth_tokens.json`` file with owner-only permissions. The file is unencrypted. Keep it private and move it before creating another connection. Stop the server with Ctrl+C.

Optional sandbox scripts
------------------------

If you have the local development scripts, run ``.venv/bin/python examples/test_account_sandbox.py`` with a fresh saved sandbox connection. The script checks account field limits, creates a sandbox account, reads and updates it, and attempts to inactivate it. QuickBooks retains the inactive record. The script also sends invalid creates to test server-side validation and writes the fault details to private, Git-ignored ``examples/qbo_faults_*.jsonl`` files. If an invalid request creates an account, the script attempts to inactivate it. Inspect its output for recovery instructions if cleanup is uncertain.

Set ``QBO_COUNTRY`` to the sandbox company's country to include its account-number length case. The script disables local validation for its upstream error probes. It uses the existing access token, so reconnect if the token has expired. Offline tests for these scripts are skipped when the scripts are absent.

With the local read-only Account List Detail script and a fresh saved sandbox connection, run::

    .venv/bin/python examples/test_account_list_detail_sandbox.py

Build the documentation
-----------------------

Building these documentation pages requires Sphinx, listed in ``docs/requirements.txt``. Once that documentation dependency has been approved and installed, build locally with::

    sphinx-build -b html docs docs/_build/html

The repository's ``.readthedocs.yaml`` configures the hosted documentation build. View the `published documentation <https://qbosdk.readthedocs.io/en/latest/>`_.

Releasing to PyPI
-----------------

The ``publish-pypi.yml`` workflow runs tests, builds and checks the distributions,
and verifies that the wheel works in a clean environment. A push to ``main``
runs these checks. A push of a tag matching the package version, such as
``v0.1.0``, also publishes through the GitHub ``pypi`` environment.

Before the first release, register a PyPI pending Trusted Publisher for project
``qbosdkonline``, GitHub owner ``jagadeshanh``, repository ``qbosdk``,
workflow ``publish-pypi.yml``, and environment ``pypi``.
