# QuickBooks SDK Requirements

This document records the requested scope and unresolved decisions. It is a starting point, not a claim that any functionality has been implemented. Update it as requirements are agreed and API contracts are verified.

## Requested capabilities

- **Authentication and redirects:** Implement the QuickBooks OAuth authorization flow. See [OAuth requirements](oauth.md) for the detailed flow and host responsibilities.
- **API coverage and contracts:** Implement and verify the operations listed in [the entity manifest](../qbo-entities-anchors.json). Record each operation's inputs, outputs, and errors against Intuit's current documentation. See the [entity progress tracker](entity-progress.md) for review, implementation, and verification status.
- **Retries:** Provide a retry mechanism that distinguishes retryable failures and avoids unintended duplicate effects on operations that change data.
- **Duplicate errors:** Recognize and report duplicate-related errors clearly, preserving useful upstream details for callers.
- **Webhooks:** Verify QuickBooks deliveries and decode CloudEvents for host applications. See [webhook requirements](webhooks.md).

## Cross-cutting expectations

- Protect credentials, tokens, and customer data; avoid exposing them in logs or test fixtures.
- Document public behavior, configuration, errors, and examples for each supported capability.
- Test successful and failed flows, including retry safety and webhook validation. Use sandbox or mocked responses as appropriate.
- Verify version-specific behavior, limits, and security requirements against the relevant Intuit documentation before implementation.

## Open decisions

- Supported platforms and packaging; the SDK uses pure Python.
- Further entities and operations, API versions, and geographic scope.
- SDK public interface, credential storage responsibilities, and integration with host applications' redirect and webhook endpoints.
- API retry policy, duplicate-error representation, and compatibility guarantees.
- Test framework, sandbox setup, release process, and coverage expectations.

- **Change data capture:** See [CDC requirements](accounting-change-data-capture.md) for incremental synchronization and its limits.
