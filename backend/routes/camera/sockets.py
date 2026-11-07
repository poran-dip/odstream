"""Socket helpers kept for compatibility.

NOTE: the socket handlers actually registered by the app live in
``routes/socket_events.py``. These functions were part of the original
camera_routes module and are still exported from there.
"""

from routes.camera.state import camera_manager


# Socket event handlers
def handle_connect(socketio_instance):
    """Handle client connection"""
    print("Client connected")
    # Send current state to newly connected client
    socketio_instance.emit(
        "camera_status",
        {
            "active": camera_manager.is_camera_active(),
            "source": camera_manager.camera_source,
            "detection_enabled": camera_manager.detection_enabled,
        },
    )
    socketio_instance.emit(
        "recording_status",
        {
            "recording": camera_manager.is_recording,
            "detection_enabled": camera_manager.detection_enabled,
            "filename": camera_manager.recording_filename,
        },
    )


def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected")
