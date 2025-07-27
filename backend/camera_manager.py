import cv2
import requests
import threading
import time

from config import Config
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
            print(f"Connecting to remote stream: {self.camera_source['url']}")
            
            # First, try to connect and see what we get
            response = requests.get(self.camera_source['url'], stream=True, timeout=10)
            response.raise_for_status()
            
            print(f"Connected to remote stream. Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Check if it's an MJPEG stream
            content_type = response.headers.get('content-type', '').lower()
            
            if 'multipart' in content_type:
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

    def _handle_single_image_polling(self):
        """Handle single image endpoint by polling"""
        while self.remote_stream_active:
            try:
                # Fetch single frame
                response = requests.get(self.camera_source['url'], timeout=5)
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
    
    def _get_base_url(self, video_feed_url):
        """Extract base URL from video feed URL"""
        # Handle different URL patterns
        if video_feed_url.endswith('/video_feed'):
            return video_feed_url[:-len('/video_feed')]
        elif video_feed_url.endswith('/video'):
            return video_feed_url[:-len('/video')]
        else:
            # If no specific endpoint, assume the URL is already the base
            return video_feed_url

    def _start_remote_detection(self):
        """Start detection on remote camera source"""
        try:
            base_url = self._get_base_url(self.camera_source['url'])
        
            # Check if remote camera is already active
            try:
                status_response = requests.get(f"{base_url}/camera_status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get('camera_active', False):
                        print("Remote camera already active")
                        # Still need to start the stream worker if not running
                        if not self.remote_stream_active:
                            self.remote_stream_active = True
                            self.remote_stream_thread = threading.Thread(target=self._remote_stream_worker)
                            self.remote_stream_thread.daemon = True
                            self.remote_stream_thread.start()
                        return True, "Remote camera already active"
            except Exception as e:
                # If status check fails, proceed with start_camera
                pass

            # Try to start camera via API
            try:
                response = requests.post(f"{base_url}/start_camera", timeout=10)
                response.raise_for_status()
                print("Remote camera started via API")
            except Exception as api_error:
                print(f"start_camera API failed (this is OK for sources like DroidCam): {api_error}")
                # Continue anyway - we'll try to connect directly to the stream
            
            # Start the remote stream worker thread regardless of API success
            self.remote_stream_active = True
            self.remote_stream_thread = threading.Thread(target=self._remote_stream_worker)
            self.remote_stream_thread.daemon = True
            self.remote_stream_thread.start()
            
            return True, "Remote camera connection established"
            
        except Exception as e:
            print(f"Error starting remote detection: {e}")
            self.remote_stream_active = False
            return False, str(e)
        
    def _stop_remote_detection(self):
        """Stop detection on remote camera source"""
        try:
            base_url = self._get_base_url(self.camera_source['url'])

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
                self.camera_source = {"type": "local", "name": "Webcam", "index": 0}
            
            self.remote_camera = self.camera_source.get('type') == 'remote'
            
            # Handle remote source
            if self.remote_camera:
                success, message = self._start_remote_detection()
                return success, message
            
            # Handle local camera - only if NOT remote
            # Load model for local cameras (needed for detection mode)
            if self.model is None:
                if not self.load_model():
                    print("Warning: Model failed to load - detection features will be disabled")
            
            # Use index from source for local camera
            camera_index = self.camera_source.get('index', 0)
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                print(f"Failed to open camera at index {camera_index}")
                return False, f"Failed to open camera at index {camera_index}"

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
            
            print(f"Camera started successfully at index {camera_index}")
            return True, f"Camera started successfully at index {camera_index}"
            
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
            if hasattr(self, 'camera') and self.camera is not None:
                try:
                    self.camera.release()
                except:
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
        if hasattr(self, 'camera') and self.camera is not None:
            try:
                self.camera.release()
            except:
                pass
            self.camera = None
        
        # Small delay to ensure cleanup is complete
        import time
        time.sleep(0.2)
        
        # Start new camera
        return self.start_camera(source)
    
    def is_camera_active(self):
        """Check if camera is active"""
        if self.remote_camera:
            return self.remote_stream_active
        return self.camera is not None and self.camera.isOpened() if self.camera else False
        
    def _get_current_frame(self):
        """Get current frame from active source"""
        try:
            if self.remote_camera:
                # Remote source
                with self.remote_frame_lock:
                    if self.remote_frame_buffer is not None:
                        return True, self.remote_frame_buffer.copy()
                    return False, None
            else:
                # Local camera - add safety check
                if self.camera is not None and self.camera.isOpened():
                    return self.camera.read()
                return False, None
        except Exception as e:
            print(f"Error getting current frame: {e}")
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
            
            # Start recording on remote camera if using remote source
            if self.remote_camera:
                try:
                    base_url = self._get_base_url(self.camera_source['url'])
                    response = requests.post(f"{base_url}/start_recording", 
                                        timeout=10)
                    if response.status_code != 200:
                        return False, f"Failed to start remote recording: {response.text}"
                    print("Remote recording started successfully")
                except Exception as e:
                    return False, f"Failed to communicate with remote camera: {e}"
                
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

            if self.remote_camera:
                try:
                    base_url = self._get_base_url(self.camera_source['url'])
                    response = requests.post(f"{base_url}/stop_recording", 
                                        timeout=10)
                    if response.status_code != 200:
                        print(f"Warning: Failed to stop remote recording: {response.text}")
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