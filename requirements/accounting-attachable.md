# Attachable requirements

Sources: [Intuit Attachable reference](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/attachable), reviewed with “Copy all for AI”, and [attachment workflow](https://static.developer.intuit.com/output_html/qbo/docs/workflows/attach-images-and-notes.html).

- Create a standalone or linked note: `POST /v3/company/<realmId>/attachable`; `Note` is required for note creation, and `AttachableRef` can link target entities.
- Read `GET /attachable/<id>` and query `GET /query?query=...`, including select-by-ID and filtering on `AttachableRef.EntityRef`. Preserve complete response envelopes and support pagination.
- Full update uses `POST /attachable` with `Id` and current `SyncToken`; omitted writable fields become null. Delete uses `POST /attachable?operation=delete` and the complete payload from a read, including the current `Id` and `SyncToken`.
- Obtain a temporary URL with `GET /download/<id>`; Intuit says it expires after 15 minutes. Return it to the caller and do not automatically follow it or send the bearer token to the destination.
- Upload one or more files with `POST /upload` and `multipart/form-data`: indexed `file_content_nn` parts and optional matching `file_metadata_nn` JSON parts. The request total must not exceed 100 MB. Preserve per-item `AttachableResponse` results and faults. Never automatically retry uploads or mutations.
- Locally validate note, file name, and documented string lengths when field validation is enabled; retain structural validation when disabled. Check multipart filenames and content types for header injection. Do not expose bearer tokens, file contents, or temporary URLs in logs.
- Offline tests cover every operation, multipart pairing and contents, bounds, encoding, malformed replies, error handling, and redirect protections. Live sandbox verification is outstanding.
