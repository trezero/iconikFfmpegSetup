"""
CLI entrypoint for ffmpeg_isg_setup.
"""
import argparse
import sys
from pathlib import Path
import subprocess
import shutil

from .constants import require_admin, DEFAULT_FFMPEG_URL, DEFAULT_ISG_DIR
from .log import logger
from .gpu import check_gpu_driver
from .isg_service import integrate
from .test_encode import smoke_test


def main():
    require_admin()
    parser = argparse.ArgumentParser(prog="ffmpeg_isg_setup")
    parser.add_argument("--ffmpeg-url", default=DEFAULT_FFMPEG_URL, help="URL for FFmpeg zip")
    parser.add_argument("--isg-dir", default=DEFAULT_ISG_DIR, help="Iconik Storage Gateway directory")
    parser.add_argument("--offline-cache", help="Path to offline cache directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing FFmpeg installation")
    parser.add_argument("--no-isg", action="store_true", help="Skip ISG integration")
    args = parser.parse_args()

    logger.info("Starting ffmpeg ISG setup")
    # Step 1: GPU check
    gpu_name, driver = check_gpu_driver()

    # Step 2: Install FFmpeg via Chocolatey
    try:
        subprocess.run(["choco", "--version"], capture_output=True, check=True)
        logger.info("Chocolatey detected")
    except FileNotFoundError:
        logger.info("Chocolatey not found: installing Chocolatey")
        ps_cmd = (
            "Set-ExecutionPolicy Bypass -Scope Process -Force; "
            "[System.Net.ServicePointManager]::SecurityProtocol = "
            "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        )
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-InputFormat",
                "None",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_cmd,
            ],
            check=True,
        )
    logger.info("Installing FFmpeg via Chocolatey")
    subprocess.run(["choco", "install", "ffmpeg", "--yes"], check=True)
    # Determine FFmpeg install path
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        logger.error("ffmpeg not found after Chocolatey installation")
        sys.exit(1)
    ffmpeg_dir = Path(ffmpeg_path).parent.parent

    # Step 5: ISG integration
    integrate(ffmpeg_dir, args.isg_dir, skip_isg=args.no_isg)

    # Step 6: Smoke test
    smoke_test(ffmpeg_dir)

    logger.info("Completed ffmpeg ISG setup")


if __name__ == "__main__":
    sys.exit(main())
