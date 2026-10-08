import platform
import socket
import customtkinter as ctk
import psutil


APP_TITLE = "PC Helper"
APP_VERSION = "0.2.0"


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

        self.detail = ctk.CTkLabel(self, text="Loading...", text_color="gray")
        self.detail.grid(row=2, column=0, padx=18, pady=(2, 8), sticky="w")

        self.progress = ctk.CTkProgressBar(self, height=8, corner_radius=4)
        self.progress.grid(row=3, column=0, padx=18, pady=(0, 16), sticky="ew")
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

        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry("900x650")
        self.minsize(760, 560)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_system_card()
        self._build_monitor()

        psutil.cpu_percent(interval=None)
        self.after(500, self.update_monitor)

    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=28, pady=(24, 10), sticky="ew")

        ctk.CTkLabel(
            frame,
            text="🖥️  PC HELPER",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text=f"Windows utility toolkit  •  v{APP_VERSION}  •  LIVE MONITOR",
            text_color="gray",
        ).pack(anchor="w", pady=(2, 0))

    def _build_system_card(self):
        card = ctk.CTkFrame(self, corner_radius=16)
        card.grid(row=1, column=0, padx=28, pady=10, sticky="ew")

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
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, padx=28, pady=(10, 24), sticky="nsew")
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
