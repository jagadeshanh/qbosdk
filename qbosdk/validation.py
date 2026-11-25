"""Validation errors raised before requests are sent to QuickBooks."""


class ValidationError(ValueError):
    """A local field validation failure; values themselves are not included."""

    def __init__(self, field, code, message, *, limit=None, actual=None):
        super().__init__(message)
        self.field = field
        self.code = code
        self.limit = limit
        self.actual = actual
