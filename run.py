"""Launch XMRig after validating pool-mining configuration."""
import argparse
import logging
import sys

from config import LOG_DIR, load_settings
from miner.process_manager import configure_logging, run_miner
from miner.xmrig import build_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Termux XMRig pool launcher")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="validate settings without mining")
    action.add_argument(
        "--optimize", action="store_true",
        help="benchmark thread-count candidates locally; does not connect to a pool",
    )
    parser.add_argument(
        "--optimizer-max-threads", type=int, default=8,
        help="maximum thread count to test with --optimize (default: 8)",
    )
    parser.add_argument(
        "--optimizer-timeout", type=int, default=90,
        help="seconds allowed for each benchmark candidate (default: 90)",
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
        print("Mode: pool")
        print(f"CPU threads: {settings.cpu_threads}")
        print(f"RandomX mode: {settings.randomx_mode}")
        print("Planned command (wallet hidden): " + " ".join(safe))
        print("This does not verify binary installation or network connectivity.")
        return 0

    if args.optimize:
        try:
            from miner.optimizer import run_optimizer
            report = run_optimizer(
                settings,
                max_threads=args.optimizer_max_threads,
                timeout_seconds=args.optimizer_timeout,
            )
        except (ValueError, FileNotFoundError) as exc:
            logging.error("Optimizer could not start: %s", exc)
            return 2
        print("Adaptive RandomX Optimizer")
        print(f"RandomX mode tested: {settings.randomx_mode}")
        for result in report["results"]:
            rate = result["hashrate_hs"]
            rate_text = f"{rate:.2f} H/s" if rate is not None else "not measured"
            suffix = " (timed out)" if result["timed_out"] else ""
            print(f"  {result['threads']:>2} thread(s): {rate_text}{suffix}")
        if report["recommended_threads"] is None:
            print("No usable benchmark rate was found. Check your XMRig build and logs.")
            return 3
        print(
            f"Recommended starting point: CPU_THREADS={report['recommended_threads']} "
            f"({report['recommended_hashrate_hs']:.2f} H/s in this benchmark)"
        )
        print(f"Report saved to: {LOG_DIR / 'optimizer.json'}")
        print("No settings were changed. Set CPU_THREADS manually after checking stability.")
        return 0

    try:
        return run_miner(settings)
    except OSError as exc:
        logging.error("Could not run XMRig: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
