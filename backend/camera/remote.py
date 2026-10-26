"""Remote camera support (e.g. odstream-remote on a Jetson, or DroidCam).

A background thread pulls frames from the remote URL and stores the latest one
in ``self.remote_frame_buffer`` (guarded by ``self.remote_frame_lock``). The
frame pipeline then reads from that buffer instead of a local ``VideoCapture``.
"""

import time
import threading

import cv2
import numpy as np
import requests


class RemoteStreamMixin:
    """Connects to, streams from, and controls a remote camera source.

    State used (initialised by the owner class):
        self.camera_source, self.remote_frame_buffer, self.remote_frame_lock,
        self.remote_stream_thread, self.remote_stream_active
    """

    # ------------------------------------------------------------------
    # Background stream worker
    # ------------------------------------------------------------------

    def _remote_stream_worker(self):
        """Worker thread to continuously fetch frames from remote source"""
        try:
            print(f"Connecting to remote stream: {self.camera_source['url']}")

            # First, try to connect and see what we get
            response = requests.get(self.camera_source["url"], stream=True, timeout=10)
            response.raise_for_status()

            print(
                f"Connected to remote stream. Content-Type: {response.headers.get('content-type', 'unknown')}"
            )

            # Check if it's an MJPEG stream
            content_type = response.headers.get("content-type", "").lower()

            if "multipart" in content_type:
                # Handle MJPEG stream
                print("Detected MJPEG stream")
                self._handle_mjpeg_stream(response)
            else:
                # Handle single image endpoint (like DroidCam /video)
                print("Detected single image endpoint, polling for frames")
                self._handle_single_image_polling()

        except Exception as e:
            print(f"Error in remote stream worker: {e}")
            self.remote_stream_active = False

    def _handle_mjpeg_stream(self, response):
        """Handle MJPEG multipart stream"""
        bytes_buffer = b""
        for chunk in response.iter_content(chunk_size=1024):
            if not self.remote_stream_active:
                break

            bytes_buffer += chunk

            # Look for JPEG frame boundaries
            start = bytes_buffer.find(b"\xff\xd8")  # JPEG start
            end = bytes_buffer.find(b"\xff\xd9")  # JPEG end

            if start != -1 and end != -1 and end > start:
                # Extract complete JPEG frame
                jpeg_data = bytes_buffer[start : end + 2]

                # Decode JPEG to OpenCV frame
                nparr = np.frombuffer(jpeg_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    with self.remote_frame_lock:
                        self.remote_frame_buffer = frame

                # Remove processed data from buffer
                bytes_buffer = bytes_buffer[end + 2 :]

    def _handle_single_image_polling(self):
        """Handle single image endpoint by polling"""
        while self.remote_stream_active:
            try:
                # Fetch single frame
                response = requests.get(self.camera_source["url"], timeout=5)
                response.raise_for_status()

                # Decode JPEG to OpenCV frame
                nparr = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    with self.remote_frame_lock:
                        self.remote_frame_buffer = frame
                    print("Frame received from single image endpoint")

                # Small delay to avoid overwhelming the source
                time.sleep(0.1)  # 10 FPS polling rate

            except Exception as e:
                print(f"Error polling single image: {e}")
                time.sleep(1)  # Wait longer on error
                break

    # ------------------------------------------------------------------
    # Remote control API helpers
    # ------------------------------------------------------------------

    def _get_base_url(self, video_feed_url):
        """Extract base URL from video feed URL

        e.g. ``http://host:5000/api/video_feed`` -> ``http://host:5000/api``
        """
        # Handle different URL patterns
        if video_feed_url.endswith("/video_feed"):
            return video_feed_url[: -len("/video_feed")]
        if video_feed_url.endswith("/video"):
            return video_feed_url[: -len("/video")]
        # If no specific endpoint, assume the URL is already the base
        return video_feed_url

    def _start_remote_stream_thread(self):
        """Mark the remote stream active and spawn the daemon worker thread."""
        self.remote_stream_active = True
        self.remote_stream_thread = threading.Thread(
            target=self._remote_stream_worker
        )
        self.remote_stream_thread.daemon = True
        self.remote_stream_thread.start()

    def _start_remote_detection(self):
        """Start detection on remote camera source"""
        try:
            base_url = self._get_base_url(self.camera_source["url"])

            # Check if remote camera is already active
            try:
                status_response = requests.get(f"{base_url}/camera_status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("camera_active", False):
                        print("Remote camera already active")
                        # Still need to start the stream worker if not running
                        if not self.remote_stream_active:
                            self._start_remote_stream_thread()
                        return True, "Remote camera already active"
            except Exception:
                # If status check fails, proceed with start_camera
                pass

            # Try to start camera via API
            try:
                response = requests.post(f"{base_url}/start_camera", timeout=10)
                response.raise_for_status()
                print("Remote camera started via API")
            except Exception as api_error:
                print(
                    f"start_camera API failed (this is OK for sources like DroidCam): {api_error}"
                )
                # Continue anyway - we'll try to connect directly to the stream

            # Start the remote stream worker thread regardless of API success
            self._start_remote_stream_thread()

            return True, "Remote camera connection established"

        except Exception as e:
            print(f"Error starting remote detection: {e}")
            self.remote_stream_active = False
            return False, str(e)

    def _stop_remote_detection(self):
        """Stop detection on remote camera source"""
        try:
            base_url = self._get_base_url(self.camera_source["url"])

            # Stop the stream worker
            self.remote_stream_active = False
            if self.remote_stream_thread and self.remote_stream_thread.is_alive():
                self.remote_stream_thread.join(timeout=5)

            # Stop remote camera
            try:
                response = requests.post(f"{base_url}/stop_camera", timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"Warning: Failed to stop remote camera: {e}")

            # Drop the last buffered frame so stale images aren't served
            with self.remote_frame_lock:
                self.remote_frame_buffer = None

            return True, "Remote camera detection stopped"

        except Exception as e:
            print(f"Error stopping remote detection: {e}")
            return False, str(e)
