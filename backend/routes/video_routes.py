from pathlib import Path
import mimetypes
from flask import Blueprint, jsonify, request, send_file, abort
from video_manager import VideoManager

# Create blueprint
video_bp = Blueprint("video", __name__)

# Initialize video manager
video_manager = VideoManager()


@video_bp.route("/api/videos", methods=["GET"])
def get_videos():
    """Get all video files from the directory"""
    videos = video_manager.get_video_files()
    return jsonify({"success": True, "videos": videos, "count": len(videos)})


@video_bp.route("/api/videos/<filename>", methods=["GET"])
def serve_video(filename):
    """Serve a video file"""
    file_path = video_manager.get_video_path(filename)

    if not file_path:
        abort(404)

    # Get the MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "video/mp4"  # Default fallback

    try:
        return send_file(str(file_path), mimetype=mime_type)
    except Exception as e:
        print(f"Error serving file: {e}")
        abort(500)


@video_bp.route("/api/videos/<filename>/rename", methods=["POST"])
def rename_video(filename):
    """Rename a video file"""
    data = request.get_json()
    new_name = data.get("new_name")

    if not new_name:
        return jsonify({"success": False, "error": "New name is required"}), 400

    # Ensure the new name has the same extension
    old_path = Path(filename)
    new_path = Path(new_name)

    if old_path.suffix.lower() != new_path.suffix.lower():
        new_name = new_path.stem + old_path.suffix

    success, message = video_manager.rename_video(filename, new_name)

    if success:
        return jsonify({"success": True, "message": message, "new_name": new_name})

    return jsonify({"success": False, "error": message}), 400


@video_bp.route("/api/videos/<filename>/delete", methods=["DELETE"])
def delete_video(filename):
    """Delete a video file"""
    success, message = video_manager.delete_video(filename)

    if success:
        return jsonify({"success": True, "message": message})

    return jsonify({"success": False, "error": message}), 400


def get_video_manager():
    """Get the video manager instance"""
    return video_manager


def set_video_manager(new_manager):
    """Set a new video manager instance"""
    global video_manager
    video_manager = new_manager
