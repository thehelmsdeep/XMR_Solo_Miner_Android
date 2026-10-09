"""CLI for validating settings and launching XMRig."""
import argparse
import logging
import sys

from config import load_settings
from miner.process_manager import configure_logging, run_miner
from miner.xmrig import build_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Termux XMRig launcher")
    parser.add_argument("--check", action="store_true", help="validate settings without starting mining")
    args = parser.parse_args()

    try:
        settings = load_settings()
        command = build_command(settings)
    except (ValueError, ImportError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    if args.check:
        safe_command = ["<wallet-hidden>" if item == settings.wallet_address else item for item in command]
        print("Configuration: OK")
        print(f"Mode: {settings.mining_mode}")
        print(f"CPU threads: {settings.cpu_threads}")
        print("Planned command (wallet address hidden): " + " ".join(safe_command))
        print("Note: this does not verify that XMRig is installed or the endpoint is reachable.")
        return 0

    try:
        return run_miner(settings)
    except OSError as exc:
        logging.error("Could not run XMRig: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
