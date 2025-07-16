#!/usr/bin/env python3

import time
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk
import webbrowser
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Full Stack App Launcher")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Process tracking
        self.backend_process = None
        self.frontend_process = None
        self.processes = []
        
        # Setup UI
        self.setup_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Get script directory
        self.script_dir = Path(__file__).parent.absolute()
        
        # Detect OS
        self.os_type = platform.system().lower()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Full Stack Application Launcher", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Backend status
        self.backend_frame = ttk.Frame(status_frame)
        self.backend_frame.pack(fill=tk.X, pady=5)
        
        self.backend_icon = ttk.Label(self.backend_frame, text="⏳", font=('Arial', 12))
        self.backend_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.backend_label = ttk.Label(self.backend_frame, text="Backend: Ready to start")
        self.backend_label.pack(side=tk.LEFT)
        
        # Frontend status
        self.frontend_frame = ttk.Frame(status_frame)
        self.frontend_frame.pack(fill=tk.X, pady=5)
        
        self.frontend_icon = ttk.Label(self.frontend_frame, text="⏳", font=('Arial', 12))
        self.frontend_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frontend_label = ttk.Label(self.frontend_frame, text="Frontend: Ready to start")
        self.frontend_label.pack(side=tk.LEFT)
        
        # Browser status
        self.browser_frame = ttk.Frame(status_frame)
        self.browser_frame.pack(fill=tk.X, pady=5)
        
        self.browser_icon = ttk.Label(self.browser_frame, text="⏳", font=('Arial', 12))
        self.browser_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.browser_label = ttk.Label(self.browser_frame, text="Browser: Ready to launch")
        self.browser_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=300)
        self.progress.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Start button
        self.start_button = ttk.Button(buttons_frame, text="🚀 Start Application", 
                                     command=self.start_application, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(buttons_frame, text="🛑 Stop All", 
                                    command=self.stop_all, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status text
        self.status_text = tk.Text(main_frame, height=6, width=50, wrap=tk.WORD)
        self.status_text.pack(pady=(20, 0), fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
    def log_message(self, message):
        """Add message to status text"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def update_status(self, component, status, icon):
        """Update component status"""
        if component == "backend":
            self.backend_label.config(text=f"Backend: {status}")
            self.backend_icon.config(text=icon)
        elif component == "frontend":
            self.frontend_label.config(text=f"Frontend: {status}")
            self.frontend_icon.config(text=icon)
        elif component == "browser":
            self.browser_label.config(text=f"Browser: {status}")
            self.browser_icon.config(text=icon)
        self.root.update()
        
    def start_application(self):
        """Start the full application"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        
        # Start in separate thread to prevent UI freezing
        threading.Thread(target=self.launch_sequence, daemon=True).start()
        
    def launch_sequence(self):
        """Launch sequence for starting all components"""
        try:
            # Step 1: Start Backend
            self.log_message("Starting backend server...")
            self.update_status("backend", "Starting...", "⏳")
            self.progress['value'] = 10
            
            if self.start_backend():
                self.update_status("backend", "Running ✓", "✅")
                self.log_message("Backend server started successfully")
                self.progress['value'] = 40
                
                # Wait for backend to be ready
                time.sleep(3)
                
                # Step 2: Start Frontend
                self.log_message("Starting frontend server...")
                self.update_status("frontend", "Starting...", "⏳")
                self.progress['value'] = 50
                
                if self.start_frontend():
                    self.update_status("frontend", "Running ✓", "✅")
                    self.log_message("Frontend server started successfully")
                    self.progress['value'] = 80
                    
                    # Wait for frontend to be ready
                    time.sleep(5)
                    
                    # Step 3: Launch Browser
                    self.log_message("Opening browser...")
                    self.update_status("browser", "Launching...", "⏳")
                    self.progress['value'] = 90
                    
                    if self.open_browser():
                        self.update_status("browser", "Opened ✓", "✅")
                        self.log_message("Browser opened successfully")
                        self.progress['value'] = 100
                        
                        self.log_message("🎉 Application launched successfully!")
                        self.log_message("To stop servers, click 'Stop All' button")
                    else:
                        self.log_message("❌ Failed to open browser")
                else:
                    self.log_message("❌ Failed to start frontend")
                    self.update_status("frontend", "Failed ❌", "❌")
            else:
                self.log_message("❌ Failed to start backend")
                self.update_status("backend", "Failed ❌", "❌")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            
    def start_backend(self):
        """Start backend server"""
        try:
            backend_path = self.script_dir / "backend"
            
            if self.os_type == "windows":
              python_exe = backend_path / "venv" / "Scripts" / "python.exe"
              if not python_exe.exists():
                  self.log_message("Virtual environment not found. Please create it first.")
                  return False

              cmd = f'"{python_exe}" "{backend_path / "app.py"}"'
              self.backend_process = subprocess.Popen(
                  cmd,
                  shell=True,
                  creationflags=subprocess.CREATE_NEW_CONSOLE
              )
            else:
                # Unix-like (macOS, Linux)
                venv_activate = backend_path / "venv" / "bin" / "activate"
                if not venv_activate.exists():
                    self.log_message("Virtual environment not found. Creating...")
                    return False
                    
                if self.os_type == "darwin":  # macOS
                    cmd = f'''osascript -e 'tell application "Terminal" to do script "cd \\"{backend_path}\\" && source venv/bin/activate && python app.py"' '''
                else:  # Linux
                    cmd = f'gnome-terminal --title="Backend Server" -- bash -c "cd \\"{backend_path}\\" && source venv/bin/activate && python app.py; exec bash"'
                
                self.backend_process = subprocess.Popen(cmd, shell=True)
            
            self.processes.append(self.backend_process)
            return True
            
        except Exception as e:
            self.log_message(f"Backend error: {str(e)}")
            return False
            
    def start_frontend(self):
        """Start frontend server"""
        try:
            frontend_path = self.script_dir / "frontend"
            
            if self.os_type == "windows":
                # Windows
                cmd = f'cd /d "{frontend_path}" && npm run dev'
                self.frontend_process = subprocess.Popen(
                    cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Unix-like (macOS, Linux)
                if self.os_type == "darwin":  # macOS
                    cmd = f'''osascript -e 'tell application "Terminal" to do script "cd \\"{frontend_path}\\" && npm run dev"' '''
                else:  # Linux
                    cmd = f'gnome-terminal --title="Frontend Server" -- bash -c "cd \\"{frontend_path}\\" && npm run dev; exec bash"'
                
                self.frontend_process = subprocess.Popen(cmd, shell=True)
            
            self.processes.append(self.frontend_process)
            return True
            
        except Exception as e:
            self.log_message(f"Frontend error: {str(e)}")
            return False
            
    def open_browser(self):
        """Open browser"""
        try:
            webbrowser.open("http://localhost:5173/")
            return True
        except Exception as e:
            self.log_message(f"Browser error: {str(e)}")
            return False
            
    def stop_all(self):
        """Stop all processes"""
        self.log_message("Stopping all servers...")
        
        # Kill all tracked processes
        for process in self.processes:
            try:
                if process and process.poll() is None:
                    if self.os_type == "windows":
                        process.terminate()
                    else:
                        process.terminate()
                        process.wait(timeout=5)
            except Exception as e:
                self.log_message(f"Error stopping process: {str(e)}")
        
        # Additional cleanup for Windows
        if self.os_type == "windows":
            try:
                # Kill any remaining python/node processes
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                             capture_output=True, text=True)
                subprocess.run(["taskkill", "/F", "/IM", "node.exe"], 
                             capture_output=True, text=True)
            except:
                pass
        
        self.processes.clear()
        
        # Reset UI
        self.update_status("backend", "Stopped", "⏹️")
        self.update_status("frontend", "Stopped", "⏹️")
        self.update_status("browser", "Closed", "⏹️")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress['value'] = 0
        
        self.log_message("All servers stopped")
        
    def on_closing(self):
        """Handle window closing"""
        self.stop_all()
        self.root.destroy()
        
    def run(self):
        """Start the GUI application"""
        self.log_message("App Launcher ready!")
        self.log_message("Click 'Start Application' to begin")
        self.root.mainloop()

if __name__ == "__main__":
    app = AppLauncher()
    app.run()