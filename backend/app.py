from flask import Flask, Response, jsonify, request, send_file, abort
from flask_cors import CORS
import cv2
from ultralytics import YOLO
from pathlib import Path
import mimetypes
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variables for YOLO detection
model = None
camera = None

# File System Configuration
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}
DEFAULT_VIDEO_PATH = Path(__file__).resolve().parent.parent / 'shared' / 'recordings'

class VideoManager:
    def __init__(self, base_path=DEFAULT_VIDEO_PATH):
        self.base_path = Path(base_path)
        
    def get_video_files(self):
        """Get all video files from the specified directory"""
        videos = []
        
        if not self.base_path.exists():
            return videos
            
        try:
            for file_path in self.base_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                    stat = file_path.stat()
                    videos.append({
                        'id': str(file_path.name),
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stat.st_size,
                        'lastModified': int(stat.st_mtime * 1000)  # Convert to milliseconds
                    })
        except Exception as e:
            print(f"Error reading directory: {e}")
            
        return sorted(videos, key=lambda x: x['lastModified'], reverse=True)
    
    def rename_video(self, old_name, new_name):
        """Rename a video file"""
        old_path = self.base_path / old_name
        new_path = self.base_path / new_name
        
        if not old_path.exists():
            return False, "File not found"
            
        if new_path.exists():
            return False, "A file with that name already exists"
            
        try:
            old_path.rename(new_path)
            return True, "File renamed successfully"
        except Exception as e:
            return False, f"Error renaming file: {str(e)}"
    
    def delete_video(self, filename):
        """Delete a video file"""
        file_path = self.base_path / filename
        
        if not file_path.exists():
            return False, "File not found"
            
        try:
            file_path.unlink()
            return True, "File deleted successfully"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def get_video_path(self, filename):
        """Get the full path of a video file"""
        file_path = self.base_path / filename
        return file_path if file_path.exists() else None

# Initialize video manager
video_manager = VideoManager()

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all video files from the directory"""
    videos = video_manager.get_video_files()
    return jsonify({
        'success': True,
        'videos': videos,
        'count': len(videos)
    })

@app.route('/api/videos/<filename>', methods=['GET'])
def serve_video(filename):
    """Serve a video file"""
    file_path = video_manager.get_video_path(filename)
    
    if not file_path:
        abort(404)
    
    # Get the MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = 'video/mp4'  # Default fallback
    
    try:
        return send_file(str(file_path), mimetype=mime_type)
    except Exception as e:
        print(f"Error serving file: {e}")
        abort(500)

@app.route('/api/videos/<filename>/rename', methods=['POST'])
def rename_video(filename):
    """Rename a video file"""
    data = request.get_json()
    new_name = data.get('new_name')
    
    if not new_name:
        return jsonify({
            'success': False,
            'error': 'New name is required'
        }), 400
    
    # Ensure the new name has the same extension
    old_path = Path(filename)
    new_path = Path(new_name)
    
    if old_path.suffix.lower() != new_path.suffix.lower():
        new_name = new_path.stem + old_path.suffix
    
    success, message = video_manager.rename_video(filename, new_name)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'new_name': new_name
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/videos/<filename>/delete', methods=['DELETE'])
def delete_video(filename):
    """Delete a video file"""
    success, message = video_manager.delete_video(filename)
    
    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'success': True,
        'video_path': str(video_manager.base_path),
        'video_extensions': list(VIDEO_EXTENSIONS)
    })

@app.route('/api/config/path', methods=['POST'])
def set_video_path():
    """Set the video directory path"""
    data = request.get_json()
    new_path = data.get('path')
    
    if not new_path:
        return jsonify({
            'success': False,
            'error': 'Path is required'
        }), 400
    
    path = Path(new_path)
    if not path.exists():
        return jsonify({
            'success': False,
            'error': 'Path does not exist'
        }), 400
    
    if not path.is_dir():
        return jsonify({
            'success': False,
            'error': 'Path is not a directory'
        }), 400
    
    global video_manager
    video_manager = VideoManager(new_path)
    
    return jsonify({
        'success': True,
        'message': 'Video path updated successfully',
        'path': str(path)
    })

def load_model():
    global model
    try:
        print("Loading YOLOv8 model...")
        model = YOLO('yolov8n.pt')
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def generate_frames():
    global camera, model
    
    print("Starting frame generation...")
    
    while True:
        if camera is None:
            print("Camera stopped, ending stream...")
            break
            
        success, frame = camera.read()
        if not success:
            print("Stream ended (camera stopped or disconnected)")
            break
        
        try:
            # Apply YOLO detection
            if model is not None:
                results = model(frame, verbose=False)
                annotated_frame = results[0].plot()
                # Only log detections when objects are found
                if len(results[0].boxes) > 0:
                    print(f"YOLO detected {len(results[0].boxes)} objects")
            else:
                annotated_frame = frame
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame, 
                                     [cv2.IMWRITE_JPEG_QUALITY, 80])
            
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start_camera')
def start_camera():
    global camera
    
    try:
        print("Starting camera...")
        
        # Load model if not loaded
        if model is None:
            if not load_model():
                return jsonify({'error': 'Failed to load model'}), 500
        
        # Initialize camera
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("Failed to open camera")
            return jsonify({'error': 'Failed to open camera'}), 500
        
        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("Camera started successfully")
        return jsonify({'message': 'Camera started successfully'})
        
    except Exception as e:
        print(f"Error starting camera: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_camera')
def stop_camera():
    global camera
    
    try:
        if camera is not None:
            camera.release()
            camera = None
            print("Camera stopped")
        
        return jsonify({'message': 'Camera stopped'})
        
    except Exception as e:
        print(f"Error stopping camera: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video_feed')
def video_feed():
    print("Video feed endpoint called")
    
    if camera is None:
        print("Camera not initialized")
        return jsonify({'error': 'Camera not started'}), 400
    
    print("Starting video stream...")
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/debug')
def debug():
    return jsonify({
        'model_loaded': model is not None,
        'camera_active': camera is not None and camera.isOpened() if camera else False
    })

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Video directory: {video_manager.base_path}")
    print(f"Server will be available at: http://localhost:5000")

    # Check if default directory exists
    if not video_manager.base_path.exists():
        print(f"Warning: Default video directory '{video_manager.base_path}' does not exist!")
        print("You can change the path using the /api/config/path endpoint")
    
    app.run(debug=True, port=5000, threaded=True)