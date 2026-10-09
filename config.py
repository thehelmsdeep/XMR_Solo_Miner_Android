"""Configuration defaults and validation for the Termux XMRig launcher."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "logs"

# Never store a wallet address, seed phrase, or private key in source control.
DEFAULT_MINING_MODE = "pool"
DEFAULT_CPU_THREADS = 8
# Eight threads may increase heat and battery use on a phone. RandomX light mode
# avoids allocating the ~2.3 GiB fast dataset, which can overwhelm Android
# devices with 3–4 GiB RAM. Use RANDOMX_MODE=fast only if there is enough memory.
DEFAULT_RANDOMX_MODE = "light"
DEFAULT_XMRIG_PATH = "/data/data/com.termux/files/home/xmrig/build/xmrig"
DEFAULT_POOL_HOST = "xmrpool.eu"
DEFAULT_POOL_PORT = 3333
DEFAULT_POOL_TLS = True

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_RANDOMX_MODES = {"auto", "fast", "light"}


@dataclass(frozen=True)
class Settings:
    wallet_address: str
    mining_mode: str
    cpu_threads: int
    randomx_mode: str
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
    wallet = os.getenv("XMR_WALLET_ADDRESS", "").strip()
    if not wallet:
        raise ValueError("XMR_WALLET_ADDRESS is required; set your public receiving address in the environment")
    if not is_plausible_monero_address(wallet):
        raise ValueError("XMR_WALLET_ADDRESS does not look like a standard mainnet Monero address (expected 95 or 106 characters)")

    mode = os.getenv("MINING_MODE", DEFAULT_MINING_MODE).strip().lower()
    if mode not in ("p2pool", "pool", "solo"):
        raise ValueError("MINING_MODE must be p2pool, pool, or solo")

    randomx_mode = os.getenv("RANDOMX_MODE", DEFAULT_RANDOMX_MODE).strip().lower()
    if randomx_mode not in VALID_RANDOMX_MODES:
        raise ValueError("RANDOMX_MODE must be auto, fast, or light")

    try:
        threads = int(os.getenv("CPU_THREADS", str(DEFAULT_CPU_THREADS)))
        p2port = int(os.getenv("P2POOL_STRATUM_PORT", "3333"))
        poolport = int(os.getenv("POOL_PORT", str(DEFAULT_POOL_PORT)))
        rpcport = int(os.getenv("MONERO_RPC_PORT", "18081"))
    except ValueError as exc:
        raise ValueError("Thread count and ports must be integers") from exc

    if not 1 <= threads <= 256:
        raise ValueError("CPU_THREADS must be between 1 and 256")
    if not 1 <= p2port <= 65535 or not 1 <= rpcport <= 65535:
        raise ValueError("Ports must be between 1 and 65535")
    if mode == "pool" and not 1 <= poolport <= 65535:
        raise ValueError("POOL_PORT must be between 1 and 65535 when MINING_MODE=pool")

    xmrig_path = os.getenv("XMRIG_PATH", DEFAULT_XMRIG_PATH).strip()
    p2host = os.getenv("P2POOL_STRATUM_HOST", "127.0.0.1").strip()
    poolhost = os.getenv("POOL_HOST", DEFAULT_POOL_HOST).strip()
    pool_tls_raw = os.getenv("POOL_TLS", "true" if DEFAULT_POOL_TLS else "false").strip().lower()
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

    return Settings(
        wallet, mode, threads, randomx_mode, xmrig_path, p2host, p2port,
        poolhost, poolport, pool_tls, rpchost, rpcport, log_level
    )
