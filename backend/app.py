from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes import register_all_routes
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register all blueprints
    register_all_routes(app)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Boston Energy Insights API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'energy': '/api/energy/*',
                'weather': '/api/weather/*',
                'traffic': '/api/traffic/*',
                'insights': '/api/insights/*',
                'dashboard': '/api/dashboard/*'
            },
            'documentation': 'See README.md for API documentation'
        }), 200
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            from utils.supabase_client import SupabaseClient
            db = SupabaseClient()
            # Test database connection
            db.get_client().table('energy_buildings').select('id').limit(1).execute()
            
            return jsonify({
                'status': 'healthy',
                'service': 'Energy Insights API',
                'database': 'connected',
                'timestamp': Config.DATA_END_DATE.isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'Energy Insights API',
                'database': 'disconnected',
                'error': str(e)
            }), 503
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    logger.info("Flask application created successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5001)