import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from config import load_settings
from miner.optimizer import (
    build_benchmark_command, candidate_thread_counts, parse_hashrate, run_optimizer,
)

SPEED_HS = "speed 10s/60s/15m 23.12 21.93 n/a H/s max 23.12 H/s"
SPEED_KHS = "speed 10s/60s/15m 1.25 1.20 n/a kH/s max 1.30 kH/s"


class OptimizerTests(unittest.TestCase):
    def test_parse_hashrate_normalizes_units(self):
        self.assertEqual(parse_hashrate(SPEED_HS), 23.12)
        self.assertEqual(parse_hashrate(SPEED_KHS), 1250.0)
        self.assertEqual(parse_hashrate("speed 10s/60s/15m 0.01 0.01 n/a MH/s"), 10000.0)

    def test_parse_hashrate_returns_none_when_missing(self):
        self.assertIsNone(parse_hashrate("XMRig starting"))

    def test_candidate_counts_are_bounded_and_unique(self):
        self.assertEqual(candidate_thread_counts(8, 8), [1, 2, 4, 8])
        self.assertEqual(candidate_thread_counts(8, 6), [1, 2, 4, 6])
        self.assertEqual(candidate_thread_counts(4, 2), [1, 2])

    def test_candidate_count_validation(self):
        with self.assertRaises(ValueError):
            candidate_thread_counts(0, 8)

    def test_benchmark_command_has_no_pool_or_wallet(self):
        command = build_benchmark_command("/tmp/xmrig", 4, "light")
        self.assertIn("--bench=1M", command)
        self.assertIn("--threads", command)
        self.assertIn("4", command)
        self.assertIn("--randomx-mode=light", command)
        self.assertNotIn("--url", command)
        self.assertNotIn("--user", command)

    def test_optimizer_saves_best_candidate_without_mutating_settings(self):
        settings = load_settings()
        fake_results = {
            "1": SPEED_HS,
            "2": SPEED_KHS,
            "4": "speed 10s/60s/15m 1.10 1.00 n/a kH/s max 1.10 kH/s",
        }

        def fake_runner(command, **kwargs):
            threads = command[command.index("--threads") + 1]
            return SimpleNamespace(stdout=fake_results[threads], returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "miner.optimizer._resolve_executable", return_value="/fake/xmrig"
        ):
            output = Path(temp_dir) / "optimizer.json"
            report = run_optimizer(
                settings, max_threads=4, timeout_seconds=30, output_path=output,
                runner=fake_runner, cpu_count=4,
            )
            self.assertTrue(output.exists())
            self.assertEqual(report["recommended_threads"], 2)
            self.assertEqual(report["recommended_hashrate_hs"], 1250.0)
            self.assertEqual(settings.cpu_threads, 8)

    def test_optimizer_records_timeout(self):
        settings = load_settings()

        def timeout_runner(command, **kwargs):
            raise subprocess.TimeoutExpired(
                command, timeout=kwargs["timeout"], output=SPEED_HS
            )

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "miner.optimizer._resolve_executable", return_value="/fake/xmrig"
        ):
            report = run_optimizer(
                settings, max_threads=1, timeout_seconds=30,
                output_path=Path(temp_dir) / "optimizer.json",
                runner=timeout_runner, cpu_count=1,
            )
        self.assertTrue(report["results"][0]["timed_out"])
        self.assertEqual(report["recommended_threads"], 1)

    def test_timeout_validation(self):
        settings = load_settings()
        with self.assertRaises(ValueError):
            run_optimizer(settings, timeout_seconds=1)


if __name__ == "__main__":
    unittest.main()
