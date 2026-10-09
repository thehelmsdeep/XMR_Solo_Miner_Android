"""Launch XMRig after validating configuration and Solo daemon readiness."""
import argparse
import logging
import sys

from config import load_settings
from miner.monero_rpc import MoneroDaemonError, ensure_monero_ready
from miner.process_manager import configure_logging, run_miner
from miner.xmrig import build_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Termux XMRig launcher")
    parser.add_argument("--check", action="store_true", help="validate settings without mining")
    parser.add_argument(
        "--check-daemon",
        action="store_true",
        help="check that the Monero RPC daemon is reachable and synchronized (Solo mode only)",
    )
    args = parser.parse_args()
    try:
        settings = load_settings()
        command = build_command(settings)
    except (ValueError, ImportError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    if args.check:
        safe = ["<wallet-hidden>" if value == settings.wallet_address else value for value in command]
        print("Configuration: OK")
        print(f"Mode: {settings.mining_mode}")
        print(f"CPU threads: {settings.cpu_threads}")
        print(f"RandomX mode: {settings.randomx_mode}")
        print("Planned command (wallet hidden): " + " ".join(safe))
        if settings.mining_mode == "solo":
            print(
                "Solo prerequisite: a fully synchronized Monero daemon must be running "
                f"at {settings.monero_rpc_host}:{settings.monero_rpc_port}."
            )
        print("This does not verify binary installation or network connectivity.")
        return 0

    if args.check_daemon and settings.mining_mode != "solo":
        print("--check-daemon requires MINING_MODE=solo.", file=sys.stderr)
        return 2

    if args.check_daemon or settings.mining_mode == "solo":
        try:
            info = ensure_monero_ready(settings.monero_rpc_host, settings.monero_rpc_port)
        except MoneroDaemonError as exc:
            logging.error("Solo readiness check failed: %s", exc)
            return 2
        logging.info(
            "Monero daemon RPC is reachable and reports a ready chain (height=%s target=%s)",
            info.get("height", "unknown"),
            info.get("target_height", "unknown"),
        )
        if args.check_daemon:
            print("Monero daemon: reachable and synchronized")
            print(f"Height: {info.get('height', 'unknown')}")
            print(f"Target height: {info.get('target_height', 'unknown')}")
            print("Daemon check: OK")
            return 0

    try:
        return run_miner(settings)
    except OSError as exc:
        logging.error("Could not run XMRig: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
