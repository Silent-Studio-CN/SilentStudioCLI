"""Cross-platform detection and command alias registration."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Tuple

ALIASES = ("ss", "silentstudio")


def current_platform() -> Tuple[str, str]:
    """Return normalized (os, arch), e.g. ("windows", "arm64")."""
    if sys.platform.startswith("win"):
        os_name = "windows"
    elif sys.platform == "darwin":
        os_name = "macos"
    else:
        os_name = "linux"

    machine = os.uname().machine.lower() if hasattr(os, "uname") else os.environ.get("PROCESSOR_ARCHITECTURE", "")
    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    elif machine in ("i386", "i686", "x86"):
        arch = "x86"
    else:
        arch = machine or "unknown"
    return os_name, arch


def is_windows() -> bool:
    return current_platform()[0] == "windows"


def script_directory() -> Path:
    """Directory where pip installs console entry points."""
    return Path(sys.executable).resolve().parent


def _alias_names() -> Tuple[str, str]:
    if is_windows():
        return "ss.exe", "silentstudio.exe"
    return "ss", "silentstudio"


def _current_alias() -> Optional[str]:
    name = Path(sys.argv[0]).name.lower()
    if name.endswith(".exe"):
        name = name[:-4]
    return name if name in ALIASES else None


def ensure_command_aliases() -> Optional[Path]:
    """Create the missing alias next to the installed entry point.

    Returns the created alias path, or None when both already exist.
    """
    current = _current_alias()
    if current is None:
        return None

    ss_name, silent_name = _alias_names()
    ss_path = script_directory() / ss_name
    silent_path = script_directory() / silent_name

    if current == "ss" and silent_path.exists():
        return None
    if current == "silentstudio" and ss_path.exists():
        return None

    source = Path(sys.argv[0])
    target = silent_path if current == "ss" else ss_path
    try:
        if target.exists():
            return None
        if is_windows():
            shutil.copy2(source, target)
        else:
            target.symlink_to(source.name)
        return target
    except OSError:
        try:
            shutil.copy2(source, target)
            return target
        except OSError:
            return None
