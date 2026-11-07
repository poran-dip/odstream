"""Starting, stopping and switching the active camera source."""

import time

import cv2
from config import Config


class CameraLifecycleMixin:
    """Owns the camera on/off lifecycle for both local and remote sources.

    A *source* is a dict sent by the frontend, e.g.
        ``{"type": "local", "name": "Webcam", "index": 0}``
        ``{"type": "remote", "name": "Jetson", "url": "http://.../video_feed"}``

    Requires ``RemoteStreamMixin`` (remote start/stop), ``ModelMixin``
    (``load_model``) and ``CaptureMixin`` (``stop_recording``).
    """

    def start_camera(self, source=None):
        """Start camera capture - local or remote"""
        try:
            print("Starting camera...")

            # Set camera source
            if source:
                self.camera_source = source
            else:
                self.camera_source = {"type": "local", "name": "Webcam", "index": 0}

            self.remote_camera = self.camera_source.get("type") == "remote"

            # Handle remote source
            if self.remote_camera:
                success, message = self._start_remote_detection()
                if success:
                    self.camera_started_at = time.time()
                return success, message

            # Handle local camera - only if NOT remote
            # Load model for local cameras (needed for detection mode)
            if self.model is None and not self.load_model():
                print(
                    "Warning: Model failed to load - detection features will be disabled"
                )

            # Use index from source for local camera
            camera_index = self.camera_source.get("index", 0)
            self.camera = cv2.VideoCapture(camera_index)

            if not self.camera.isOpened():
                print(f"Failed to open camera at index {camera_index}")
                return False, f"Failed to open camera at index {camera_index}"

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)

            self.camera_started_at = time.time()
            print(f"Camera started successfully at index {camera_index}")
            return True, f"Camera started successfully at index {camera_index}"

        except Exception as e:
            print(f"Error starting camera: {e}")
            return False, str(e)

    def stop_camera(self):
        """Stop camera capture"""
        # Any stop (including a source change) resets the uptime
        self.camera_started_at = None
        try:
            # Stop recording if active
            if self.is_recording:
                self.stop_recording()

            # Close log file
            if self.log_file:
                self.log_file.close()
                self.log_file = None
                self.detection_buffer = []
                self.last_logged_detection = None

            # Disable detection
            self.detection_enabled = False

            # Handle remote source
            if self.remote_camera:
                success, message = self._stop_remote_detection()
                self.camera_source = None
                self.remote_camera = False
                return success, message

            # Handle local camera - make sure to release properly
            if self.camera is not None:
                try:
                    self.camera.release()
                    print("Local camera released")
                except Exception as e:
                    print(f"Error releasing camera: {e}")
                finally:
                    self.camera = None

            # Clean up camera source references
            self.camera_source = None
            self.remote_camera = False

            print("Camera stopped")
            return True, "Camera stopped"

        except Exception as e:
            print(f"Error stopping camera: {e}")
            # Force cleanup even on error
            if hasattr(self, "camera") and self.camera is not None:
                try:
                    self.camera.release()
                except Exception:
                    pass
                self.camera = None
            self.camera_source = None
            self.remote_camera = False
            return False, str(e)

    def change_camera_source(self, source):
        """Change camera source (stops current camera and starts new one)"""
        print(f"Changing camera source to: {source}")

        # Stop current camera with better error handling
        try:
            self.stop_camera()
        except Exception as e:
            print(f"Warning: Error stopping current camera: {e}")
            # Force cleanup
            self.camera = None
            self.camera_source = None
            self.remote_camera = False

        # Force cleanup of any lingering camera objects
        if hasattr(self, "camera") and self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass
            self.camera = None

        # Small delay to ensure cleanup is complete
        time.sleep(0.2)

        # Start new camera
        return self.start_camera(source)

    def is_camera_active(self):
        """Check if camera is active"""
        if self.remote_camera:
            # Remote sources are "active" while the stream worker is running
            return self.remote_stream_active
        return (
            self.camera is not None and self.camera.isOpened() if self.camera else False
        )

    def get_uptime_seconds(self):
        """Seconds since the current camera session started, or None if off.

        Sent to clients as ``uptime_seconds`` so every tab shows the real
        camera uptime instead of the time since it connected. A relative value
        (not a timestamp) avoids clock differences between server and clients.
        """
        if self.camera_started_at is None or not self.is_camera_active():
            return None
        return round(time.time() - self.camera_started_at, 1)
