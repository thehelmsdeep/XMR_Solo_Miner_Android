"""Launch XMRig, save its logs, and render a compact live Termux dashboard."""
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from config import LOG_DIR, Settings
from miner.dashboard import MinerDashboard
from miner.xmrig import build_command


def configure_logging(level: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "miner.log", encoding="utf-8"),
        ],
        force=True,
    )


def _render_dashboard(dashboard: MinerDashboard) -> None:
    # Clear only an interactive terminal; redirected output remains ordinary logs.
    if sys.stdout.isatty():
        print("\033[2J\033[H" + dashboard.render(), flush=True)


def run_miner(settings: Settings) -> int:
    command = build_command(settings)
    executable = shutil.which(command[0])
    if executable:
        command[0] = executable
    elif Path(command[0]).expanduser().is_file():
        command[0] = str(Path(command[0]).expanduser().resolve())
    else:
        logging.error("XMRig executable not found: %s; install it or set XMRIG_PATH", settings.xmrig_path)
        return 127

    logging.info(
        "Launching XMRig mode=%s threads=%s randomx_mode=%s; command arguments are not logged",
        settings.mining_mode,
        settings.cpu_threads,
        settings.randomx_mode,
    )
    dashboard = MinerDashboard(settings.wallet_address, str(LOG_DIR / "miner.log"))
    process = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        _render_dashboard(dashboard)
        if process.stdout is not None:
            for line in process.stdout:
                message = line.rstrip()
                logging.info("XMRig: %s", message)
                if dashboard.consume(message):
                    _render_dashboard(dashboard)
        return_code = process.wait()
        if return_code != 0:
            logging.warning("XMRig exited with status %s", return_code)
        else:
            logging.info("XMRig exited normally")
        return return_code
    except KeyboardInterrupt:
        logging.info("Stopping XMRig")
        if process is None:
            return 130
        process.terminate()
        try:
            return process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logging.warning("XMRig did not stop in time; killing it")
            process.kill()
            return process.wait()
    finally:
        if process is not None and process.stdout is not None:
            process.stdout.close()
