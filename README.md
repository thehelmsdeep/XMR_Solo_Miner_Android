# XMR Solo Miner Android

A Python launcher for an already-installed XMRig binary on Termux, with P2Pool and Solo command modes.

> **Early development:** this repository does not install XMRig, run a Monero node or P2Pool, or verify payouts. Test on your device before relying on it.

## Requirements

- Termux and Python 3.10+
- A compatible XMRig executable built for your Android device
- P2Pool Stratum endpoint for P2Pool mode, or reachable Monero daemon RPC for Solo mode

## Install

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
python run.py --check
```

Set `XMR_WALLET_ADDRESS` in your local `.env` to your public primary Monero address. Never put a seed phrase or private key in this repository. `.env` is ignored by Git.

## Settings

- `MINING_MODE=p2pool` or `MINING_MODE=solo`
- `XMRIG_PATH`: installed XMRig executable path
- `CPU_THREADS`: begin with a low thread count on phones
- `P2POOL_STRATUM_HOST` / `P2POOL_STRATUM_PORT`: P2Pool endpoint
- `MONERO_RPC_HOST` / `MONERO_RPC_PORT`: daemon endpoint for Solo mode

Do not expose unauthenticated RPC to the public internet. Use a trusted node and secure network configuration.

## Commands

```bash
python run.py --check
python run.py
python -m unittest discover -s tests -v
```

`--check` validates settings and prints a planned command with the wallet hidden; it does not verify endpoint connectivity or binary availability. `python run.py` launches XMRig and handles Ctrl+C shutdown.

## Important

Phone mining can cause heat, battery wear and throttling. P2Pool shares are not equivalent to a solo block reward, and no payout is guaranteed. Logs are written to `logs/miner.log`; review them before sharing. License has not yet been specified.
