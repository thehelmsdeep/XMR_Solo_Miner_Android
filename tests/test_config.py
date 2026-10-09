import os
import unittest
from unittest.mock import patch

from config import DEFAULT_XMR_WALLET_ADDRESS, is_plausible_monero_address, load_settings
from miner.xmrig import build_command


class ConfigTests(unittest.TestCase):
    def settings_env(self, **extra):
        values = {"XMR_WALLET_ADDRESS": "4" + "A" + "1" * 93, "MINING_MODE": "p2pool", "CPU_THREADS": "2"}
        values.update(extra)
        return patch.dict(os.environ, values, clear=True)

    def test_default_wallet_is_used_when_env_is_empty(self):
        with self.settings_env(XMR_WALLET_ADDRESS=""):
            self.assertEqual(load_settings().wallet_address, DEFAULT_XMR_WALLET_ADDRESS)

    def test_custom_wallet_overrides_default(self):
        wallet = "4" + "A" + "1" * 93
        with self.settings_env(XMR_WALLET_ADDRESS=wallet):
            self.assertEqual(load_settings().wallet_address, wallet)

    def test_reject_malformed_wallet_length(self):
        with self.settings_env(XMR_WALLET_ADDRESS="not-a-wallet"):
            with self.assertRaisesRegex(ValueError, "XMR_WALLET_ADDRESS"):
                load_settings()

    def test_address_shape_supports_standard_and_subaddress(self):
        self.assertTrue(is_plausible_monero_address("4" + "A" * 94))
        self.assertTrue(is_plausible_monero_address("8" + "A" * 94))
        self.assertTrue(is_plausible_monero_address("4" + "A" * 105))
        self.assertFalse(is_plausible_monero_address("8" + "A" * 105))

    def test_reject_unknown_mode(self):
        with self.settings_env(MINING_MODE="invalid"):
            with self.assertRaises(ValueError):
                load_settings()

    def test_reject_invalid_thread_count(self):
        with self.settings_env(CPU_THREADS="0"):
            with self.assertRaisesRegex(ValueError, "CPU_THREADS"):
                load_settings()

    def test_reject_invalid_log_level(self):
        with self.settings_env(LOG_LEVEL="verbose"):
            with self.assertRaisesRegex(ValueError, "LOG_LEVEL"):
                load_settings()

    def test_p2pool_command_uses_wallet_and_endpoint(self):
        with self.settings_env():
            settings = load_settings()
        command = build_command(settings)
        self.assertIn("--keepalive", command)
        self.assertIn("--url", command)
        self.assertIn("127.0.0.1:3333", command)
        self.assertIn(settings.wallet_address, command)

    def test_solo_command_has_daemon_flag(self):
        with self.settings_env(MINING_MODE="solo"):
            command = build_command(load_settings())
        self.assertIn("--daemon", command)
        self.assertIn("127.0.0.1:18081", command)


if __name__ == "__main__":
    unittest.main()
