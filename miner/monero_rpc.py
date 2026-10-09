"""Safe, read-only readiness checks for a local Monero daemon RPC endpoint."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class MoneroDaemonError(RuntimeError):
    """Raised when the Monero daemon cannot be used for solo mining."""


def get_monero_info(host: str, port: int, timeout: float = 3.0) -> dict:
    """Call the read-only get_info RPC method and return its result object."""
    if not host or not 1 <= int(port) <= 65535:
        raise MoneroDaemonError("Invalid Monero RPC host or port.")

    endpoint = f"http://{host}:{int(port)}/json_rpc"
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "xmr-solo-miner-android",
        "method": "get_info",
    }).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            document = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise MoneroDaemonError(
            f"Monero RPC returned HTTP {exc.code}. Check the daemon RPC endpoint."
        ) from exc
    except (URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise MoneroDaemonError(
            f"Cannot reach Monero RPC at {host}:{port} ({reason}). "
            "Start monerod and verify MONERO_RPC_HOST/MONERO_RPC_PORT."
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MoneroDaemonError("Monero RPC returned an invalid JSON response.") from exc

    if not isinstance(document, dict):
        raise MoneroDaemonError("Monero RPC response is not a JSON object.")
    if document.get("error"):
        message = document["error"].get("message", "unknown RPC error")
        raise MoneroDaemonError(f"Monero RPC error: {message}")

    result = document.get("result")
    if not isinstance(result, dict):
        raise MoneroDaemonError(
            "Monero RPC response has no result object; check the RPC endpoint."
        )
    if "height" not in result:
        raise MoneroDaemonError(
            "Monero RPC did not return blockchain height; this may not be a Monero daemon."
        )
    return result


def ensure_monero_ready(host: str, port: int, timeout: float = 3.0) -> dict:
    """Require a reachable daemon that is not reporting an active sync."""
    info = get_monero_info(host, port, timeout=timeout)
    height = int(info.get("height", 0) or 0)
    target_height = int(info.get("target_height", 0) or 0)

    if info.get("busy_syncing") is True or info.get("synchronized") is False:
        raise MoneroDaemonError(
            f"Monero node is still syncing (height {height}, target {target_height}). "
            "Wait until synchronization completes before solo mining."
        )
    if target_height > 0 and height < target_height:
        raise MoneroDaemonError(
            f"Monero node is behind (height {height}, target {target_height}). "
            "Wait until synchronization completes before solo mining."
        )
    return info
