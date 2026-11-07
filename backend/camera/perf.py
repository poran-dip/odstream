"""Performance metrics: FPS, pipeline latency, detection count, benchmarks.

``generate_frames`` (see frames.py) feeds this mixin once per frame:

    _publish_fps(fps)          - once a second; stores it and emits the
                                 ``perf_update`` Socket.IO event
    _record_pipeline_latency() - after each JPEG encode; capture -> encode time
    _write_benchmark_sample()  - appends FPS/latency to a benchmark log while
                                 detection is on (rate-limited)

``_last_capture_time`` is set in ``_get_current_frame`` right before reading a
local camera frame. Remote sources don't set it, so they report no latency.
"""

import time
from datetime import datetime

from config import Config


class PerfMixin:
    """FPS / latency tracking and benchmark logging.

    State used (initialised by the owner class):
        self._socketio, self._current_fps, self._last_capture_time,
        self._pipeline_latency_ms, self._latency_history,
        self._max_latency_samples, self._last_detection_count,
        self.benchmarking, self._benchmark_log_file,
        self._benchmark_last_write, self._benchmark_interval,
        self.detection_enabled
    """

    def set_socketio(self, socketio):
        """Give the manager a Socket.IO server to emit ``perf_update`` on."""
        self._socketio = socketio

    # ------------------------------------------------------------------
    # Live metrics
    # ------------------------------------------------------------------

    def _publish_fps(self, fps):
        """Store the latest FPS and push it, with latency and detection count,
        to every connected client."""
        self._current_fps = fps
        if self._socketio:
            self._socketio.emit(
                "perf_update",
                {
                    "fps": fps,
                    "pipeline_latency_ms": self._pipeline_latency_ms,
                    "detection_count": self._last_detection_count,
                },
            )

    def _record_pipeline_latency(self):
        """Capture -> encode latency for the frame that was just encoded.

        Keeps a rolling window of the last ``_max_latency_samples`` values for
        ``get_latency_stats``.
        """
        if self._last_capture_time is None:
            return
        encode_done = time.time()
        latency_ms = (encode_done - self._last_capture_time) * 1000
        self._pipeline_latency_ms = round(latency_ms, 1)
        self._latency_history.append(latency_ms)
        if len(self._latency_history) > self._max_latency_samples:
            self._latency_history.pop(0)

    def get_latency_stats(self):
        """Return pipeline latency stats (capture -> encode)"""
        if not self._latency_history:
            return {
                "fps": self._current_fps,
                "pipeline_latency_ms": None,
                "avg_ms": None,
                "min_ms": None,
                "max_ms": None,
            }
        return {
            "fps": self._current_fps,
            "pipeline_latency_ms": self._pipeline_latency_ms,
            "avg_ms": round(sum(self._latency_history) / len(self._latency_history), 2),
            "min_ms": round(min(self._latency_history), 2),
            "max_ms": round(max(self._latency_history), 2),
            "samples": len(self._latency_history),
        }

    # ------------------------------------------------------------------
    # Benchmark log (shared/detections/benchmark_<time>.txt)
    # ------------------------------------------------------------------

    def _init_benchmark_log(self):
        """Initialize benchmark log file for FPS/latency measurement sessions"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = Config.DEFAULT_LOG_PATH / f"benchmark_{timestamp}.txt"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # Stays open for the whole recording; closed in stop_recording
            self._benchmark_log_file = open(  # noqa: SIM115
                log_path, "w", encoding="utf-8"
            )
            self._benchmark_log_file.write(
                f"Benchmark Log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            self._benchmark_log_file.write(
                f"Sample interval: {self._benchmark_interval}s "
                f"(~{int(1 / self._benchmark_interval)}x/sec)\n"
            )
            self._benchmark_log_file.write("-" * 60 + "\n")
            self._benchmark_log_file.write("timestamp,fps,pipeline_latency_ms\n")
            self._benchmark_log_file.flush()
            print(f"Benchmark log initialized: {log_path}")
        except Exception as e:
            print(f"Error initializing benchmark log: {e}")
            self._benchmark_log_file = None

    def _write_benchmark_sample(self):
        """Write a single FPS/latency sample if benchmarking is enabled

        Only runs while detection is on (i.e. while recording), at most once
        per ``_benchmark_interval`` seconds. The log is created lazily.
        """
        if not self.benchmarking or not self.detection_enabled:
            return
        now = time.time()
        if now - self._benchmark_last_write < self._benchmark_interval:
            return
        if self._benchmark_log_file is None:
            self._init_benchmark_log()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            fps = self._current_fps or 0.0
            latency = self._pipeline_latency_ms or 0.0
            self._benchmark_log_file.write(f"{timestamp},{fps},{latency:.2f}\n")
            self._benchmark_log_file.flush()
            self._benchmark_last_write = now
        except Exception as e:
            print(f"Error writing benchmark sample: {e}")

    def _close_benchmark_log(self):
        """Close the benchmark log (called when recording stops)."""
        if self._benchmark_log_file:
            self._benchmark_log_file.close()
            self._benchmark_log_file = None
