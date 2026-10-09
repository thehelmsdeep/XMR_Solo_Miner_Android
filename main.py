"""CLI for validating settings and launching XMRig."""
import argparse
import sys
from config import load_settings
from miner.xmrig import build_command

def main():
    parser = argparse.ArgumentParser(description="Termux XMRig launcher")
    parser.add_argument("--check", action="store_true", help="validate settings without launching")
    args = parser.parse_args()
    try:
        settings = load_settings()
        command = build_command(settings)
    except (ValueError, ImportError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    if args.check:
        safe = ["<wallet-hidden>" if arg == settings.wallet_address else arg for arg in command]
        print("Configuration: OK")
        print(f"Mode: {settings.mining_mode}")
        print(f"CPU threads: {settings.cpu_threads}")
        print("Planned command (wallet hidden): " + " ".join(safe))
        print("This does not confirm the node/pool is reachable or that XMRig is installed.")
        return 0
    print("Launcher process management is not installed yet; use --check for now.")
    return 3

if __name__ == "__main__":
    raise SystemExit(main())
