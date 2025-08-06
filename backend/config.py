import os
from pathlib import Path
import re

# File System Configuration
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".3gp",
    ".ogv",
}
DEFAULT_VIDEO_PATH = Path(__file__).resolve().parent.parent / "shared" / "recordings"
DEFAULT_SNAPS_PATH = Path(__file__).resolve().parent.parent / "shared" / "screenshots"
DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "shared" / "detections"


def read_api_url_from_runtime_env():
    """Read API_URL from the runtime-env.ts file"""
    # Navigate from backend to uwod-rc/shared/runtime-env.ts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # Go up from backend to uwod-rc
    runtime_env_path = os.path.join(parent_dir, "shared", "runtime-env.ts")

    try:
        with open(runtime_env_path, "r") as file:
            content = file.read()

        # Extract API_URL using regex
        pattern = r'export const API_URL = "([^"]+)"'
        match = re.search(pattern, content)

        if match:
            return match.group(1)
        else:
            raise ValueError("API_URL not found in runtime-env.ts")

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Runtime environment file not found at {runtime_env_path}"
        )
    except Exception as e:
        raise Exception(f"Error reading API_URL from runtime-env.ts: {str(e)}")


# Read API_URL from the TypeScript file
API_URL = read_api_url_from_runtime_env()
API_BASE_URL = f"{API_URL}:5000/api"
JETSON_API_BASE_URL = "http://jetson-nano.local:5000/api"

DEFAULT_SOURCES = [
    {"id": "local", "name": "Local Camera", "url": None},
    {
        "id": "jetson1",
        "name": "Jetson Nano",
        "url": f"{JETSON_API_BASE_URL}/video_feed",
    },
]


class Config:
    SECRET_KEY = "YOLOTUBE_69"

    """Application configuration"""
    DEBUG = True
    PORT = 5000
    THREADED = True

    # Video configuration
    VIDEO_EXTENSIONS = VIDEO_EXTENSIONS
    DEFAULT_VIDEO_PATH = DEFAULT_VIDEO_PATH
    DEFAULT_SNAPS_PATH = DEFAULT_SNAPS_PATH
    DEFAULT_LOG_PATH = DEFAULT_LOG_PATH

    # Camera configuration
    # 0 for webcam
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30

    # Video settings configuration
    DEFAULT_VIDEO_SETTINGS = {
        "brightness": 0,  # -100 to 100 (0 = no change)
        "contrast": 1.0,  # 0.0 to 3.0 (1.0 = no change)
        "saturation": 1.0,  # 0.0 to 2.0 (1.0 = no change)
    }

    # YOLO configuration
    OFFICIAL_NEW_MODEL = True  # v5nu, v8n, etc. do not use for v5n or custom models
    YOLO_MODEL_VERSION = "v5"
    YOLO_MODEL_PATH = "models/yolov5nu.pt"
    JPEG_QUALITY = 80
