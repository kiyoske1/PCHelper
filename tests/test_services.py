from pathlib import Path

from pc_helper.config import AppSettings, SettingsStore
from pc_helper.system import CleanupService, DiskService, ProcessService, format_size


def test_format_size_bytes():
    assert format_size(0) == "0.0 B"


def test_format_size_megabytes():
    assert format_size(1024 * 1024) == "1.0 MB"


def test_format_size_negative_is_safe():
    assert format_size(-10) == "0.0 B"


def test_settings_normalize():
    settings = AppSettings(topmost=0, refresh_ms=99999)
    settings.normalize()
    assert settings.topmost is False
    assert settings.refresh_ms == 5000


def test_settings_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(SettingsStore, "path", staticmethod(lambda: path))
    original = AppSettings(topmost=False, refresh_ms=1500)
    SettingsStore.save(original)
    loaded = SettingsStore.load()
    assert loaded == original


def test_disk_usage_temp_path(tmp_path):
    payload = tmp_path / "data.bin"
    payload.write_bytes(b"x" * 1024)
    usage = DiskService.usage(str(tmp_path))
    assert usage["total"] > 0
    assert usage["used"] >= 1024
    assert usage["free"] > 0


def test_cleanup_eligibility(tmp_path, monkeypatch):
    old_file = tmp_path / "old.tmp"
    old_file.write_bytes(b"abc")
    monkeypatch.setattr(CleanupService, "paths", staticmethod(lambda: [Path(tmp_path)]))
    monkeypatch.setattr(CleanupService, "MIN_AGE_SECONDS", 0)
    assert CleanupService.scan() >= 3


def test_current_process_is_protected():
    ok, message = ProcessService.terminate(__import__("os").getpid())
    assert ok is False
    assert "protected" in message.lower()
