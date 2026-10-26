"""Terminal output, log messages, status indicators and URL detection."""

import re
import time
import tkinter as tk
import webbrowser


class OutputMixin:
    """Everything that writes to the UI after it is built.

    Child process output is read on background threads and handed to the Tk
    main loop with ``root.after`` so widgets are only touched from Tk's thread.
    """

    # ------------------------------------------------------------------
    # Terminals & logs
    # ------------------------------------------------------------------

    def clear_all_terminals(self):
        self.backend_terminal.delete(1.0, tk.END)
        self.frontend_terminal.delete(1.0, tk.END)
        self.logs_terminal.delete(1.0, tk.END)

    def append_to_terminal(self, terminal_widget, text):
        terminal_widget.insert(tk.END, text)
        terminal_widget.see(tk.END)
        self.root.update_idletasks()

    def read_process_output(self, process, terminal_widget, process_name):
        """Pump a child process's stdout/stderr into a terminal widget.

        Runs on a background thread until the process exits. Frontend output
        is also scanned for the dev-server URL.
        """
        try:
            while process.poll() is None:
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            clean_line = self.ansi_escape.sub('', line)
                            self.root.after(0, self.append_to_terminal, terminal_widget, clean_line)
                            if process_name == "Frontend":
                                self.extract_url_from_output(line, process_name)
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        self.root.after(0, self.append_to_terminal, terminal_widget, f"{line}")
                        if process_name == "Frontend":
                            self.extract_url_from_output(line, process_name)
                time.sleep(0.1)
        except Exception as e:
            self.root.after(0, self.append_to_terminal, terminal_widget,
                             f"[{process_name}] Error: {str(e)}\n")

    def log_message(self, message):
        """Append a timestamped line to the Logs tab."""
        timestamp = time.strftime('%H:%M:%S')
        log_text = f"{timestamp} - {message}\n"
        self.logs_terminal.insert(tk.END, log_text)
        self.logs_terminal.see(tk.END)
        self.root.update()

    # ------------------------------------------------------------------
    # Status cards
    # ------------------------------------------------------------------

    def update_status(self, component, status, color):
        """Update a status card. ``component`` is backend/frontend/browser."""
        if component == "backend":
            self.backend_status_label.config(text=status)
            self.backend_status_dot.config(fg=color)
        elif component == "frontend":
            self.frontend_status_label.config(text=status)
            self.frontend_status_dot.config(fg=color)
        elif component == "browser":
            self.browser_status_label.config(text=status)
            self.browser_status_dot.config(fg=color)
        self.root.update()

    # ------------------------------------------------------------------
    # App URL
    # ------------------------------------------------------------------

    def launch_app_url(self):
        try:
            webbrowser.open(self.app_url)
            self.log_message(f"🌐 Opened {self.app_url} in browser")
        except Exception as e:
            self.log_message(f"❌ Failed to open URL: {str(e)}")

    def extract_url_from_output(self, text, process_name):
        """Look for a dev-server URL in a line of output (e.g. Vite's
        "Local: http://localhost:5173/") and remember it as ``self.app_url``."""
        url_patterns = [
            r'http://localhost:\d+/?',
            r'http://127\.0\.0\.1:\d+/?',
            r'Local:\s+(http://[^\s]+)',
            r'running at (http://[^\s]+)',
            r'Available on:\s+(http://[^\s]+)'
        ]

        for pattern in url_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                if url != self.app_url:
                    self.app_url = url
                    self.log_message(f"🔗 Detected {process_name} URL: {url}")
                    self.launch_url_button.config(state=tk.NORMAL)
                return url
        return None
