import os
import unittest
from unittest.mock import patch

import run
from miner.monero_rpc import MoneroDaemonError


class SoloPreflightCliTests(unittest.TestCase):
    def solo_env(self):
        return patch.dict(os.environ, {
            "MINING_MODE": "solo",
            "CPU_THREADS": "1",
            "MONERO_RPC_HOST": "127.0.0.1",
            "MONERO_RPC_PORT": "18081",
        }, clear=True)

    @patch("run.configure_logging")
    @patch("run.ensure_monero_ready", return_value={
        "height": 100, "target_height": 100, "busy_syncing": False
    })
    def test_check_daemon_reports_ready_without_starting_miner(self, ensure_ready, _logging):
        with self.solo_env(), patch("sys.argv", ["run.py", "--check-daemon"]), patch(
            "run.run_miner"
        ) as run_miner:
            self.assertEqual(run.main(), 0)
        ensure_ready.assert_called_once_with("127.0.0.1", 18081)
        run_miner.assert_not_called()

    @patch("run.configure_logging")
    @patch("run.ensure_monero_ready", side_effect=MoneroDaemonError("node unavailable"))
    def test_solo_start_stops_when_daemon_is_unavailable(self, ensure_ready, _logging):
        with self.solo_env(), patch("sys.argv", ["run.py"]), patch("run.run_miner") as run_miner:
            self.assertEqual(run.main(), 2)
        ensure_ready.assert_called_once_with("127.0.0.1", 18081)
        run_miner.assert_not_called()

    @patch("run.configure_logging")
    def test_check_daemon_is_rejected_outside_solo_mode(self, _logging):
        with patch.dict(os.environ, {"MINING_MODE": "pool"}, clear=True), patch(
            "sys.argv", ["run.py", "--check-daemon"]
        ):
            self.assertEqual(run.main(), 2)


if __name__ == "__main__":
    unittest.main()
