#!/data/data/com.termux/files/usr/bin/bash
set -u
printf 'Architecture: '; uname -m
printf 'Kernel: '; uname -r
printf 'Python: '; python --version 2>&1 || true
printf 'XMRig: '; command -v xmrig || echo 'not found'
printf 'Monero daemon: '; command -v monerod || echo 'not found'
printf 'P2Pool: '; command -v p2pool || echo 'not found'
printf '\nThis diagnostic does not install software or test network connectivity.\n'
