![PC Helper](assets/pc-helper-banner.jpg)

# PC Helper

> **YOUR SYSTEM. YOUR CONTROL.**
>
> A dark, local-first Windows control center for people who want their PC tools in one place.

**v1.1.0** · **Windows 10/11** · **Python 3.10+** · **MIT License**

[![CI](https://github.com/kiyoske1/PCHelper/actions/workflows/ci.yml/badge.svg)](https://github.com/kiyoske1/PCHelper/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/kiyoske1/PCHelper?style=flat-square)](https://github.com/kiyoske1/PCHelper/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-7c6cff?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-6d5dfc?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

---

## ◈ What is PC Helper?

**PC Helper** is a lightweight Windows utility built with Python and CustomTkinter.

It combines everyday PC maintenance and diagnostics into one compact interface:

**monitor → clean → diagnose → inspect → control**

No accounts. No telemetry. No remote backend. Your machine stays yours.

---

## ⚡ Features

| Module | What it does |
|---|---|
| 📊 **Monitor** | Live CPU, RAM and system-drive usage |
| 🧹 **Cleanup** | Scans and safely removes old temporary files |
| 🌐 **Network** | Local IP, ping diagnostics and DNS flush |
| 🛠️ **Windows Tools** | Quick access to built-in Windows utilities |
| 🧩 **Processes** | Search, inspect and safely terminate processes |
| 💾 **Disk Analyzer** | Partition usage and largest folders |
| ⚙️ **Settings** | Refresh interval and always-on-top preferences |
| 🖥️ **Floating UI** | Borderless dark interface with draggable title bar |

### System Monitor

- Live CPU usage
- Live RAM usage
- System-drive usage
- CPU model
- OS and architecture
- Hostname
- System uptime
- Configurable refresh interval from **0.5 to 5 seconds**

### Cleanup

- Windows temporary folders
- Background scanning
- Only files older than **one hour**
- Skips active/recent files
- Skips symlinked directories
- Confirmation before deletion

### Network

- Local IP detection
- Ping any host
- DNS cache flush
- Background diagnostics
- Windows-only operations are guarded

### Windows Tools

One-click access to:

- Task Manager
- Device Manager
- Control Panel
- Command Prompt
- PowerShell
- Services
- System Information
- Disk Cleanup
- Windows Update

### Process Manager

- Search running processes
- CPU and RAM information
- Up to 100 processes
- Explicit termination confirmation
- Protects PID 0
- Protects PID 4
- Protects PC Helper itself

### Disk Analyzer

- Detects available partitions
- Used/free capacity
- Background scanning
- Finds large top-level folders
- Skips inaccessible locations
- Does not follow symlinks

---

## 🎨 Interface

PC Helper uses a dark, minimal interface with a subtle cyberpunk/anime-inspired atmosphere.

The goal is simple:

> **Make Windows tools feel like one coherent application instead of twenty disconnected utilities.**

---

## 🧱 Project structure

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
│   ├── pc-helper.svg
│   └── pc-helper-banner.jpg
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
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
~~~

The UI does not perform heavy cleanup, disk or process scans directly on the Tkinter event loop. Expensive work is delegated to background threads, then safely returned to the UI thread.

---

## 🚀 Run locally

### 1. Clone

~~~powershell
git clone https://github.com/kiyoske1/PCHelper.git
cd PCHelper
~~~

### 2. Create a virtual environment

~~~powershell
python -m venv .venv
.venv\Scripts\activate
~~~

### 3. Install dependencies

~~~powershell
pip install -r requirements.txt
~~~

### 4. Launch

~~~powershell
python main.py
~~~

---

## 🧪 Development

Install development dependencies:

~~~powershell
pip install -r requirements-dev.txt
~~~

Run tests:

~~~powershell
pytest
~~~

Run lint:

~~~powershell
ruff check .
~~~

---

## 📦 Build a Windows .exe

For a normal local build, open a **non-administrator** terminal inside the project directory.

Do **not** run PyInstaller from `C:\Windows\System32`.

~~~powershell
pyinstaller --noconfirm --clean --onefile --windowed --name PC-Helper main.py
~~~

The executable will appear here:

~~~text
dist/
└── PC-Helper.exe
~~~

### GitHub Actions build

The Windows workflow can also:

1. Install dependencies
2. Run pytest
3. Run Ruff
4. Generate the Windows icon
5. Build `PC-Helper.exe`
6. Build the NSIS installer
7. Upload build artifacts
8. Create a GitHub Release for `v*` tags

---

## 🔒 Privacy

PC Helper is **local-first**.

- No account
- No telemetry
- No analytics SDK
- No remote backend
- No background network service
- Network diagnostics only run when requested

Your system information stays on your computer.

---

## 🧪 Quality

CI currently checks the project against:

- Python 3.10
- Python 3.12
- Python 3.13
- pytest
- Ruff

The project also contains tests for settings persistence, disk usage, cleanup behavior, formatting and process protection.

---

## 🗺️ Roadmap

### Done

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
- [x] Security documentation
- [x] Contribution guide

### Next

- [ ] Hardware temperature sensors
- [ ] Windows startup toggle
- [ ] Desktop notifications
- [ ] Automatic update checker
- [ ] CPU/RAM/Disk history charts
- [ ] Per-drive visual charts
- [ ] More system diagnostics

---

## 🧠 Philosophy

PC Helper is not trying to replace every Windows utility.

It is trying to remove the friction between:

**"Something is wrong with my PC."**

and

**"I know exactly what is happening."**

One window. Useful tools. No unnecessary cloud layer.

---

## 👤 Author

Built by **Kiyoske**.

GitHub: https://github.com/kiyoske1

Licensed under the **MIT License**.

---

<p align="center">
  <sub>PC Helper v1.1.0 · More than just a tool.</sub>
</p>
