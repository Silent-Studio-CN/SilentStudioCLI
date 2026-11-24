import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from typing import Optional, Dict, Any, Tuple

import requests

from .config import load_config, load_installed, save_installed
from .sources import _version_key
from .utils import (
    get_system_language,
    run_pip_command,
    check_package_installed,
    get_package_version,
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


def _stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=3)
    except Exception:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                               capture_output=True)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass


def _run_pip_install(pkg_name: str, url: str, scope: str, lang: str):
    """Run pip under a pty for live progress, killing the process tree on Ctrl+C."""
    from .progress import InstallProgress

    temp_dir = tempfile.mkdtemp(prefix="ss-pip-")
    command = [sys.executable, "-m", "pip", "install", "--upgrade",
               "--progress-bar", "on", "--disable-pip-version-check",
               "-i", url, pkg_name]
    if scope == "user":
        command.insert(4, "--user")

    env = os.environ.copy()
    env.update({"TMPDIR": temp_dir, "TEMP": temp_dir, "TMP": temp_dir,
                "PYTHONUNBUFFERED": "1", "TERM": "xterm-256color"})

    # Keep pip on a pipe: a pty makes rich/terminal-size negotiation hang on
    # some terminals. The progress bars still update from pip stage events.
    use_pty = False
    master = None
    slave = None
    if use_pty:
        import pty
        master, slave = pty.openpty()
        kwargs = {"stdout": slave, "stderr": slave, "stdin": subprocess.DEVNULL}
    else:
        kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}

    kwargs["env"] = env
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    progress = InstallProgress(lang)
    proc = subprocess.Popen(command, **kwargs)
    if use_pty:
        os.close(slave)
        reader = os.fdopen(master, "rb", buffering=0)
    else:
        reader = proc.stdout

    progress.start()
    output = []
    buffer = []
    try:
        while True:
            chunk = reader.read(1) if reader else b""
            if not chunk:
                break
            char = chunk.decode("utf-8", "replace")
            if char in ("\r", "\n"):
                line = "".join(buffer).strip()
                buffer = []
                if not line:
                    continue
                output.append(line)
                if "Collecting" in line:
                    progress.update("collect", 100)
                if "Downloading" in line or "Using cached" in line:
                    progress.update("download", 0)
                match = re.search(r"(\d{1,3})%", line)
                if match:
                    progress.update("download", int(match.group(1)))
                if "Installing collected packages" in line:
                    progress.update("download", 100)
                    progress.update("install", 10)
                if "Successfully installed" in line:
                    progress.update("install", 100)
            else:
                buffer.append(char)
        proc.wait()
        if proc.returncode == 0:
            progress.finish()
            return True, ""
        progress.cancel()
        errors = [line for line in output if "ERROR" in line or "error:" in line]
        return False, "\n".join(errors[-8:] or output[-8:])
    except KeyboardInterrupt:
        _stop_process(proc)
        progress.cancel()
        raise
    finally:
        if proc.poll() is None:
            _stop_process(proc)
        try:
            reader.close()
        except Exception:
            pass
        if use_pty and master is not None:
            try:
                os.close(master)
            except Exception:
                pass
        shutil.rmtree(temp_dir, ignore_errors=True)


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

    success, stderr = _run_pip_install(pkg_name, url, scope, get_system_language())
    if success:
        installed = get_package_version(pkg_name)
        if installed:
            record_installation(pkg_name, installed, "pypi")
        return True, f"✅ 成功安装 {pkg_name} (版本: {installed or version or '未知'}, 源: {name})"

    return False, f"❌ 安装失败: {stderr}"

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
    
    # 1. 拉取 SilentStudio 索引（不显示独立动画，列表本身有进度）
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
