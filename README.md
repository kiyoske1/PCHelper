# 🖥️ PC Helper

> A polished, local-first Windows control center built with Python.

**Version 1.0.0**

## ✨ Features

- 📊 Live CPU, RAM and disk monitoring
- 🪟 Borderless floating window with drag support
- 📌 Always-on-top toggle and custom window controls
- 🧹 Temporary file scanner and cleanup with confirmation
- 🌐 Local IP detection, ping and DNS flush
- 🛠️ One-click access to common Windows tools
- 🌙 Compact dark interface with sidebar navigation
- 🔒 Local-first design, no telemetry and no account required

## 🧰 Tech stack

Python 3.10+ • CustomTkinter • psutil • pytest • Ruff

## 🚀 Run

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Development checks:

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

## 📁 Structure

```text
PCHelper/
├── main.py
├── pc_helper/
│   ├── __init__.py
│   └── system.py
├── tests/
│   └── test_services.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

## 🗺️ Roadmap

- [x] System monitor
- [x] Cleanup tools
- [x] Network diagnostics
- [x] Windows tools launcher
- [x] Floating UI
- [x] Sidebar navigation
- [x] Tests and lint configuration
- [x] Process manager
- [ ] Disk analyzer
- [ ] Settings
- [ ] Windows installer
- [ ] Automated GitHub Actions release

## 👤 Author

Built by **Kiyoske**.
