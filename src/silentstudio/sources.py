"""Multi-index PyPI version discovery."""
from __future__ import annotations

import itertools
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple

from .config import load_config
from .utils import spinner as animate_spinner

_ACTIVE = set()
_ACTIVE_LOCK = threading.Lock()
_CANCELLED = threading.Event()


def terminate_all() -> None:
    """Stop every in-flight source query immediately."""
    _CANCELLED.set()
    with _ACTIVE_LOCK:
        processes = list(_ACTIVE)
    for proc in processes:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                               capture_output=True)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


DEFAULT_SOURCES: List[Tuple[str, str]] = [
    ("PyPI", "https://pypi.org/simple"),
    ("Aliyun", "https://mirrors.aliyun.com/pypi/simple"),
    ("Tsinghua", "https://pypi.tuna.tsinghua.edu.cn/simple"),
    ("Tencent", "https://mirrors.cloud.tencent.com/pypi/simple"),
]


def get_sources() -> List[Tuple[str, str]]:
    config = load_config()
    raw = config.get("pypi_sources")
    if isinstance(raw, list) and raw:
        result = []
        for item in raw:
            if isinstance(item, dict) and item.get("name") and item.get("url"):
                result.append((item["name"], item["url"]))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                result.append((str(item[0]), str(item[1])))
        if result:
            return result
    return list(DEFAULT_SOURCES)


def _parse_versions(output: str) -> List[str]:
    match = re.search(r"Available versions:\s*(.+)", output)
    if match:
        return [v.strip() for v in match.group(1).split(",") if v.strip()]
    match = re.search(r"^\S+\s+\(([^)]+)\)", output, re.MULTILINE)
    return [match.group(1).strip()] if match else []


def query_source(package: str, url: str, timeout: int = 30) -> Optional[str]:
    """Return the newest version advertised by one index, or None."""
    if _CANCELLED.is_set():
        return None
    command = [sys.executable, "-m", "pip", "index", "versions", package,
               "-i", url, "--disable-pip-version-check"]
    kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
              "text": True, "encoding": "utf-8", "errors": "replace"}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(command, **kwargs)
    except Exception:
        return None
    with _ACTIVE_LOCK:
        _ACTIVE.add(proc)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        versions = _parse_versions(stdout or stderr or "")
        return versions[0] if versions else None
    except subprocess.TimeoutExpired:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                               capture_output=True)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            proc.kill()
        return None
    except Exception:
        return None
    finally:
        with _ACTIVE_LOCK:
            _ACTIVE.discard(proc)


def _stream_table(package: str, sources, minimum: float = 1.5):
    """Query all sources concurrently and animate each version cell."""
    rows = [None] * len(sources)

    def worker(index: int, url: str) -> None:
        rows[index] = query_source(package, url)

    threads = []
    for index, (_, url) in enumerate(sources):
        thread = threading.Thread(target=worker, args=(index, url), daemon=True)
        thread.start()
        threads.append(thread)

    print(f"Package: {package}")
    width = max(40, shutil.get_terminal_size((80, 24)).columns - 1)
    header = f"{'Source':<12} {'Version':<16} URL"[:width]
    print(header)
    print("-" * min(72, width))

    def line_for(cell: str, name: str, url: str) -> str:
        return f"{name:<12} {cell:<16} {url}"[:width]

    for index, (name, url) in enumerate(sources):
        print(line_for("", name, url))

    started = time.monotonic()
    frames = itertools.cycle("|/-\\")
    sys.stdout.write("\x1b[?25l")
    try:
        while True:
            pending = [index for index, value in enumerate(rows) if value is None]
            elapsed = time.monotonic() - started
            # As soon as one source resolves, let the user choose; the other
            # queries keep running in the background.
            if elapsed >= minimum and (not pending or any(value for value in rows)):
                break
            sys.stdout.write(f"\x1b[{len(sources)}A")
            for index, (name, url) in enumerate(sources):
                cell = rows[index] or next(frames)
                sys.stdout.write("\r" + line_for(cell, name, url).ljust(width) + "\n")
            sys.stdout.flush()
            time.sleep(0.12)
        sys.stdout.write(f"\x1b[{len(sources)}A")
        for index, (name, url) in enumerate(sources):
            sys.stdout.write("\r" + line_for(rows[index] or "...", name, url).ljust(width) + "\n")
        sys.stdout.flush()
    finally:
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()
    return [(name, url, rows[index]) for index, (name, url) in enumerate(sources)]


def query_all(package: str, spinner: bool = False) -> List[Tuple[str, str, Optional[str]]]:
    sources = get_sources()
    if spinner and sys.stdout.isatty():
        return _stream_table(package, sources)
    return [(name, url, query_source(package, url)) for name, url in sources]


def _version_key(value: Optional[str]) -> Tuple[int, ...]:
    if not value:
        return ()
    try:
        from packaging.version import Version
        return tuple(Version(value).release)
    except Exception:
        return tuple(int(p) for p in re.findall(r"\d+", value)[:4])


def best_source(package: str) -> Optional[Tuple[str, str, str]]:
    """Return (name, url, version) for the index with the newest version."""
    found = [(name, url, version) for name, url, version in query_all(package) if version]
    if not found:
        return None
    return max(found, key=lambda item: _version_key(item[2]))


def print_report(package: str, rows: Optional[List[Tuple[str, str, Optional[str]]]] = None, show_package: bool = True) -> None:
    rows = rows if rows is not None else query_all(package)
    if show_package:
        print(f"Package: {package}")
    print(f"{'Source':<12} {'Version':<16} URL")
    print("-" * 72)
    for name, url, version in rows:
        print(f"{name:<12} {version or 'not found':<16} {url}")


def handle_sources(package: str) -> int:
    print_report(package)
    return 0
