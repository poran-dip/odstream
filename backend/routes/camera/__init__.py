"""
Camera HTTP routes, split by concern.

All modules register their handlers on the single ``camera_bp`` blueprint
defined in ``state.py``; ``routes/camera_routes.py`` imports them so the
routes get registered, and re-exports the public helpers used by ``app.py``.

    state.py      - blueprint, shared CameraManager, Socket.IO broadcast helper
    validation.py - validation of camera source payloads
    control.py    - start / change / stop camera, active check, video feed
    recording.py  - snapshots and recording start / stop / status
    settings.py   - camera status, video settings, debug info
    sockets.py    - legacy socket handlers (connect / disconnect)
"""
