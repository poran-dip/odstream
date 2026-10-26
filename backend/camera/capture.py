"""Snapshots and video recording."""

from pathlib import Path
from datetime import datetime

import cv2
import requests

from config import Config


class CaptureMixin:
    """Saves still images and records (YOLO-annotated) video to disk.

    Snapshots go to ``shared/screenshots`` and recordings to
    ``shared/recordings``. For remote sources the remote device is also asked
    to start/stop its own recording.

    State used (initialised by the owner class):
        self.is_recording, self.recording_filename, self.video_writer,
        self.detection_enabled, self.log_file, self.detection_buffer,
        self.last_logged_detection, self.camera, self.camera_source,
        self.remote_camera, self.model
    """

    def _source_name(self):
        """Name of the active source, used in output filenames."""
        return (
            self.camera_source.get("name", "local") if self.camera_source else "local"
        )

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def take_snapshot(self):
        """Take a snapshot and save it

        Returns ``(success, message, filepath_or_None)``.
        """
        if not self.is_camera_active():
            return False, "Camera not active", None

        try:
            # Capture frame
            success, frame = self._get_current_frame()
            if not success or frame is None:
                return False, "Failed to capture frame", None

            # Apply YOLO detection if enabled and available
            if (
                self.detection_enabled
                and not self.remote_camera
                and self.model is not None
            ):
                annotated_frame, _ = self._annotate_frame(frame)
            else:
                annotated_frame = frame

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pic_{self._source_name()}_{timestamp}.jpg"
            output_path = Config.DEFAULT_SNAPS_PATH / filename

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            success = cv2.imwrite(str(output_path), annotated_frame)

            if success:
                print(f"Snapshot saved: {filename}")
                return True, f"Snapshot saved: {filename}", str(output_path)

            return False, "Failed to save snapshot", None

        except Exception as e:
            print(f"Error taking snapshot: {e}")
            return False, str(e), None

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def start_recording(self, output_path=None):
        """Start recording with YOLO detection enabled"""
        if not self.is_camera_active():
            return False, "Camera not active"

        if self.is_recording:
            return False, "Recording already in progress"

        try:
            # Enable detection mode when recording starts
            self.detection_enabled = True

            # Start recording on remote camera if using remote source
            if self.remote_camera:
                try:
                    base_url = self._get_base_url(self.camera_source["url"])
                    response = requests.post(f"{base_url}/start_recording", timeout=10)
                    if response.status_code != 200:
                        print(
                            "Failed to start remote recording, continuing with local recording anyway"
                        )
                    else:
                        print("Remote recording started successfully")
                except Exception as e:
                    return False, f"Failed to communicate with remote camera: {e}"

            # Initialize log file for detection logging
            if not self.remote_camera:
                self._init_log_file()

            # Generate filename if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rec_{self._source_name()}_{timestamp}.mp4"
                output_path = Config.DEFAULT_VIDEO_PATH / filename
            else:
                output_path = Path(output_path)

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Define codec (H.264) and create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*"avc1")

            # Get frame dimensions from current source
            success, sample_frame = self._get_current_frame()
            if success and sample_frame is not None:
                height, width = sample_frame.shape[:2]
            else:
                width, height = Config.CAMERA_WIDTH, Config.CAMERA_HEIGHT

            # Get FPS based on source type
            if self.remote_camera:
                fps = Config.CAMERA_FPS
            else:
                fps = (
                    self.camera.get(cv2.CAP_PROP_FPS)
                    if self.camera
                    else Config.CAMERA_FPS
                )

            self.video_writer = cv2.VideoWriter(
                str(output_path), fourcc, fps, (width, height)
            )

            if not self.video_writer.isOpened():
                return False, "Failed to initialize video writer"

            self.is_recording = True
            self.recording_filename = str(output_path)
            print(f"Started recording with detection to: {output_path}")

            return True, f"Recording with detection started: {output_path.name}"

        except Exception as e:
            print(f"Error starting recording: {e}")
            return False, str(e)

    def stop_recording(self):
        """Stop recording video and disable detection

        Returns ``(success, message, saved_path_or_None)`` on the normal paths.
        """
        if not self.is_recording:
            return False, "No recording in progress"

        try:
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None

            # Disable detection mode
            self.detection_enabled = False

            # Close log file
            if self.log_file:
                self.log_file.close()
                self.log_file = None
                self.detection_buffer = []
                self.last_logged_detection = None

            filename = (
                Path(self.recording_filename).name
                if self.recording_filename
                else "unknown"
            )
            self.is_recording = False

            # Ask the remote device to stop its own recording too
            if self.remote_camera:
                try:
                    base_url = self._get_base_url(self.camera_source["url"])
                    response = requests.post(f"{base_url}/stop_recording", timeout=10)
                    if response.status_code != 200:
                        print(
                            f"Warning: Failed to stop remote recording: {response.text}"
                        )
                    else:
                        print("Remote recording stopped successfully")
                except Exception as e:
                    print(f"Warning: Failed to communicate with remote camera: {e}")

            saved_filename = self.recording_filename
            self.recording_filename = None

            print(f"Recording stopped, detection disabled: {filename}")
            return True, f"Recording saved: {filename}", saved_filename

        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False, str(e), None
