# XMR Solo Miner Android

A Python-based Termux launcher and monitor for **XMRig** with two planned modes:

- **P2Pool** — XMRig connects to a P2Pool Stratum endpoint.
- **Solo** — XMRig mines through a configured Monero daemon RPC endpoint.

> **Status:** foundation / early development. This repository currently validates configuration and prepares XMRig command lines; it does not install or compile XMRig, run P2Pool, or verify payouts automatically yet. A running process or accepted pool share is not proof of a Monero block reward.

## Requirements

- Android device with Termux.
- Python 3.10+.
- A compatible XMRig binary built for your device/Android environment.
- For P2Pool: a reachable P2Pool Stratum endpoint and a Monero node configured as required by P2Pool.
- For Solo: a reachable Monero daemon RPC endpoint that permits mining.

## Install in Termux

```bash
pkg update
pkg install python git
git clone https://github.com/thehelmsdeep/XMR_Solo_Miner_Android.git
cd XMR_Solo_Miner_Android
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py --check
```

Edit `.env` locally and set your **public primary Monero wallet address**. Never put a seed phrase or private key in this project. The `.env` file is ignored by Git.

## Configuration

See `.env.example`. Select `MINING_MODE=p2pool` or `MINING_MODE=solo`.

- `XMRIG_PATH`: path to an already installed XMRig executable.
- `P2POOL_STRATUM_HOST` / `P2POOL_STRATUM_PORT`: P2Pool Stratum host and port.
- `MONERO_RPC_HOST` / `MONERO_RPC_PORT`: daemon RPC host and port for solo mode.
- `CPU_THREADS`: number of CPU threads XMRig may use.

Do not expose an unauthenticated RPC endpoint to the public internet. Use a trusted node and secure network configuration.

## Commands

```bash
python main.py --check    # validate settings and print the planned command
python main.py            # launch XMRig if configured and available
```

The launcher fails safely if required settings or the XMRig executable are missing. Exact daemon compatibility and permissions depend on your node setup.

## Safety / expectations

- Mining on a phone can cause heat, battery wear, throttling, and high power use. Start with a low thread count and monitor device temperature.
- P2Pool shares are not the same as a solo block reward. Payouts depend on P2Pool rules and valid shares.
- No profitability or payout is guaranteed.
- Logs are written to `logs/miner.log`; review them before sharing.

## Development

```bash
python -m unittest discover -s tests -v
```

License: not specified yet. Add a license before redistributing the project.
