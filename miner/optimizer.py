"""Safe, local XMRig benchmark helper for choosing a stable thread count."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from config import LOG_DIR, Settings

_SPEED_RE = re.compile(
    r"speed\s+\S+\s+([0-9]+(?:\.[0-9]+)?)\s+"
    r"[0-9]+(?:\.[0-9]+)?\s+(?:[0-9]+(?:\.[0-9]+)?|n/a)\s+"
    r"(MH/s|kH/s|H/s)", re.IGNORECASE
)


@dataclass(frozen=True)
class BenchmarkResult:
    threads: int
    randomx_mode: str
    hashrate_hs: float | None
    elapsed_seconds: float
    return_code: int | None
    timed_out: bool = False
    error: str | None = None


def parse_hashrate(output: str) -> float | None:
    """Parse the current 10-second XMRig speed and normalize it to H/s."""
    matches = list(_SPEED_RE.finditer(output))
    if not matches:
        return None
    match = matches[-1]
    rate = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "kh/s":
        rate *= 1_000
    elif unit == "mh/s":
        rate *= 1_000_000
    return rate


def candidate_thread_counts(max_threads: int, cpu_count: int | None = None) -> list[int]:
    """Return a small, bounded set of thread counts for an initial device scan."""
    if not 1 <= max_threads <= 64:
        raise ValueError("max_threads must be between 1 and 64")
    available = cpu_count or os.cpu_count() or 1
    limit = max(1, min(max_threads, available))
    candidates = {1, limit}
    value = 2
    while value < limit:
        candidates.add(value)
        value *= 2
    return sorted(candidates)


def build_benchmark_command(xmrig_path: str, threads: int, randomx_mode: str) -> list[str]:
    """Build an offline benchmark command without wallet or pool arguments."""
    if threads < 1:
        raise ValueError("threads must be at least 1")
    if randomx_mode not in {"auto", "fast", "light"}:
        raise ValueError("randomx_mode must be auto, fast, or light")
    return [
        xmrig_path, "--no-color", "--bench=1M", "--threads", str(threads),
        f"--randomx-mode={randomx_mode}",
    ]


def _resolve_executable(path: str) -> str:
    found = shutil.which(path)
    if found:
        return found
    candidate = Path(path).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    raise FileNotFoundError(f"XMRig executable not found: {path}")


def run_optimizer(
    settings: Settings,
    *,
    max_threads: int = 8,
    timeout_seconds: int = 90,
    output_path: Path | None = None,
    runner: Callable = subprocess.run,
    cpu_count: int | None = None,
) -> dict:
    """Benchmark thread-count candidates and persist results without starting mining."""
    if timeout_seconds < 5 or timeout_seconds > 600:
        raise ValueError("timeout_seconds must be between 5 and 600")
    executable = _resolve_executable(settings.xmrig_path)
    counts = candidate_thread_counts(max_threads, cpu_count)
    results: list[BenchmarkResult] = []

    for threads in counts:
        command = build_benchmark_command(executable, threads, settings.randomx_mode)
        started = time.monotonic()
        try:
            completed = runner(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                timeout=timeout_seconds, check=False,
            )
            elapsed = time.monotonic() - started
            results.append(BenchmarkResult(
                threads=threads,
                randomx_mode=settings.randomx_mode,
                hashrate_hs=parse_hashrate(completed.stdout or ""),
                elapsed_seconds=round(elapsed, 2),
                return_code=completed.returncode,
            ))
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            raw_output = exc.stdout or ""
            if isinstance(raw_output, bytes):
                raw_output = raw_output.decode("utf-8", errors="replace")
            results.append(BenchmarkResult(
                threads=threads,
                randomx_mode=settings.randomx_mode,
                hashrate_hs=parse_hashrate(raw_output),
                elapsed_seconds=round(elapsed, 2),
                return_code=None,
                timed_out=True,
                error=f"Benchmark exceeded {timeout_seconds} seconds",
            ))
        except OSError as exc:
            results.append(BenchmarkResult(
                threads=threads,
                randomx_mode=settings.randomx_mode,
                hashrate_hs=None,
                elapsed_seconds=round(time.monotonic() - started, 2),
                return_code=None,
                error=str(exc),
            ))

    valid = [r for r in results if r.hashrate_hs is not None and r.hashrate_hs > 0]
    best = max(valid, key=lambda r: r.hashrate_hs) if valid else None
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": "xmrig --bench=1M",
        "randomx_mode": settings.randomx_mode,
        "max_threads_requested": max_threads,
        "recommended_threads": best.threads if best else None,
        "recommended_hashrate_hs": best.hashrate_hs if best else None,
        "results": [asdict(result) for result in results],
        "note": (
            "Short local benchmark estimates may not predict long-term performance "
            "after Android thermal throttling. No mining configuration was changed."
        ),
    }
    destination = output_path or (LOG_DIR / "optimizer.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
