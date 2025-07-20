import cv2
import requests
import threading
import time

from config import Config, API_URL
from datetime import datetime
from pathlib import Path
import numpy as np

class CameraManager:
    def __init__(self):
        self.model = None
        self.camera = None
        self.video_writer = None
        self.is_recording = False
        self.recording_filename = None
        self.log_file = None
        self.detection_buffer = []
        self.stable_frames_required = 3
        self.last_logged_detection = None
        
        # Detection mode - controls whether YOLO is applied
        self.detection_enabled = False
        
        # Remote source support
        self.camera_source = None
        self.remote_camera = False
        self.remote_frame_buffer = None
        self.remote_frame_lock = threading.Lock()
        self.remote_stream_thread = None
        self.remote_stream_active = False
        
    def load_model(self):
        """Load YOLO model"""
        try:
            print(f"Loading YOLO model from {Config.YOLO_MODEL_PATH}")

            if not Config.CUSTOM_MODEL:
                from ultralytics import YOLO
                self.model = YOLO(Config.YOLO_MODEL_PATH)
            else:
                import torch
                checkpoint = torch.load(Config.YOLO_MODEL_PATH, map_location='cpu')
    
                if hasattr(checkpoint, 'model'):
                    self.model = checkpoint.model
                elif 'model' in checkpoint:
                    self.model = checkpoint['model']
                elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                    raise NotImplementedError("State dict loading requires model architecture definition")
                else:
                    self.model = checkpoint
                
                if hasattr(self.model, 'eval'):
                    self.model.eval()
            
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def _init_log_file(self):
        """Initialize log file for detection counts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = self.camera_source.get('name', 'unknown') if self.camera_source else 'local'
            log_filename = f"log_{source_name}_{timestamp}.txt"
            log_path = Config.DEFAULT_LOG_PATH / log_filename
            
            # Ensure directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.log_file = open(log_path, 'w')
            self.log_file.write(f"Detection Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_file.write(f"Camera Source: {source_name}\n")
            self.log_file.write("Format: [TIMESTAMP] Objects: class(confidence), class(confidence), ...\n")
            self.log_file.write("Note: Only logs when detections are stable for 3+ frames\n")
            self.log_file.write("-" * 70 + "\n")
            self.log_file.flush()
            
            print(f"Log file initialized: {log_path}")
            
        except Exception as e:
            print(f"Error initializing log file: {e}")
            self.log_file = None
    
    def _format_detection_string(self, results):
        """Format detection results into a readable string"""
        if not results or len(results[0].boxes) == 0:
            return "No objects detected"
        
        detections = []
        for box in results[0].boxes:
            if box.conf[0] >= 0.3:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names[class_id]
                detections.append(f"{class_name}({confidence:.2f})")
        
        if not detections:
            return "No high-confidence objects detected"
        
        return ", ".join(detections)
    
    def _log_detection(self, results):
        """Log detection results if they are stable"""
        if not self.log_file:
            return
        
        detection_signature = self._format_detection_string(results)
        self.detection_buffer.append(detection_signature)
        
        if len(self.detection_buffer) > self.stable_frames_required:
            self.detection_buffer.pop(0)
        
        if len(self.detection_buffer) == self.stable_frames_required:
            if all(det == self.detection_buffer[0] for det in self.detection_buffer):
                if detection_signature != self.last_logged_detection:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_file.write(f"[{timestamp}] Objects: {detection_signature}\n")
                    self.log_file.flush()
                    self.last_logged_detection = detection_signature
    
    def _remote_stream_worker(self):
        """Worker thread to continuously fetch frames from remote source"""
        try:
            response = requests.get(self.camera_source['url'], stream=True, timeout=10)
            response.raise_for_status()
            
            bytes_buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                if not self.remote_stream_active:
                    break
                    
                bytes_buffer += chunk
                
                # Look for JPEG frame boundaries
                start = bytes_buffer.find(b'\xff\xd8')  # JPEG start
                end = bytes_buffer.find(b'\xff\xd9')    # JPEG end
                
                if start != -1 and end != -1 and end > start:
                    # Extract complete JPEG frame
                    jpeg_data = bytes_buffer[start:end+2]
                    
                    # Decode JPEG to OpenCV frame
                    nparr = np.frombuffer(jpeg_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        with self.remote_frame_lock:
                            self.remote_frame_buffer = frame
                    
                    # Remove processed data from buffer
                    bytes_buffer = bytes_buffer[end+2:]
                    
        except Exception as e:
            print(f"Error in remote stream worker: {e}")
            self.remote_stream_active = False
    
    def _start_remote_detection(self):
        """Start detection on remote camera source"""
        try:
            response = requests.post(f"{self.camera_source['url'].replace('/api/video_feed', '')}/api/start_camera", timeout=10)
            response.raise_for_status()
            
            # Start the remote stream worker thread
            self.remote_stream_active = True
            self.remote_stream_thread = threading.Thread(target=self._remote_stream_worker)
            self.remote_stream_thread.daemon = True
            self.remote_stream_thread.start()
            
            return True, "Remote camera detection started"
            
        except Exception as e:
            print(f"Error starting remote detection: {e}")
            return False, str(e)
    
    def _stop_remote_detection(self):
        """Stop detection on remote camera source"""
        try:
            # Stop the stream worker
            self.remote_stream_active = False
            if self.remote_stream_thread and self.remote_stream_thread.is_alive():
                self.remote_stream_thread.join(timeout=5)
            
            # Stop remote camera
            base_url = self.camera_source['url'].replace('/api/video_feed', '')
            response = requests.post(f"{base_url}/api/stop_camera", timeout=10)
            response.raise_for_status()
            
            with self.remote_frame_lock:
                self.remote_frame_buffer = None
            
            return True, "Remote camera detection stopped"
            
        except Exception as e:
            print(f"Error stopping remote detection: {e}")
            return False, str(e)
    
    def start_camera(self, source=None):
        """Start camera capture - local or remote"""
        try:
            print("Starting camera...")
            
            # Set camera source
            if source:
                self.camera_source = source
            else:
                self.camera_source = {"id": "local", "name": "Local Camera", "url": None}
            
            source_url = self.camera_source.get('url')
            self.remote_camera = source_url is not None and not any(
                host in source_url.lower() for host in ['localhost', '127.0.0.1', f"{API_URL}"]
            )
            
            # Load model for local cameras (needed for detection mode)
            if not self.remote_camera:
                if self.model is None:
                    if not self.load_model():
                        print("Warning: Model failed to load - detection features will be disabled")
            
            # Handle remote source
            if self.remote_camera:
                success, message = self._start_remote_detection()
                return success, message
            
            # Handle local camera
            self.camera = cv2.VideoCapture(Config.CAMERA_INDEX)
            
            if not self.camera.isOpened():
                print("Failed to open camera")
                return False, "Failed to open camera"
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
            
            print("Camera started successfully")
            return True, "Camera started successfully"
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False, str(e)
    
    def stop_camera(self):
        """Stop camera capture"""
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
            
            # Handle local camera
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                print("Camera stopped")
            
            self.camera_source = None
            self.remote_camera = False
            return True, "Camera stopped"
            
        except Exception as e:
            print(f"Error stopping camera: {e}")
            return False, str(e)
    
    def change_camera_source(self, source):
        """Change camera source (stops current camera and starts new one)"""
        print(f"Changing camera source to: {source}")
        
        # Stop current camera
        self.stop_camera()
        
        # Start new camera
        return self.start_camera(source)
    
    def is_camera_active(self):
        """Check if camera is active"""
        if self.remote_camera:
            return self.remote_stream_active
        return self.camera is not None and self.camera.isOpened() if self.camera else False

    def _get_current_frame(self):
        """Get current frame from active source"""
        if self.remote_camera:
            # Remote source
            with self.remote_frame_lock:
                if self.remote_frame_buffer is not None:
                    return True, self.remote_frame_buffer.copy()
                return False, None
        else:
            # Local camera
            if self.camera is not None:
                return self.camera.read()
            return False, None
    
    def take_snapshot(self):
        """Take a snapshot and save it"""
        if not self.is_camera_active():
            return False, "Camera not active", None
        
        try:
            # Capture frame
            success, frame = self._get_current_frame()
            if not success or frame is None:
                return False, "Failed to capture frame", None
            
            # Apply YOLO detection if enabled and available
            if self.detection_enabled and not self.remote_camera and self.model is not None:
                results = self.model(frame, verbose=False)
                annotated_frame = results[0].plot()
            else:
                annotated_frame = frame
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = self.camera_source.get('name', 'local') if self.camera_source else 'local'
            filename = f"pic_{source_name}_{timestamp}.jpg"
            output_path = Config.DEFAULT_SNAPS_PATH / filename
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            success = cv2.imwrite(str(output_path), annotated_frame)
            
            if success:
                print(f"Snapshot saved: {filename}")
                return True, f"Snapshot saved: {filename}", str(output_path)
            else:
                return False, "Failed to save snapshot", None
                
        except Exception as e:
            print(f"Error taking snapshot: {e}")
            return False, str(e), None
    
    def start_recording(self, output_path=None):
        """Start recording with YOLO detection enabled"""
        if not self.is_camera_active():
            return False, "Camera not active"
        
        if self.is_recording:
            return False, "Recording already in progress"
        
        try:
            # Enable detection mode when recording starts
            self.detection_enabled = True
            
            # Initialize log file for detection logging
            if not self.remote_camera:
                self._init_log_file()
            
            # Generate filename if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                source_name = self.camera_source.get('name', 'local') if self.camera_source else 'local'
                filename = f"rec_{source_name}_{timestamp}.mp4"
                output_path = Config.DEFAULT_VIDEO_PATH / filename
            else:
                output_path = Path(output_path)
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Define codec and create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            
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
                fps = self.camera.get(cv2.CAP_PROP_FPS) if self.camera else Config.CAMERA_FPS
            
            self.video_writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps,
                (width, height)
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
        """Stop recording video and disable detection"""
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
            
            filename = Path(self.recording_filename).name if self.recording_filename else "unknown"
            self.is_recording = False
            saved_filename = self.recording_filename
            self.recording_filename = None
            
            print(f"Recording stopped, detection disabled: {filename}")
            return True, f"Recording saved: {filename}", saved_filename
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False, str(e), None
    
    def generate_frames(self):
        """Generate frames - raw video by default, with YOLO when recording"""
        print("Starting frame generation...")
        failed_frames = 0
        max_failed_frames = 30
        
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
                
                if self.remote_camera:
                    # For remote sources, continue trying
                    time.sleep(0.1)
                    continue
                else:
                    print("Stream ended (camera stopped or disconnected)")
                    break
            
            # Reset failed frames counter on successful frame
            failed_frames = 0
            
            try:
                # Apply YOLO detection only when detection is enabled (during recording)
                if self.detection_enabled and not self.remote_camera and self.model is not None:
                    results = self.model(frame, verbose=False)
                    annotated_frame = results[0].plot()
                    # Log detection results if they are stable
                    self._log_detection(results)
                else:
                    # For raw video streaming or remote cameras, use frame as-is
                    annotated_frame = frame
                
                # Save frame to video if recording
                if self.is_recording and self.video_writer is not None:
                    self.video_writer.write(annotated_frame)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame, 
                                         [cv2.IMWRITE_JPEG_QUALITY, Config.JPEG_QUALITY])
                
                if ret:
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    print("Failed to encode frame")
                    break
                    
            except Exception as e:
                print(f"Error processing frame: {e}")
                break
        
        print("Frame generation ended")