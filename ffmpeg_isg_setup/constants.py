import ctypes
import sys

DEFAULT_FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.zip"
DEFAULT_ISG_DIR = "C:\\Program Files\\IconikStorageGateway"

def require_admin():
    """Exit if not run as admin."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        sys.exit("❌  Run this script from an elevated PowerShell or Command Prompt.")
