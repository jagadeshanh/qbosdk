Authentication
==============

The SDK supports the QuickBooks OAuth 2.0 authorization-code flow for the accounting scope. Register the exact redirect URI in the Intuit app settings, including its path and trailing slash.

.. code-block:: python

    from qbosdk import OAuthClient

    client = OAuthClient.from_env()
    authorization_url, state = client.authorization_url()
    # Store state in this user's short-lived, single-use server-side session.
    # Redirect their browser to authorization_url.

    # On the callback, retrieve and consume the state from the same session.
    tokens, realm_id = client.exchange_callback(callback_url, state)
    # Securely persist tokens and realm_id for this connection.

The callback URL contains sensitive data. Handle it server-side and redirect the browser to a clean URL. The host application owns session state, callback routing, token storage, and refresh synchronization. Encrypt persisted tokens and associate them with the correct user, environment, and company.

When an access token expires, serialize refreshes for the connection across workers and persist the returned token pair atomically::

    new_tokens = client.refresh(tokens.refresh_token)
    # Persist both tokens before using the connection again.

The SDK does not automatically retry token exchanges or persist tokens. If a refresh fails or its outcome is unknown, follow the host application's recovery process; reauthorization may be necessary. Never log tokens or callback URLs. See `Intuit's OAuth guide <https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0>`_.
