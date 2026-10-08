from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AppSettings:
    topmost: bool = True
    refresh_ms: int = 1000

    def normalize(self) -> None:
        self.topmost = bool(self.topmost)
        self.refresh_ms = max(500, min(5000, int(self.refresh_ms)))


class SettingsStore:
    @staticmethod
    def path() -> Path:
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / ".pc-helper"
        return base / "PC Helper" / "settings.json"

    @classmethod
    def load(cls) -> AppSettings:
        settings = AppSettings()
        try:
            payload = json.loads(cls.path().read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                settings = AppSettings(
                    topmost=payload.get("topmost", True),
                    refresh_ms=payload.get("refresh_ms", 1000),
                )
        except (OSError, ValueError, TypeError):
            pass
        settings.normalize()
        return settings

    @classmethod
    def save(cls, settings: AppSettings) -> None:
        settings.normalize()
        path = cls.path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(".tmp")
            temp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
            temp.replace(path)
        except OSError:
            pass
