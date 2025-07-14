from pathlib import Path

# File System Configuration
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}
DEFAULT_VIDEO_PATH = Path(__file__).resolve().parent.parent / 'shared' / 'recordings'
DEFAULT_SNAPS_PATH = Path(__file__).resolve().parent.parent / 'shared' / 'screenshots'
DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / 'shared' / 'detections'

API_BASE_URL = "http://localhost:5000/api"
JETSON_API_BASE_URL = "http://jetson-nano.local:5000/api"

DEFAULT_SOURCES = [
    {"id": "local", "name": "Local Camera", "url": None},
    {"id": "jetson1", "name": "Jetson Nano", "url": f"{JETSON_API_BASE_URL}/video_feed"}
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
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # YOLO configuration
    YOLO_MODEL_PATH = 'yolov8n.pt'
    JPEG_QUALITY = 80