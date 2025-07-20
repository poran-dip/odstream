#!/usr/bin/env python3

import time
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk
import webbrowser
from pathlib import Path
import queue
import io

class AppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Full Stack App Launcher")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a1a')
        
        # Configure custom styles
        self.setup_styles()
        
        # Center the window
        self.center_window()
        
        # Process tracking
        self.backend_process = None
        self.frontend_process = None
        self.processes = []

        self.backend_queue = queue.Queue()
        self.frontend_queue = queue.Queue()
        self.backend_output = io.StringIO()
        self.frontend_output = io.StringIO()
        self.app_url = "http://localhost:5173/"
        
        # Setup UI
        self.setup_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Get script directory
        self.script_dir = Path(__file__).parent.absolute()
        
        # Detect OS
        self.os_type = platform.system().lower()
        
    def setup_styles(self):
        """Setup custom styles for modern appearance"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom colors
        self.colors = {
            'bg': '#1a1a1a',
            'card_bg': '#2d2d2d',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040'
        }
        
        # Configure styles
        self.style.configure('Card.TFrame', background=self.colors['card_bg'], relief='flat', borderwidth=1)
        self.style.configure('Header.TLabel', background=self.colors['bg'], foreground=self.colors['text'], 
                            font=('Segoe UI', 24, 'bold'))
        self.style.configure('Subtitle.TLabel', background=self.colors['bg'], foreground=self.colors['text_secondary'], 
                            font=('Segoe UI', 11))
        self.style.configure('Status.TLabel', background=self.colors['card_bg'], foreground=self.colors['text'], 
                            font=('Segoe UI', 10))
        self.style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), padding=(15, 8))
        self.style.configure('Secondary.TButton', font=('Segoe UI', 9), padding=(10, 5))
        self.style.configure('Success.TLabel', background=self.colors['card_bg'], foreground=self.colors['success'], 
                            font=('Segoe UI', 10, 'bold'))
        self.style.configure('Warning.TLabel', background=self.colors['card_bg'], foreground=self.colors['warning'], 
                            font=('Segoe UI', 10, 'bold'))
        self.style.configure('Error.TLabel', background=self.colors['card_bg'], foreground=self.colors['error'], 
                            font=('Segoe UI', 10, 'bold'))
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        
    def setup_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.setup_header(main_container)
        
        # Status cards section
        self.setup_status_cards(main_container)
        
        # Control panel
        self.setup_control_panel(main_container)
        
        # Terminal section
        self.setup_modern_terminal(main_container)
        
    def setup_header(self, parent):
        """Setup modern header with gradient-like appearance"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Title with emoji
        title_label = ttk.Label(header_frame, text="🚀 Full Stack Launcher", style='Header.TLabel')
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Launch your development environment with ease", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
    def setup_status_cards(self, parent):
        """Setup modern status cards"""
        cards_frame = tk.Frame(parent, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Configure grid columns
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        
        # Backend card
        self.backend_card = self.create_status_card(cards_frame, "Backend", "🔧", "Ready to start")
        self.backend_card.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        
        # Frontend card
        self.frontend_card = self.create_status_card(cards_frame, "Frontend", "🎨", "Ready to start")
        self.frontend_card.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Browser card
        self.browser_card = self.create_status_card(cards_frame, "Browser", "🌐", "Ready to launch")
        self.browser_card.grid(row=0, column=2, sticky='ew', padx=(10, 0))
        
    def create_status_card(self, parent, title, emoji, status):
        """Create a modern status card"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=15)
        
        # Card header
        header_frame = tk.Frame(card, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Emoji icon
        emoji_label = tk.Label(header_frame, text=emoji, font=('Segoe UI', 20), 
                              bg=self.colors['card_bg'], fg=self.colors['text'])
        emoji_label.pack(side=tk.LEFT)
        
        # Title
        title_label = tk.Label(header_frame, text=title, font=('Segoe UI', 12, 'bold'), 
                              bg=self.colors['card_bg'], fg=self.colors['text'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        status_frame = tk.Frame(card, bg=self.colors['card_bg'])
        status_frame.pack(fill=tk.X)
        
        # Status dot
        status_dot = tk.Label(status_frame, text="●", font=('Segoe UI', 12), 
                             bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        status_dot.pack(side=tk.LEFT)
        
        # Status text
        status_label = tk.Label(status_frame, text=status, font=('Segoe UI', 10), 
                               bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        status_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Store references for updates
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
        
    def setup_control_panel(self, parent):
        """Setup modern control panel"""
        control_frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
        control_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Progress section
        progress_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Progress label
        self.progress_label = tk.Label(progress_frame, text="Ready to start", 
                                      font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                                      fg=self.colors['text_secondary'])
        self.progress_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Modern progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400, height=8)
        self.progress.pack(fill=tk.X)
        
        # Buttons section
        buttons_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Main action buttons
        self.start_button = tk.Button(buttons_frame, text="🚀 Start Application", 
                                     font=('Segoe UI', 11, 'bold'), bg=self.colors['accent'], 
                                     fg='white', relief='flat', padx=20, pady=10, 
                                     command=self.start_application, cursor='hand2')
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_button = tk.Button(buttons_frame, text="🛑 Stop All", 
                                    font=('Segoe UI', 11, 'bold'), bg=self.colors['error'], 
                                    fg='white', relief='flat', padx=20, pady=10, 
                                    command=self.stop_all, state=tk.DISABLED, cursor='hand2')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.launch_url_button = tk.Button(buttons_frame, text="🌐 Open App", 
                                          font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                                          fg=self.colors['text'], relief='flat', padx=15, pady=8, 
                                          command=self.launch_app_url, state=tk.DISABLED, 
                                          cursor='hand2', bd=1, highlightcolor=self.colors['border'])
        self.launch_url_button.pack(side=tk.LEFT)
        
        # Add hover effects
        self.add_button_hover_effects()
        
    def add_button_hover_effects(self):
        """Add hover effects to buttons"""
        def on_enter(e, button, color):
            button.configure(bg=color)
            
        def on_leave(e, button, color):
            button.configure(bg=color)
            
        # Start button hover
        self.start_button.bind("<Enter>", lambda e: on_enter(e, self.start_button, '#3d8bff'))
        self.start_button.bind("<Leave>", lambda e: on_leave(e, self.start_button, self.colors['accent']))
        
        # Stop button hover
        self.stop_button.bind("<Enter>", lambda e: on_enter(e, self.stop_button, '#d32f2f'))
        self.stop_button.bind("<Leave>", lambda e: on_leave(e, self.stop_button, self.colors['error']))
        
        # Launch URL button hover
        self.launch_url_button.bind("<Enter>", lambda e: on_enter(e, self.launch_url_button, '#3d3d3d'))
        self.launch_url_button.bind("<Leave>", lambda e: on_leave(e, self.launch_url_button, self.colors['card_bg']))
        
    def setup_modern_terminal(self, parent):
        """Setup modern terminal with tabs"""
        terminal_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Terminal header
        header_frame = tk.Frame(terminal_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Terminal title
        terminal_title = tk.Label(header_frame, text="📟 Terminal Output", 
                                 font=('Segoe UI', 12, 'bold'), bg=self.colors['card_bg'], 
                                 fg=self.colors['text'])
        terminal_title.pack(side=tk.LEFT)
        
        # Terminal controls
        controls_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
        controls_frame.pack(side=tk.RIGHT)
        
        # Clear all button
        clear_btn = tk.Button(controls_frame, text="🗑️ Clear All", font=('Segoe UI', 9), 
                             bg=self.colors['border'], fg=self.colors['text'], relief='flat', 
                             padx=10, pady=5, command=self.clear_all_terminals, cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        
        # Create notebook for terminal tabs
        self.terminal_notebook = ttk.Notebook(terminal_frame)
        self.terminal_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Backend terminal tab
        backend_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(backend_frame, text="🔧 Backend")
        
        self.backend_terminal = tk.Text(backend_frame, height=12, bg='#0d1117', fg='#58a6ff', 
                                       font=('Consolas', 10), wrap=tk.WORD, relief='flat',
                                       insertbackground='#58a6ff', selectbackground='#264f78')
        self.backend_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frontend terminal tab
        frontend_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(frontend_frame, text="🎨 Frontend")
        
        self.frontend_terminal = tk.Text(frontend_frame, height=12, bg='#0d1117', fg='#7dd3fc', 
                                        font=('Consolas', 10), wrap=tk.WORD, relief='flat',
                                        insertbackground='#7dd3fc', selectbackground='#264f78')
        self.frontend_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Logs tab
        logs_frame = tk.Frame(self.terminal_notebook, bg='#0d1117')
        self.terminal_notebook.add(logs_frame, text="📋 Logs")
        
        self.logs_terminal = tk.Text(logs_frame, height=12, bg='#0d1117', fg='#a5d6ff', 
                                    font=('Consolas', 10), wrap=tk.WORD, relief='flat',
                                    insertbackground='#a5d6ff', selectbackground='#264f78')
        self.logs_terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbars to all terminals
        self.add_scrollbars_to_terminals()
        
    def add_scrollbars_to_terminals(self):
        """Add scrollbars to terminal widgets"""
        for terminal in [self.backend_terminal, self.frontend_terminal, self.logs_terminal]:
            scrollbar = ttk.Scrollbar(terminal.master)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            terminal.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=terminal.yview)
    
    def launch_app_url(self):
        """Launch the application URL in browser"""
        try:
            webbrowser.open(self.app_url)
            self.log_message(f"🌐 Opened {self.app_url} in browser")
        except Exception as e:
            self.log_message(f"❌ Failed to open URL: {str(e)}")
        
    def extract_url_from_output(self, text, process_name):
        """Extract URL from terminal output"""
        import re
        
        # Common patterns for local dev servers
        url_patterns = [
            r'http://localhost:\d+/?',
            r'http://127\.0\.0\.1:\d+/?',
            r'https://localhost:\d+/?',
            r'Local:\s+(http://[^\s]+)',
            r'Network:\s+(http://[^\s]+)',
            r'running at (http://[^\s]+)',
            r'Available on:\s+(http://[^\s]+)',
            r'Local development server started at (http://[^\s]+)'
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                if url != self.app_url:
                    self.app_url = url
                    self.log_message(f"🔗 Detected {process_name} URL: {url}")
                    # Enable the launch button once we detect a URL
                    self.launch_url_button.config(state=tk.NORMAL)
                return url
        return None

    def clear_all_terminals(self):
        """Clear all terminal outputs"""
        self.backend_terminal.delete(1.0, tk.END)
        self.frontend_terminal.delete(1.0, tk.END)
        self.logs_terminal.delete(1.0, tk.END)

    def append_to_terminal(self, terminal_widget, text):
        """Append text to terminal widget"""
        terminal_widget.insert(tk.END, text)
        terminal_widget.see(tk.END)
        self.root.update_idletasks()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main Control Tab
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Control Panel")
        
        # Terminal Output Tab
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="Terminal Output")
        
        # Setup main control panel
        self.setup_control_panel(main_frame)
        
        # Setup terminal output panel
        self.setup_terminal_panel(terminal_frame)
        
    def setup_control_panel(self, parent):
        # Main frame with padding
        main_frame = ttk.Frame(parent, padding="20")
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
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Launch URL button
        self.launch_url_button = ttk.Button(buttons_frame, text="🌐 Open App", 
                                        command=self.launch_app_url, state=tk.DISABLED)
        self.launch_url_button.pack(side=tk.LEFT)
        
        # Status text
        self.status_text = tk.Text(main_frame, height=6, width=50, wrap=tk.WORD)
        self.status_text.pack(pady=(20, 0), fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
    def setup_terminal_panel(self, parent):
        # Create paned window for splitting terminal outputs
        paned_window = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Backend terminal frame
        backend_frame = ttk.LabelFrame(paned_window, text="Backend Terminal", padding="5")
        paned_window.add(backend_frame, weight=1)
        
        # Backend terminal text widget
        self.backend_terminal = tk.Text(backend_frame, height=15, bg='black', fg='white', 
                                    font=('Consolas', 10), wrap=tk.WORD)
        self.backend_terminal.pack(fill=tk.BOTH, expand=True)
        
        # Backend terminal scrollbar
        backend_scrollbar = ttk.Scrollbar(self.backend_terminal)
        backend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backend_terminal.config(yscrollcommand=backend_scrollbar.set)
        backend_scrollbar.config(command=self.backend_terminal.yview)
        
        # Frontend terminal frame
        frontend_frame = ttk.LabelFrame(paned_window, text="Frontend Terminal", padding="5")
        paned_window.add(frontend_frame, weight=1)
        
        # Frontend terminal text widget
        self.frontend_terminal = tk.Text(frontend_frame, height=15, bg='black', fg='white', 
                                        font=('Consolas', 10), wrap=tk.WORD)
        self.frontend_terminal.pack(fill=tk.BOTH, expand=True)
        
        # Frontend terminal scrollbar
        frontend_scrollbar = ttk.Scrollbar(self.frontend_terminal)
        frontend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.frontend_terminal.config(yscrollcommand=frontend_scrollbar.set)
        frontend_scrollbar.config(command=self.frontend_terminal.yview)
        
        # Clear buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Clear backend button
        ttk.Button(buttons_frame, text="Clear Backend", 
                command=lambda: self.backend_terminal.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Clear frontend button
        ttk.Button(buttons_frame, text="Clear Frontend", 
                command=lambda: self.frontend_terminal.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Clear all button
        ttk.Button(buttons_frame, text="Clear All", 
                command=self.clear_all_terminals).pack(side=tk.LEFT, padx=5)
    
    def launch_app_url(self):
        """Launch the application URL in browser"""
        try:
            webbrowser.open(self.app_url)
            self.log_message(f"Opened {self.app_url} in browser")
        except Exception as e:
            self.log_message(f"Failed to open URL: {str(e)}")
        
    def extract_url_from_output(self, text, process_name):
        """Extract URL from terminal output"""
        import re
        
        # Common patterns for local dev servers
        url_patterns = [
            r'http://localhost:\d+/?',
            r'http://127\.0\.0\.1:\d+/?',
            r'https://localhost:\d+/?',
            r'Local:\s+(http://[^\s]+)',
            r'Network:\s+(http://[^\s]+)',
            r'running at (http://[^\s]+)',
            r'Available on:\s+(http://[^\s]+)',
            r'Local development server started at (http://[^\s]+)'
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                if url != self.app_url:
                    self.app_url = url
                    self.log_message(f"Detected {process_name} URL: {url}")
                    # Enable the launch button once we detect a URL
                    self.launch_url_button.config(state=tk.NORMAL)
                return url
        return None

    def clear_all_terminals(self):
        """Clear all terminal outputs"""
        self.backend_terminal.delete(1.0, tk.END)
        self.frontend_terminal.delete(1.0, tk.END)

    def append_to_terminal(self, terminal_widget, text):
        """Append text to terminal widget"""
        terminal_widget.insert(tk.END, text)
        terminal_widget.see(tk.END)
        self.root.update_idletasks()

    def read_process_output(self, process, terminal_widget, process_name):
        """Read output from process and display in terminal"""
        try:
            while process.poll() is None:
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        self.root.after(0, self.append_to_terminal, terminal_widget, line)
                        # Check for URL in output
                        if process_name == "Frontend":
                            self.extract_url_from_output(line, process_name)
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        self.root.after(0, self.append_to_terminal, terminal_widget, f"{line}")
                        # Check for URL in error output too (some servers log to stderr)
                        if process_name == "Frontend":
                            self.extract_url_from_output(line, process_name)
                time.sleep(0.1)
        except Exception as e:
            self.root.after(0, self.append_to_terminal, terminal_widget, f"[{process_name}] Error reading output: {str(e)}\n")
            
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
                time.sleep(10)
                
                # Step 2: Start Frontend
                self.log_message("Starting frontend server...")
                self.update_status("frontend", "Starting...", "⏳")
                self.progress['value'] = 50
                
                if self.start_frontend():
                    self.update_status("frontend", "Running ✓", "✅")
                    self.log_message("Frontend server started successfully")
                    self.progress['value'] = 80
                    
                    # Wait for frontend to be ready
                    time.sleep(8)
                    
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
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
            else:
                # Unix-like (macOS, Linux)
                venv_activate = backend_path / "venv" / "bin" / "activate"
                if not venv_activate.exists():
                    self.log_message("Virtual environment not found. Creating...")
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
            
            # Start thread to read backend output
            threading.Thread(target=self.read_process_output, 
                            args=(self.backend_process, self.backend_terminal, "Backend"), 
                            daemon=True).start()
            
            return True
            
        except Exception as e:
            self.log_message(f"Backend error: {str(e)}")
            return False
            
    def start_frontend(self):
        """Start frontend server"""
        try:
            frontend_path = self.script_dir / "frontend"
            
            if self.os_type == "windows":
                cmd = f'cd /d "{frontend_path}" && npm run dev'
                self.frontend_process = subprocess.Popen(
                    cmd, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
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
            
            # Start thread to read frontend output
            threading.Thread(target=self.read_process_output, 
                            args=(self.frontend_process, self.frontend_terminal, "Frontend"), 
                            daemon=True).start()
            
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