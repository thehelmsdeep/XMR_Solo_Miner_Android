"""Parse XMRig text output into a compact Termux status dashboard.

Hash totals are estimates derived from reported hashrate; XMRig's text stream
does not provide an exact cumulative hash counter.
"""
import re
import time

_RATE_RE = re.compile(r"speed\s+10s/60s/15m\s+([\d.]+)\s+[^\s]+\s+[^\s]+\s+([kMGT]?H/s)")
_SHARE_RE = re.compile(r"(?:accepted|rejected)\s+\((\d+)/(\d+)\)")
_DIFF_RE = re.compile(r"new job .*? diff\s+(\d+)")
_JOB_RE = re.compile(r"new job .*? algo\s+(\S+)\s+height\s+(\d+)")


def _rate_to_hs(value: str, unit: str) -> float:
    scale = {"H/s": 1, "kH/s": 1_000, "MH/s": 1_000_000,
             "GH/s": 1_000_000_000, "TH/s": 1_000_000_000_000}
    return float(value) * scale[unit]


class MinerDashboard:
    def __init__(self, wallet: str, log_path: str = "logs/miner.log"):
        self.wallet = wallet
        self.log_path = log_path
        self.status = "Starting..."
        self.hashrate_hs = 0.0
        self.interval_hashes = 0
        self.total_hashes_est = 0.0
        self.accepted = 0
        self.rejected = 0
        self.pool_diff = "unknown"
        self.last_job = "none"
        self.last_event = "Waiting for XMRig..."
        self.started = time.monotonic()
        self._last_sample = None

    def consume(self, line: str) -> bool:
        """Update state from one XMRig line; return True when dashboard changes."""
        changed = False
        lower = line.lower()
        if "use pool " in lower:
            self.status = "Connected"
            self.last_event = "Connected to pool"
            changed = True
        if "new job " in lower:
            self.status = "Mining..."
            match = _DIFF_RE.search(line)
            if match:
                self.pool_diff = match.group(1)
            match = _JOB_RE.search(line)
            if match:
                self.last_job = f"{match.group(1)} @ height {match.group(2)}"
            self.last_event = "Pool sent a new job"
            changed = True
        if "dns error" in lower or "connection refused" in lower or "connect error" in lower or "connection timeout" in lower:
            self.status = "Connection error"
            self.last_event = line.strip()
            changed = True
        share_match = _SHARE_RE.search(line)
        if share_match:
            self.accepted = int(share_match.group(1))
            self.rejected = int(share_match.group(2))
            if "rejected" in lower:
                self.last_event = "Share rejected"
            else:
                self.last_event = "Share accepted"
            changed = True
        rate_match = _RATE_RE.search(line)
        if rate_match:
            rate = _rate_to_hs(rate_match.group(1), rate_match.group(2))
            now = time.monotonic()
            if self._last_sample is not None:
                elapsed = max(0.0, now - self._last_sample)
                self.total_hashes_est += self.hashrate_hs * elapsed
            self._last_sample = now
            self.hashrate_hs = rate
            self.interval_hashes = round(rate * 10)
            self.status = "Mining..." if self.status != "Connection error" else self.status
            self.last_event = "Hashrate updated"
            changed = True
        return changed

    def render(self) -> str:
        return "\n".join([
            "============== XMR CPU Miner ==============",
            f"Wallet       : {self.wallet}",
            f"Status       : {self.status}",
            f"Hashrate     : {self._format_rate()}",
            f"Interval Hash: ~{self.interval_hashes} (estimated from 10s rate)",
            f"Total Hashes : ~{int(self.total_hashes_est)} (estimated)",
            f"Accepted     : {self.accepted}",
            f"Rejected     : {self.rejected}",
            f"Pool Diff    : {self.pool_diff}",
            f"Last Job     : {self.last_job}",
            f"Last Event   : {self.last_event}",
            f"Log File     : {self.log_path}",
            "===========================================",
        ])
