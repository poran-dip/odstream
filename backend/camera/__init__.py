"""
Building blocks for ``CameraManager``.

The camera manager used to live in a single ~800 line file. It is now split
into small mixin classes, one per concern, which ``camera_manager.py`` stitches
back together into the public ``CameraManager`` class:

    model.py        - YOLO model loading, inference/annotation, result formatting
    detection_log.py- writing stable detections to a text log file
    remote.py       - pulling frames from a remote (HTTP/MJPEG) camera source
    lifecycle.py    - starting / stopping / switching camera sources
    frames.py       - reading frames, applying video settings, the MJPEG generator
    capture.py      - snapshots and video recording
    perf.py         - FPS / latency metrics and benchmark logging

All mixins share state through ``self``; every attribute they rely on is
initialised in ``CameraManager.__init__``.
"""

from camera.capture import CaptureMixin
from camera.detection_log import DetectionLogMixin
from camera.frames import FrameMixin
from camera.lifecycle import CameraLifecycleMixin
from camera.model import ModelMixin
from camera.perf import PerfMixin
from camera.remote import RemoteStreamMixin

__all__ = [
    "CameraLifecycleMixin",
    "CaptureMixin",
    "DetectionLogMixin",
    "FrameMixin",
    "ModelMixin",
    "PerfMixin",
    "RemoteStreamMixin",
]
