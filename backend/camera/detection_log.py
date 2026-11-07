"""Text log of detections, written only when a detection is stable."""

from datetime import datetime

from config import Config


class DetectionLogMixin:
    """Writes detection results to ``shared/detections/log_<source>_<time>.txt``.

    To avoid flooding the log with flickering detections, a result is only
    written once it has been identical for ``self.stable_frames_required``
    consecutive frames, and only if it differs from the last logged result.

    State used (initialised by the owner class):
        self.log_file, self.detection_buffer, self.stable_frames_required,
        self.last_logged_detection, self.camera_source
    Requires ``_format_detection_string`` (from ``ModelMixin``).
    """

    def _init_log_file(self):
        """Initialize log file for detection counts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = (
                self.camera_source.get("name", "unknown")
                if self.camera_source
                else "local"
            )
            log_filename = f"log_{source_name}_{timestamp}.txt"
            log_path = Config.DEFAULT_LOG_PATH / log_filename

            # Ensure directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Write a small header describing the log format
            self.log_file = open(log_path, "w", encoding="utf-8")  # noqa: SIM115
            self.log_file.write(
                f"Detection Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            self.log_file.write(f"Camera Source: {source_name}\n")
            self.log_file.write(
                "Format: [TIMESTAMP] Objects: class(confidence), class(confidence), ...\n"
            )
            self.log_file.write(
                "Note: Only logs when detections are stable for 3+ frames\n"
            )
            self.log_file.write("-" * 70 + "\n")
            self.log_file.flush()

            print(f"Log file initialized: {log_path}")

        except Exception as e:
            print(f"Error initializing log file: {e}")
            self.log_file = None

    def _log_detection(self, results):
        """Log detection results if they are stable"""
        if not self.log_file:
            return

        detection_signature = self._format_detection_string(results)
        self.detection_buffer.append(detection_signature)

        # Keep only the last N signatures (sliding window)
        if len(self.detection_buffer) > self.stable_frames_required:
            self.detection_buffer.pop(0)

        # Window is full and every entry matches -> detection is stable
        if (
            len(self.detection_buffer) == self.stable_frames_required
            and all(det == self.detection_buffer[0] for det in self.detection_buffer)
            # Only write when the stable detection actually changed
            and detection_signature != self.last_logged_detection
        ):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_file.write(f"[{timestamp}] Objects: {detection_signature}\n")
            self.log_file.flush()
            self.last_logged_detection = detection_signature
