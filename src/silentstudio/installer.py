import json
import sys
from typing import Optional, Dict, Any, Tuple

import requests

from .config import load_config, load_installed, save_installed
from .sources import _version_key
from .utils import (
    get_system_language,
    run_pip_command,
    check_package_installed,
    get_package_version,
    spinner as animate_spinner,
)


def fetch_index() -> list:
    """从服务器拉取索引"""
    config = load_config()
    index_url = config.get("index_url", "")
    
    try:
        resp = requests.get(index_url, timeout=10)
        if resp.status_code == 200:
            entries = []
            for line in resp.text.splitlines():
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return entries
        return []
    except Exception:
        return []


def check_pypi(pkg_name: str) -> Tuple[bool, Optional[str]]:
    """检查 PyPI 上是否存在该包"""
    try:
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            version = data.get("info", {}).get("version")
            return True, version
        return False, None
    except Exception:
        return False, None


def _choose_source(rows, lang: str):
    if not sys.stdin.isatty():
        best = max(rows, key=lambda item: _version_key(item[2])) if any(r[2] for r in rows) else rows[0]
        return best

    while True:
        prompt = "选择安装源: " if lang == "zh-CN" else "Select source: "
        try:
            choice = input(prompt).strip()
        except EOFError:
            print()
            return max(rows, key=lambda item: _version_key(item[2])) if any(r[2] for r in rows) else rows[0]
        if not choice:
            return max(rows, key=lambda item: _version_key(item[2])) if any(r[2] for r in rows) else rows[0]
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(rows):
                return rows[index - 1]
        for row in rows:
            if row[0].lower() == choice.lower():
                return row
        print("无效的源，请重新输入。" if lang == "zh-CN" else "Invalid source, try again.")


def install_package(pkg_name: str, channel: str = "pypi", source=None) -> Tuple[bool, str]:
    """安装包；source 为空时查询所有源并交互选择。"""
    config = load_config()
    scope = config.get("install_scope", "user")

    if channel != "pypi":
        return False, f"❌ 不支持的渠道: {channel}"

    from .sources import query_all, print_report, get_sources, _version_key

    if source is None:
        rows = query_all(pkg_name, spinner=True)
        if not sys.stdout.isatty():
            print_report(pkg_name, rows, show_package=False)
        if not rows:
            return False, f"❌ 未找到 {pkg_name} 的任何源"
        source = _choose_source(rows, get_system_language())

    name, url, version = source
    if not version:
        print(f"{name} 并没有查询到 {pkg_name}，将尝试执行安装命令 1/1" if get_system_language() == "zh-CN"
              else f"{name} did not report {pkg_name}; trying install anyway (1/1)")

    success, stdout, stderr = run_pip_command(
        ["install", "--upgrade", "-i", url, pkg_name],
        scope=scope,
    )
    if success:
        installed = get_package_version(pkg_name)
        if installed:
            record_installation(pkg_name, installed, "pypi")
        return True, f"✅ 成功安装 {pkg_name} (版本: {installed or version or '未知'}, 源: {name})"

    return False, f"❌ 安装失败: {stderr or stdout}"

def record_installation(name: str, version: str, channel: str) -> None:
    """记录安装到 installed.json"""
    data = load_installed()
    
    # 检查是否已存在
    for pkg in data["installed"]:
        if pkg["name"] == name:
            pkg["version"] = version
            pkg["channel"] = channel
            pkg["installed_at"] = __import__("datetime").datetime.now().isoformat()
            save_installed(data)
            return
    
    # 新增
    data["installed"].append({
        "name": name,
        "version": version,
        "channel": channel,
        "installed_at": __import__("datetime").datetime.now().isoformat()
    })
    save_installed(data)


def handle_install(pkg_name: str, lang: str) -> int:
    """处理安装逻辑"""
    # 检查是否已安装
    if check_package_installed(pkg_name):
        version = get_package_version(pkg_name)
        msg_zh = f"✅ {pkg_name} 已安装 (版本: {version})"
        msg_en = f"✅ {pkg_name} is already installed (version: {version})"
        print(msg_zh if lang == "zh-CN" else msg_en)
        return 0
    
    # 1. 拉取 SilentStudio 索引
    label = "正在查询 SilentStudio 索引..." if lang == "zh-CN" else "Querying SilentStudio index..."
    with animate_spinner(label):
        index = fetch_index()
    
    # 查找匹配
    matched = None
    for entry in index:
        if entry.get("name", "").lower() == pkg_name.lower():
            matched = entry
            break
        # 也通过 pkg_name 匹配
        if entry.get("pkg_name", "").lower() == pkg_name.lower():
            matched = entry
            break
    
    if matched:
        channel = matched.get("channel", "pypi")
        pkg_name_actual = matched.get("pkg_name", pkg_name)
        
        if channel == "pypi":
            print(f"📦 从 PyPI 安装 {pkg_name_actual}..." if lang == "zh-CN" else f"📦 Installing {pkg_name_actual} from PyPI...")
            success, msg = install_package(pkg_name_actual, "pypi")
            print(msg)
            return 0 if success else 1
    
    if not matched:
        print(f"[{pkg_name}] 未在已配置的所有源列表中找到" if lang == "zh-CN"
              else f"[{pkg_name}] was not found in any configured source")

    target = matched.get("pkg_name", pkg_name) if matched else pkg_name
    success, msg = install_package(target, "pypi")
    print(msg)
    return 0 if success else 1
