import platform
import socket
import customtkinter as ctk
import psutil


APP_TITLE = "PC Helper"
APP_VERSION = "0.1.0"


class PCInfo:
    @staticmethod
    def cpu():
        name = platform.processor() or "Unknown CPU"
        cores = psutil.cpu_count(logical=False) or 0
        threads = psutil.cpu_count(logical=True) or 0
        return f"{name} | {cores} cores / {threads} threads"

    @staticmethod
    def memory():
        mem = psutil.virtual_memory()
        used = mem.used / (1024 ** 3)
        total = mem.total / (1024 ** 3)
        return f"{used:.1f} GB / {total:.1f} GB ({mem.percent:.0f}%)"

    @staticmethod
    def windows():
        return f"{platform.system()} {platform.release()} ({platform.version()})"

    @staticmethod
    def hostname():
        return socket.gethostname()

    @staticmethod
    def architecture():
        return platform.machine()


class PCHelper(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry("760x520")
        self.minsize(680, 460)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_system_card()
        self._build_actions()

        self.refresh_info()

    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=28, pady=(24, 10), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="🖥️  PC HELPER",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            frame,
            text=f"Windows utility toolkit  •  v{APP_VERSION}",
            text_color="gray",
        ).grid(row=1, column=0, pady=(2, 0), sticky="w")

    def _build_system_card(self):
        card = ctk.CTkFrame(self, corner_radius=16)
        card.grid(row=1, column=0, padx=28, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="SYSTEM",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 12), sticky="w")

        self.info_labels = {}

        rows = [
            ("CPU", "cpu"),
            ("RAM", "ram"),
            ("Windows", "windows"),
            ("Architecture", "architecture"),
            ("Hostname", "hostname"),
        ]

        for index, (label, key) in enumerate(rows, start=1):
            ctk.CTkLabel(
                card,
                text=label,
                text_color="gray",
            ).grid(row=index, column=0, padx=(20, 12), pady=7, sticky="w")

            value = ctk.CTkLabel(card, text="Loading...", anchor="w")
            value.grid(row=index, column=1, padx=(0, 20), pady=7, sticky="ew")
            self.info_labels[key] = value

    def _build_actions(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, padx=28, pady=(10, 24), sticky="nsew")
        frame.grid_columnconfigure((0, 1), weight=1)

        actions = [
            ("📊  Monitor", "Coming in v0.2"),
            ("🧹  Cleanup", "Coming in v0.3"),
            ("🌐  Network", "Coming in v0.4"),
            ("🔧  Windows Tools", "Coming in v0.5"),
        ]

        for index, (title, subtitle) in enumerate(actions):
            button = ctk.CTkButton(
                frame,
                text=f"{title}\n{subtitle}",
                height=72,
                corner_radius=14,
                state="disabled",
            )
            button.grid(
                row=index // 2,
                column=index % 2,
                padx=7,
                pady=7,
                sticky="ew",
            )

        ctk.CTkButton(
            frame,
            text="↻  Refresh system information",
            height=40,
            command=self.refresh_info,
        ).grid(row=2, column=0, columnspan=2, padx=7, pady=(14, 0), sticky="ew")

    def refresh_info(self):
        data = {
            "cpu": PCInfo.cpu(),
            "ram": PCInfo.memory(),
            "windows": PCInfo.windows(),
            "architecture": PCInfo.architecture(),
            "hostname": PCInfo.hostname(),
        }

        for key, value in data.items():
            self.info_labels[key].configure(text=value)


if __name__ == "__main__":
    app = PCHelper()
    app.mainloop()
