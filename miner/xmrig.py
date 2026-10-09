"""Build argument lists for an installed XMRig executable."""
from config import Settings


def build_command(settings: Settings) -> list[str]:
    command = [
        settings.xmrig_path,
        "--no-color",
        "--threads",
        str(settings.cpu_threads),
        "--print-time",
        "10",
        "--user",
        settings.wallet_address,
    ]

    if settings.mining_mode == "p2pool":
        command += [
            "--url",
            f"{settings.p2pool_stratum_host}:{settings.p2pool_stratum_port}",
            "--keepalive",
        ]
    elif settings.mining_mode == "pool":
        command += [
            "--url",
            f"{settings.pool_host}:{settings.pool_port}",
            "--pass",
            "x",
            "--keepalive",
        ]
        if settings.pool_tls:
            command.append("--tls")
    elif settings.mining_mode == "solo":
        command += [
            "--daemon",
            "--url",
            f"{settings.monero_rpc_host}:{settings.monero_rpc_port}",
        ]
    else:
        raise ValueError("Unsupported mode")

    return command
