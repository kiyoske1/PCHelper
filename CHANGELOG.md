# Changelog

## 1.1.0 - 2026-10-08

### Added
- Persistent local settings
- System uptime in the monitor
- Configurable ping target
- Drive selection in Disk Analyzer
- Async background workers for expensive operations
- CI across Python 3.10, 3.12 and 3.13
- Production-oriented NSIS installer metadata
- Security and contribution guidance

### Fixed
- Cleanup no longer targets files newer than one hour
- Cleanup never follows symlinks
- Process Manager no longer blocks the UI during refresh
- Disk Analyzer no longer blocks the UI during recursive scans
- Windows Update launcher uses Explorer protocol handling
- System disk monitoring now follows the Windows system drive
- PC Helper's own process is protected from termination
- Background callbacks are ignored safely during shutdown
- Windows-only actions are guarded on non-Windows platforms

### Build
- Windows icon is generated from the tracked SVG during CI
- PyInstaller executable and NSIS installer are produced automatically
- GitHub Releases receive both Windows artifacts for version tags
