from flask import Blueprint, jsonify, Response, request
from camera_manager import CameraManager

# Create blueprint
camera_bp = Blueprint('camera', __name__)

# Initialize camera manager
camera_manager = CameraManager()

@camera_bp.route('/api/start_camera')
def start_camera():
    """Start camera endpoint"""
    success, message = camera_manager.start_camera()
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

@camera_bp.route('/api/stop_camera')
def stop_camera():
    """Stop camera endpoint"""
    success, message = camera_manager.stop_camera()
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

@camera_bp.route('/api/video_feed')
def video_feed():
    """Video feed endpoint"""
    print("Video feed endpoint called")
    
    if not camera_manager.is_camera_active():
        print("Camera not initialized")
        return jsonify({'error': 'Camera not started'}), 400
    
    print("Starting video stream...")
    return Response(camera_manager.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/api/snapshot', methods=['POST'])
def take_snapshot():
    """Take a snapshot of current frame"""
    success, message, filepath = camera_manager.take_snapshot()
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'filepath': filepath
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@camera_bp.route('/api/start_recording', methods=['POST'])
def start_recording():
    """Start recording annotated video"""
    data = request.get_json() or {}
    output_path = data.get('output_path')
    
    success, message = camera_manager.start_recording(output_path)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'recording': True
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@camera_bp.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    """Stop recording video"""
    result = camera_manager.stop_recording()
    
    if len(result) == 3:  # success, message, filename
        success, message, filename = result
    else:  # backwards compatibility
        success, message = result
        filename = None
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'recording': False,
            'filename': filename
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@camera_bp.route('/api/recording_status', methods=['GET'])
def recording_status():
    """Get current recording status"""
    return jsonify({
        'recording': camera_manager.is_recording,
        'filename': camera_manager.recording_filename,
        'camera_active': camera_manager.is_camera_active()
    })

@camera_bp.route('/api/debug')
def debug():
    """Debug endpoint to check camera and model status"""
    return jsonify({
        'model_loaded': camera_manager.model is not None,
        'camera_active': camera_manager.is_camera_active(),
        'recording': camera_manager.is_recording,
        'recording_filename': camera_manager.recording_filename
    })

def get_camera_manager():
    """Get the camera manager instance"""
    return camera_manager