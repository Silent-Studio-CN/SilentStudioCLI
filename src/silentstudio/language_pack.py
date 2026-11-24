"""First-run IP language detection and remote language packs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import requests

from .config import load_config, save_config

PACK_DIR = Path.home() / ".silentstudio" / "lang"
MARKER = Path.home() / ".silentstudio" / ".language_initialized"
RAW_BASES = [
    "https://raw.githubusercontent.com/Silent-Studio-CN/SilentStudioCLI/main/lang",
    "https://gh-proxy.com/https://raw.githubusercontent.com/Silent-Studio-CN/SilentStudioCLI/main/lang",
    "https://ghproxy.net/https://raw.githubusercontent.com/Silent-Studio-CN/SilentStudioCLI/main/lang",
]

COUNTRY_LANGUAGE = {
    "CN": "zh-CN", "TW": "zh-TW", "HK": "zh-TW", "MO": "zh-TW",
    "JP": "ja", "KR": "ko", "RU": "ru",
    "ES": "es", "MX": "es", "AR": "es", "CO": "es", "CL": "es", "PE": "es",
    "IT": "it",
}


def detect_country() -> Optional[str]:
    for url in ("https://ipapi.co/country/", "https://ipinfo.io/country"):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                value = response.text.strip().upper()
                if len(value) == 2:
                    return value
        except Exception:
            continue
    return None


def language_for_country(country: Optional[str]) -> str:
    if not country:
        return "en"
    return COUNTRY_LANGUAGE.get(country.upper(), "en")


def download_pack(language: str) -> bool:
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    target = PACK_DIR / f"{language}.json"
    for base in RAW_BASES:
        try:
            response = requests.get(f"{base}/{language}.json", timeout=6)
            if response.status_code != 200:
                continue
            data = response.json()
            if not isinstance(data, dict):
                continue
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return True
        except Exception:
            continue
    return False


def first_run_language() -> Optional[str]:
    """Return a language on the first auto run, or None if already initialized."""
    config = load_config()
    if config.get("language", "auto") != "auto" or MARKER.exists():
        return None

    language = language_for_country(detect_country())
    download_pack(language)
    config["language"] = language
    save_config(config)
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(language + "\n", encoding="utf-8")
    return language


def reset_first_run() -> None:
    if MARKER.exists():
        MARKER.unlink()
