# 🖥️ PC Helper

> A polished, local-first Windows control center built with Python.

**Version 1.1.0**

PC Helper is a small desktop toolkit for monitoring a Windows PC, cleaning safe temporary files, diagnosing connectivity, inspecting processes, analyzing disk usage, and opening built-in Windows utilities.

## ✨ What it can do

### 📊 System Monitor
- Live CPU, RAM and system-drive usage
- CPU model, OS, architecture, hostname and uptime
- Configurable refresh interval from 0.5 to 5 seconds

### 🧹 Cleanup
- Scans Windows temporary folders
- Runs in a background thread so the UI stays responsive
- Only targets files older than one hour
- Leaves active/recent temporary files alone
- Explicit confirmation before deletion

### 🌐 Network
- Detects local IP
- Ping any host, such as 1.1.1.1
- Flush Windows DNS cache
- Background diagnostics with visible status

### 🛠️ Windows Tools
One-click launchers for:
- Task Manager
- Device Manager
- Control Panel
- Command Prompt
- PowerShell
- Services
- System Information
- Disk Cleanup
- Windows Update

### 🧩 Process Manager
- Search running processes
- CPU and RAM information
- Shows up to 100 processes
- Explicit END confirmation
- Protects PID 0, PID 4 and PC Helper itself

### 💾 Disk Analyzer
- Detects available partitions
- Shows used/free capacity
- Scans largest top-level folders in the background
- Skips inaccessible locations and symlinked directories

### ⚙️ Settings
- Always-on-top preference
- Monitoring refresh interval
- Settings are persisted locally in %APPDATA%\PC Helper\settings.json

## 🧱 Architecture

~~~text
PCHelper/
├── main.py
├── pc_helper/
│   ├── __init__.py
│   ├── config.py
│   └── system.py
├── tests/
│   └── test_services.py
├── assets/
│   └── pc-helper.svg
├── installer/
│   └── PC-Helper.nsi
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── build-windows.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── LICENSE
└── README.md
~~~

The UI never performs large cleanup, disk or process scans directly on the Tkinter event loop. Expensive operations are delegated to background worker threads and their results are applied back on the UI thread.

## 🚀 Run locally

~~~powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
~~~

Development checks:

~~~powershell
pip install -r requirements-dev.txt
pytest
ruff check .
~~~

## 📦 Windows build

The release workflow builds on windows-latest and:

1. Installs runtime and development dependencies
2. Runs tests and Ruff
3. Generates a Windows .ico from the tracked SVG
4. Builds a single-file GUI executable with PyInstaller
5. Builds an NSIS installer
6. Uploads both artifacts
7. Creates a GitHub Release when a v* tag is pushed

## 🔒 Privacy

PC Helper is local-first:
- no account
- no telemetry
- no analytics SDK
- no remote backend
- network features only run when you explicitly press a diagnostic button

## 🧪 Quality

CI tests the project against Python 3.10, 3.12 and 3.13 and runs both pytest and Ruff.

## 🗺️ Roadmap

- [x] System monitor
- [x] Uptime and system details
- [x] Safe temporary cleanup
- [x] Network diagnostics
- [x] Windows tools launcher
- [x] Floating borderless UI
- [x] Sidebar navigation
- [x] Async background tasks
- [x] Process manager
- [x] Disk analyzer
- [x] Persistent settings
- [x] Tests and lint
- [x] Windows executable build
- [x] NSIS installer
- [x] Automated GitHub Actions release
- [ ] Hardware temperature sensors
- [ ] Startup with Windows
- [ ] Notifications
- [ ] Update checker
- [ ] Per-drive visual charts

## 👤 Author

Built by **Kiyoske** under the MIT License.
