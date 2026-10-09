"""Environment configuration loader."""
import os
from dataclasses import dataclass
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "logs"

@dataclass(frozen=True)
class Settings:
    wallet_address: str
    mining_mode: str
    cpu_threads: int
    xmrig_path: str
    p2pool_stratum_host: str
    p2pool_stratum_port: int
    monero_rpc_host: str
    monero_rpc_port: int
    log_level: str

def load_settings():
    if load_dotenv is not None:
        load_dotenv(ROOT_DIR / ".env")
    wallet = os.getenv("XMR_WALLET_ADDRESS", "").strip()
    if not wallet:
        raise ValueError("Set XMR_WALLET_ADDRESS in your local .env file")
    mode = os.getenv("MINING_MODE", "p2pool").strip().lower()
    if mode not in ("p2pool", "solo"):
        raise ValueError("MINING_MODE must be p2pool or solo")
    try:
        threads = int(os.getenv("CPU_THREADS", "2"))
        p2port = int(os.getenv("P2POOL_STRATUM_PORT", "3333"))
        rpcport = int(os.getenv("MONERO_RPC_PORT", "18081"))
    except ValueError as exc:
        raise ValueError("Thread count and ports must be integers") from exc
    if not 1 <= threads <= 256 or not 1 <= p2port <= 65535 or not 1 <= rpcport <= 65535:
        raise ValueError("Thread count or port is outside the allowed range")
    return Settings(wallet, mode, threads, os.getenv("XMRIG_PATH", "xmrig"),
        os.getenv("P2POOL_STRATUM_HOST", "127.0.0.1"), p2port,
        os.getenv("MONERO_RPC_HOST", "127.0.0.1"), rpcport,
        os.getenv("LOG_LEVEL", "INFO").upper())
