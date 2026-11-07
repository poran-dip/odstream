#!/usr/bin/env python3
"""
Desktop launcher for ODStream.

Starts the Flask backend and the Vite frontend dev server, shows their output
in a small Tk window, and opens the app in the browser.

The UI, output handling and process management live in the ``launcher``
package; this file just stitches them together.
"""

import platform
import re
import tkinter as tk
from pathlib import Path

from launcher import COLORS, OutputMixin, ProcessMixin, UIMixin


class AppLauncher(UIMixin, OutputMixin, ProcessMixin):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Full Stack App Launcher")
        self.root.geometry("600x700")
        self.root.configure(bg="#1a1a1a")
        # Strips ANSI colour codes from child process output
        self.ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

        self.colors = dict(COLORS)

        # Child processes (backend / frontend dev servers)
        self.backend_process = None
        self.frontend_process = None
        self.processes = []

        self.app_url = "http://localhost:5173/"
        self.script_dir = Path(__file__).parent.absolute()
        self.os_type = platform.system().lower()

        self.setup_ui()
        self.center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.stop_all()
        self.root.destroy()

    def run(self):
        self.log_message("App Launcher ready!")
        self.root.mainloop()


if __name__ == "__main__":
    app = AppLauncher()
    app.run()
