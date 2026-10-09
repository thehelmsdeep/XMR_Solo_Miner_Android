"""Environment configuration loader and validation."""
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "logs"
DEFAULT_XMR_WALLET_ADDRESS = "45YfAsuTdSjSo2rw5ov137A8Y6TdY6pY3Z5ZWQa6oX28A1ysnbjBsWxc7nFxB3hWH73e318AQD7c7MYXXkL7CpMn3UBEYu2"
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True)
class Settings:
    wallet_address: str
    mining_mode: str
    cpu_threads: int
    xmrig_path: str
    p2pool_stratum_host: str
    p2pool_stratum_port: int
    pool_host: str
    pool_port: int
    pool_tls: bool
    monero_rpc_host: str
    monero_rpc_port: int
    log_level: str


def is_plausible_monero_address(address: str) -> bool:
    """Check common mainnet Monero address prefix/length, not its checksum."""
    return (len(address) == 95 and address[0] in ("4", "8")) or (len(address) == 106 and address[0] == "4")


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(ROOT_DIR / ".env")

    wallet = os.getenv("XMR_WALLET_ADDRESS", "").strip() or DEFAULT_XMR_WALLET_ADDRESS
    if not is_plausible_monero_address(wallet):
        raise ValueError("XMR_WALLET_ADDRESS does not look like a standard mainnet Monero address (expected 95 or 106 characters)")

    mode = os.getenv("MINING_MODE", "p2pool").strip().lower()
    if mode not in ("p2pool", "pool", "solo"):
        raise ValueError("MINING_MODE must be p2pool, pool, or solo")

    try:
        threads = int(os.getenv("CPU_THREADS", "2"))
        p2port = int(os.getenv("P2POOL_STRATUM_PORT", "3333"))
        poolport = int(os.getenv("POOL_PORT", "0"))
        rpcport = int(os.getenv("MONERO_RPC_PORT", "18081"))
    except ValueError as exc:
        raise ValueError("Thread count and ports must be integers") from exc

    if not 1 <= threads <= 256:
        raise ValueError("CPU_THREADS must be between 1 and 256")
    if not 1 <= p2port <= 65535 or not 1 <= rpcport <= 65535:
        raise ValueError("Ports must be between 1 and 65535")
    if mode == "pool":
        if not 1 <= poolport <= 65535:
            raise ValueError("POOL_PORT must be between 1 and 65535 when MINING_MODE=pool")
    
    xmrig_path = os.getenv("XMRIG_PATH", "xmrig").strip()
    p2host = os.getenv("P2POOL_STRATUM_HOST", "127.0.0.1").strip()
    poolhost = os.getenv("POOL_HOST", "").strip()
    pool_tls_raw = os.getenv("POOL_TLS", "false").strip().lower()
    if pool_tls_raw not in ("1", "true", "yes", "0", "false", "no"):
        raise ValueError("POOL_TLS must be true or false")
    pool_tls = pool_tls_raw in ("1", "true", "yes")
    rpchost = os.getenv("MONERO_RPC_HOST", "127.0.0.1").strip()
    if not xmrig_path or not p2host or not rpchost:
        raise ValueError("XMRIG_PATH and endpoint hosts must not be empty")
    if mode == "pool" and (not poolhost or poolhost.upper() == "YOUR_MONERO_POOL_HOST"):
        raise ValueError("POOL_HOST must be set to your chosen Monero pool hostname when MINING_MODE=pool")

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in VALID_LOG_LEVELS:
        raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")

    return Settings(wallet, mode, threads, xmrig_path, p2host, p2port, poolhost, poolport, pool_tls, rpchost, rpcport, log_level)
