"""Camera control routes: start, change source, stop, status check, feed."""

from flask import Response, jsonify, request

from routes.camera.state import broadcast, camera_bp, camera_manager
from routes.camera.validation import validate_source


@camera_bp.route("/api/start_camera", methods=["POST"])
def start_camera():
    """Start camera with optional source parameter"""
    data = request.get_json() or {}
    source = data.get("source")

    success, message = camera_manager.start_camera(source)

    # If source is provided, validate it
    # NOTE: validation runs *after* start_camera (existing behaviour, kept as-is)
    if source:
        error = validate_source(source)
        if error:
            return error

    if success:
        # Broadcast to all connected clients
        broadcast(
            "camera_status",
            {
                "active": True,
                "source": camera_manager.camera_source,
                "message": message,
            },
        )

        return jsonify({"message": message, "source": camera_manager.camera_source})

    return jsonify({"error": message}), 500


@camera_bp.route("/api/change_camera_source", methods=["POST"])
def change_camera_source():
    """Change camera source (replaces start_camera since camera is always running)"""
    data = request.get_json() or {}
    source = data.get("source")

    if not source:
        return jsonify({"error": "Source parameter is required"}), 400

    # Validate source structure based on type
    error = validate_source(source)
    if error:
        return error

    success, message = camera_manager.change_camera_source(source)

    if success:
        # Broadcast to all connected clients
        broadcast(
            "camera_status",
            {
                "active": True,
                "source": camera_manager.camera_source,
                "message": message,
            },
        )

        return jsonify(
            {
                "success": True,
                "message": message,
                "source": camera_manager.camera_source,
            }
        )

    return jsonify({"success": False, "error": message}), 500


@camera_bp.route("/api/stop_camera")
def stop_camera():
    """Stop camera endpoint (mainly for shutdown or emergencies)"""
    success, message = camera_manager.stop_camera()

    if success:
        # Broadcast to all connected clients
        broadcast(
            "camera_status", {"active": False, "source": None, "message": message}
        )

        return jsonify({"message": message})

    return jsonify({"error": message}), 500


@camera_bp.route("/api/is_camera_active")
def is_camera_active():
    """Check if a camera is already active"""
    is_active = camera_manager.is_camera_active()

    if is_active:
        return jsonify(
            {
                "message": "Camera active",
                "data": {
                    "active": True,
                    "source": camera_manager.camera_source,
                    "detection_enabled": camera_manager.detection_enabled,
                },
            }
        )

    return jsonify(
        {
            "message": "Camera inactive",
            "data": {"active": False, "source": None, "detection_enabled": False},
        }
    )


@camera_bp.route("/api/video_feed")
def video_feed():
    """Video feed endpoint - streams raw video by default, annotated when recording"""
    print("Video feed endpoint called")

    if not camera_manager.is_camera_active():
        print("Camera not initialized")
        return jsonify({"error": "Camera not started"}), 400

    print("Starting video stream...")
    # MJPEG stream: each part is a JPEG produced by CameraManager.generate_frames
    return Response(
        camera_manager.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
