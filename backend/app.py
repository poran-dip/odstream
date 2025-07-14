from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from routes.video_routes import video_bp, get_video_manager
from routes.camera_routes import camera_bp, init_socketio
from routes.config_routes import config_bp
from routes.socket_events import register_socket_events

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize socketio in camera routes
    init_socketio(socketio)
    
    # Register socket events
    register_socket_events(socketio)
    
    # Register blueprints
    app.register_blueprint(video_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(config_bp)
    
    return app, socketio

def main():
    """Main application entry point"""
    app, socketio = create_app()
    
    print("Starting Flask server with SocketIO...")
    
    # Get video manager to check directory
    video_manager = get_video_manager()
    print(f"Video directory: {video_manager.base_path}")
    print(f"Server will be available at: http://localhost:{Config.PORT}")

    # Check if default directory exists
    if not video_manager.base_path.exists():
        print(f"Warning: Default video directory '{video_manager.base_path}' does not exist!")
        print("You can change the path using the /api/config/path endpoint")
    
    # Use socketio.run instead of app.run
    socketio.run(
        app,
        host='0.0.0.0',
        debug=Config.DEBUG,
        port=Config.PORT
    )

if __name__ == '__main__':
    main()