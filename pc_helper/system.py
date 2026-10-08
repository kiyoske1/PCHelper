import os
import platform
import socket
import subprocess
import tempfile
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
    def details():
        return {
            "CPU": SystemService.cpu_name(),
            "Windows": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Hostname": socket.gethostname(),
        }


class CleanupService:
    @staticmethod
    def paths():
        paths = [Path(tempfile.gettempdir())]
        windir = os.environ.get("WINDIR")
        if windir:
            paths.append(Path(windir) / "Temp")
        return list(dict.fromkeys(paths))

    @staticmethod
    def scan():
        total = 0
        for folder in CleanupService.paths():
            if not folder.exists():
                continue
            for item in folder.rglob("*"):
                try:
                    if item.is_file():
                        total += item.stat().st_size
                except OSError:
                    continue
        return total

    @staticmethod
    def clean():
        removed_bytes = 0
        removed_files = 0
        for folder in CleanupService.paths():
            if not folder.exists():
                continue
            for item in sorted(folder.rglob("*"), reverse=True):
                try:
                    if item.is_file() or item.is_symlink():
                        size = item.stat().st_size if item.is_file() else 0
                        item.unlink()
                        removed_bytes += size
                        removed_files += 1
                    elif item.is_dir():
                        item.rmdir()
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
