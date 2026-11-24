#!/usr/bin/env python3
import argparse
import subprocess
import sys
from typing import Optional

from . import __version__
from .config import load_config
from .utils import get_system_language
from .installer import handle_install
from .list_packages import handle_list_packages
from .project_new import handle_new
from .sources import handle_sources
from .platform import ensure_command_aliases


def show_help(lang: str) -> None:
    """显示帮助信息"""
    from .i18n import help_text
    print(help_text(__version__, lang))


GIT_COMMANDS = {
    "status", "log", "diff", "add", "commit", "push", "pull", "fetch",
    "branch", "checkout", "switch", "restore", "remote", "tag", "stash",
}


def _main():
    """主入口"""
    ensure_command_aliases()

    from .language_pack import first_run_language
    from .i18n import apply_cached_pack

    detected = first_run_language()
    config = load_config()
    lang = detected or get_system_language(config.get("language", "auto"))
    apply_cached_pack(lang)

    argv = sys.argv[1:]
    if argv and argv[0] in ("release", "releases"):
        from .release import handle_release
        return handle_release(argv[1:])
    if argv and argv[0] == "git":
        return subprocess.call(["git", *argv[1:]])
    if argv and argv[0] in GIT_COMMANDS:
        return subprocess.call(["git", *argv])
    if argv and argv[0] == "install" and len(argv) > 1 and argv[1] != "list":
        return handle_install(argv[1], lang)
    if argv and argv[0] == "config":
        from .config_cli import handle_config
        return handle_config(argv[1:])
    if argv and argv[0].startswith("-") and argv[0] not in ("-v", "--version", "-h", "--help"):
        print("Unknown option: " + argv[0])
        return 2
    
    # 检查是否有参数
    if len(sys.argv) == 1:
        show_help(lang)
        return 0
    
    # 解析参数
    parser = argparse.ArgumentParser(
        prog="silentstudio",
        description="SilentStudio CLI - 让开发者体验更好一点" if lang == "zh-CN" else "SilentStudio CLI - Making developer experience better",
        add_help=False  # 自定义帮助
    )
    
    # 全局选项
    parser.add_argument("-v", "--version", action="store_true", help="显示版本号")
    parser.add_argument("-h", "--help", action="store_true", help="显示帮助信息")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # new 子命令
    new_parser = subparsers.add_parser("new", help="创建新项目", add_help=False)
    new_parser.add_argument("name", help="项目名称")
    new_parser.add_argument("-l", "--lang", dest="language", required=True, help="编程语言 (java/python/go)")
    
    # install list 子命令
    install_parser = subparsers.add_parser("install", help="安装相关", add_help=False)
    install_subparsers = install_parser.add_subparsers(dest="install_cmd", help="安装子命令")
    list_parser = install_subparsers.add_parser("list", help="列出已安装的库", add_help=False)

    sources_parser = subparsers.add_parser("sources", help="查看各 PyPI 源的版本", add_help=False)
    sources_parser.add_argument("package", help="包名")
    
    # 解析已知参数，忽略未知（处理 silentstudio <pkg_name>）
    args, unknown = parser.parse_known_args()
    
    # 处理 -h/--help
    if args.help or (len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help")):
        show_help(lang)
        return 0
    
    # 处理 -v/--version
    if args.version:
        print(f"SilentStudio CLI v{__version__}")
        return 0
    
    
    # 处理子命令
    if args.command == "new":
        return handle_new(args.name, args.language)
    
    if args.command == "sources":
        return handle_sources(args.package)

    if args.command == "install":
        if args.install_cmd == "list":
            return handle_list_packages()
        else:
            if lang == "zh-CN":
                print("❌ 未知的 install 子命令，请使用: silentstudio install list")
            else:
                print("❌ Unknown install subcommand, use: silentstudio install list")
            return 1
    
    # 处理 silentstudio <pkg_name> (安装)
    if len(sys.argv) >= 2:
        pkg_name = sys.argv[1]
        # 排除命令本身
        if pkg_name not in ("new", "install", "-v", "--version", "-h", "--help"):
            return handle_install(pkg_name, lang)
    
    # 默认显示帮助
    show_help(lang)
    return 0


def main():
    try:
        return _main()
    except KeyboardInterrupt:
        try:
            from .sources import terminate_all
            terminate_all()
        except Exception:
            pass
        from .i18n import tr
        print("\n" + tr("cancelled", get_system_language()))
        return 130


if __name__ == "__main__":
    sys.exit(main())