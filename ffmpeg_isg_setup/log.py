"""
Logging configuration for ffmpeg_isg_setup using Rich.
"""
import logging
from rich.console import Console
from rich.logging import RichHandler

console = Console()
logger = logging.getLogger("ffmpeg_isg_setup")
logger.setLevel(logging.INFO)
handler = RichHandler(console=console, show_time=False, show_level=True, show_path=False)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
