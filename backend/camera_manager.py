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
    PerfMixin,
    RemoteStreamMixin,
)
from config import Config


class CameraManager(
    CameraLifecycleMixin,
    CaptureMixin,
    FrameMixin,
    RemoteStreamMixin,
    DetectionLogMixin,
    PerfMixin,
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

        # time.time() when the current camera session started (see
        # CameraLifecycleMixin.get_uptime_seconds); None while stopped
        self.camera_started_at = None

        # --- Performance metrics (see PerfMixin) ---
        self._last_detection_count = 0
        self._socketio = None  # set via set_socketio() from the routes
        self._current_fps = None
        self._last_capture_time = None
        self._last_encode_time = None
        self._pipeline_latency_ms = None
        self._latency_history = []
        self._max_latency_samples = 30

        # Benchmarking: logs FPS/latency samples while recording
        self.benchmarking = True
        self._benchmark_log_file = None
        self._benchmark_last_write = 0.0
        self._benchmark_interval = 0.5  # seconds between samples
