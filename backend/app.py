from flask import Flask
from flask_cors import CORS
from config import Config
from routes.video_routes import video_bp, get_video_manager
from routes.camera_routes import camera_bp
from routes.config_routes import config_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(video_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(config_bp)
    
    return app

def main():
    """Main application entry point"""
    app = create_app()
    
    print("Starting Flask server...")
    
    # Get video manager to check directory
    video_manager = get_video_manager()
    print(f"Video directory: {video_manager.base_path}")
    print(f"Server will be available at: http://localhost:{Config.PORT}")

    # Check if default directory exists
    if not video_manager.base_path.exists():
        print(f"Warning: Default video directory '{video_manager.base_path}' does not exist!")
        print("You can change the path using the /api/config/path endpoint")
    
    app.run(
        debug=Config.DEBUG,
        port=Config.PORT,
        threaded=Config.THREADED
    )

if __name__ == '__main__':
    main()