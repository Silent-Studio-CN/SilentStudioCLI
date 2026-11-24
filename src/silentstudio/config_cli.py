"""ss config command."""
from __future__ import annotations

import sys

from .config import load_config, save_config
from .i18n import LANGUAGES, normalize_language
from .utils import get_system_language

KEYS = {
    "language": "auto | " + " | ".join(LANGUAGES),
    "install_scope": "user | system",
    "pypi_mirror": "PyPI mirror URL",
    "index_url": "SilentStudio index URL",
}


def _current(lang: str, scope: str) -> str:
    return f"当前安装范围: {scope}" if lang == "zh-CN" else f"Current install scope: {scope}"


def handle_config(argv: list[str]) -> int:
    config = load_config()
    lang = get_system_language(config.get("language", "auto"))

    if not argv:
        for key, desc in KEYS.items():
            print(f"{key} = {config.get(key, '')}    # {desc}")
        return 0

    key = argv[0].lower()
    if key == "install":
        key = "install_scope"

    if key not in KEYS:
        print(f"Unknown config key: {key}" if lang != "zh-CN" else f"未知配置项：{key}")
        print("Keys: " + ", ".join(KEYS))
        return 2

    value = argv[1] if len(argv) > 1 else None

    if key == "install_scope":
        if value is None:
            print(_current(lang, config.get("install_scope", "user")))
            prompt = "选择安装范围 [1] user [2] system: " if lang == "zh-CN" else "Install scope [1] user [2] system: "
            try:
                choice = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 130
            value = {"1": "user", "2": "system"}.get(choice, choice)
        value = value.lower()
        if value not in ("user", "system"):
            print("install_scope must be user or system")
            return 2

    if key == "language":
        if value is None:
            print(f"language = {config.get('language', 'auto')}")
            prompt = "选择语言（auto/en/zh-CN/zh-TW/ja/ko/ru/es/it）: "
            try:
                value = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 130
        if value != "auto":
            value = normalize_language(value)

    if key == "language" and value == "auto":
        from .language_pack import reset_first_run
        reset_first_run()

    config[key] = value
    save_config(config)
    print(f"{key} = {value}")
    return 0
