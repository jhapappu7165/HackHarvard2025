from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.energy_routes import energy_bp
from routes.insights_routes import insights_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(energy_bp, url_prefix='/api/energy')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Energy Management System API',
            'version': '1.0',
            'endpoints': {
                'generate_data': '/api/energy/generate-data [POST]',
                'get_buildings': '/api/energy/buildings [GET]',
                'get_readings': '/api/energy/buildings/<id>/readings [GET]',
                'dashboard': '/api/energy/dashboard-data [GET]',
                'generate_insights': '/api/insights/generate-insights [POST]',
                'get_insights': '/api/insights/insights [GET]',
                'building_insights': '/api/insights/insights/building/<id> [GET]'
            }
        })
    
    @app.route('/health')
    def health():
            return jsonify({'status': 'healthy', 'service': 'energy-api'}), 200
        
    return app

if __name__ == '__main__':
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)