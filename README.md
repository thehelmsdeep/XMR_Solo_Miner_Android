# XMR Solo Miner Android

A Python launcher for an already-installed XMRig binary on Termux, with P2Pool, standard pool, and solo command modes.

> **Early development:** this repository does not install XMRig, run a Monero node or P2Pool, or verify payouts. Passing unit tests does not prove mining works on a device.

## Requirements

- Termux and Python 3.10+
- A compatible XMRig executable built for your Android device

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

- Receiving wallet: the public Monero address currently set in `config.py`
- Mining mode: `pool`
- CPU threads: `8` (higher phone heat and battery use are possible)
- RandomX mode: `light` (lower memory use, usually lower hashrate)
- XMRig path: `/data/data/com.termux/files/home/xmrig/build/xmrig`
- Pool endpoint: `xmrpool.eu:3333`
- TLS: enabled

RandomX fast mode allocates a dataset of roughly 2.3 GiB. On Android devices with limited RAM this can cause heavy memory pressure or process termination. The default `light` mode uses substantially less memory to prioritize stability; it can produce a lower hashrate. If your device has sufficient RAM and you want to test fast mode, set `RANDOMX_MODE=fast`. Supported values are `auto`, `fast`, and `light`.

The config loader checks common address prefixes and lengths, but does **not** verify the address checksum or prove wallet ownership.

## Optional overrides

The defaults can be overridden with environment variables, for example:

```bash
export XMR_WALLET_ADDRESS='YOUR_PUBLIC_MONERO_RECEIVING_ADDRESS'
export CPU_THREADS=2
export RANDOMX_MODE=light
export XMRIG_PATH="$HOME/xmrig/build/xmrig"
python run.py --check
```

Other supported settings include `XMR_WALLET_ADDRESS`, `MINING_MODE` (`p2pool`, `pool`, or `solo`), `RANDOMX_MODE`, `POOL_HOST`, `POOL_PORT`, `POOL_TLS`, P2Pool endpoint settings, Monero daemon RPC settings, and `LOG_LEVEL`. A local `.env` file is not loaded.

## Pool and payouts

The built-in example uses XMRPool.eu at `xmrpool.eu:3333` with TLS. Check the pool's current official instructions and payout threshold before mining: https://www.xmrpool.eu/xmr-monero-easy-mining-guide.html. Its published minimum payment may be impractical for a low-hashrate phone. The pool may change its endpoint or payout rules.

The `pool` mode sends the wallet as XMRig's `--user`, sets `--pass x`, and adds `--tls`. A pool's connection policy and payout rules still apply. Do not assume a pool will pay just because XMRig starts.

## Commands

```bash
python run.py --check
python run.py
python -m unittest discover -s tests -v
```

`--check` validates settings and prints a planned command with the wallet hidden; it does not verify binary installation or network connectivity. `python run.py` launches XMRig, streams its output to `logs/miner.log`, logs nonzero XMRig exit statuses, and handles Ctrl+C shutdown. In an interactive Termux terminal it also renders a live dashboard with status, hashrate, estimated interval/total hashes, accepted/rejected shares, pool difficulty, last job, and log path. XMRig hashrate is printed every 10 seconds. Hash totals are estimates derived from reported rates, not exact counters; redirected/non-interactive output remains normal timestamped logs. Connection errors such as DNS failure or network-unreachable messages reset the displayed live hashrate to zero. `python main.py` remains a compatibility entry point.

## Important

Phone mining can cause heat, battery wear and throttling. Pool rewards depend on accepted work, pool rules, fees, payout thresholds, and luck; no payout is guaranteed. Review logs before sharing because miner output can include wallet and connection details. License has not yet been specified.
