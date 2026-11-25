import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from importlib.util import find_spec
from pathlib import Path
from unittest.mock import patch

if find_spec("examples.sandbox_support") is None:
    raise unittest.SkipTest("Local sandbox support script is unavailable.")

from examples import sandbox_support


class SandboxConfigurationTests(unittest.TestCase):
    def test_sandbox_connection_and_validation_setting(self):
        data = {"environment": "sandbox", "access_token": "example", "realm_id": "123",
                "obtained_at": datetime.now(timezone.utc).isoformat(), "expires_in": 3600}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tokens.json"
            path.write_text(json.dumps(data))
            with patch.object(sandbox_support, "TOKEN_FILE", path), patch.dict("os.environ", {"QBO_VALIDATE_FIELDS": "false"}):
                client = sandbox_support.sandbox_client("US")
                self.assertFalse(client.validate_fields)
                data["environment"] = "production"
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    sandbox_support.sandbox_client()
                data["environment"] = "sandbox"
                data["obtained_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    sandbox_support.sandbox_client()
