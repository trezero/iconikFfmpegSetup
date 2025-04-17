"""
Download and verify FFmpeg archive with resume support.
"""
import sys
import hashlib
import requests
import tempfile
from pathlib import Path

from .log import logger

def download_with_resume(url: str, dest: Path) -> Path:
    """Download a file with HTTP Range resume to destination path."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    existing = dest.stat().st_size if dest.exists() else 0
    headers = {}
    if existing:
        headers['Range'] = f"bytes={existing}-"
        logger.info(f"Resuming download for {dest.name} at byte {existing}")
    else:
        logger.info(f"Starting download for {dest.name}")
    try:
        r = requests.get(url, stream=True, headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        sys.exit(1)
    mode = 'ab' if existing else 'wb'
    with open(dest, mode) as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest

def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 of a file."""
    hash_sha = hashlib.sha256()
    with file_path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_sha.update(chunk)
    return hash_sha.hexdigest()

def fetch_ffmpeg_archive(ffmpeg_url: str, cache_dir: str = None) -> Path:
    """
    Download (or reuse offline cache) and verify FFmpeg ZIP archive.
    Returns path to FFmpeg ZIP.
    """
    zip_name = ffmpeg_url.rsplit('/', 1)[-1]
    base_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / 'ffmpeg_isg_setup'
    base_dir.mkdir(parents=True, exist_ok=True)
    zip_path = base_dir / zip_name
    sha_url = ffmpeg_url + '.sha256'
    sha_path = base_dir / f"{zip_name}.sha256"

    if cache_dir:
        # Offline cache: verify and reuse
        if not zip_path.exists() or not sha_path.exists():
            logger.error(f"Offline cache missing {zip_path} or {sha_path}")
            sys.exit(1)
        expected = sha_path.read_text().split()[0]
        actual = compute_sha256(zip_path)
        if actual != expected:
            logger.error(f"SHA256 mismatch in cache: expected {expected}, got {actual}")
            sys.exit(1)
        logger.info(f"Verified cached FFmpeg archive at {zip_path}")
        return zip_path

    # Download SHA file and archive
    download_with_resume(sha_url, sha_path)
    expected = sha_path.read_text().split()[0]
    download_with_resume(ffmpeg_url, zip_path)
    actual = compute_sha256(zip_path)
    if actual != expected:
        logger.error(f"SHA256 mismatch: expected {expected}, got {actual}")
        sys.exit(1)
    logger.info(f"Downloaded and verified FFmpeg archive at {zip_path}")
    return zip_path
