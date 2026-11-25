"""JSON request encoding that retains decimal values without binary rounding."""

import json
from decimal import Decimal


def dumps(value):
    """Encode JSON data, including finite Decimal numbers, as a string."""
    active = set()

    def encode(item):
        if isinstance(item, Decimal):
            if not item.is_finite():
                raise ValueError("non-finite decimal")
            return str(item)
        if item is None or isinstance(item, (bool, str, int, float)):
            return json.dumps(item, allow_nan=False)
        if isinstance(item, (list, tuple, dict)):
            identity = id(item)
            if identity in active:
                raise ValueError("circular reference")
            active.add(identity)
            try:
                if isinstance(item, dict):
                    if any(not isinstance(key, str) for key in item):
                        raise TypeError("JSON object keys must be strings")
                    return "{" + ",".join(json.dumps(key) + ":" + encode(val) for key, val in item.items()) + "}"
                return "[" + ",".join(encode(val) for val in item) + "]"
            finally:
                active.remove(identity)
        raise TypeError("unsupported JSON value")

    return encode(value)
