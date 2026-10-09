import os
import unittest
from unittest.mock import patch

from config import (
    DEFAULT_CPU_THREADS,
    DEFAULT_MINING_MODE,
    DEFAULT_POOL_HOST,
    DEFAULT_POOL_PORT,
    DEFAULT_POOL_TLS,
    DEFAULT_RANDOMX_MODE,
    DEFAULT_XMR_WALLET_ADDRESS,
    DEFAULT_XMRIG_PATH,
    is_plausible_monero_address,
    load_settings,
)
from miner.xmrig import build_command


TEST_WALLET = "4" + "A" + "1" * 93


class ConfigTests(unittest.TestCase):
    def settings_env(self, **extra):
        values = {
            "XMR_WALLET_ADDRESS": TEST_WALLET,
            "MINING_MODE": "pool",
            "CPU_THREADS": "2",
        }
        values.update(extra)
        return patch.dict(os.environ, values, clear=True)

    def test_default_wallet_is_configured_in_code(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
        self.assertEqual(settings.wallet_address, DEFAULT_XMR_WALLET_ADDRESS)
        self.assertEqual(settings.wallet_address, "45YfAsuTdSjSo2rw5ov137A8Y6TdY6pY3Z5ZWQa6oX28A1ysnbjBsWxc7nFxB3hWH73e318AQD7c7MYXXkL7CpMn3UBEYu2")

    def test_ready_to_use_defaults_are_configured_in_code(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
        self.assertEqual(settings.mining_mode, DEFAULT_MINING_MODE)
        self.assertEqual(settings.mining_mode, "pool")
        self.assertEqual(settings.cpu_threads, DEFAULT_CPU_THREADS)
        self.assertEqual(settings.cpu_threads, 8)
        self.assertEqual(settings.randomx_mode, DEFAULT_RANDOMX_MODE)
        self.assertEqual(settings.randomx_mode, "light")
        self.assertEqual(settings.xmrig_path, DEFAULT_XMRIG_PATH)
        self.assertEqual(settings.pool_host, DEFAULT_POOL_HOST)
        self.assertEqual(settings.pool_port, DEFAULT_POOL_PORT)
        self.assertEqual(settings.pool_tls, DEFAULT_POOL_TLS)
        command = build_command(settings)
        self.assertIn("xmrpool.eu:3333", command)
        self.assertIn("--tls", command)
        self.assertIn("--threads", command)
        self.assertEqual(command[command.index("--threads") + 1], "8")
        self.assertIn("--randomx-mode=light", command)
        self.assertNotIn("--daemon", command)

    def test_randomx_mode_can_be_overridden(self):
        with self.settings_env(RANDOMX_MODE="fast"):
            settings = load_settings()
        self.assertEqual(settings.randomx_mode, "fast")
        self.assertIn("--randomx-mode=fast", build_command(settings))

    def test_reject_invalid_randomx_mode(self):
        with self.settings_env(RANDOMX_MODE="turbo"):
            with self.assertRaisesRegex(ValueError, "RANDOMX_MODE"):
                load_settings()

    def test_custom_wallet_overrides_default(self):
        wallet = "4" + "B" + "2" * 93
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
            with self.assertRaisesRegex(ValueError, "Only MINING_MODE=pool"):
                load_settings()

    def test_reject_solo_mode(self):
        with self.settings_env(MINING_MODE="solo"):
            with self.assertRaisesRegex(ValueError, "Only MINING_MODE=pool"):
                load_settings()

    def test_reject_p2pool_mode(self):
        with self.settings_env(MINING_MODE="p2pool"):
            with self.assertRaisesRegex(ValueError, "Only MINING_MODE=pool"):
                load_settings()

    def test_reject_invalid_thread_count(self):
        with self.settings_env(CPU_THREADS="0"):
            with self.assertRaisesRegex(ValueError, "CPU_THREADS"):
                load_settings()

    def test_reject_invalid_log_level(self):
        with self.settings_env(LOG_LEVEL="verbose"):
            with self.assertRaisesRegex(ValueError, "LOG_LEVEL"):
                load_settings()

    def test_reject_invalid_pool_tls_value(self):
        with self.settings_env(POOL_TLS="sometimes"):
            with self.assertRaisesRegex(ValueError, "POOL_TLS"):
                load_settings()

    def test_pool_command_uses_configured_endpoint_and_password(self):
        with self.settings_env(
            POOL_HOST="pool.example.org",
            POOL_PORT="4242",
            POOL_TLS="false",
        ):
            settings = load_settings()
        command = build_command(settings)
        self.assertIn("pool.example.org:4242", command)
        self.assertIn("--pass", command)
        self.assertIn("x", command)
        self.assertIn(settings.wallet_address, command)
        self.assertIn("--keepalive", command)
        self.assertNotIn("--tls", command)
        self.assertNotIn("--daemon", command)

    def test_pool_command_can_enable_tls(self):
        with self.settings_env(POOL_HOST="pool.example.org", POOL_PORT="4242", POOL_TLS="true"):
            settings = load_settings()
        self.assertIn("--tls", build_command(settings))

    def test_pool_mode_requires_host(self):
        with self.settings_env(POOL_HOST="", POOL_PORT="4242"):
            with self.assertRaisesRegex(ValueError, "POOL_HOST"):
                load_settings()

    def test_pool_mode_requires_valid_port(self):
        with self.settings_env(POOL_HOST="pool.example.org", POOL_PORT="0"):
            with self.assertRaisesRegex(ValueError, "POOL_PORT"):
                load_settings()


if __name__ == "__main__":
    unittest.main()
