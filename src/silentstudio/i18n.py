"""Small built-in localization layer for the CLI."""
from __future__ import annotations

import locale
import os
from typing import Dict

LANGUAGES: Dict[str, str] = {
    "en": "English",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "Русский",
    "es": "Español",
    "it": "Italiano",
}

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "cancelled": "Cancelled.",
        "project": "Project name",
        "repository": "Repository",
        "workflow": "Workflow",
        "ref": "Ref",
        "tag": "Tag template",
        "saved": "Saved {project} to {path}",
        "invalid_repo": "Invalid repository: {repo!r}. Expected owner/repo",
        "configured": "Configured projects:",
        "usage": "Usage: ss release <project> <version> [commit]",
        "no_projects": "No projects configured. Run: ss release config",
        "version_required": "version is required",
        "unknown_project": "Project '{project}' is not configured. Run: ss release config {project}",
        "package": "Package",
        "source": "Source",
        "version": "Version",
        "not_found": "not found",
    },
    "zh-CN": {
        "cancelled": "已取消。",
        "project": "项目名称",
        "repository": "仓库",
        "workflow": "工作流",
        "ref": "引用",
        "tag": "Tag 模板",
        "saved": "已保存 {project} 到 {path}",
        "invalid_repo": "仓库格式无效：{repo!r}，应为 owner/repo",
        "configured": "已配置项目：",
        "usage": "用法：ss release <project> <version> [commit]",
        "no_projects": "还没有配置项目。运行：ss release config",
        "version_required": "缺少版本号",
        "unknown_project": "项目 '{project}' 未配置。运行：ss release config {project}",
        "package": "包名",
        "source": "源",
        "version": "版本",
        "not_found": "未找到",
    },
    "zh-TW": {
        "cancelled": "已取消。",
        "project": "專案名稱",
        "repository": "倉庫",
        "workflow": "工作流程",
        "ref": "參照",
        "tag": "Tag 範本",
        "saved": "已儲存 {project} 到 {path}",
        "invalid_repo": "倉庫格式無效：{repo!r}，應為 owner/repo",
        "configured": "已設定專案：",
        "usage": "用法：ss release <project> <version> [commit]",
        "no_projects": "尚未設定專案。執行：ss release config",
        "version_required": "缺少版本號",
        "unknown_project": "專案 '{project}' 未設定。執行：ss release config {project}",
        "package": "套件",
        "source": "來源",
        "version": "版本",
        "not_found": "找不到",
    },
    "ja": {
        "cancelled": "キャンセルしました。",
        "project": "プロジェクト名",
        "repository": "リポジトリ",
        "workflow": "ワークフロー",
        "ref": "参照",
        "tag": "タグのテンプレート",
        "saved": "{project} を {path} に保存しました",
        "invalid_repo": "リポジトリ形式が無効です: {repo!r}（owner/repo）",
        "configured": "設定済みプロジェクト:",
        "usage": "使い方: ss release <project> <version> [commit]",
        "no_projects": "プロジェクトが未設定です。実行: ss release config",
        "version_required": "バージョンが必要です",
        "unknown_project": "プロジェクト '{project}' は未設定です。実行: ss release config {project}",
        "package": "パッケージ",
        "source": "ソース",
        "version": "バージョン",
        "not_found": "見つかりません",
    },
    "ko": {
        "cancelled": "취소되었습니다.",
        "project": "프로젝트 이름",
        "repository": "저장소",
        "workflow": "워크플로",
        "ref": "참조",
        "tag": "태그 템플릿",
        "saved": "{project}을(를) {path}에 저장했습니다",
        "invalid_repo": "저장소 형식이 잘못되었습니다: {repo!r} (owner/repo)",
        "configured": "설정된 프로젝트:",
        "usage": "사용법: ss release <project> <version> [commit]",
        "no_projects": "설정된 프로젝트가 없습니다. 실행: ss release config",
        "version_required": "버전이 필요합니다",
        "unknown_project": "프로젝트 '{project}'이(가) 설정되지 않았습니다. 실행: ss release config {project}",
        "package": "패키지",
        "source": "소스",
        "version": "버전",
        "not_found": "찾을 수 없음",
    },
    "ru": {
        "cancelled": "Отменено.",
        "project": "Имя проекта",
        "repository": "Репозиторий",
        "workflow": "Workflow",
        "ref": "Ветка/ref",
        "tag": "Шаблон тега",
        "saved": "Сохранено {project} в {path}",
        "invalid_repo": "Неверный формат репозитория: {repo!r}. Нужно owner/repo",
        "configured": "Настроенные проекты:",
        "usage": "Использование: ss release <project> <version> [commit]",
        "no_projects": "Проекты не настроены. Запустите: ss release config",
        "version_required": "Требуется версия",
        "unknown_project": "Проект '{project}' не настроен. Запустите: ss release config {project}",
        "package": "Пакет",
        "source": "Источник",
        "version": "Версия",
        "not_found": "не найдено",
    },
    "es": {
        "cancelled": "Cancelado.",
        "project": "Nombre del proyecto",
        "repository": "Repositorio",
        "workflow": "Workflow",
        "ref": "Referencia",
        "tag": "Plantilla de tag",
        "saved": "Guardado {project} en {path}",
        "invalid_repo": "Repositorio inválido: {repo!r}. Se espera owner/repo",
        "configured": "Proyectos configurados:",
        "usage": "Uso: ss release <project> <version> [commit]",
        "no_projects": "No hay proyectos configurados. Ejecuta: ss release config",
        "version_required": "Falta la versión",
        "unknown_project": "El proyecto '{project}' no está configurado. Ejecuta: ss release config {project}",
        "package": "Paquete",
        "source": "Fuente",
        "version": "Versión",
        "not_found": "no encontrado",
    },
    "it": {
        "cancelled": "Annullato.",
        "project": "Nome progetto",
        "repository": "Repository",
        "workflow": "Workflow",
        "ref": "Riferimento",
        "tag": "Template tag",
        "saved": "Salvato {project} in {path}",
        "invalid_repo": "Repository non valido: {repo!r}. Atteso owner/repo",
        "configured": "Progetti configurati:",
        "usage": "Uso: ss release <project> <version> [commit]",
        "no_projects": "Nessun progetto configurato. Esegui: ss release config",
        "version_required": "Versione richiesta",
        "unknown_project": "Il progetto '{project}' non è configurato. Esegui: ss release config {project}",
        "package": "Pacchetto",
        "source": "Fonte",
        "version": "Versione",
        "not_found": "non trovato",
    },
}


