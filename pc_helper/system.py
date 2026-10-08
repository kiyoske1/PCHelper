import os
import platform
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import psutil


class SystemService:
    @staticmethod
    def cpu_name():
        return platform.processor() or "Unknown CPU"

    @staticmethod
    def snapshot():
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(Path.cwd().anchor or "/")
        return {
            "cpu": psutil.cpu_percent(interval=None),
            "ram": memory.percent,
            "ram_used": memory.used,
            "ram_total": memory.total,
            "disk": disk.percent,
            "disk_used": disk.used,
            "disk_total": disk.total,
        }

    @staticmethod
    def uptime():
        seconds = max(0, int(time.time() - psutil.boot_time()))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours or days:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)

    @staticmethod
    def details():
        return {
            "CPU": SystemService.cpu_name(),
            "OS": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Hostname": socket.gethostname(),
            "Uptime": SystemService.uptime(),
        }


class CleanupService:
    MIN_AGE_SECONDS = 3600
    @staticmethod
    def paths():
        paths = [Path(tempfile.gettempdir())]
        windir = os.environ.get("WINDIR")
        if windir:
            paths.append(Path(windir) / "Temp")
        return list(dict.fromkeys(paths))

    @classmethod
    def _eligible(cls, item):
        try:
            if not item.is_file() and not item.is_symlink():
                return False
            return time.time() - item.stat().st_mtime >= cls.MIN_AGE_SECONDS
        except OSError:
            return False

    @classmethod
    def scan(cls):
        total = 0
        for folder in cls.paths():
            if not folder.exists():
                continue
            for item in folder.rglob("*"):
                if cls._eligible(item):
                    try:
                        total += item.stat().st_size
                    except OSError:
                        continue
        return total

    @classmethod
    def clean(cls):
        removed_bytes = 0
        removed_files = 0
        for folder in cls.paths():
            if not folder.exists():
                continue
            for item in sorted(folder.rglob("*"), reverse=True):
                try:
                    if cls._eligible(item):
                        size = item.stat().st_size if item.is_file() else 0
                        item.unlink()
                        removed_bytes += size
                        removed_files += 1
                    elif item.is_dir() and not item.is_symlink():
                        try:
                            item.rmdir()
                        except OSError:
                            pass
                except OSError:
                    continue
        return removed_files, removed_bytes


class NetworkService:
    @staticmethod
    def ping(host="8.8.8.8"):
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "2000", host],
                capture_output=True, text=True, timeout=4,
            )
            if result.returncode != 0:
                return False, "No response"
            for line in result.stdout.splitlines():
                if "Average" in line or "Среднее" in line:
                    return True, line.strip()
            return True, "Host is reachable"
        except (OSError, subprocess.SubprocessError):
            return False, "Ping failed"

    @staticmethod
    def local_ip():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                return sock.getsockname()[0]
        except OSError:
            return "Unavailable"

    @staticmethod
    def flush_dns():
        try:
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5,
            )
            return result.returncode == 0, (
                "DNS cache flushed successfully." if result.returncode == 0
                else "Could not flush DNS cache."
            )
        except (OSError, subprocess.SubprocessError):
            return False, "DNS command failed."


class WindowsTools:
    TOOLS = {
        "Task Manager": ["taskmgr.exe"],
        "Device Manager": ["devmgmt.msc"],
        "Control Panel": ["control.exe"],
        "Command Prompt": ["cmd.exe"],
        "PowerShell": ["powershell.exe"],
        "Services": ["services.msc"],
        "System Information": ["msinfo32.exe"],
        "Disk Cleanup": ["cleanmgr.exe"],
        "Windows Update": ["ms-settings:windowsupdate"],
    }

    @staticmethod
    def open_tool(name):
        command = WindowsTools.TOOLS.get(name)
        if not command:
            return False, "Unknown Windows tool."
        try:
            subprocess.Popen(command, shell=False)
            return True, f"{name} opened."
        except (OSError, subprocess.SubprocessError) as error:
            return False, str(error)




class DiskService:
    @staticmethod
    def usage(path=None):
        target = path or (os.environ.get("SystemDrive", "C:") + "\\")
        usage = psutil.disk_usage(target)
        return {
            "path": target,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
        }

    @staticmethod
    def largest_entries(path=None, limit=12):
        root = Path(path or (os.environ.get("SystemDrive", "C:") + "\\"))
        entries = []
        try:
            for item in root.iterdir():
                try:
                    if item.is_dir():
                        size = sum(file.stat().st_size for file in item.rglob("*") if file.is_file())
                    elif item.is_file():
                        size = item.stat().st_size
                    else:
                        continue
                    entries.append({"name": item.name or str(item), "path": str(item), "size": size})
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError):
            return []
        return sorted(entries, key=lambda item: item["size"], reverse=True)[:limit]


class ProcessService:
    @staticmethod
    def list_processes(search=""):
        rows = []
        query = search.strip().lower()
        for process in psutil.process_iter(["pid", "name", "username", "memory_info"]):
            try:
                name = process.info["name"] or "Unknown"
                if query and query not in name.lower():
                    continue
                rows.append({
                    "pid": process.info["pid"],
                    "name": name,
                    "user": process.info["username"] or "System",
                    "ram": process.info["memory_info"].rss if process.info["memory_info"] else 0,
                    "cpu": process.cpu_percent(None),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        rows.sort(key=lambda item: (item["cpu"], item["ram"]), reverse=True)
        return rows

    @staticmethod
    def terminate(pid):
        try:
            process = psutil.Process(int(pid))
            process.terminate()
            return True, f"Process {pid} terminated."
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
            return False, str(error)


def format_size(value):
    value = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
