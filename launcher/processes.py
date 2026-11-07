"""Starting and stopping the backend / frontend dev servers."""

import subprocess
import threading
import time
import tkinter as tk
import webbrowser


class ProcessMixin:
    """Launch sequence: backend -> (wait) -> frontend -> (wait) -> browser.

    Expects ``self.script_dir`` (repo root), ``self.os_type`` and
    ``self.processes`` to be set by the owner class.
    """

    def start_application(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress["value"] = 0
        # Run the (slow, sleeping) launch sequence off the Tk thread
        threading.Thread(target=self.launch_sequence, daemon=True).start()

    def launch_sequence(self):
        try:
            self.log_message("Starting backend server...")
            self.update_status("backend", "Starting...", self.colors["warning"])
            self.progress["value"] = 10

            if self.start_backend():
                self.update_status("backend", "Running ✓", self.colors["success"])
                self.log_message("Backend server started successfully")
                self.progress["value"] = 40

                time.sleep(3)

                self.log_message("Starting frontend server...")
                self.update_status("frontend", "Starting...", self.colors["warning"])
                self.progress["value"] = 50

                if self.start_frontend():
                    self.update_status("frontend", "Running ✓", self.colors["success"])
                    self.log_message("Frontend server started successfully")
                    self.progress["value"] = 80

                    time.sleep(3)

                    self.log_message("Opening browser...")
                    self.update_status(
                        "browser", "Launching...", self.colors["warning"]
                    )
                    self.progress["value"] = 90

                    if self.open_browser():
                        self.update_status(
                            "browser", "Opened ✓", self.colors["success"]
                        )
                        self.log_message("Browser opened successfully")
                        self.progress["value"] = 100
                        self.log_message("🎉 Application launched successfully!")
                    else:
                        self.log_message("❌ Failed to open browser")
                else:
                    self.log_message("❌ Failed to start frontend")
                    self.update_status("frontend", "Failed ❌", self.colors["error"])
            else:
                self.log_message("❌ Failed to start backend")
                self.update_status("backend", "Failed ❌", self.colors["error"])

        except Exception as e:
            self.log_message(f"❌ Error: {e!s}")

    # ------------------------------------------------------------------
    # Individual services
    # ------------------------------------------------------------------

    def _spawn(self, cmd):
        """Start a shell command with line-buffered text stdout/stderr pipes."""
        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

    def start_backend(self):
        """Run backend/app.py using the backend's virtualenv."""
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
                cmd = (
                    f'cd "{backend_path}" && source venv/bin/activate && python app.py'
                )

            self.backend_process = self._spawn(cmd)

            self.processes.append(self.backend_process)

            threading.Thread(
                target=self.read_process_output,
                args=(self.backend_process, self.backend_terminal, "Backend"),
                daemon=True,
            ).start()

            return True

        except Exception as e:
            self.log_message(f"Backend error: {e!s}")
            return False

    def start_frontend(self):
        """Run ``npm run dev`` in the frontend directory."""
        try:
            frontend_path = self.script_dir / "frontend"

            if self.os_type == "windows":
                cmd = f'cd /d "{frontend_path}" && npm run dev'
            else:
                cmd = f'cd "{frontend_path}" && npm run dev'

            self.frontend_process = self._spawn(cmd)

            self.processes.append(self.frontend_process)

            threading.Thread(
                target=self.read_process_output,
                args=(self.frontend_process, self.frontend_terminal, "Frontend"),
                daemon=True,
            ).start()

            return True

        except Exception as e:
            self.log_message(f"Frontend error: {e!s}")
            return False

    def open_browser(self):
        try:
            webbrowser.open("http://localhost:5173/")
            return True
        except Exception as e:
            self.log_message(f"Browser error: {e!s}")
            return False

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def stop_all(self):
        """Terminate every spawned process and reset the UI."""
        self.log_message("Stopping all servers...")

        for process in self.processes:
            try:
                if process and process.poll() is None:
                    process.terminate()
                    if self.os_type != "windows":
                        process.wait(timeout=5)
            except Exception as e:
                self.log_message(f"Error stopping process: {e!s}")

        self.processes.clear()

        self.update_status("backend", "Stopped", self.colors["text_secondary"])
        self.update_status("frontend", "Stopped", self.colors["text_secondary"])
        self.update_status("browser", "Closed", self.colors["text_secondary"])

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.launch_url_button.config(state=tk.DISABLED)
        self.progress["value"] = 0

        self.log_message("All servers stopped")
