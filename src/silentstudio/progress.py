"""Live install progress bars."""
from __future__ import annotations

import shutil
import sys

LABELS = {
    "zh-CN": ("收集", "下载", "安装", "总进度"),
    "zh-TW": ("收集", "下載", "安裝", "總進度"),
    "ja": ("取得", "ダウンロード", "インストール", "合計"),
    "ko": ("수집", "다운로드", "설치", "전체"),
    "ru": ("Сбор", "Загрузка", "Установка", "Всего"),
    "es": ("Recolectar", "Descargar", "Instalar", "Total"),
    "it": ("Raccolta", "Download", "Installazione", "Totale"),
    "en": ("Collect", "Download", "Install", "Total"),
}


def _bar(percent: int, width: int = 16) -> str:
    percent = max(0, min(100, percent))
    filled = int(width * percent / 100)
    return "[" + "=" * filled + " " * (width - filled) + "]"


class InstallProgress:
    def __init__(self, lang: str) -> None:
        labels = LABELS.get(lang, LABELS["en"])
        self.collect_label, self.download_label, self.install_label, self.total_label = labels
        self.collect = 0
        self.download = 0
        self.install = 0
        self.total = 0
        self._started = False
        self._interactive = sys.stdout.isatty()
        self.width = max(40, shutil.get_terminal_size((80, 24)).columns - 1)

    def _lines(self) -> list[str]:
        return [
            f"{self.collect_label} {self.collect}%",
            f"{self.download_label}{_bar(self.download)} {self.download:3d}%",
            f"{self.install_label}{_bar(self.install)} {self.install:3d}%",
            f"{self.total_label}{_bar(self.total)} {self.total:3d}%",
        ]

    def _draw(self, initial: bool = False) -> None:
        lines = self._lines()
        if not self._interactive:
            if initial:
                for line in lines:
                    print(line[: self.width])
            return
        if not initial:
            sys.stdout.write("\x1b[4A")
        for line in lines:
            sys.stdout.write("\r" + line[: self.width].ljust(self.width) + "\n")
        sys.stdout.flush()

    def start(self) -> None:
        self._started = True
        if self._interactive:
            sys.stdout.write("\x1b[?25l")
        self._draw(initial=True)

    def update(self, stage: str, percent: int) -> None:
        percent = max(0, min(100, percent))
        if stage == "collect":
            self.collect = percent
            self.total = max(self.total, 10 * percent // 100)
        elif stage == "download":
            self.download = percent
            self.total = max(self.total, 20 + percent // 2)
        elif stage == "install":
            self.install = percent
            self.total = max(self.total, 70 + percent * 3 // 10)
        elif stage == "total":
            self.total = percent
        self._draw()

    def finish(self) -> None:
        self.collect = self.download = self.install = self.total = 100
        self._draw()
        if self._interactive:
            sys.stdout.write("\x1b[?25h")
            sys.stdout.flush()

    def cancel(self) -> None:
        if self._interactive:
            sys.stdout.write("\x1b[?25h\n")
            sys.stdout.flush()
