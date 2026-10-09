import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from miner.monero_rpc import (
    MoneroDaemonError,
    ensure_monero_ready,
    get_monero_info,
)


def response_for(document):
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(document).encode()
    return response


class MoneroRpcTests(unittest.TestCase):
    @patch("miner.monero_rpc.urlopen")
    def test_get_info_posts_read_only_rpc_method(self, urlopen):
        urlopen.return_value = response_for({
            "jsonrpc": "2.0",
            "id": "xmr-solo-miner-android",
            "result": {"height": 100, "target_height": 100},
        })
        result = get_monero_info("127.0.0.1", 18081)
        self.assertEqual(result["height"], 100)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:18081/json_rpc")
        self.assertEqual(json.loads(request.data)["method"], "get_info")

    @patch("miner.monero_rpc.urlopen")
    def test_ensure_ready_accepts_synced_node(self, urlopen):
        urlopen.return_value = response_for({
            "result": {"height": 100, "target_height": 100, "busy_syncing": False}
        })
        self.assertEqual(ensure_monero_ready("127.0.0.1", 18081)["height"], 100)

    @patch("miner.monero_rpc.urlopen")
    def test_ensure_ready_rejects_syncing_node(self, urlopen):
        urlopen.return_value = response_for({
            "result": {"height": 90, "target_height": 100, "busy_syncing": True}
        })
        with self.assertRaisesRegex(MoneroDaemonError, "still syncing"):
            ensure_monero_ready("127.0.0.1", 18081)

    @patch("miner.monero_rpc.urlopen")
    def test_ensure_ready_rejects_node_behind_target(self, urlopen):
        urlopen.return_value = response_for({
            "result": {"height": 90, "target_height": 100}
        })
        with self.assertRaisesRegex(MoneroDaemonError, "behind"):
            ensure_monero_ready("127.0.0.1", 18081)

    @patch("miner.monero_rpc.urlopen", side_effect=URLError("connection refused"))
    def test_unreachable_daemon_has_actionable_error(self, _urlopen):
        with self.assertRaisesRegex(MoneroDaemonError, "Start monerod"):
            get_monero_info("127.0.0.1", 18081)

    @patch("miner.monero_rpc.urlopen")
    def test_rpc_error_is_reported(self, urlopen):
        urlopen.return_value = response_for({
            "error": {"code": -1, "message": "daemon busy"}
        })
        with self.assertRaisesRegex(MoneroDaemonError, "daemon busy"):
            get_monero_info("127.0.0.1", 18081)

    def test_invalid_port_is_rejected(self):
        with self.assertRaisesRegex(MoneroDaemonError, "Invalid Monero RPC"):
            get_monero_info("127.0.0.1", 70000)


if __name__ == "__main__":
    unittest.main()
