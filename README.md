# iconikFfmpegSetup

A CLI tool to automate GPU‑enabled FFmpeg installation and integrate with iconik Storage Gateway on Windows 11.

## Features

- Admin rights check
- NVIDIA GPU/driver detection and warning
- Chocolatey installation (with ffmpeg package)
- System PATH configuration
- iconik Storage Gateway integration
- NVENC hardware encoding smoke test
- Human‑readable and machine JSON logging

## Prerequisites

- Windows 11 x64 (22H2 or later) – Admin privileges required  
- PowerShell 7+  
- Python 3.10–3.12 (for development)

## Installation

```powershell
git clone https://github.com/trezero/iconikFfmpegSetup.git
cd iconikFfmpegSetup
pip install .
```

## Usage

```powershell
python -m ffmpeg_isg_setup
```

### Options

- `--isg-dir <path>`: iconik Storage Gateway install directory (default: from registry or `C:\Program Files\IconikStorageGateway`)  
- `--offline-cache <dir>`: Reuse pre‑downloaded artifacts  
- `--force`: Overwrite existing FFmpeg installation  
- `--no-isg`: Skip Storage Gateway integration  

## Logs

- `setup_report.txt`: human‑readable summary  
- `setup_report.json`: machine‑readable audit log  

## Development

- Edit source in `ffmpeg_isg_setup/`  
- Install dev requirements: `pip install -r requirements.txt`  
- Run tests: `pytest`

## CI

GitHub Actions workflow for self‑hosted Windows GPU runner is located under `.github/workflows`.

## License

MIT License. See [LICENSE](LICENSE).