from flask_socketio import emit
from routes.camera_routes import get_camera_manager

def register_socket_events(socketio):
    """Register all socket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print('Client connected')
        
        camera_manager = get_camera_manager()
        
        # Send current camera state to newly connected client
        emit('camera_status', {
            'active': camera_manager.is_camera_active(),
            'source': camera_manager.camera_source
        })
        
        # Send current recording state
        emit('recording_status', {
            'recording': camera_manager.is_recording,
            'filename': camera_manager.recording_filename
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')

    @socketio.on('request_status')
    def handle_status_request():
        """Handle explicit status requests from clients"""
        camera_manager = get_camera_manager()
        
        emit('camera_status', {
            'active': camera_manager.is_camera_active(),
            'source': camera_manager.camera_source
        })
        
        emit('recording_status', {
            'recording': camera_manager.is_recording,
            'filename': camera_manager.recording_filename
        })

    @socketio.on('ping')
    def handle_ping():
        """Handle ping requests for connection testing"""
        emit('pong', {'timestamp': __import__('time').time()})