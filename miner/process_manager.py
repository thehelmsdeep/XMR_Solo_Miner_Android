"""Launch and stop an installed XMRig process."""
import logging
import shutil
import subprocess
from pathlib import Path
from config import LOG_DIR, Settings
from miner.xmrig import build_command

def configure_logging(level: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "miner.log", encoding="utf-8")])

def run_miner(settings: Settings) -> int:
    command = build_command(settings)
    found = shutil.which(command[0])
    if found:
        command[0] = found
    elif Path(command[0]).expanduser().is_file():
        command[0] = str(Path(command[0]).expanduser().resolve())
    else:
        logging.error("XMRig executable not found: %s; install it or set XMRIG_PATH", settings.xmrig_path)
        return 127
    logging.info("Launching XMRig mode=%s threads=%s; arguments are not logged", settings.mining_mode, settings.cpu_threads)
    try:
        process = subprocess.Popen(command)
        return process.wait()
    except KeyboardInterrupt:
        logging.info("Stopping XMRig")
        process.terminate()
        try:
            return process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait()
