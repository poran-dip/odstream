import cv2
from ultralytics import YOLO
from config import Config
from datetime import datetime
from pathlib import Path

class CameraManager:
    def __init__(self):
        self.model = None
        self.camera = None
        self.video_writer = None
        self.is_recording = False
        self.recording_filename = None
        self.log_file = None
        self.detection_buffer = []  # Buffer to track stability
        self.stable_frames_required = 3  # Require 3 consistent frames
        self.last_logged_detection = None  # Track last logged detection for comparison
        
    def load_model(self):
        """Load YOLO model"""
        try:
            print("Loading YOLOv8 model...")
            self.model = YOLO(Config.YOLO_MODEL_PATH)
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def _init_log_file(self):
        """Initialize log file for detection counts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"log_{timestamp}.txt"
            log_path = Config.DEFAULT_LOG_PATH / log_filename
            
            # Ensure directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.log_file = open(log_path, 'w')
            self.log_file.write(f"Detection Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_file.write("Format: [TIMESTAMP] Objects detected: COUNT\n")
            self.log_file.write("-" * 50 + "\n")
            self.log_file.flush()
            
            print(f"Log file initialized: {log_path}")
            
        except Exception as e:
            print(f"Error initializing log file: {e}")
            self.log_file = None
    
    def _init_log_file(self):
        """Initialize log file for detection counts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"log_{timestamp}.txt"
            log_path = Config.DEFAULT_LOG_PATH / log_filename
            
            # Ensure directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.log_file = open(log_path, 'w')
            self.log_file.write(f"Detection Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
            if box.conf[0] >= 0.3:  # Only log detections with confidence >= 0.3
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
        
        # Create detection signature for comparison
        detection_signature = self._format_detection_string(results)
        
        # Add to buffer
        self.detection_buffer.append(detection_signature)
        
        # Keep buffer size manageable
        if len(self.detection_buffer) > self.stable_frames_required:
            self.detection_buffer.pop(0)
        
        # Check if we have enough frames and they're all the same
        if len(self.detection_buffer) == self.stable_frames_required:
            # Check if all detections in buffer are the same
            if all(det == self.detection_buffer[0] for det in self.detection_buffer):
                # Check if this is different from last logged detection
                if detection_signature != self.last_logged_detection:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_file.write(f"[{timestamp}] Objects: {detection_signature}\n")
                    self.log_file.flush()
                    self.last_logged_detection = detection_signature
    
    def start_camera(self):
        """Start camera capture"""
        try:
            print("Starting camera...")
            
            # Load model if not loaded
            if self.model is None:
                if not self.load_model():
                    return False, "Failed to load model"
            
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("Failed to open camera")
                return False, "Failed to open camera"
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
            
            # Initialize log file
            self._init_log_file()
            
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
            
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                print("Camera stopped")
            
            return True, "Camera stopped"
            
        except Exception as e:
            print(f"Error stopping camera: {e}")
            return False, str(e)
    
    def is_camera_active(self):
        """Check if camera is active"""
        return self.camera is not None and self.camera.isOpened() if self.camera else False
    
    def take_snapshot(self):
        """Take a snapshot and save it"""
        if not self.is_camera_active():
            return False, "Camera not active", None
        
        try:
            # Capture frame
            success, frame = self.camera.read()
            if not success:
                return False, "Failed to capture frame", None
            
            # Apply YOLO detection if model is loaded
            if self.model is not None:
                results = self.model(frame, verbose=False)
                annotated_frame = results[0].plot()
            else:
                annotated_frame = frame
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pic_{timestamp}.jpg"
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
        """Start recording annotated video"""
        if not self.is_camera_active():
            return False, "Camera not active"
        
        if self.is_recording:
            return False, "Recording already in progress"
        
        try:
            # Generate filename if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rec_{timestamp}.mp4"
                output_path = Config.DEFAULT_VIDEO_PATH / filename
            else:
                output_path = Path(output_path)
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Define codec and create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            self.video_writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.camera.get(cv2.CAP_PROP_FPS),
                (Config.CAMERA_WIDTH, Config.CAMERA_HEIGHT)
            )
            
            if not self.video_writer.isOpened():
                return False, "Failed to initialize video writer"
            
            self.is_recording = True
            self.recording_filename = str(output_path)
            print(f"Started recording to: {output_path}")
            
            return True, f"Recording started: {output_path.name}"
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False, str(e)
    
    def stop_recording(self):
        """Stop recording video"""
        if not self.is_recording:
            return False, "No recording in progress"
        
        try:
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            
            filename = Path(self.recording_filename).name if self.recording_filename else "unknown"
            self.is_recording = False
            saved_filename = self.recording_filename
            self.recording_filename = None
            
            print(f"Recording stopped and saved: {filename}")
            return True, f"Recording saved: {filename}", saved_filename
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False, str(e), None
    
    def generate_frames(self):
        """Generate frames with YOLO detection"""
        print("Starting frame generation...")
        
        while True:
            if self.camera is None:
                print("Camera stopped, ending stream...")
                break
                
            success, frame = self.camera.read()
            if not success:
                print("Stream ended (camera stopped or disconnected)")
                break
            
            try:
                # Apply YOLO detection
                if self.model is not None:
                    results = self.model(frame, verbose=False)
                    annotated_frame = results[0].plot()
                    # Log detection results if they are stable
                    self._log_detection(results)
                else:
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