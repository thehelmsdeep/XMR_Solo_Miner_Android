# XMR Solo Miner Android

A Python launcher for an already-installed XMRig binary on Termux, with P2Pool, standard pool, and solo command modes.

> **Early development:** this repository does not install XMRig, run a Monero node or P2Pool, select a mining pool, or verify payouts. Passing unit tests does not prove mining works on a device.

## Requirements

- Termux and Python 3.10+
- A compatible XMRig executable built for your Android device
- P2Pool Stratum endpoint for P2Pool mode, a configured Monero mining pool for pool mode, or reachable Monero daemon RPC for Solo mode

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

- `MINING_MODE=p2pool`, `pool`, or `solo`
- `XMRIG_PATH`: installed XMRig executable path
- `CPU_THREADS`: begin with a low thread count on phones
- `P2POOL_STRATUM_HOST` / `P2POOL_STRATUM_PORT`: P2Pool Stratum endpoint (default is local `127.0.0.1:3333`)
- `POOL_HOST` / `POOL_PORT`: hostname and port published by the standard Monero pool you choose
- `POOL_TLS=true`: enable XMRig TLS for a pool endpoint that explicitly supports TLS; otherwise use `false`
- `MONERO_RPC_HOST` / `MONERO_RPC_PORT`: daemon endpoint for Solo mode (default is local `127.0.0.1:18081`)
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`

### Standard pool mode

Edit your local `.env` and set the exact hostname, port, and TLS setting published by the pool you choose:

```dotenv
MINING_MODE=pool
POOL_HOST=hostname-from-the-pool-documentation
POOL_PORT=port-from-the-pool-documentation
POOL_TLS=true
```

For example, XMRPool.eu currently documents `xmrpool.eu:3333` with TLS enabled. Its guide lists a 0.07 XMR minimum payment for a personal Monero wallet; check the pool's current official documentation and payout threshold before choosing it. That threshold may be impractical for a low-hashrate phone. Official setup details: https://www.xmrpool.eu/xmr-monero-easy-mining-guide.html

The `pool` mode sends the wallet as XMRig's `--user`, sets `--pass x`, and adds `--tls` only when `POOL_TLS=true`. A pool may require a different password/worker format; follow that pool's official instructions. Do not assume a pool will pay just because XMRig starts.

## Commands

```bash
python run.py --check
python run.py
python -m unittest discover -s tests -v
```

`--check` validates settings and prints a planned command with the wallet hidden; it does not verify binary installation or network connectivity. `python run.py` launches XMRig, streams its output to the terminal and `logs/miner.log`, and handles Ctrl+C shutdown. `python main.py` remains a compatibility entry point.

## Important

Phone mining can cause heat, battery wear and throttling. Pool rewards depend on accepted work, pool rules, fees, payout thresholds, and luck; no payout is guaranteed. Review logs before sharing because miner output can include wallet and connection details. License has not yet been specified.
