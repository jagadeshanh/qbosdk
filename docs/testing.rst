Testing and development
=======================

Run the offline suite from the repository root::

    python3 -m unittest discover -s tests -v

The repository README describes the included OAuth test server and optional local sandbox scripts. Tests for those scripts are skipped when the scripts are absent. The Account lifecycle test creates a real sandbox account and attempts to inactivate it; QuickBooks retains the inactive record. It also sends invalid creates to test server validation, records faults in a private Git-ignored JSONL file, and may create an account if an invalid request unexpectedly succeeds. Inspect the output for recovery instructions if cleanup is uncertain.

With the local read-only Account List Detail script and a fresh saved sandbox connection, run::

    .venv/bin/python examples/test_account_list_detail_sandbox.py

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
