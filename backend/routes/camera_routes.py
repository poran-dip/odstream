from flask import Blueprint, jsonify, Response, request
from flask_socketio import emit
from camera_manager import CameraManager

# Create blueprint
camera_bp = Blueprint('camera', __name__)

# Initialize camera manager
camera_manager = CameraManager()

# This will be injected by the main app
socketio = None

def init_socketio(socketio_instance):
    """Initialize socketio instance for this blueprint"""
    global socketio
    socketio = socketio_instance

@camera_bp.route('/api/change_camera_source', methods=['POST'])
def change_camera_source():
    """Change camera source (replaces start_camera since camera is always running)"""
    data = request.get_json() or {}
    source = data.get('source')
    
    if not source:
        return jsonify({'error': 'Source parameter is required'}), 400
    
    success, message = camera_manager.change_camera_source(source)
    
    if success:
        # Broadcast to all connected clients
        if socketio:
            socketio.emit('camera_status', {
                'active': True,
                'source': camera_manager.camera_source,
                'message': message
            })
        
        return jsonify({
            'message': message,
            'source': camera_manager.camera_source
        })
    else:
        return jsonify({'error': message}), 500

@camera_bp.route('/api/stop_camera')
def stop_camera():
    """Stop camera endpoint (mainly for shutdown or emergencies)"""
    success, message = camera_manager.stop_camera()
    
    if success:
        # Broadcast to all connected clients
        if socketio:
            socketio.emit('camera_status', {
                'active': False,
                'source': None,
                'message': message
            })
        
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

@camera_bp.route('/api/is_camera_active')
def is_camera_active():
    """"Check if a camera is already active"""
    is_active = camera_manager.is_camera_active()

    if is_active:
        return jsonify({ 
            "message": "Camera active", 
            "data": { 
                "active": True,
                "source": camera_manager.camera_source,
                "detection_enabled": camera_manager.detection_enabled
        }})
    else:
        return jsonify({ 
            "message": "Camera inactive", 
            "data": {
                "active": False,
                "source": None,
                "detection_enabled": False
        }})

@camera_bp.route('/api/video_feed')
def video_feed():
    """Video feed endpoint - streams raw video by default, annotated when recording"""
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
        # Broadcast snapshot event to all connected clients
        if socketio:
            socketio.emit('snapshot_taken', {
                'success': True,
                'message': message,
                'filepath': filepath,
                'source': camera_manager.camera_source
            })
        
        return jsonify({
            'success': True,
            'message': message,
            'filepath': filepath,
            'source': camera_manager.camera_source
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@camera_bp.route('/api/start_recording', methods=['POST'])
def start_recording():
    """Start recording with YOLO detection enabled"""
    data = request.get_json() or {}
    output_path = data.get('output_path')
    
    success, message = camera_manager.start_recording(output_path)
    
    if success:
        # Broadcast to all connected clients
        if socketio:
            socketio.emit('recording_status', {
                'recording': True,
                'detection_enabled': True,
                'message': message,
                'source': camera_manager.camera_source
            })
        
        return jsonify({
            'success': True,
            'message': message,
            'recording': True,
            'detection_enabled': True,
            'source': camera_manager.camera_source
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@camera_bp.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    """Stop recording and disable YOLO detection"""
    result = camera_manager.stop_recording()
    
    if len(result) == 3:  # success, message, filename
        success, message, filename = result
    else:  # backwards compatibility
        success, message = result
        filename = None
    
    if success:
        # Broadcast to all connected clients
        if socketio:
            socketio.emit('recording_status', {
                'recording': False,
                'detection_enabled': False,
                'message': message,
                'filename': filename,
                'source': camera_manager.camera_source
            })
        
        return jsonify({
            'success': True,
            'message': message,
            'recording': False,
            'detection_enabled': False,
            'filename': filename,
            'source': camera_manager.camera_source
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
        'detection_enabled': camera_manager.detection_enabled,
        'filename': camera_manager.recording_filename,
        'camera_active': camera_manager.is_camera_active(),
        'source': camera_manager.camera_source
    })

@camera_bp.route('/api/camera_status', methods=['GET'])
def camera_status():
    """Get current camera status"""
    return jsonify({
        'active': camera_manager.is_camera_active(),
        'source': camera_manager.camera_source,
        'detection_enabled': camera_manager.detection_enabled,
        'recording': camera_manager.is_recording,
        'model_loaded': camera_manager.model is not None
    })

@camera_bp.route('/api/debug')
def debug():
    """Debug endpoint to check camera and model status"""
    return jsonify({
        'model_loaded': camera_manager.model is not None,
        'camera_active': camera_manager.is_camera_active(),
        'detection_enabled': camera_manager.detection_enabled,
        'recording': camera_manager.is_recording,
        'recording_filename': camera_manager.recording_filename,
        'camera_source': camera_manager.camera_source,
        'remote_stream_active': camera_manager.remote_stream_active if hasattr(camera_manager, 'remote_stream_active') else None
    })

# Socket event handlers
def handle_connect(socketio_instance):
    """Handle client connection"""
    print('Client connected')
    # Send current state to newly connected client
    socketio_instance.emit('camera_status', {
        'active': camera_manager.is_camera_active(),
        'source': camera_manager.camera_source,
        'detection_enabled': camera_manager.detection_enabled
    })
    socketio_instance.emit('recording_status', {
        'recording': camera_manager.is_recording,
        'detection_enabled': camera_manager.detection_enabled,
        'filename': camera_manager.recording_filename
    })

def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def get_camera_manager():
    """Get the camera manager instance"""
    return camera_manager