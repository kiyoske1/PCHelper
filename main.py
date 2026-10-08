import threading
from pathlib import Path

import customtkinter as ctk

from pc_helper import __version__
from pc_helper.config import AppSettings, SettingsStore
from pc_helper.system import CleanupService, DiskService, NetworkService, ProcessService, SystemService, WindowsTools, format_size

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_ICON = Path(__file__).resolve().parent / "assets" / "pc-helper.ico"


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title, icon):
        super().__init__(master, corner_radius=18)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=f"{icon}  {title}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=18, pady=(15, 3), sticky="w")
        self.value = ctk.CTkLabel(self, text="0%", font=ctk.CTkFont(size=28, weight="bold"))
        self.value.grid(row=1, column=0, padx=18, sticky="w")
        self.detail = ctk.CTkLabel(self, text="Loading...", text_color="gray")
        self.detail.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="w")
        self.bar = ctk.CTkProgressBar(self, height=7, corner_radius=4)
        self.bar.grid(row=3, column=0, padx=18, pady=(0, 16), sticky="ew")
        self.bar.set(0)

    def update(self, percent, detail):
        percent = max(0, min(100, float(percent)))
        self.value.configure(text=f"{percent:.0f}%")
        self.detail.configure(text=detail)
        self.bar.set(percent / 100)


class PCApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("920x720+100+70")
        self.minsize(760, 560)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._drag = (0, 0)
        self.settings: AppSettings = SettingsStore.load()
        self._task_running = False
        self._closing = False
        self.attributes("-topmost", self.settings.topmost)
        self._set_window_icon()
        self._build_splash()
        self._build_shell()
        self.show_dashboard()
        self._tick()

    def _set_window_icon(self):
        if APP_ICON.exists():
            try:
                self.iconbitmap(str(APP_ICON))
            except Exception:
                pass

    def run_async(self, task, on_success, on_error=None):
        if self._task_running:
            return
        self._task_running = True

        def worker():
            try:
                result = task()
            except Exception as error:
                callback = on_error or self._show_error
                try:
                    if not self._closing and self.winfo_exists():
                        self.after(0, lambda: callback(error))
                except Exception:
                    pass
            else:
                try:
                    if not self._closing and self.winfo_exists():
                        self.after(0, lambda: on_success(result))
                except Exception:
                    pass
            finally:
                try:
                    if not self._closing and self.winfo_exists():
                        self.after(0, self._task_finished)
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def _task_finished(self):
        self._task_running = False

    def _show_error(self, error):
        if hasattr(self, "dashboard_status") and self.dashboard_status.winfo_exists():
            self.dashboard_status.configure(text=f"● ERROR: {error}")

    def _build_splash(self):
        splash = ctk.CTkFrame(self, corner_radius=0, fg_color="#111117")
        splash.place(relx=0, rely=0, relwidth=1, relheight=1)
        ctk.CTkLabel(splash, text="▣", font=ctk.CTkFont(size=52, weight="bold"), text_color="#8b6cff").pack(pady=(150, 8))
        ctk.CTkLabel(splash, text="PC HELPER", font=ctk.CTkFont(size=28, weight="bold")).pack()
        ctk.CTkLabel(splash, text=f"v{__version__}  •  Windows utility toolkit", text_color="gray").pack(pady=6)
        self.splash_bar = ctk.CTkProgressBar(splash, width=260, height=6)
        self.splash_bar.pack(pady=22)
        self.splash_bar.set(0.35)
        self.after(450, splash.destroy)

    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, height=48, corner_radius=0, fg_color="#15151c")
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        title = ctk.CTkLabel(bar, text="●  PC HELPER", font=ctk.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, padx=(16, 8))
        ctk.CTkLabel(bar, text=f"v{__version__}  •  SYSTEM CONTROL CENTER", text_color="gray").grid(row=0, column=1, sticky="w")
        self.pin = ctk.CTkButton(bar, text="📌" if self.settings.topmost else "📍", width=34, fg_color="transparent", command=self.toggle_topmost)
        self.pin.grid(row=0, column=2)
        ctk.CTkButton(bar, text="—", width=34, fg_color="transparent", command=self.iconify_window).grid(row=0, column=3)
        ctk.CTkButton(bar, text="✕", width=34, fg_color="transparent", hover_color="#4a2025", command=self.close_app).grid(row=0, column=4, padx=(0, 10))
        for widget in (bar, title):
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag_window)

    def _build_shell(self):
        self.shell = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.shell.grid(row=1, column=0, sticky="nsew")
        self.shell.grid_columnconfigure(1, weight=1)
        self.shell.grid_rowconfigure(0, weight=1)
        self.nav = ctk.CTkFrame(self.shell, width=190, corner_radius=0, fg_color="#111117")
        self.nav.grid(row=0, column=0, sticky="nsw")
        self.content = ctk.CTkScrollableFrame(self.shell, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.content.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.nav, text="PC HELPER", font=ctk.CTkFont(size=18, weight="bold")).pack(padx=18, pady=(24, 4), anchor="w")
        ctk.CTkLabel(self.nav, text="WINDOWS TOOLKIT", text_color="gray", font=ctk.CTkFont(size=10)).pack(padx=18, anchor="w")
        for label, method in [("📊  Monitor", self.show_dashboard), ("🧹  Cleanup", self.show_cleanup), ("🌐  Network", self.show_network), ("🛠️  Windows Tools", self.show_tools), ("⚙️  Processes", self.show_processes), ("💾  Disk Analyzer", self.show_disk), ("⚙️  Settings", self.show_settings), ("ℹ️  About", self.show_about)]:
            ctk.CTkButton(self.nav, text=label, anchor="w", height=38, fg_color="transparent", hover_color="#252531", command=method).pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(self.nav, text="READY • LOCAL", text_color="#6f8", font=ctk.CTkFont(size=10)).pack(side="bottom", padx=18, pady=18, anchor="w")

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def heading(self, title, subtitle):
        ctk.CTkLabel(self.content, text=title, font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkLabel(self.content, text=subtitle, text_color="gray").grid(row=1, column=0, sticky="w", padx=8, pady=(0, 16))

    def show_dashboard(self):
        self.clear()
        self.heading("System Monitor", "Live hardware telemetry updated every second.")
        info = ctk.CTkFrame(self.content, corner_radius=18)
        info.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        details = SystemService.details()
        for i, (key, value) in enumerate(details.items()):
            ctk.CTkLabel(info, text=key, text_color="gray").grid(row=i//2, column=(i%2)*2, padx=(16, 8), pady=7, sticky="w")
            ctk.CTkLabel(info, text=value).grid(row=i//2, column=(i%2)*2+1, padx=(0, 16), pady=7, sticky="w")
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=3, column=0, sticky="ew", padx=3, pady=8)
        cards.grid_columnconfigure((0, 1, 2), weight=1)
        self.cpu = MetricCard(cards, "CPU", "⚡")
        self.ram = MetricCard(cards, "RAM", "🧠")
        self.disk = MetricCard(cards, "DISK", "💾")
        self.cpu.grid(row=0, column=0, padx=5, sticky="ew")
        self.ram.grid(row=0, column=1, padx=5, sticky="ew")
        self.disk.grid(row=0, column=2, padx=5, sticky="ew")
        self.dashboard_status = ctk.CTkLabel(self.content, text="● LIVE", text_color="gray")
        self.dashboard_status.grid(row=4, column=0, pady=12)

    def show_cleanup(self):
        self.clear()
        self.heading("Cleanup", "Remove temporary files older than one hour. Active files are left untouched.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        self.cleanup_value = ctk.CTkLabel(card, text="Not scanned", font=ctk.CTkFont(size=30, weight="bold"))
        self.cleanup_value.pack(padx=24, pady=(24, 4))
        self.cleanup_status = ctk.CTkLabel(card, text="Scan before cleaning.", text_color="gray")
        self.cleanup_status.pack(pady=(0, 16))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(0, 24))
        ctk.CTkButton(row, text="🔍  SCAN", command=self.scan_cleanup, width=140).pack(side="left", padx=5)
        ctk.CTkButton(row, text="🧹  CLEAN", command=self.clean_cleanup, width=140).pack(side="left", padx=5)

    def show_network(self):
        self.clear()
        self.heading("Network", "Basic connectivity and DNS diagnostics.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(card, text=f"Local IP  {NetworkService.local_ip()}", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=24, pady=(24, 8))
        self.net_status = ctk.CTkLabel(card, text="READY", text_color="gray")
        self.net_status.pack()
        self.net_detail = ctk.CTkLabel(card, text="", text_color="gray")
        self.net_detail.pack(pady=4)
        self.net_target = ctk.CTkEntry(card, placeholder_text="Ping target, e.g. 1.1.1.1")
        self.net_target.insert(0, "1.1.1.1")
        self.net_target.pack(fill="x", padx=24, pady=(12, 4))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=20)
        ctk.CTkButton(row, text="📡  PING", command=self.run_ping, width=140).pack(side="left", padx=5)
        ctk.CTkButton(row, text="🔄  FLUSH DNS", command=self.flush_dns, width=140).pack(side="left", padx=5)

    def show_tools(self):
        self.clear()
        self.heading("Windows Tools", "Launch common Windows administration utilities.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure((0, 1, 2), weight=1)
        for i, name in enumerate(WindowsTools.TOOLS):
            ctk.CTkButton(card, text=name, height=42, command=lambda n=name: self.open_tool(n)).grid(row=i // 3, column=i % 3, padx=7, pady=7, sticky="ew")
        self.tools_status = ctk.CTkLabel(self.content, text="READY", text_color="gray")
        self.tools_status.grid(row=3, column=0, pady=8)

    def show_disk(self):
        self.clear()
        self.heading("Disk Analyzer", "Choose a drive and inspect its largest top-level folders.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        partitions = DiskService.partitions()
        values = [p["mountpoint"] for p in partitions] or [DiskService.usage()["path"]]
        self.disk_drive = ctk.CTkOptionMenu(card, values=values)
        self.disk_drive.set(values[0])
        self.disk_drive.pack(side="left", padx=20, pady=20)
        self.disk_analyze_btn = ctk.CTkButton(card, text="ANALYZE", command=self.analyze_disk)
        self.disk_analyze_btn.pack(side="left", padx=5)
        self.disk_summary = ctk.CTkLabel(card, text="Select a drive to begin.", text_color="gray")
        self.disk_summary.pack(side="left", padx=15)
        self.disk_table = ctk.CTkScrollableFrame(self.content, corner_radius=18)
        self.disk_table.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        self._draw_disk_table([])

    def _draw_disk_table(self, entries):
        for widget in self.disk_table.winfo_children():
            widget.destroy()
        self.disk_table.grid_columnconfigure(0, weight=1)
        for col, label in enumerate(["FOLDER / FILE", "SIZE"]):
            ctk.CTkLabel(self.disk_table, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=14, pady=9, sticky="w")
        for row, item in enumerate(entries, start=1):
            ctk.CTkLabel(self.disk_table, text=item["name"]).grid(row=row, column=0, padx=14, pady=6, sticky="w")
            ctk.CTkLabel(self.disk_table, text=format_size(item["size"])).grid(row=row, column=1, padx=14, pady=6, sticky="e")

    def analyze_disk(self):
        path = self.disk_drive.get()
        self.disk_analyze_btn.configure(state="disabled", text="ANALYZING...")
        self.disk_summary.configure(text="Scanning drive, this may take a moment...")
        self.run_async(lambda: DiskService.largest_entries(path), lambda entries: self._disk_finished(path, entries))

    def _disk_finished(self, path, entries):
        if not hasattr(self, "disk_table") or not self.disk_table.winfo_exists():
            return
        self.disk_analyze_btn.configure(state="normal", text="ANALYZE")
        self._draw_disk_table(entries)
        try:
            usage = DiskService.usage(path)
            self.disk_summary.configure(text=f'{usage["percent"]:.0f}% used  •  {format_size(usage["free"])} free')
        except OSError as error:
            self.disk_summary.configure(text=f"Drive error: {error}")

    def show_processes(self):
        self.clear()
        self.heading("Process Manager", "Inspect running processes. Terminate only processes you recognize.")
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        top.grid_columnconfigure(0, weight=1)
        self.process_search = ctk.CTkEntry(top, placeholder_text="Search process...")
        self.process_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(top, text="↻  REFRESH", width=120, command=self.refresh_processes).grid(row=0, column=1)
        self.process_status = ctk.CTkLabel(self.content, text="Loading...", text_color="gray")
        self.process_status.grid(row=3, column=0, sticky="w", padx=12, pady=4)
        self.process_table = ctk.CTkScrollableFrame(self.content, corner_radius=18)
        self.process_table.grid(row=4, column=0, sticky="nsew", padx=8, pady=8)
        self.process_table.grid_columnconfigure(1, weight=1)
        self.refresh_processes()

    def refresh_processes(self):
        if not hasattr(self, "process_table") or not self.process_table.winfo_exists() or self._task_running:
            return
        self.process_status.configure(text="Refreshing processes...")
        query = self.process_search.get() if hasattr(self, "process_search") else ""
        self.run_async(lambda: ProcessService.list_processes(query), self._render_processes)

    def _render_processes(self, rows):
        if not hasattr(self, "process_table") or not self.process_table.winfo_exists():
            return
        for widget in self.process_table.winfo_children():
            widget.destroy()
        headers = ["PID", "PROCESS", "CPU", "RAM", "ACTION"]
        for col, label in enumerate(headers):
            ctk.CTkLabel(self.process_table, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=8, sticky="w")
        for row, item in enumerate(rows[:100], start=1):
            ctk.CTkLabel(self.process_table, text=str(item["pid"])).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.process_table, text=item["name"]).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.process_table, text=f'{item["cpu"]:.1f}%').grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.process_table, text=format_size(item["ram"])).grid(row=row, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkButton(self.process_table, text="END", width=60, height=28, command=lambda pid=item["pid"]: self.end_process(pid)).grid(row=row, column=4, padx=8, pady=4)
        self.process_status.configure(text=f"{len(rows)} processes found • showing up to 100")

    def end_process(self, pid):
        if pid in (0, 4):
            self.process_status.configure(text="Protected system process.")
            return
        dialog = ctk.CTkInputDialog(text=f"Type END to terminate PID {pid}:", title="Confirm process termination")
        if dialog.get_input() != "END":
            return
        self.run_async(lambda: ProcessService.terminate(pid), self._process_end_result)

    def _process_end_result(self, result):
        _ok, message = result
        if hasattr(self, "process_status") and self.process_status.winfo_exists():
            self.process_status.configure(text=message)
        self.after(300, self.refresh_processes)

    def show_settings(self):
        self.clear()
        self.heading("Settings", "Preferences are saved locally and restored on next launch.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(22, 10))
        ctk.CTkLabel(top_row, text="Always on top", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.topmost_switch = ctk.CTkSwitch(top_row, text="", command=self.apply_topmost)
        self.topmost_switch.pack(side="right")
        if self.settings.topmost:
            self.topmost_switch.select()
        else:
            self.topmost_switch.deselect()
        ctk.CTkLabel(card, text="Monitor refresh interval", text_color="gray").pack(anchor="w", padx=20, pady=(10, 4))
        self.refresh_label = ctk.CTkLabel(card, text="")
        self.refresh_label.pack(anchor="w", padx=20)
        self.refresh_slider = ctk.CTkSlider(card, from_=0.5, to=5.0, number_of_steps=9, command=self.update_refresh_label)
        self.refresh_slider.set(self.settings.refresh_ms / 1000)
        self.update_refresh_label(self.settings.refresh_ms / 1000)
        self.refresh_slider.pack(fill="x", padx=20, pady=(8, 24))
        self.settings_status = ctk.CTkLabel(card, text="Settings saved locally.", text_color="gray")
        self.settings_status.pack(pady=(0, 20))

    def apply_topmost(self):
        state = bool(self.topmost_switch.get())
        self.settings.topmost = state
        self.attributes("-topmost", state)
        self.pin.configure(text="📌" if state else "📍")
        SettingsStore.save(self.settings)

    def update_refresh_label(self, value):
        seconds = float(value)
        self.settings.refresh_ms = int(seconds * 1000)
        self.refresh_label.configure(text=f"{seconds:.1f} second" + ("" if seconds == 1 else "s"))
        SettingsStore.save(self.settings)

    def show_about(self):
        self.clear()
        self.heading("About", "PC Helper is a local-first Windows utility toolkit.")
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(card, text=f"PC Helper {__version__}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(28, 6))
        ctk.CTkLabel(card, text="Python • CustomTkinter • psutil\nBuilt by Kiyoske\nNo telemetry. No account required.", justify="center", text_color="gray").pack(pady=(0, 28))

    def scan_cleanup(self):
        self.cleanup_status.configure(text="Scanning temporary files...")
        self.run_async(CleanupService.scan, self._cleanup_scanned)

    def _cleanup_scanned(self, size):
        if not hasattr(self, "cleanup_value") or not self.cleanup_value.winfo_exists():
            return
        self.cleanup_value.configure(text=format_size(size))
        self.cleanup_status.configure(text=f"Found {format_size(size)} of eligible temporary files.")

    def clean_cleanup(self):
        result = ctk.CTkInputDialog(
            text="Type CLEAN to confirm removal of files older than one hour:",
            title="Confirm cleanup",
        ).get_input()
        if result != "CLEAN":
            return
        self.cleanup_status.configure(text="Cleaning temporary files...")
        self.run_async(CleanupService.clean, self._cleanup_finished)

    def _cleanup_finished(self, result):
        if not hasattr(self, "cleanup_value") or not self.cleanup_value.winfo_exists():
            return
        files, size = result
        self.cleanup_value.configure(text=format_size(size))
        self.cleanup_status.configure(text=f"Removed {format_size(size)} from {files} files.")

    def run_ping(self):
        target = self.net_target.get().strip()
        self.net_status.configure(text="● TESTING...")
        self.run_async(lambda: NetworkService.ping(target), self._network_finished)

    def _network_finished(self, result):
        if not hasattr(self, "net_status") or not self.net_status.winfo_exists():
            return
        ok, message = result
        self.net_status.configure(text="● ONLINE" if ok else "● OFFLINE")
        self.net_detail.configure(text=message)

    def flush_dns(self):
        self.net_status.configure(text="● WORKING...")
        self.run_async(NetworkService.flush_dns, self._dns_finished)

    def _dns_finished(self, result):
        if not hasattr(self, "net_status") or not self.net_status.winfo_exists():
            return
        ok, message = result
        self.net_status.configure(text="● DNS READY" if ok else "● ERROR")
        self.net_detail.configure(text=message)

    def open_tool(self, name):
        ok, message = WindowsTools.open_tool(name)
        if hasattr(self, "tools_status") and self.tools_status.winfo_exists():
            self.tools_status.configure(text=message if ok else f"ERROR: {message}")

    def _tick(self):
        if hasattr(self, "cpu"):
            data = SystemService.snapshot()
            self.cpu.update(data["cpu"], f'{data["cpu"]:.1f}% usage')
            self.ram.update(data["ram"], f'{format_size(data["ram_used"])} / {format_size(data["ram_total"])}')
            self.disk.update(data["disk"], f'{format_size(data["disk_used"])} / {format_size(data["disk_total"])}')
        self.after(self.settings.refresh_ms, self._tick)

    def start_drag(self, event):
        self._drag = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def drag_window(self, event):
        self.geometry(f"+{event.x_root-self._drag[0]}+{event.y_root-self._drag[1]}")

    def toggle_topmost(self):
        state = not bool(self.settings.topmost)
        self.settings.topmost = state
        self.attributes("-topmost", state)
        self.pin.configure(text="📌" if state else "📍")
        SettingsStore.save(self.settings)

    def close_app(self):
        self._closing = True
        SettingsStore.save(self.settings)
        self.destroy()

    def iconify_window(self):
        self.overrideredirect(False)
        self.iconify()
        self.after(200, lambda: self.overrideredirect(True))


if __name__ == "__main__":
    PCApp().mainloop()
