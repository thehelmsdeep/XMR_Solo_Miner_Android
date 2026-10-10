# XMR Pool Miner Android

A Python launcher for an already-installed XMRig binary on Termux. This project supports **standard Monero pool mining only**; Solo and P2Pool modes are not supported.

> **Early development:** this repository does not install XMRig or verify payouts. Passing unit tests does not prove mining works on a device.

## Requirements

- Termux and Python 3.10+
- A compatible XMRig executable built for your Android device
- A Monero pool endpoint and a public receiving wallet address

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
python run.py --check
```

The default public receiving address is configured in `config.py`. You can override it by setting `XMR_WALLET_ADDRESS` in the shell. The address is public and is not a private key or seed phrase. Never store a seed phrase or private key in this project.

The default XMRig path is specific to the Termux setup where XMRig was built and may need changing on another device.

## Built-in defaults

- Mining mode: `pool` only
- Receiving wallet: the public Monero address currently set in `config.py`
- CPU threads: `8` (higher phone heat and battery use are possible)
- RandomX mode: `light` (lower memory use, usually lower hashrate)
- XMRig path: `/data/data/com.termux/files/home/xmrig/build/xmrig`
- Pool endpoint: `xmrpool.eu:3333`
- TLS: enabled

RandomX fast mode allocates a dataset of roughly 2.3 GiB. On Android devices with limited RAM this can cause heavy memory pressure or process termination. The default `light` mode uses substantially less memory to prioritize stability; it can produce a lower hashrate. Supported values are `auto`, `fast`, and `light`.

The config loader checks common address prefixes and lengths, but does **not** verify the address checksum or prove wallet ownership.

## Adaptive RandomX Optimizer

Run a short local stress sample before mining:

```bash
python run.py --optimize
```

The optimizer samples a small set of thread counts (normally 1, 2, 4, and up to 8) using XMRig's built-in `--stress` mode and the currently configured RandomX mode. It does **not** pass a wallet or pool endpoint, submit shares, or change `CPU_THREADS` automatically. XMRig stress mode may require internet access for its own setup, but it is not configured to mine to your pool. Results are saved to `logs/optimizer.json`.

Optional controls:

```bash
python run.py --optimize --optimizer-max-threads 6 --optimizer-timeout 30
```

Each candidate is sampled for 25 seconds by default (configurable from 10 to 120 seconds). The maximum thread count is capped at the detected CPU count. These short samples are only a starting point: sustained hashrate can fall due to Android thermal throttling. Monitor temperature and compare with a longer normal run before applying the recommendation. The optimizer only tests the configured RandomX mode and does not force RandomX fast mode on memory-limited phones.

## Optional overrides

The defaults can be overridden with environment variables, for example:

```bash
export XMR_WALLET_ADDRESS='YOUR_PUBLIC_MONERO_RECEIVING_ADDRESS'
export CPU_THREADS=2
export RANDOMX_MODE=light
export XMRIG_PATH="$HOME/xmrig/build/xmrig"
python run.py --check
```

Supported settings are `XMR_WALLET_ADDRESS`, `MINING_MODE=pool`, `RANDOMX_MODE`, `POOL_HOST`, `POOL_PORT`, `POOL_TLS`, `CPU_THREADS`, `XMRIG_PATH`, and `LOG_LEVEL`. Setting `MINING_MODE=solo` or `MINING_MODE=p2pool` is rejected. A local `.env` file is not loaded automatically.

## Pool and payouts

The built-in example uses XMRPool.eu at `xmrpool.eu:3333` with TLS. Check the pool's current official instructions and payout threshold before mining: https://www.xmrpool.eu/xmr-monero-easy-mining-guide.html. Its published minimum payment may be impractical for a low-hashrate phone. The pool may change its endpoint or payout rules.

The `pool` mode sends the wallet as XMRig's `--user`, sets `--pass x`, keeps the connection alive, and adds `--tls` when enabled. A pool's connection policy and payout rules still apply. Do not assume a pool will pay just because XMRig starts.

## Commands

```bash
python run.py --check
python run.py --optimize
python run.py
python -m unittest discover -s tests -v
```

`--check` validates settings and prints a planned command with the wallet hidden; it does not verify binary installation or network connectivity. `python run.py` launches XMRig, streams its output to `logs/miner.log`, logs nonzero XMRig exit statuses, and handles Ctrl+C shutdown. In an interactive Termux terminal it also renders a live dashboard with status, hashrate, estimated interval/total hashes, accepted/rejected shares, pool difficulty, last job, and log path. XMRig hashrate is printed every 10 seconds. Hash totals are estimates derived from reported rates, not exact counters; redirected/non-interactive output remains normal timestamped logs. Connection errors such as DNS failure or network-unreachable messages reset the displayed live hashrate to zero. `python main.py` remains a compatibility entry point.

## Important

Phone mining can cause heat, battery wear and throttling. Pool rewards depend on accepted work, pool rules, fees, payout thresholds, and luck; no payout is guaranteed. Review logs before sharing because miner output can include wallet and connection details. License has not yet been specified.
