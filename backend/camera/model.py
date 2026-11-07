"""YOLO model handling: loading, running inference and formatting results."""

import platform
import sys
import warnings
from pathlib import Path

import torch
from config import Config
from ultralytics import YOLO

# The local YOLOv5 repo lives at backend/yolov5. This file is in backend/camera,
# so go up one extra level to reach the backend directory.
BACKEND_DIR = Path(__file__).parent.parent


def _uses_v8_api():
    """True when the configured model uses the Ultralytics (v8-style) API."""
    return Config.OFFICIAL_NEW_MODEL or Config.YOLO_MODEL_VERSION == "v8"


class ModelMixin:
    """Loads the YOLO model and runs it on frames.

    Supports both the Ultralytics API (YOLOv8 / "official new" models) and
    custom YOLOv5 models loaded through ``torch.hub`` from a local repo.

    Expects ``self.model`` to be initialised (to ``None``) by the owner class.
    """

    def load_model(self):
        """Load YOLO model based on config version (v5 or v8)"""
        try:
            print(
                f"Loading YOLO model ({Config.YOLO_MODEL_VERSION}) from {Config.YOLO_MODEL_PATH}"
            )

            # Handle PosixPath on Windows (models pickled on Linux/macOS)
            if platform.system() == "Windows":
                import pathlib

                pathlib.PosixPath = pathlib.WindowsPath

            if _uses_v8_api():
                # YOLOv8 (Ultralytics official)
                self.model = YOLO(Config.YOLO_MODEL_PATH)

            elif Config.YOLO_MODEL_VERSION == "v5":
                # YOLOv5 custom repo
                yolov5_path = BACKEND_DIR / "yolov5"
                if str(yolov5_path) not in sys.path:
                    sys.path.append(str(yolov5_path))

                # Suppress annoying future warnings (e.g., amp.autocast)
                warnings.filterwarnings("ignore", category=FutureWarning)

                self.model = torch.hub.load(
                    str(yolov5_path),
                    "custom",
                    path=str(Path(Config.YOLO_MODEL_PATH)),
                    source="local",
                    force_reload=True,
                )
                self.model.eval()

            else:
                raise ValueError(
                    f"Unsupported YOLO version: {Config.YOLO_MODEL_VERSION}"
                )

            print("Model loaded successfully!")
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def _annotate_frame(self, frame):
        """
        Annotate frame using YOLO model results.
        Handles YOLOv5 render() and YOLOv8 plot() differences safely.

        Returns a tuple of ``(annotated_frame, raw_results)``. If annotation is
        not possible the original frame is returned unchanged.
        """
        try:
            results = None

            if _uses_v8_api():
                results = self.model(frame, verbose=False)
                # handle list return type
                if (
                    isinstance(results, list)
                    and len(results) > 0
                    and hasattr(results[0], "plot")
                ):
                    return results[0].plot(), results
                if hasattr(results, "plot"):
                    return results.plot(), results

            elif Config.YOLO_MODEL_VERSION == "v5":
                results = self.model(frame)
                if hasattr(results, "render"):
                    return results.render()[0], results

            return frame, results  # fallback

        except Exception as e:
            print(f"Error annotating frame: {e}")
            return frame, results

    def _format_detection_string(self, results):
        """Format detection results into a readable string

        e.g. ``"person(0.91), boat(0.45)"``. Detections below the confidence
        threshold are ignored.
        """
        try:
            detections = []
            conf_threshold = 0.3

            if _uses_v8_api():
                # YOLOv8 Detections, handles both single result & list of results
                res_list = results if isinstance(results, list) else [results]
                for res in res_list:
                    if not hasattr(res, "boxes") or len(res.boxes) == 0:
                        continue
                    for box in res.boxes:
                        conf = float(box.conf)
                        if conf >= conf_threshold:
                            detections.append(f"{res.names[int(box.cls)]}({conf:.2f})")

            elif Config.YOLO_MODEL_VERSION == "v5":
                # YOLOv5 AutoShape Detections
                if len(results.xyxy[0]) == 0:
                    return "No objects detected"
                for *box, conf, cls in results.xyxy[0]:
                    if conf >= conf_threshold:
                        detections.append(f"{results.names[int(cls)]}({conf:.2f})")

            return (
                ", ".join(detections)
                if detections
                else "No high-confidence objects detected"
            )

        except Exception as e:
            print(f"Error formatting detections: {e}")
            return "Detection formatting error"
