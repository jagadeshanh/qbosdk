Attachments
===========

Use the Accounting client for Attachable notes and files. Operations return the original Intuit response envelopes::

    note = client.create_attachable_note({"Note": "Example note"})
    attachment = client.read_attachable(note["Attachable"]["Id"])["Attachable"]
    page = client.query_attachables("SELECT * FROM Attachable")
    for item in client.iter_attachables(page_size=100):
        print(item["Id"])

``full_update_attachable(attachment)`` is a full update: provide the current ``Id`` and ``SyncToken`` and every writable field to retain, because omitted fields are cleared. ``delete_attachable(attachment)`` deletes the attachment and expects the full current payload from a read. These mutations are not retried automatically.

Upload one or more files as bytes, optionally with metadata and entity links::

    response = client.upload_attachments([{
        "filename": "receipt.txt",
        "content_type": "text/plain",
        "content": b"Example receipt",
        "metadata": {"FileName": "receipt.txt", "ContentType": "text/plain"},
    }])

Inspect each ``AttachableResponse`` entry; QuickBooks may report per-file faults. The total multipart request cannot exceed 100 MB. ``attachable_download_url(id)`` returns an Intuit temporary HTTPS URL, which can contain sensitive credentials and expires; the SDK does not fetch it or forward the bearer token to that URL. Use it promptly and do not log it. Consult `Intuit's attachment reference <https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/attachable>`_ for supported file types and entity linking.
