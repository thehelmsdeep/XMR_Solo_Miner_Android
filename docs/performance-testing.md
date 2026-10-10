# RandomX performance testing on Android / Termux

The thread benchmark uses XMRig's **offline RandomX benchmark mode**. It does not connect to a pool, submit shares, or estimate earnings. It is for comparing thread counts on the same device.

## Requirements

- Python 3
- A working XMRig executable built with benchmark support (XMRig 6.4.0 or newer)
- Enough free memory for the selected RandomX mode

## Run on the phone

From the repository root:

```bash
python -m unittest discover -s tests -v
python tools/benchmark_randomx_threads.py --xmrig ~/xmrig/build/xmrig --threads 1,2,4,6,8 --bench 250K --mode light --repeats 2
```

For a longer test, use `--bench 500K` or `--bench 1M`; these can take considerably longer. The script writes a machine-readable report to `logs/randomx-benchmark.json` by default. Change it with `--json-out PATH`.

## Reading results

- Compare repeated results for each thread count; ignore a single unusually fast run.
- Keep the phone cool, remove its case if appropriate, and avoid charging during the comparison.
- The best sustained rate may be lower than the first run due to thermal throttling.
- `light` mode is the recommended starting point for phones with limited RAM. Do not force `fast` mode unless the device has enough available memory.
- An offline benchmark is not evidence of a successful pool connection. For pool mining, separately verify accepted shares in XMRig logs and the pool dashboard.

## Current defaults

The project defaults to 8 CPU threads based on the maintainer's on-device comparison. This is a starting point, not a guarantee that 8 threads will be best on every Android phone. Override it with `CPU_THREADS=4` (or another tested value) when launching the pool miner if sustained temperature or responsiveness is a concern.
