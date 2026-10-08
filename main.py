import os
import platform
import socket
import subprocess
import tempfile
import customtkinter as ctk
import psutil


APP_TITLE = "PC Helper"
APP_VERSION = "0.6.0"


class PCInfo:
    @staticmethod
    def cpu_name():
        return platform.processor() or "Unknown CPU"

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent(interval=None)

    @staticmethod
    def memory():
        mem = psutil.virtual_memory()
        return mem.used / (1024 ** 3), mem.total / (1024 ** 3), mem.percent

    @staticmethod
    def disk():
        disk = psutil.disk_usage("/")
        return disk.used / (1024 ** 3), disk.total / (1024 ** 3), disk.percent

    @staticmethod
    def windows():
        return f"{platform.system()} {platform.release()}"

    @staticmethod
    def hostname():
        return socket.gethostname()

    @staticmethod
    def architecture():
        return platform.machine()


class Cleaner:
    @staticmethod
    def _folder_size(path):
        total = 0
        if not os.path.exists(path):
            return 0

        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [
                d for d in dirs
                if not os.path.islink(os.path.join(root, d))
            ]
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                except (OSError, PermissionError):
                    pass
        return total

    @staticmethod
    def temp_paths():
        paths = [tempfile.gettempdir()]
        windows_temp = os.environ.get("WINDIR")
        if windows_temp:
            paths.append(os.path.join(windows_temp, "Temp"))
        return list(dict.fromkeys(paths))

    @staticmethod
    def scan():
        return sum(Cleaner._folder_size(path) for path in Cleaner.temp_paths())

    @staticmethod
    def clean():
        removed_bytes = 0
        removed_files = 0

        for folder in Cleaner.temp_paths():
            if not os.path.exists(folder):
                continue

            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    try:
                        size = os.path.getsize(path)
                        os.remove(path)
                        removed_bytes += size
                        removed_files += 1
                    except (OSError, PermissionError):
                        pass

                for name in dirs:
                    path = os.path.join(root, name)
                    try:
                        os.rmdir(path)
                    except (OSError, PermissionError):
                        pass

        return removed_files, removed_bytes


class NetworkTools:
    @staticmethod
    def ping(host="8.8.8.8"):
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "2000", host],
                capture_output=True,
                text=True,
                timeout=4,
            )

            if result.returncode != 0:
                return False, "No response"

            for line in result.stdout.splitlines():
                if "Average" in line or "Среднее" in line:
                    return True, line.strip()

            return True, "Host is reachable"
        except (subprocess.SubprocessError, OSError):
            return False, "Ping failed"

    @staticmethod
    def ip_address():
        try:
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if "IPv4" in line or "IPv4-адрес" in line:
                    return line.split(":", 1)[-1].strip()
            return "Not found"
        except (subprocess.SubprocessError, OSError):
            return "Unavailable"

    @staticmethod
    def flush_dns():
        try:
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if result.returncode == 0:
                return True, "DNS cache flushed successfully."
            return False, "Could not flush DNS cache."
        except (subprocess.SubprocessError, OSError):
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
            return False, f"Could not open {name}: {error}"


def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title, icon, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")

        self.value = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.value.grid(row=1, column=0, padx=18, sticky="w")

        self.detail = ctk.CTkLabel(
            self,
            text="Loading...",
            text_color="gray",
        )
        self.detail.grid(row=2, column=0, padx=18, pady=(2, 8), sticky="w")

        self.progress = ctk.CTkProgressBar(
            self,
            height=8,
            corner_radius=4,
        )
        self.progress.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 16),
            sticky="ew",
        )
        self.progress.set(0)

    def update(self, percent, detail):
        percent = max(0.0, min(100.0, float(percent)))
        self.value.configure(text=f"{percent:.0f}%")
        self.detail.configure(text=detail)
        self.progress.set(percent / 100)


