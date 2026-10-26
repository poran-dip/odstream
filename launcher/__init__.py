"""
Pieces of the desktop launcher (``run_app.py``).

``run_app.py`` defines ``AppLauncher`` and stitches these mixins together:

    theme.py     - colour palette and fonts
    ui.py        - building the Tk window (status cards, buttons, terminals)
    output.py    - terminal output, logging, status updates, URL detection
    processes.py - starting / stopping the backend & frontend dev servers
"""

from launcher.theme import COLORS
from launcher.ui import UIMixin
from launcher.output import OutputMixin
from launcher.processes import ProcessMixin

__all__ = ["COLORS", "UIMixin", "OutputMixin", "ProcessMixin"]
