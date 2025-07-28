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

@camera_bp.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start camera with optional source parameter"""
    data = request.get_json() or {}
    source = data.get('source')
    
    success, message = camera_manager.start_camera(source)
    
    # If source is provided, validate it
    if source:
        source_type = source.get('type')
        if not source_type:
            return jsonify({'error': 'Source type is required'}), 400
        
        if source_type == 'local':
            if 'index' not in source:
                return jsonify({'error': 'Camera index is required for local sources'}), 400
            if not isinstance(source['index'], int) or source['index'] < 0:
                return jsonify({'error': 'Camera index must be a non-negative integer'}), 400
        elif source_type == 'remote':
            if 'url' not in source:
                return jsonify({'error': 'URL is required for remote sources'}), 400
            if not source['url'].startswith(('http://', 'https://')):
                return jsonify({'error': 'URL must be a valid HTTP/HTTPS URL'}), 400
        else:
            return jsonify({'error': 'Source type must be either "local" or "remote"'}), 400
    
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

@camera_bp.route('/api/change_camera_source', methods=['POST'])
def change_camera_source():
    """Change camera source (replaces start_camera since camera is always running)"""
    data = request.get_json() or {}
    source = data.get('source')
    
    if not source:
        return jsonify({'error': 'Source parameter is required'}), 400
    
    # Validate source structure based on type
    source_type = source.get('type')
    if not source_type:
        return jsonify({'error': 'Source type is required'}), 400
    
    if source_type == 'local':
        if 'index' not in source:
            return jsonify({'error': 'Camera index is required for local sources'}), 400
        if not isinstance(source['index'], int) or source['index'] < 0:
            return jsonify({'error': 'Camera index must be a non-negative integer'}), 400
    elif source_type == 'remote':
        if 'url' not in source:
            return jsonify({'error': 'URL is required for remote sources'}), 400
        if not source['url'].startswith(('http://', 'https://')):
            return jsonify({'error': 'URL must be a valid HTTP/HTTPS URL'}), 400
    else:
        return jsonify({'error': 'Source type must be either "local" or "remote"'}), 400
    
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
            'success': True,
            'message': message,
            'source': camera_manager.camera_source
        })
    else:
        return jsonify({'success': False, 'error': message}), 500

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

@camera_bp.route('/api/video_settings', methods=['GET'])
def get_video_settings():
    """Get current video settings (brightness, contrast, saturation)"""
    try:
        current_settings = {
            'brightness': camera_manager.brightness,
            'contrast': camera_manager.contrast,
            'saturation': camera_manager.saturation
        }
        
        return jsonify({
            'success': True,
            'message': 'Video settings retrieved successfully',
            'data': current_settings
        })
        
    except Exception as e:
        error_message = f"Failed to get video settings: {str(e)}"
        return jsonify({
            'success': False,
            'error': error_message
        }), 400

@camera_bp.route('/api/update_video_settings', methods=['POST'])
def update_video_settings():
    """Update video settings (brightness, contrast, saturation)"""
    data = request.get_json() or {}
    
    brightness = data.get('brightness')
    contrast = data.get('contrast')
    saturation = data.get('saturation')
    
    try:
        # Update settings in camera manager
        camera_manager.update_video_settings(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation
        )
        
        # Get current settings to return
        current_settings = {
            'brightness': camera_manager.brightness,
            'contrast': camera_manager.contrast,
            'saturation': camera_manager.saturation
        }
        
        # Broadcast to all connected clients
        if socketio:
            socketio.emit('video_settings_updated', {
                'data': current_settings,
                'message': 'Video settings updated successfully'
            })
        
        return jsonify({
            'success': True,
            'message': 'Video settings updated successfully',
            'settings': current_settings
        })
        
    except Exception as e:
        error_message = f"Failed to update video settings: {str(e)}"
        return jsonify({
            'success': False,
            'error': error_message
        }), 400

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