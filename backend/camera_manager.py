"""
CameraManager: the single object the Flask routes talk to.

The implementation is split across mixins in the ``camera`` package (see
``camera/__init__.py`` for an overview). This file only stitches them together
and defines the shared state they all operate on.
"""

import threading

from camera import (
    CameraLifecycleMixin,
    CaptureMixin,
    DetectionLogMixin,
    FrameMixin,
    ModelMixin,
    RemoteStreamMixin,
)
from config import Config


class CameraManager(
    CameraLifecycleMixin,
    CaptureMixin,
    FrameMixin,
    RemoteStreamMixin,
    DetectionLogMixin,
    ModelMixin,
):
    """Manages the active camera (local or remote), streaming, YOLO detection,
    snapshots and recordings."""

    def __init__(self):
        # --- YOLO model (lazy-loaded on first local camera start) ---
        self.model = None

        # --- Local camera / recording ---
        self.camera = None  # cv2.VideoCapture for local sources
        self.video_writer = None  # cv2.VideoWriter while recording
        self.is_recording = False
        self.recording_filename = None

        # --- Detection logging (see DetectionLogMixin) ---
        self.log_file = None
        self.detection_buffer = []
        self.stable_frames_required = 3
        self.last_logged_detection = None

        # Initialize video settings from config
        self.brightness = Config.DEFAULT_VIDEO_SETTINGS["brightness"]
        self.contrast = Config.DEFAULT_VIDEO_SETTINGS["contrast"]
        self.saturation = Config.DEFAULT_VIDEO_SETTINGS["saturation"]

        # Detection mode - controls whether YOLO is applied
        self.detection_enabled = False

        # --- Remote source support (see RemoteStreamMixin) ---
        self.camera_source = None  # source dict from the frontend
        self.remote_camera = False  # True when camera_source["type"] == "remote"
        self.remote_frame_buffer = None  # latest frame pulled by the worker
        self.remote_frame_lock = threading.Lock()
        self.remote_stream_thread = None
        self.remote_stream_active = False
