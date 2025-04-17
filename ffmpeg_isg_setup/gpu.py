"""
GPU and driver detection via nvidia-smi.
"""
import subprocess
import sys
from .log import logger

def check_gpu_driver(min_driver=570):
    """Check for NVIDIA GPU and driver version >= min_driver.xxx.

    Exits with code 20 if no GPU detected. Warns if driver older.
    Returns (gpu_name, driver_version).
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        logger.error("No NVIDIA GPU detected.")
        sys.exit(20)
    except subprocess.CalledProcessError as e:
        logger.error(f"nvidia-smi failed: {e.stderr.strip()}")
        sys.exit(20)

    line = result.stdout.strip().splitlines()[0]
    name, drv = [s.strip() for s in line.split(",", 1)]
    major = int(drv.split(".")[0])
    if major < min_driver:
        logger.warning(f"Old driver ({drv}). NVENC may not be available.")
    else:
        logger.info(f"Found GPU {name} with driver {drv}.")
    return name, drv
