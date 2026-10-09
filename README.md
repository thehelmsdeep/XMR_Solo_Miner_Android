# XMR Solo Miner Android

A Python launcher for an already-installed XMRig binary on Termux, with P2Pool and Solo command modes.

> **Early development:** this repository does not install XMRig, run a Monero node or P2Pool, or verify payouts. Passing unit tests does not prove mining works on a device.

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
cp -n .env.example .env
nano .env
python run.py --check
```

## Wallet privacy

The current default receiving address is stored in `config.py` and `.env.example`, as requested. Since this is a public repository, that public address is visible to anyone. It is not a private key or seed phrase. You can override it locally with `XMR_WALLET_ADDRESS` in `.env`; `.env` is ignored by Git. Never store a seed phrase or private key in this project.

The config loader checks common Monero address prefixes and lengths, but it does **not** verify the address checksum or prove that you control the wallet.

## Settings

- `MINING_MODE=p2pool` or `MINING_MODE=solo`
- `XMRIG_PATH`: installed XMRig executable path
- `CPU_THREADS`: begin with a low thread count on phones
- `P2POOL_STRATUM_HOST` / `P2POOL_STRATUM_PORT`: P2Pool endpoint (default is local `127.0.0.1:3333`)
- `MONERO_RPC_HOST` / `MONERO_RPC_PORT`: daemon endpoint for Solo mode (default is local `127.0.0.1:18081`)
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`

The local default endpoints only work if the corresponding service is actually running on the same device. This repository does not launch or configure those services. Do not expose unauthenticated RPC to the public internet; use a trusted node and secure network configuration.

## Commands

```bash
python run.py --check
python run.py
python -m unittest discover -s tests -v
```

`--check` validates settings and prints a planned command with the wallet hidden; it does not verify binary installation or network connectivity. `python run.py` launches XMRig, streams its output to the terminal and `logs/miner.log`, and handles Ctrl+C shutdown. `python main.py` remains a compatibility entry point.

## Important

Phone mining can cause heat, battery wear and throttling. P2Pool shares are not equivalent to a solo block reward, and no payout is guaranteed. Review logs before sharing because miner output can include wallet and connection details. License has not yet been specified.
