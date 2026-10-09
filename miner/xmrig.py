"""Build argument lists for an installed XMRig executable."""
from config import Settings


def build_command(settings: Settings) -> list[str]:
    if settings.mining_mode != "pool":
        raise ValueError("Only pool mining is supported")

    command = [
        settings.xmrig_path,
        "--no-color",
        "--threads",
        str(settings.cpu_threads),
        f"--randomx-mode={settings.randomx_mode}",
        "--print-time",
        "10",
        "--user",
        settings.wallet_address,
        "--url",
        f"{settings.pool_host}:{settings.pool_port}",
        "--pass",
        "x",
        "--keepalive",
    ]
    if settings.pool_tls:
        command.append("--tls")
    return command
