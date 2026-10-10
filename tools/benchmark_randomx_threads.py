#!/usr/bin/env python3
"""Run repeatable offline XMRig RandomX benchmarks at several thread counts.

This does not connect to a pool and cannot measure accepted shares or earnings.
Requires an XMRig build that supports --bench (XMRig 6.4.0+).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_threads(value: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("threads must be comma-separated integers, e.g. 1,2,4,8") from exc
    if not values or any(n < 1 or n > 256 for n in values):
        raise argparse.ArgumentTypeError("thread counts must be between 1 and 256")
    if len(set(values)) != len(values):
        raise argparse.ArgumentTypeError("thread counts must not contain duplicates")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xmrig", default=shutil.which("xmrig") or str(
        Path.home() / "xmrig" / "build" / "xmrig"
    ), help="path to XMRig executable (default: PATH or ~/xmrig/build/xmrig)")
    parser.add_argument("--threads", type=parse_threads, default=parse_threads("1,2,4,6,8"),
                        help="comma-separated thread counts (default: 1,2,4,6,8)")
    parser.add_argument("--bench", choices=("250K", "500K", "1M"), default="250K",
                        help="RandomX offline benchmark size (default: 250K)")
    parser.add_argument("--mode", choices=("light", "fast", "auto"), default="light",
                        help="RandomX memory mode (default: light; recommended for low-RAM phones)")
    parser.add_argument("--repeats", type=int, default=2, help="runs per thread count (default: 2)")
    parser.add_argument("--timeout", type=int, default=600, help="timeout in seconds per run (default: 600)")
    parser.add_argument("--json-out", default="logs/randomx-benchmark.json",
                        help="JSON report path (default: logs/randomx-benchmark.json)")
    args = parser.parse_args()

    executable = shutil.which(args.xmrig) or (args.xmrig if Path(args.xmrig).is_file() else None)
    if not executable:
        print(f"ERROR: XMRig executable not found: {args.xmrig}", file=sys.stderr)
        return 2
    if args.repeats < 1 or args.repeats > 10:
        parser.error("--repeats must be between 1 and 10")
    if args.timeout < 1:
        parser.error("--timeout must be positive")

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "xmrig": executable,
        "benchmark": args.bench,
        "randomx_mode": args.mode,
        "note": "Offline RandomX benchmark only; no pool shares or earnings are measured.",
        "runs": [],
    }
    print("OFFLINE RANDOMX BENCHMARK")
    print(f"XMRig: {executable} | bench={args.bench} | mode={args.mode}")
    print("This test does not connect to a pool. Keep the phone cool and compare sustained runs.\n")

    for threads in args.threads:
        for repeat in range(1, args.repeats + 1):
            command = [
                executable, f"--bench={args.bench}", "--threads", str(threads),
                f"--randomx-mode={args.mode}", "--no-color", "--no-title",
            ]
            started = time.monotonic()
            print(f"\n--- threads={threads}, run={repeat}/{args.repeats} ---", flush=True)
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, errors="replace",
                    timeout=args.timeout, check=False,
                )
                elapsed = round(time.monotonic() - started, 3)
                output = (result.stdout or "") + (("\n" + result.stderr) if result.stderr else "")
                run = {
                    "threads": threads, "repeat": repeat, "elapsed_seconds": elapsed,
                    "return_code": result.returncode, "command": command, "output": output,
                }
                report["runs"].append(run)
                # Preserve XMRig's own benchmark summary, including any errors.
                lines = output.strip().splitlines()
                print("\n".join(lines[-18:]) if lines else "(XMRig produced no output)")
                if result.returncode:
                    print(f"WARNING: XMRig returned exit code {result.returncode}")
            except subprocess.TimeoutExpired as exc:
                elapsed = round(time.monotonic() - started, 3)
                partial = exc.stdout or ""
                if isinstance(partial, bytes):
                    partial = partial.decode("utf-8", errors="replace")
                report["runs"].append({
                    "threads": threads, "repeat": repeat, "elapsed_seconds": elapsed,
                    "return_code": None, "timed_out": True, "command": command,
                    "output": partial,
                })
                print(f"TIMEOUT after {elapsed}s; try a larger --timeout or smaller --bench size.")

    output_path = Path(args.json_out).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nJSON report saved to: {output_path}")
    print("Choose the best thread count using repeated results and phone temperature—not the fastest single run.")
    return 0 if all(run.get("return_code") == 0 for run in report["runs"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