class PCHelper(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("820x760+120+80")
        self.minsize(680, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()

        self._build_system_card()
        self._build_monitor()
        self._build_cleanup()
        self._build_network()
        self._build_windows_tools()

        psutil.cpu_percent(interval=None)
        self.after(500, self.update_monitor)

    def _build_header(self):
        self.titlebar = ctk.CTkFrame(
            self,
            height=48,
            corner_radius=0,
            fg_color=("#15151c", "#15151c"),
        )
        self.titlebar.grid(row=0, column=0, sticky="ew")
        self.titlebar.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.titlebar,
            text=f"●  {APP_TITLE}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, padx=(16, 8), pady=8)

        self.subtitle_label = ctk.CTkLabel(
            self.titlebar,
            text=f"v{APP_VERSION}  •  LIVE CONTROL CENTER",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        )
        self.subtitle_label.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        self.pin_button = ctk.CTkButton(
            self.titlebar,
            text="📌",
            width=32,
            height=30,
            fg_color="transparent",
            hover_color=("#252531", "#252531"),
            command=self.toggle_topmost,
        )
        self.pin_button.grid(row=0, column=2, padx=2)

        ctk.CTkButton(
            self.titlebar,
            text="—",
            width=32,
            height=30,
            fg_color="transparent",
            hover_color=("#252531", "#252531"),
            command=self.iconify_window,
        ).grid(row=0, column=3, padx=2)

        ctk.CTkButton(
            self.titlebar,
            text="✕",
            width=32,
            height=30,
            fg_color="transparent",
            hover_color=("#4a2025", "#4a2025"),
            command=self.destroy,
        ).grid(row=0, column=4, padx=(2, 10))

        for widget in (self.titlebar, self.title_label, self.subtitle_label):
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag_window)

    def _build_body(self):
        self.body = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
        )
        self.body.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

    def start_drag(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def drag_window(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def toggle_topmost(self):
        current = self.attributes("-topmost")
        self.attributes("-topmost", not current)
        self.pin_button.configure(text="📌" if not current else "📍")

    def iconify_window(self):
        self.overrideredirect(False)
        self.iconify()
        self.after(100, lambda: self.overrideredirect(True))

    def _build_system_card(self):
        card = ctk.CTkFrame(self.body, corner_radius=16)
        card.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="SYSTEM",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 10), sticky="w")

        info = [
            ("CPU", PCInfo.cpu_name()),
            ("Windows", PCInfo.windows()),
            ("Architecture", PCInfo.architecture()),
            ("Hostname", PCInfo.hostname()),
        ]

        for row, (name, value) in enumerate(info, start=1):
            ctk.CTkLabel(card, text=name, text_color="gray").grid(
                row=row, column=0, padx=(20, 12), pady=5, sticky="w"
            )
            ctk.CTkLabel(card, text=value, anchor="w").grid(
                row=row, column=1, padx=(0, 20), pady=5, sticky="ew"
            )

    def _build_monitor(self):
        frame = ctk.CTkFrame(self.body, fg_color="transparent")
        frame.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            frame,
            text="📊 LIVE MONITOR",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

        self.cpu_card = MetricCard(frame, "CPU", "⚡")
        self.ram_card = MetricCard(frame, "RAM", "🧠")
        self.disk_card = MetricCard(frame, "DISK", "💾")

        self.cpu_card.grid(row=1, column=0, padx=5, sticky="nsew")
        self.ram_card.grid(row=1, column=1, padx=5, sticky="nsew")
        self.disk_card.grid(row=1, column=2, padx=5, sticky="nsew")

        self.status = ctk.CTkLabel(
            frame,
            text="● LIVE  •  updating every 1 second",
            text_color="gray",
        )
        self.status.grid(row=2, column=0, columnspan=3, pady=(14, 0))

    def _build_cleanup(self):
        card = ctk.CTkFrame(self.body, corner_radius=16)
        card.grid(row=2, column=0, padx=18, pady=8, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="🧹 CLEANUP",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(16, 6), sticky="w")

        ctk.CTkLabel(
            card,
            text="Temporary Windows files",
            text_color="gray",
        ).grid(row=1, column=0, padx=20, pady=(4, 12), sticky="w")

        self.cleanup_size = ctk.CTkLabel(
            card,
            text="Not scanned",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.cleanup_size.grid(row=1, column=1, padx=10, pady=(4, 12), sticky="w")

        self.scan_button = ctk.CTkButton(
            card,
            text="🔍 SCAN",
            command=self.scan_cleanup,
            width=120,
        )
        self.scan_button.grid(row=1, column=2, padx=(10, 20), pady=(4, 12))

        self.clean_button = ctk.CTkButton(
            card,
            text="🧹 CLEAN",
            command=self.clean_cleanup,
            width=120,
            state="disabled",
        )
        self.clean_button.grid(row=2, column=2, padx=(10, 20), pady=(0, 16))

        self.cleanup_status = ctk.CTkLabel(
            card,
            text="Scan temporary files before cleaning.",
            text_color="gray",
        )
        self.cleanup_status.grid(
            row=2, column=0, columnspan=2, padx=20, pady=(0, 16), sticky="w"
        )

    def _build_network(self):
        card = ctk.CTkFrame(self.body, corner_radius=16)
        card.grid(row=3, column=0, padx=18, pady=8, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="🌐 NETWORK DIAGNOSTICS",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(16, 10), sticky="w")

        self.network_status = ctk.CTkLabel(
            card,
            text="● READY",
            text_color="gray",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.network_status.grid(row=1, column=0, padx=20, pady=6, sticky="w")

        self.ip_label = ctk.CTkLabel(
            card,
            text="Local IP: detecting...",
            text_color="gray",
        )
        self.ip_label.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        self.ping_button = ctk.CTkButton(
            card,
            text="📡 PING",
            command=self.run_ping,
            width=120,
        )
        self.ping_button.grid(row=1, column=2, padx=(10, 20), pady=6)

        self.dns_button = ctk.CTkButton(
            card,
            text="🔄 FLUSH DNS",
            command=self.flush_dns,
            width=120,
        )
        self.dns_button.grid(row=2, column=2, padx=(10, 20), pady=(4, 16))

        self.network_details = ctk.CTkLabel(
            card,
            text="Press PING to test connectivity to 8.8.8.8.",
            text_color="gray",
        )
        self.network_details.grid(
            row=2, column=0, columnspan=2, padx=20, pady=(4, 16), sticky="w"
        )

        self.after(100, self.load_network_info)

    def _build_windows_tools(self):
        card = ctk.CTkFrame(self.body, corner_radius=16)
        card.grid(row=4, column=0, padx=18, pady=(8, 18), sticky="ew")
        card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            card,
            text="🛠️ WINDOWS TOOLS",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(16, 10), sticky="w")

        tools = [
            ("📋 Task Manager", "Task Manager"),
            ("🔧 Device Manager", "Device Manager"),
            ("⚙️ Control Panel", "Control Panel"),
            ("⌨️ Command Prompt", "Command Prompt"),
            ("💻 PowerShell", "PowerShell"),
            ("🔩 Services", "Services"),
            ("ℹ️ System Information", "System Information"),
            ("🧹 Disk Cleanup", "Disk Cleanup"),
            ("🔄 Windows Update", "Windows Update"),
        ]

        for index, (label, tool_name) in enumerate(tools):
            row = 1 + index // 3
            column = index % 3

            ctk.CTkButton(
                card,
                text=label,
                command=lambda name=tool_name: self.open_windows_tool(name),
                height=38,
            ).grid(
                row=row,
                column=column,
                padx=6,
                pady=6,
                sticky="ew",
            )

    def open_windows_tool(self, name):
        success, message = WindowsTools.open_tool(name)
        self.network_details.configure(text=message)

    def load_network_info(self):
        self.ip_label.configure(
            text=f"Local IP: {NetworkTools.ip_address()}"
        )

    def run_ping(self):
        self.ping_button.configure(state="disabled")
        self.network_status.configure(text="● TESTING...")
        self.network_details.configure(text="Pinging 8.8.8.8...")
        self.update_idletasks()

        try:
            success, message = NetworkTools.ping()
            if success:
                self.network_status.configure(text="● ONLINE")
                self.network_details.configure(text=message)
            else:
                self.network_status.configure(text="● OFFLINE")
                self.network_details.configure(text=message)
        finally:
            self.ping_button.configure(state="normal")

    def flush_dns(self):
        self.network_status.configure(text="● WORKING...")
        self.network_details.configure(text="Flushing DNS cache...")
        self.update_idletasks()

        success, message = NetworkTools.flush_dns()
        self.network_status.configure(text="● DNS READY" if success else "● ERROR")
        self.network_details.configure(text=message)

    def scan_cleanup(self):
        try:
            size = Cleaner.scan()
            self.cleanup_size.configure(text=format_size(size))
            self.cleanup_status.configure(
                text=f"Found {format_size(size)} of temporary files."
            )
            self.clean_button.configure(state="normal" if size > 0 else "disabled")
        except Exception as error:
            self.cleanup_status.configure(text=f"Scan error: {error}")
            self.clean_button.configure(state="disabled")

    def clean_cleanup(self):
        confirmed = ctk.CTkInputDialog(
            text="Type CLEAN to confirm temporary file cleanup:",
            title="Confirm cleanup",
        ).get_input()

        if confirmed != "CLEAN":
            self.cleanup_status.configure(text="Cleanup cancelled.")
            return

        self.clean_button.configure(state="disabled")
        self.scan_button.configure(state="disabled")
        self.cleanup_status.configure(text="Cleaning temporary files...")
        self.update_idletasks()

        try:
            removed_files, removed_bytes = Cleaner.clean()
            self.cleanup_size.configure(text="0 B")
            self.cleanup_status.configure(
                text=f"Cleaned {format_size(removed_bytes)} from {removed_files} files."
            )
        except Exception as error:
            self.cleanup_status.configure(text=f"Cleanup error: {error}")
        finally:
            self.scan_button.configure(state="normal")

    def update_monitor(self):
        try:
            cpu = PCInfo.cpu_usage()
            ram_used, ram_total, ram_percent = PCInfo.memory()
            disk_used, disk_total, disk_percent = PCInfo.disk()

            self.cpu_card.update(cpu, f"{cpu:.1f}% usage")
            self.ram_card.update(ram_percent, f"{ram_used:.1f} / {ram_total:.1f} GB")
            self.disk_card.update(disk_percent, f"{disk_used:.1f} / {disk_total:.1f} GB")

            self.status.configure(text="● LIVE  •  updating every 1 second")
        except Exception as error:
            self.status.configure(text=f"Monitor error: {error}")

        self.after(1000, self.update_monitor)


if __name__ == "__main__":
    app = PCHelper()
    app.mainloop()
