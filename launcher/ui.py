"""Builds the launcher window: status cards, controls and terminal tabs."""

import tkinter as tk
from tkinter import ttk

from launcher.theme import TERMINAL_BG


class UIMixin:
    """Creates all Tk widgets. Widgets the rest of the app needs are stored
    on ``self`` (status labels/dots, buttons, progress bar, terminals).

    Expects ``self.root`` and ``self.colors``, plus the button callbacks
    ``start_application``, ``stop_all``, ``launch_app_url`` and
    ``clear_all_terminals`` (provided by the other mixins).
    """

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def setup_ui(self):
        # Sections are packed top-to-bottom in this order
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(
            main_container,
            text="🚀 Full Stack Launcher",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
        )
        title_label.pack(anchor=tk.W, pady=(0, 30))

        self._build_status_cards(main_container)
        self._build_controls(main_container)
        self._build_terminals(main_container)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _build_status_cards(self, parent):
        """Row of three cards: Backend / Frontend / Browser."""
        cards_frame = tk.Frame(parent, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, pady=(0, 25))

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)

        self.backend_status = self.create_status_card(
            cards_frame, "Backend", "🔧", "Ready to start"
        )
        self.backend_status.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.frontend_status = self.create_status_card(
            cards_frame, "Frontend", "🎨", "Ready to start"
        )
        self.frontend_status.grid(row=0, column=1, sticky="ew", padx=5)

        self.browser_status = self.create_status_card(
            cards_frame, "Browser", "🌐", "Ready to launch"
        )
        self.browser_status.grid(row=0, column=2, sticky="ew", padx=(10, 0))

    def _build_controls(self, parent):
        """Progress label/bar and the Start / Stop / Open buttons."""
        control_frame = tk.Frame(parent, bg=self.colors["card_bg"])
        control_frame.pack(fill=tk.X, pady=(0, 25))

        self.progress_label = tk.Label(
            control_frame,
            text="Ready to start",
            font=("Segoe UI", 10),
            bg=self.colors["card_bg"],
            fg=self.colors["text_secondary"],
        )
        self.progress_label.pack(anchor=tk.W, padx=20, pady=(20, 8))

        self.progress = ttk.Progressbar(control_frame, mode="determinate", length=400)
        self.progress.pack(fill=tk.X, padx=20)

        buttons_frame = tk.Frame(control_frame, bg=self.colors["card_bg"])
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)

        self.start_button = tk.Button(
            buttons_frame,
            text="🚀 Start Application",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["accent"],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.start_application,
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))

        self.stop_button = tk.Button(
            buttons_frame,
            text="🛑 Stop All",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["error"],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.stop_all,
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))

        self.launch_url_button = tk.Button(
            buttons_frame,
            text="🌐 Open App",
            font=("Segoe UI", 10),
            bg=self.colors["border"],
            fg=self.colors["text"],
            relief="flat",
            padx=15,
            pady=8,
            command=self.launch_app_url,
            state=tk.DISABLED,
        )
        self.launch_url_button.pack(side=tk.LEFT)

    def _build_terminals(self, parent):
        """Tabbed terminal output: Backend / Frontend / Logs."""
        terminal_frame = tk.Frame(parent, bg=self.colors["card_bg"])
        terminal_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(terminal_frame, bg=self.colors["card_bg"])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        terminal_title = tk.Label(
            header_frame,
            text="🖥️ Terminal Output",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
        )
        terminal_title.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            header_frame,
            text="🗑️ Clear All",
            font=("Segoe UI", 9),
            bg=self.colors["border"],
            fg=self.colors["text"],
            relief="flat",
            padx=10,
            pady=5,
            command=self.clear_all_terminals,
        )
        clear_btn.pack(side=tk.RIGHT)

        self.terminal_notebook = ttk.Notebook(terminal_frame)
        self.terminal_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.backend_terminal = self._add_terminal_tab("🔧 Backend", "#58a6ff")
        self.frontend_terminal = self._add_terminal_tab("🎨 Frontend", "#7dd3fc")
        self.logs_terminal = self._add_terminal_tab("📋 Logs", "#a5d6ff")

    def _add_terminal_tab(self, title, text_color):
        """Add a tab with a read-out Text widget to the notebook and return it."""
        frame = tk.Frame(self.terminal_notebook, bg=TERMINAL_BG)
        self.terminal_notebook.add(frame, text=title)

        terminal = tk.Text(
            frame,
            height=12,
            bg=TERMINAL_BG,
            fg=text_color,
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief="flat",
        )
        terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return terminal

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------

    def create_status_card(self, parent, title, emoji, status):
        """Card with an emoji + title header and a status dot + text row.

        The dot and status label are stored as ``self.<title>_status_dot`` /
        ``self.<title>_status_label`` so ``update_status`` can change them.
        """
        card = tk.Frame(parent, bg=self.colors["card_bg"], relief="flat", bd=1)

        header_frame = tk.Frame(card, bg=self.colors["card_bg"])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        emoji_label = tk.Label(
            header_frame,
            text=emoji,
            font=("Segoe UI", 20),
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
        )
        emoji_label.pack(side=tk.LEFT)

        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
        )
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        status_frame = tk.Frame(card, bg=self.colors["card_bg"])
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        status_dot = tk.Label(
            status_frame,
            text="◯",
            font=("Segoe UI", 12),
            bg=self.colors["card_bg"],
            fg=self.colors["text_secondary"],
        )
        status_dot.pack(side=tk.LEFT)

        status_label = tk.Label(
            status_frame,
            text=status,
            font=("Segoe UI", 10),
            bg=self.colors["card_bg"],
            fg=self.colors["text_secondary"],
        )
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
