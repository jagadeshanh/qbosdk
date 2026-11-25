import json
import unittest
from importlib.util import find_spec
from unittest.mock import Mock, patch

from qbosdk import AccountingError

if find_spec("examples.test_account_sandbox") is None or find_spec("examples.sandbox_support") is None:
    raise unittest.SkipTest("Local sandbox scripts are unavailable.")

from examples.test_account_sandbox import probe, run


class SandboxTestFlow(unittest.TestCase):
    def test_flow_and_cleanup(self):
        client = Mock()
        original = {"Id": "42", "SyncToken": "0", "Name": "SDK sandbox test abc " + "x" * 79, "AccountType": "Bank", "Active": True}
        updated = {**original, "SyncToken": "1", "Description": "SDK sandbox integration test"}
        inactive = {**updated, "SyncToken": "2", "Active": False}
        client.create_account.side_effect = [ValueError("too long"), {"Account": original}]
        client.read_account.side_effect = [{"Account": original}, {"Account": updated}, {"Account": updated}, {"Account": inactive}]
        client.full_update_account.side_effect = [{"Account": updated}, {"Account": inactive}]
        with patch("examples.test_account_sandbox.secrets.token_hex", return_value="abc"):
            run(client)
        self.assertEqual(client.full_update_account.call_count, 2)
        self.assertFalse(client.full_update_account.call_args.args[0]["Active"])
        self.assertEqual(client.full_update_account.call_args.args[0]["SyncToken"], "1")

    def test_failure_still_cleans_up(self):
        client = Mock()
        original = {"Id": "42", "SyncToken": "0", "Name": "SDK sandbox test abc " + "x" * 79, "AccountType": "Bank", "Active": True}
        inactive = {**original, "Active": False}
        client.create_account.side_effect = [ValueError("too long"), {"Account": original}]
        client.read_account.side_effect = [RuntimeError("read failed"), {"Account": original}, {"Account": inactive}]
        with patch("examples.test_account_sandbox.secrets.token_hex", return_value="abc"), self.assertRaises(RuntimeError):
            run(client)
        self.assertFalse(client.full_update_account.call_args.args[0]["Active"])


class ProbeTests(unittest.TestCase):
    @patch("examples.test_account_sandbox.os.fsync")
    def test_fault_recorded_with_code(self, _fsync):
        log = Mock()
        client = Mock()
        client.create_account.side_effect = AccountingError("failed", status=400, fault={"type": "ValidationFault", "Error": [{"code": "2050", "Message": "Invalid value", "Detail": "Too long"}]})
        probe(client, log, "invalid_name", {"Name": "test", "AccountType": "Bank"})
        entries = [json.loads(call.args[0]) for call in log.write.call_args_list]
        self.assertEqual(entries[0]["status"], "started")
        self.assertEqual(entries[1]["errors"][0]["code"], "2050")
        self.assertEqual(entries[1]["errors"][0]["Detail"], "Too long")

    @patch("examples.test_account_sandbox.os.fsync")
    def test_uncertain_result_stops(self, _fsync):
        log = Mock()
        client = Mock()
        client.create_account.side_effect = AccountingError("network")
        with self.assertRaises(RuntimeError):
            probe(client, log, "case", {"Name": "test"})
        self.assertEqual(json.loads(log.write.call_args_list[-1].args[0])["status"], "unknown")

    @patch("examples.test_account_sandbox.os.fsync")
    def test_unexpected_success_is_inactivated(self, _fsync):
        log = Mock()
        client = Mock()
        current = {"Id": "1", "SyncToken": "0", "Name": "test", "AccountType": "Bank", "Active": True}
        client.create_account.return_value = {"Account": current}
        client.full_update_account.return_value = {"Account": {**current, "Active": False}}
        client.read_account.side_effect = [{"Account": current}, {"Account": {**current, "Active": False}}]
        with self.assertRaises(RuntimeError):
            probe(client, log, "case", {"Name": "test"})
        self.assertFalse(client.full_update_account.call_args.args[0]["Active"])
        self.assertEqual(json.loads(log.write.call_args_list[-1].args[0])["status"], "inactivated")

    def test_main_always_runs_remote_validation_and_preserves_normal_setting(self):
        from examples.test_account_sandbox import main
        normal = Mock(validate_fields=True)
        remote = Mock(validate_fields=False)
        with patch.dict("os.environ", {"QBO_COUNTRY": "US"}), \
             patch("examples.test_account_sandbox.sandbox_client", side_effect=[normal, remote]) as factory, \
             patch("examples.test_account_sandbox.run_probe") as remote_test, \
             patch("examples.test_account_sandbox.run") as lifecycle:
            self.assertEqual(main(), 0)
        factory.assert_any_call("US")
        factory.assert_any_call("US", validate_fields=False)
        remote_test.assert_called_once_with(remote, "US")
        lifecycle.assert_called_once_with(normal)

    def test_main_does_not_create_lifecycle_account_when_validation_outcome_unknown(self):
        from examples.test_account_sandbox import main
        with patch.dict("os.environ", {}, clear=True), \
             patch("examples.test_account_sandbox.sandbox_client", side_effect=[Mock(), Mock()]), \
             patch("examples.test_account_sandbox.run_probe", side_effect=RuntimeError("uncertain")), \
             patch("examples.test_account_sandbox.run") as lifecycle:
            self.assertEqual(main(), 1)
            lifecycle.assert_not_called()
