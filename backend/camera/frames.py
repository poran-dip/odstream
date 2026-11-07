"""Frame acquisition, image adjustments and the MJPEG streaming generator."""

import time

import cv2
from config import Config


class FrameMixin:
    """Reads frames from the active source and streams them to clients.

    Raw frames are streamed by default; when ``self.detection_enabled`` is on
    (i.e. while recording a local camera) frames are YOLO-annotated, logged,
    and written to the active video file.

    State used (initialised by the owner class):
        self.brightness, self.contrast, self.saturation, self.camera,
        self.remote_camera, self.remote_frame_buffer, self.remote_frame_lock,
        self.detection_enabled, self.model, self.is_recording, self.video_writer
    """

    # ------------------------------------------------------------------
    # Video settings (brightness / contrast / saturation)
    # ------------------------------------------------------------------

    def update_video_settings(self, brightness=None, contrast=None, saturation=None):
        """Update video settings from frontend"""
        if brightness is not None:
            self.brightness = max(-100, min(100, brightness))  # Clamp to valid range
        if contrast is not None:
            self.contrast = max(0.0, min(3.0, contrast))
        if saturation is not None:
            self.saturation = max(0.0, min(2.0, saturation))

        print(
            f"Video settings updated - Brightness: {self.brightness}, Contrast: {self.contrast}, Saturation: {self.saturation}"
        )

    def _apply_settings(self, frame):
        """Apply brightness, saturation, and contrast adjustments to frame"""
        if frame is None:
            return frame

        # Convert BGR to HSV for saturation adjustment
        if self.saturation != 1.0:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], self.saturation)
            frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Apply brightness and contrast
        if self.contrast != 1.0 or self.brightness != 0:
            frame = cv2.convertScaleAbs(
                frame, alpha=self.contrast, beta=self.brightness
            )

        return frame

    # ------------------------------------------------------------------
    # Frame acquisition
    # ------------------------------------------------------------------

    def _get_current_frame(self):
        """Get current frame from active source

        Returns ``(success, frame)`` with video settings already applied.
        """
        try:
            if self.remote_camera:
                # Remote source: copy the latest frame from the worker's buffer
                with self.remote_frame_lock:
                    if self.remote_frame_buffer is not None:
                        frame = self.remote_frame_buffer.copy()
                        return True, self._apply_settings(frame)
                    return False, None
            else:
                # Local camera - add safety check
                if self.camera is not None and self.camera.isOpened():
                    success, frame = self.camera.read()
                    if success and frame is not None:
                        frame = self._apply_settings(frame)
                    return success, frame
                return False, None
        except Exception as e:
            print(f"Error getting current frame: {e}")
            return False, None

    # ------------------------------------------------------------------
    # MJPEG stream generator (consumed by the /api/video_feed route)
    # ------------------------------------------------------------------

    def generate_frames(self):
        """Generate frames - raw video by default, with YOLO when recording"""
        print("Starting frame generation...")
        failed_frames = 0
        max_failed_frames = 30

        fps_counter = 0
        fps_timer = time.time()
        fps_interval = 1.0  # print FPS every 1 second

        while True:
            if not self.is_camera_active():
                print("Camera stopped, ending stream...")
                break

            success, frame = self._get_current_frame()
            if not success or frame is None:
                failed_frames += 1
                if failed_frames % 5 == 0:
                    print(f"Failed to get frame ({failed_frames}/{max_failed_frames})")

                if failed_frames >= max_failed_frames:
                    print("Too many failed frames, ending stream...")
                    break

                # Remote frames can lag behind briefly - wait and retry
                if self.remote_camera:
                    time.sleep(0.1)
                    continue

                print("Stream ended (camera stopped or disconnected)")
                break

            # Reset failed frames counter on successful frame
            failed_frames = 0

            # ----- FPS calculation -----
            fps_counter += 1
            current_time = time.time()
            elapsed = current_time - fps_timer
            if elapsed >= fps_interval:
                fps = fps_counter / elapsed
                print(f"[FPS] {fps:.2f}")
                fps_counter = 0
                fps_timer = current_time
            # ---------------------------

            try:
                # Apply YOLO detection only when detection is enabled (during recording)
                if (
                    self.detection_enabled
                    and not self.remote_camera
                    and self.model is not None
                ):
                    annotated_frame, results = self._annotate_frame(frame)
                    if results:
                        self._log_detection(results)
                else:
                    annotated_frame = frame

                # Save frame to video if recording
                if self.is_recording and self.video_writer is not None:
                    self.video_writer.write(annotated_frame)

                # Encode frame as JPEG
                ret, buffer = cv2.imencode(
                    ".jpg",
                    annotated_frame,
                    [cv2.IMWRITE_JPEG_QUALITY, Config.JPEG_QUALITY],
                )

                if ret:
                    # Emit one part of the multipart/x-mixed-replace response
                    frame_bytes = buffer.tobytes()
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )
                else:
                    print("Failed to encode frame")
                    break

            except Exception as e:
                print(f"Error processing frame: {e}")
                break

        print("Frame generation ended")
