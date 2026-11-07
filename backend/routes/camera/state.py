"""Shared state for the camera routes: blueprint, manager and Socket.IO."""

from camera_manager import CameraManager
from flask import Blueprint

# Create blueprint (every camera route module registers onto this one)
camera_bp = Blueprint("camera", __name__)

# Initialize camera manager (single shared instance for the whole app)
camera_manager = CameraManager()

# This will be injected by the main app via init_socketio()
SOCKETIO = None


def init_socketio(socketio_instance):
    """Initialize socketio instance for this blueprint"""
    global SOCKETIO
    SOCKETIO = socketio_instance
    # Lets the manager emit "perf_update" from the frame loop
    camera_manager.set_socketio(socketio_instance)


def broadcast(event, payload):
    """Emit ``event`` to all connected clients, if Socket.IO is set up."""
    if SOCKETIO:
        SOCKETIO.emit(event, payload)


def get_camera_manager():
    """Get the camera manager instance"""
    return camera_manager