def normalize_language(value: str) -> str:
    value = (value or "").replace("_", "-").lower()
    if value.startswith("zh"):
        if any(tag in value for tag in ("tw", "hk", "mo", "hant")):
            return "zh-TW"
        return "zh-CN"
    for code in LANGUAGES:
        if value == code.lower() or value.startswith(code.lower() + "-"):
            return code
    return "en"


def detect_language() -> str:
    raw = (os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES")
           or os.environ.get("LANG") or "")
    if raw:
        return normalize_language(raw)
    try:
        value = locale.getdefaultlocale()[0]
        if value:
            return normalize_language(value)
    except Exception:
        pass
    return "en"


def get_language(config_lang: str = "auto") -> str:
    if config_lang and config_lang != "auto":
        return normalize_language(config_lang)
    return detect_language()


def tr(key: str, lang: str = "en", **kwargs) -> str:
    table = STRINGS.get(lang, STRINGS["en"])
    text = table.get(key, STRINGS["en"].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text


HELP_TEXT = {
    "en": {
        "usage": "Usage", "examples": "Examples", "more": "More info",
        "show_help": "Show this help", "show_version": "Show version",
        "new": "Create a new project", "pkg": "Install an ecosystem package",
        "install_list": "List installed packages", "sources": "Show versions across PyPI sources",
        "release": "Publish a GitHub release", "git": "Pass through to git",
        "shortcuts": "Common git shortcuts",
    },
    "zh-CN": {
        "usage": "用法", "examples": "示例", "more": "更多信息",
        "show_help": "显示此帮助", "show_version": "显示版本号",
        "new": "创建新项目", "pkg": "查询并安装生态库",
        "install_list": "列出已安装的库", "sources": "查看各 PyPI 源的版本",
        "release": "触发 GitHub Release", "git": "git 透传",
        "shortcuts": "常用 git 快捷命令",
    },
    "zh-TW": {
        "usage": "用法", "examples": "範例", "more": "更多資訊",
        "show_help": "顯示此說明", "show_version": "顯示版本號",
        "new": "建立新專案", "pkg": "查詢並安裝生態套件",
        "install_list": "列出已安裝的套件", "sources": "查看各 PyPI 來源的版本",
        "release": "觸發 GitHub Release", "git": "git 透傳",
        "shortcuts": "常用 git 快捷指令",
    },
    "ja": {
        "usage": "使い方", "examples": "例", "more": "詳細",
        "show_help": "このヘルプを表示", "show_version": "バージョンを表示",
        "new": "新しいプロジェクトを作成", "pkg": "エコシステムのパッケージをインストール",
        "install_list": "インストール済みパッケージを一覧", "sources": "PyPI ソースごとのバージョンを表示",
        "release": "GitHub Release を実行", "git": "git にそのまま渡す",
        "shortcuts": "よく使う git コマンド",
    },
    "ko": {
        "usage": "사용법", "examples": "예시", "more": "자세히",
        "show_help": "도움말 표시", "show_version": "버전 표시",
        "new": "새 프로젝트 만들기", "pkg": "생태계 패키지 설치",
        "install_list": "설치된 패키지 목록", "sources": "PyPI 소스별 버전 표시",
        "release": "GitHub Release 실행", "git": "git으로 전달",
        "shortcuts": "자주 쓰는 git 명령",
    },
    "ru": {
        "usage": "Использование", "examples": "Примеры", "more": "Подробнее",
        "show_help": "Показать справку", "show_version": "Показать версию",
        "new": "Создать новый проект", "pkg": "Установить пакет экосистемы",
        "install_list": "Список установленных пакетов", "sources": "Версии по источникам PyPI",
        "release": "Запустить GitHub Release", "git": "Передать в git",
        "shortcuts": "Частые команды git",
    },
    "es": {
        "usage": "Uso", "examples": "Ejemplos", "more": "Más información",
        "show_help": "Mostrar esta ayuda", "show_version": "Mostrar versión",
        "new": "Crear un proyecto nuevo", "pkg": "Instalar un paquete del ecosistema",
        "install_list": "Listar paquetes instalados", "sources": "Mostrar versiones por fuente PyPI",
        "release": "Publicar un GitHub Release", "git": "Pasar directamente a git",
        "shortcuts": "Atajos de git habituales",
    },
    "it": {
        "usage": "Uso", "examples": "Esempi", "more": "Ulteriori informazioni",
        "show_help": "Mostra questo aiuto", "show_version": "Mostra versione",
        "new": "Crea un nuovo progetto", "pkg": "Installa un pacchetto dell'ecosistema",
        "install_list": "Elenca i pacchetti installati", "sources": "Mostra le versioni per fonte PyPI",
        "release": "Pubblica una GitHub Release", "git": "Passa direttamente a git",
        "shortcuts": "Scorciatoie git comuni",
    },
}


def help_text(version: str, lang: str) -> str:
    h = HELP_TEXT.get(lang, HELP_TEXT["en"])
    lines = [
        f"SilentStudio CLI v{version}",
        "Home: https://github.com/Silent-Studio-CN/SilentStudioCLI",
        "",
        f"{h['usage']}:",
        f"  ss                       {h['show_help']}",
        f"  ss -v, --version         {h['show_version']}",
        f"  ss new <name> -l <lang>  {h['new']}",
        f"  ss <pkg>                 {h['pkg']}",
        f"  ss install list          {h['install_list']}",
        f"  ss sources <pkg>         {h['sources']}",
        f"  ss config [key] [value] {h.get('config', 'Show or change configuration')}",
        f"  ss release <project> <version>  {h['release']}",
        f"  ss git <args...>         {h['git']}",
        f"  ss status/commit/push    {h['shortcuts']}",
        "",
        f"{h['examples']}:",
        "  ss new my-app -l java",
        "  ss slimemold",
        "  ss install list",
        "  ss sources silentstudio",
        "  ss release silentcraft 3.18",
        "",
        f"{h['more']}: https://github.com/Silent-Studio-CN/SilentStudioCLI",
    ]
    return "\n".join(lines)

