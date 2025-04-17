"""
PATH editing via winreg and environment broadcast.
"""
import os
import winreg
import ctypes
from .log import logger

def add_to_system_path(path: str) -> None:
    """Add a directory to the SYSTEM PATH and broadcast change."""
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        0, winreg.KEY_READ | winreg.KEY_WRITE
    )
    try:
        current, _ = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        current = ""
    paths = current.split(os.pathsep) if current else []
    if path in paths:
        logger.info(f"{path} already in system PATH")
    else:
        new_value = os.pathsep.join([current, path]) if current else path
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_value)
        logger.info(f"Added {path} to system PATH")
        # Broadcast WM_SETTINGCHANGE
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        res = ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            None
        )
        if not res:
            logger.warning("Failed to broadcast environment change")
    key.Close()
