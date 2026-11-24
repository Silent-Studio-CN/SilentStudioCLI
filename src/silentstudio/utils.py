import contextlib
import itertools
import locale
import subprocess
import sys
import threading
import time
from typing import Optional, Tuple


def detect_language() -> str:
    """检测系统语言"""
    from .i18n import detect_language as _detect
    return _detect()


def get_system_language(config_lang: str = "auto") -> str:
    """获取最终使用的语言"""
    from .i18n import get_language
    return get_language(config_lang)


def run_pip_command(args: list, scope: str = "user") -> Tuple[bool, str, str]:
    """执行 pip 命令"""
    cmd = [sys.executable, "-m", "pip"]
    cmd.extend(args)
    if scope == "user" and len(cmd) > 3:
        cmd.insert(4, "--user")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


@contextlib.contextmanager
def spinner(label: str = "", minimum: float = 1.5):
    """Print a label and animate a one-line spinner for at least minimum seconds."""
    if label:
        print(label, flush=True)
    if not sys.stdout.isatty():
        yield
        return

    stop = threading.Event()

    def animate() -> None:
        for char in itertools.cycle("-\\|/"):
            if stop.is_set():
                break
            print(f"\r{char}", end="", flush=True)
            time.sleep(0.12)

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    started = time.monotonic()
    try:
        yield
        remaining = minimum - (time.monotonic() - started)
        if remaining > 0:
            time.sleep(remaining)
    finally:
        stop.set()
        thread.join(timeout=1)
        print("\r" + " " * 8 + "\r", end="", flush=True)


def get_pip_packages() -> list:
    """获取所有已安装的 pip 包"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        return []
    except Exception:
        return []


def get_package_version(pkg_name: str) -> Optional[str]:
    """获取指定包的版本号"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", pkg_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def check_package_installed(pkg_name: str) -> bool:
    """检查包是否已安装"""
    return get_package_version(pkg_name) is not None