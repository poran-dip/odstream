from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from routes.video_routes import video_bp, get_video_manager
from routes.camera_routes import camera_bp, init_socketio, get_camera_manager
from routes.config_routes import config_bp
from routes.socket_events import register_socket_events
import socket
import os
from pathlib import Path

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        # Fallback to localhost if unable to determine IP
        return "127.0.0.1"

def generate_runtime_env():
    """Generate the runtime environment TypeScript file"""
    ip_address = get_local_ip()
    port = Config.PORT
    
    # Create the runtime-env.ts content
    content = f"""// this file is generated at runtime - do not modify this
export const API_URL = "{ip_address}";
"""
    
    # Determine the path to the runtime-env.ts file
    # Assuming the structure: wod/backend/app.py and uwod/shared/runtime-env.ts
    current_dir = Path(__file__).parent
    runtime_env_path = current_dir.parent / "shared" / "runtime-env.ts"
    
    try:
        # Create the directory if it doesn't exist
        runtime_env_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the content to the file
        with open(runtime_env_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Generated runtime-env.ts with API_URL: http://{ip_address}:{port}")
        return True
    except Exception as e:
        print(f"✗ Failed to generate runtime-env.ts: {e}")
        return False

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
    
    # Auto-start camera after app initialization
    with app.app_context():
        camera_manager = get_camera_manager()
        success, message = camera_manager.start_camera()
        if success:
            print(f"✓ Camera auto-started: {message}")
        else:
            print(f"✗ Failed to auto-start camera: {message}")
    
    return app, socketio

def main():
    """Main application entry point"""
    # Generate runtime environment file before starting the server
    generate_runtime_env()
    
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