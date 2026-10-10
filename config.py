"""Configuration defaults and validation for the Termux XMRig launcher."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "logs"

# Public receiving address only. Never put a seed phrase or private key here.
DEFAULT_XMR_WALLET_ADDRESS = "45YfAsuTdSjSo2rw5ov137A8Y6TdY6pY3Z5ZWQa6oX28A1ysnbjBsWxc7nFxB3hWH73e318AQD7c7MYXXkL7CpMn3UBEYu2"
DEFAULT_MINING_MODE = "pool"
# The maintainer's Android device tested higher throughput at 8 threads. RandomX light
# mode remains the safe default for phones with limited RAM; users can override threads.
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
    pool_host: str
    pool_port: int
    pool_tls: bool
    log_level: str


def is_plausible_monero_address(address: str) -> bool:
    """Check common mainnet Monero address prefix/length, not its checksum."""
    return (len(address) == 95 and address[0] in ("4", "8")) or (len(address) == 106 and address[0] == "4")


def load_settings() -> Settings:
    wallet = os.getenv("XMR_WALLET_ADDRESS", "").strip() or DEFAULT_XMR_WALLET_ADDRESS
    if not is_plausible_monero_address(wallet):
        raise ValueError("XMR_WALLET_ADDRESS does not look like a standard mainnet Monero address (expected 95 or 106 characters)")

    mode = os.getenv("MINING_MODE", DEFAULT_MINING_MODE).strip().lower()
    if mode != "pool":
        raise ValueError("Only MINING_MODE=pool is supported")

    randomx_mode = os.getenv("RANDOMX_MODE", DEFAULT_RANDOMX_MODE).strip().lower()
    if randomx_mode not in VALID_RANDOMX_MODES:
        raise ValueError("RANDOMX_MODE must be auto, fast, or light")

    try:
        threads = int(os.getenv("CPU_THREADS", str(DEFAULT_CPU_THREADS)))
        poolport = int(os.getenv("POOL_PORT", str(DEFAULT_POOL_PORT)))
    except ValueError as exc:
        raise ValueError("Thread count and pool port must be integers") from exc

    if not 1 <= threads <= 256:
        raise ValueError("CPU_THREADS must be between 1 and 256")
    if not 1 <= poolport <= 65535:
        raise ValueError("POOL_PORT must be between 1 and 65535")

    xmrig_path = os.getenv("XMRIG_PATH", DEFAULT_XMRIG_PATH).strip()
    poolhost = os.getenv("POOL_HOST", DEFAULT_POOL_HOST).strip()
    pool_tls_raw = os.getenv("POOL_TLS", "true" if DEFAULT_POOL_TLS else "false").strip().lower()
    if pool_tls_raw not in ("1", "true", "yes", "0", "false", "no"):
        raise ValueError("POOL_TLS must be true or false")
    pool_tls = pool_tls_raw in ("1", "true", "yes")
    if not xmrig_path or not poolhost or poolhost.upper() == "YOUR_MONERO_POOL_HOST":
        raise ValueError("XMRIG_PATH and POOL_HOST must not be empty")

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in VALID_LOG_LEVELS:
        raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")

    return Settings(
        wallet, mode, threads, randomx_mode, xmrig_path,
        poolhost, poolport, pool_tls, log_level
    )
