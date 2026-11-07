"""
Camera routes entry point.

The handlers themselves live in the ``routes/camera`` package (see its
``__init__.py`` for the layout). Importing those modules here registers their
routes on ``camera_bp``; this file then re-exports everything other modules
(``app.py``, ``socket_events.py``) import from ``routes.camera_routes``.
"""

# Route modules - imported for their side effect of registering routes
from routes.camera import control, recording, settings  # noqa: F401

# Legacy socket helpers
from routes.camera.sockets import handle_connect, handle_disconnect

# Shared blueprint / manager / Socket.IO wiring
from routes.camera.state import (
    camera_bp,
    camera_manager,
    get_camera_manager,
    init_socketio,
)

__all__ = [
    "camera_bp",
    "camera_manager",
    "get_camera_manager",
    "handle_connect",
    "handle_disconnect",
    "init_socketio",
]
