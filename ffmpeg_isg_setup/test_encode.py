"""
Smoke-test hardware encoding using FFmpeg NVENC.
"""
import subprocess
import sys
from pathlib import Path

from .log import logger

def smoke_test(ffmpeg_dir: Path) -> None:
    """Run a 5-second sample encode and check NVENC support."""
    sample = Path(__file__).parent / "sample.mp4"
    if not sample.exists():
        logger.warning("sample.mp4 not found; skipping smoke test")
        return
    cmd = [
        str(ffmpeg_dir / "bin" / "ffmpeg.exe"),
        "-hide_banner", "-y", "-hwaccel", "cuda",
        "-i", str(sample),
        "-c:v", "h264_nvenc", "-f", "null", "-"
    ]
    logger.info("Running NVENC smoke test")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or "NVENC" not in result.stderr:
        logger.error("Smoke test failed")
        sys.exit(1)
    logger.info("Smoke test passed")
