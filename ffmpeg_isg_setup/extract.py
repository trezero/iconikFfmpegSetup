"""
Extract and stage FFmpeg archive.
"""
import zipfile
import shutil
tempfile
from pathlib import Path
from .log import logger

def extract_ffmpeg(zip_path: Path, target_dir: Path = Path("C:/ffmpeg"), force: bool = False) -> Path:
    """Unzip archive and move to target_dir."""
    tmp = Path(tempfile.mkdtemp(prefix="ffmpeg_extract_"))
    logger.info(f"Extracting {zip_path} to {tmp}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(tmp)
    extracted = next(tmp.iterdir())
    if target_dir.exists():
        if force:
            logger.info(f"Removing existing {target_dir}")
            shutil.rmtree(target_dir)
        else:
            logger.info(f"{target_dir} exists; skipping extraction")
            return target_dir
    logger.info(f"Moving {extracted} to {target_dir}")
    shutil.move(str(extracted), str(target_dir))
    return target_dir
