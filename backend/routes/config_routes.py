from pathlib import Path
from datetime import datetime
from flask import Blueprint, jsonify, request
from video_manager import VideoManager
from config import VIDEO_EXTENSIONS
from routes.video_routes import get_video_manager, set_video_manager

# Create blueprint
config_bp = Blueprint("config", __name__)


@config_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"success": True, "status": "healthy", "timestamp": datetime.now().isoformat()}
    )


@config_bp.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration"""
    video_manager = get_video_manager()
    return jsonify(
        {
            "success": True,
            "video_path": str(video_manager.base_path),
            "video_extensions": list(VIDEO_EXTENSIONS),
        }
    )


@config_bp.route("/api/config/path", methods=["POST"])
def set_video_path():
    """Set the video directory path"""
    data = request.get_json()
    new_path = data.get("path")

    if not new_path:
        return jsonify({"success": False, "error": "Path is required"}), 400

    path = Path(new_path)
    if not path.exists():
        return jsonify({"success": False, "error": "Path does not exist"}), 400

    if not path.is_dir():
        return jsonify({"success": False, "error": "Path is not a directory"}), 400

    # Update video manager with new path
    new_video_manager = VideoManager(new_path)
    set_video_manager(new_video_manager)

    return jsonify(
        {
            "success": True,
            "message": "Video path updated successfully",
            "path": str(path),
        }
    )
