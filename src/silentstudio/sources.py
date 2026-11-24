"""Multi-index PyPI version discovery."""
from __future__ import annotations

import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

from .config import load_config

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
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package,
             "-i", url, "--disable-pip-version-check"],
            capture_output=True, text=True, timeout=timeout,
        )
        versions = _parse_versions(result.stdout or result.stderr or "")
        return versions[0] if versions else None
    except Exception:
        return None


def query_all(package: str) -> List[Tuple[str, str, Optional[str]]]:
    return [(name, url, query_source(package, url)) for name, url in get_sources()]


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


def print_report(package: str, rows: Optional[List[Tuple[str, str, Optional[str]]]] = None) -> None:
    rows = rows if rows is not None else query_all(package)
    print(f"Package: {package}")
    print(f"{'Source':<12} {'Version':<16} URL")
    print("-" * 72)
    for name, url, version in rows:
        print(f"{name:<12} {version or 'not found':<16} {url}")


def handle_sources(package: str) -> int:
    print_report(package)
    return 0
