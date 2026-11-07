"""Capture routes: snapshots and recording start / stop / status."""

from flask import jsonify, request

from routes.camera.state import broadcast, camera_bp, camera_manager


@camera_bp.route("/api/snapshot", methods=["POST"])
def take_snapshot():
    """Take a snapshot of current frame"""
    success, message, filepath = camera_manager.take_snapshot()

    if success:
        # Broadcast snapshot event to all connected clients
        broadcast(
            "snapshot_taken",
            {
                "success": True,
                "message": message,
                "filepath": filepath,
                "source": camera_manager.camera_source,
            },
        )

        return jsonify(
            {
                "success": True,
                "message": message,
                "filepath": filepath,
                "source": camera_manager.camera_source,
            }
        )

    return jsonify({"success": False, "error": message}), 400


@camera_bp.route("/api/start_recording", methods=["POST"])
def start_recording():
    """Start recording with YOLO detection enabled"""
    data = request.get_json() or {}
    output_path = data.get("output_path")

    success, message = camera_manager.start_recording(output_path)

    if success:
        # Broadcast to all connected clients
        broadcast(
            "recording_status",
            {
                "recording": True,
                "detection_enabled": True,
                "message": message,
                "source": camera_manager.camera_source,
            },
        )

        return jsonify(
            {
                "success": True,
                "message": message,
                "recording": True,
                "detection_enabled": True,
                "source": camera_manager.camera_source,
            }
        )

    return jsonify({"success": False, "error": message}), 400


@camera_bp.route("/api/stop_recording", methods=["POST"])
def stop_recording():
    """Stop recording and disable YOLO detection"""
    result = camera_manager.stop_recording()

    # stop_recording returns 3 values normally, but only 2 when nothing was
    # being recorded
    if len(result) == 3:  # success, message, filename
        success, message, filename = result
    else:  # backwards compatibility
        success, message = result
        filename = None

    if success:
        # Broadcast to all connected clients
        broadcast(
            "recording_status",
            {
                "recording": False,
                "detection_enabled": False,
                "message": message,
                "filename": filename,
                "source": camera_manager.camera_source,
            },
        )

        return jsonify(
            {
                "success": True,
                "message": message,
                "recording": False,
                "detection_enabled": False,
                "filename": filename,
                "source": camera_manager.camera_source,
            }
        )

    return jsonify({"success": False, "error": message}), 400


@camera_bp.route("/api/recording_status", methods=["GET"])
def recording_status():
    """Get current recording status"""
    return jsonify(
        {
            "recording": camera_manager.is_recording,
            "detection_enabled": camera_manager.detection_enabled,
            "filename": camera_manager.recording_filename,
            "camera_active": camera_manager.is_camera_active(),
            "source": camera_manager.camera_source,
        }
    )
