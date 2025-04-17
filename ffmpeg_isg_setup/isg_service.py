"""
ISG integration: stop/start service, deploy binary, patch config.
"""
import subprocess
import time
import shutil
import configparser
import sys
import winreg
from pathlib import Path
from .constants import DEFAULT_ISG_DIR
from .log import logger


def locate_isg_dir(cli_dir: str = None) -> Path:
    """Return the ISG install directory, preferring CLI override or registry."""
    if cli_dir:
        return Path(cli_dir)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Pixit\IconikStorageGateway")
        install, _ = winreg.QueryValueEx(key, "InstallDir")
        winreg.CloseKey(key)
        return Path(install)
    except OSError:
        logger.info(f"ISG registry not found; using default {DEFAULT_ISG_DIR}")
        return Path(DEFAULT_ISG_DIR)


def stop_isg_service(timeout: int = 30) -> None:
    """Stop the Iconik Storage Gateway service."""
    logger.info("Stopping Iconik Storage Gateway service")
    subprocess.run(["sc", "stop", "iconik Storage Gateway"], check=False)
    start = time.time()
    while time.time() - start < timeout:
        out = subprocess.run(["sc", "query", "iconik Storage Gateway"], capture_output=True, text=True)
        if "STOPPED" in out.stdout:
            logger.info("Service stopped")
            return
        time.sleep(1)
    logger.warning("Service stop timed out")


def deploy_binary(ffmpeg_dir: Path, isg_dir: Path) -> None:
    """Copy FFmpeg binaries into ISG bin directory."""
    bin_dir = isg_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    for exe in ("ffmpeg.exe", "ffprobe.exe"):
        src = ffmpeg_dir / "bin" / exe
        dst = bin_dir / exe
        shutil.copy2(src, dst)
        logger.info(f"Copied {exe} to {dst}")


def patch_config(isg_dir: Path, codec: str = "h264_nvenc", vbr: str = "8000k") -> None:
    """Patch ISG config.ini for proxy settings."""
    cfg = isg_dir / "config.ini"
    if not cfg.exists():
        logger.info("config.ini not found; skipping patch")
        return
    parser = configparser.ConfigParser()
    parser.read(cfg)
    section = "iconik"
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section, "proxy-videocodec", codec)
    parser.set(section, "proxy-vbr", vbr)
    with cfg.open('w') as f:
        parser.write(f)
    logger.info("Patched config.ini")


def start_isg_service() -> None:
    """Start the Iconik Storage Gateway service."""
    logger.info("Starting Iconik Storage Gateway service")
    subprocess.run(["sc", "start", "iconik Storage Gateway"], check=True)
    logger.info("Service start issued")


def integrate(ffmpeg_dir: Path, cli_dir: str = None, skip_isg: bool = False) -> None:
    """High-level ISG integration workflow."""
    if skip_isg:
        logger.info("ISG integration skipped")
        return
    isg_dir = locate_isg_dir(cli_dir)
    stop_isg_service()
    deploy_binary(ffmpeg_dir, isg_dir)
    patch_config(isg_dir)
    start_isg_service()
