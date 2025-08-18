#!/usr/bin/env python3

import time
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk
import webbrowser
from pathlib import Path
import re

class AppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Full Stack App Launcher")
        self.root.geometry("600x700")
        self.root.configure(bg='#1a1a1a')
        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

        self.colors = {
            'bg': '#1a1a1a',
            'card_bg': '#2d2d2d',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040'
        }

        self.backend_process = None
        self.frontend_process = None
        self.processes = []
        self.app_url = "http://localhost:5173/"
        self.script_dir = Path(__file__).parent.absolute()
        self.os_type = platform.system().lower()

        self.setup_ui()
        self.center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(main_container, text="🚀 Full Stack Launcher",
                              font=('Segoe UI', 24, 'bold'), bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack(anchor=tk.W, pady=(0, 30))

        cards_frame = tk.Frame(main_container, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 25))

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)

        self.backend_status = self.create_status_card(cards_frame, "Backend", "🔧", "Ready to start")
        self.backend_status.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        self.frontend_status = self.create_status_card(cards_frame, "Frontend",
                                                        "🎨", "Ready to start")
        self.frontend_status.grid(row=0, column=1, sticky='ew', padx=5)

        self.browser_status = self.create_status_card(cards_frame, "Browser",
                                                       "🌐", "Ready to launch")
        self.browser_status.grid(row=0, column=2, sticky='ew', padx=(10, 0))

        control_frame = tk.Frame(main_container, bg=self.colors['card_bg'])
        control_frame.pack(fill=tk.X, pady=(0, 25))

        self.progress_label = tk.Label(control_frame, text="Ready to start",
                                      font=('Segoe UI', 10), bg=self.colors['card_bg'],
                                      fg=self.colors['text_secondary'])
        self.progress_label.pack(anchor=tk.W, padx=20, pady=(20, 8))

        self.progress = ttk.Progressbar(control_frame, mode='determinate', length=400)
        self.progress.pack(fill=tk.X, padx=20)

        buttons_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)

        self.start_button = tk.Button(buttons_frame, text="🚀 Start Application",
                                     font=('Segoe UI', 11, 'bold'), bg=self.colors['accent'],
                                     fg='white', relief='flat', padx=20, pady=10,
                                     command=self.start_application)
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))

        self.stop_button = tk.Button(buttons_frame, text="🛑 Stop All",
                                    font=('Segoe UI', 11, 'bold'), bg=self.colors['error'],
                                    fg='white', relief='flat', padx=20, pady=10,
                                    command=self.stop_all, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))

        self.launch_url_button = tk.Button(buttons_frame, text="🌐 Open App",
                                          font=('Segoe UI', 10), bg=self.colors['border'],
                                          fg=self.colors['text'], relief='flat', padx=15, pady=8,
                                          command=self.launch_app_url, state=tk.DISABLED)
        self.launch_url_button.pack(side=tk.LEFT)

        terminal_frame = tk.Frame(main_container, bg=self.colors['card_bg'])
        terminal_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(terminal_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        terminal_title = tk.Label(header_frame, text="🖥️ Terminal Output",
                                 font=('Segoe UI', 12, 'bold'), bg=self.colors['card_bg'],
                                 fg=self.colors['text'])
        terminal_title.pack(side=tk.LEFT)

        clear_btn = tk.Button(header_frame, text="🗑️ Clear All", font=('Segoe UI', 9),
                             bg=self.colors['border'], fg=self.colors['text'], relief='flat',
                             padx=10, pady=5, command=self.clear_all_terminals)
        clear_btn.pack(side=tk.RIGHT)

        self.terminal_notebook = ttk.Notebook(terminal_frame)
        self.terminal_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        backend_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(backend_frame, text="🔧 Backend")

        self.backend_terminal = tk.Text(backend_frame, height=12, bg='#0d1117', fg='#58a6ff',
                                       font=('Consolas', 10), wrap=tk.WORD, relief='flat')
        self.backend_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frontend_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(frontend_frame, text="🎨 Frontend")

        self.frontend_terminal = tk.Text(frontend_frame, height=12, bg='#0d1117', fg='#7dd3fc',
                                        font=('Consolas', 10), wrap=tk.WORD, relief='flat')
        self.frontend_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        logs_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(logs_frame, text="📋 Logs")

        self.logs_terminal = tk.Text(logs_frame, height=12, bg='#0d1117', fg='#a5d6ff',
                                    font=('Consolas', 10), wrap=tk.WORD, relief='flat')
        self.logs_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_status_card(self, parent, title, emoji, status):
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', bd=1)

        header_frame = tk.Frame(card, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        emoji_label = tk.Label(header_frame, text=emoji, font=('Segoe UI', 20),
                              bg=self.colors['card_bg'], fg=self.colors['text'])
        emoji_label.pack(side=tk.LEFT)

        title_label = tk.Label(header_frame, text=title, font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['card_bg'], fg=self.colors['text'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        status_frame = tk.Frame(card, bg=self.colors['card_bg'])
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        status_dot = tk.Label(status_frame, text="◯", font=('Segoe UI', 12),
                             bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        status_dot.pack(side=tk.LEFT)

        status_label = tk.Label(status_frame, text=status, font=('Segoe UI', 10),
                               bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        status_label.pack(side=tk.LEFT, padx=(8, 0))

        if title == "Backend":
            self.backend_status_dot = status_dot
            self.backend_status_label = status_label
        elif title == "Frontend":
            self.frontend_status_dot = status_dot
            self.frontend_status_label = status_label
        elif title == "Browser":
            self.browser_status_dot = status_dot
            self.browser_status_label = status_label

        return card

    def launch_app_url(self):
        try:
            webbrowser.open(self.app_url)
            self.log_message(f"🌐 Opened {self.app_url} in browser")
        except Exception as e:
            self.log_message(f"❌ Failed to open URL: {str(e)}")

    def extract_url_from_output(self, text, process_name):
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

    def clear_all_terminals(self):
        self.backend_terminal.delete(1.0, tk.END)
        self.frontend_terminal.delete(1.0, tk.END)
        self.logs_terminal.delete(1.0, tk.END)

    def append_to_terminal(self, terminal_widget, text):
        terminal_widget.insert(tk.END, text)
        terminal_widget.see(tk.END)
        self.root.update_idletasks()

    def read_process_output(self, process, terminal_widget, process_name):
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
        timestamp = time.strftime('%H:%M:%S')
        log_text = f"{timestamp} - {message}\n"
        self.logs_terminal.insert(tk.END, log_text)
        self.logs_terminal.see(tk.END)
        self.root.update()

    def update_status(self, component, status, color):
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

    def start_application(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        threading.Thread(target=self.launch_sequence, daemon=True).start()

    def launch_sequence(self):
        try:
            self.log_message("Starting backend server...")
            self.update_status("backend", "Starting...", self.colors['warning'])
            self.progress['value'] = 10

            if self.start_backend():
                self.update_status("backend", "Running ✓", self.colors['success'])
                self.log_message("Backend server started successfully")
                self.progress['value'] = 40

                time.sleep(3)

                self.log_message("Starting frontend server...")
                self.update_status("frontend", "Starting...", self.colors['warning'])
                self.progress['value'] = 50

                if self.start_frontend():
                    self.update_status("frontend", "Running ✓", self.colors['success'])
                    self.log_message("Frontend server started successfully")
                    self.progress['value'] = 80

                    time.sleep(3)

                    self.log_message("Opening browser...")
                    self.update_status("browser", "Launching...", self.colors['warning'])
                    self.progress['value'] = 90

                    if self.open_browser():
                        self.update_status("browser", "Opened ✓", self.colors['success'])
                        self.log_message("Browser opened successfully")
                        self.progress['value'] = 100
                        self.log_message("🎉 Application launched successfully!")
                    else:
                        self.log_message("❌ Failed to open browser")
                else:
                    self.log_message("❌ Failed to start frontend")
                    self.update_status("frontend", "Failed ❌", self.colors['error'])
            else:
                self.log_message("❌ Failed to start backend")
                self.update_status("backend", "Failed ❌", self.colors['error'])

        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")

    def start_backend(self):
        try:
            backend_path = self.script_dir / "backend"

            if self.os_type == "windows":
                python_exe = backend_path / "venv" / "Scripts" / "python.exe"
                if not python_exe.exists():
                    self.log_message("Virtual environment not found.")
                    return False
                cmd = f'"{python_exe}" "{backend_path / "app.py"}"'
            else:
                venv_activate = backend_path / "venv" / "bin" / "activate"
                if not venv_activate.exists():
                    self.log_message("Virtual environment not found.")
                    return False
                cmd = f'cd "{backend_path}" && source venv/bin/activate && python app.py'

            self.backend_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes.append(self.backend_process)

            threading.Thread(target=self.read_process_output,
                            args=(self.backend_process, self.backend_terminal, "Backend"),
                            daemon=True).start()

            return True

        except Exception as e:
            self.log_message(f"Backend error: {str(e)}")
            return False

    def start_frontend(self):
        try:
            frontend_path = self.script_dir / "frontend"

            if self.os_type == "windows":
                cmd = f'cd /d "{frontend_path}" && npm run dev'
            else:
                cmd = f'cd "{frontend_path}" && npm run dev'

            self.frontend_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes.append(self.frontend_process)

            threading.Thread(target=self.read_process_output,
                            args=(self.frontend_process, self.frontend_terminal, "Frontend"),
                            daemon=True).start()

            return True

        except Exception as e:
            self.log_message(f"Frontend error: {str(e)}")
            return False

    def open_browser(self):
        try:
            webbrowser.open("http://localhost:5173/")
            return True
        except Exception as e:
            self.log_message(f"Browser error: {str(e)}")
            return False

    def stop_all(self):
        self.log_message("Stopping all servers...")

        for process in self.processes:
            try:
                if process and process.poll() is None:
                    process.terminate()
                    if self.os_type != "windows":
                        process.wait(timeout=5)
            except Exception as e:
                self.log_message(f"Error stopping process: {str(e)}")

        self.processes.clear()

        self.update_status("backend", "Stopped", self.colors['text_secondary'])
        self.update_status("frontend", "Stopped", self.colors['text_secondary'])
        self.update_status("browser", "Closed", self.colors['text_secondary'])

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.launch_url_button.config(state=tk.DISABLED)
        self.progress['value'] = 0

        self.log_message("All servers stopped")

    def on_closing(self):
        self.stop_all()
        self.root.destroy()

    def run(self):
        self.log_message("App Launcher ready!")
        self.root.mainloop()

if __name__ == "__main__":
    app = AppLauncher()
    app.run()
