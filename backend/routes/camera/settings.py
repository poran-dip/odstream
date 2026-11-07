"""Status and video-settings routes, plus a debug endpoint."""

from flask import jsonify, request

from routes.camera.state import broadcast, camera_bp, camera_manager


def _current_video_settings():
    """Snapshot of the manager's current brightness / contrast / saturation."""
    return {
        "brightness": camera_manager.brightness,
        "contrast": camera_manager.contrast,
        "saturation": camera_manager.saturation,
    }


@camera_bp.route("/api/camera_status", methods=["GET"])
def camera_status():
    """Get current camera status"""
    return jsonify(
        {
            "active": camera_manager.is_camera_active(),
            "source": camera_manager.camera_source,
            "uptime_seconds": camera_manager.get_uptime_seconds(),
            "detection_enabled": camera_manager.detection_enabled,
            "recording": camera_manager.is_recording,
            "model_loaded": camera_manager.model is not None,
        }
    )


@camera_bp.route("/api/video_settings", methods=["GET"])
def get_video_settings():
    """Get current video settings (brightness, contrast, saturation)"""
    try:
        current_settings = _current_video_settings()

        return jsonify(
            {
                "success": True,
                "message": "Video settings retrieved successfully",
                "data": current_settings,
            }
        )

    except Exception as e:
        error_message = f"Failed to get video settings: {e!s}"
        return jsonify({"success": False, "error": error_message}), 400


@camera_bp.route("/api/update_video_settings", methods=["POST"])
def update_video_settings():
    """Update video settings (brightness, contrast, saturation)"""
    data = request.get_json() or {}

    brightness = data.get("brightness")
    contrast = data.get("contrast")
    saturation = data.get("saturation")

    try:
        # Update settings in camera manager (values are clamped there)
        camera_manager.update_video_settings(
            brightness=brightness, contrast=contrast, saturation=saturation
        )

        # Get current settings to return
        current_settings = _current_video_settings()

        # Broadcast to all connected clients
        broadcast(
            "video_settings_updated",
            {
                "data": current_settings,
                "message": "Video settings updated successfully",
            },
        )

        return jsonify(
            {
                "success": True,
                "message": "Video settings updated successfully",
                "settings": current_settings,
            }
        )

    except Exception as e:
        error_message = f"Failed to update video settings: {e!s}"
        return jsonify({"success": False, "error": error_message}), 400


@camera_bp.route("/api/debug")
def debug():
    """Debug endpoint to check camera and model status"""
    return jsonify(
        {
            "model_loaded": camera_manager.model is not None,
            "camera_active": camera_manager.is_camera_active(),
            "detection_enabled": camera_manager.detection_enabled,
            "recording": camera_manager.is_recording,
            "recording_filename": camera_manager.recording_filename,
            "camera_source": camera_manager.camera_source,
            "remote_stream_active": (
                camera_manager.remote_stream_active
                if hasattr(camera_manager, "remote_stream_active")
                else None
            ),
            "latency": camera_manager.get_latency_stats(),
        }
    )
