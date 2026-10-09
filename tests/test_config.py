import os
import unittest
from unittest.mock import patch
from config import DEFAULT_XMR_WALLET_ADDRESS, load_settings
from miner.xmrig import build_command

class ConfigTests(unittest.TestCase):
    def settings_env(self, **extra):
        values = {"XMR_WALLET_ADDRESS": "4" + "A" + "1" * 93, "MINING_MODE": "p2pool", "CPU_THREADS": "2"}
        values.update(extra)
        return patch.dict(os.environ, values, clear=True)

    def test_p2pool_settings(self):
        with self.settings_env():
            settings = load_settings()
        self.assertEqual(settings.mining_mode, "p2pool")

    def test_empty_wallet_uses_default(self):
        with self.settings_env(XMR_WALLET_ADDRESS=""):
            settings = load_settings()
        self.assertEqual(settings.wallet_address, DEFAULT_XMR_WALLET_ADDRESS)

    def test_reject_unknown_mode(self):
        with self.settings_env(MINING_MODE="invalid"):
            with self.assertRaises(ValueError):
                load_settings()

    def test_solo_command_has_daemon_flag(self):
        with self.settings_env(MINING_MODE="solo"):
            command = build_command(load_settings())
        self.assertIn("--daemon", command)

if __name__ == "__main__":
    unittest.main()
