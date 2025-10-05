"""
API Routes for Boston Energy Insights
"""

from flask import Blueprint
from .energy_routes import energy_bp
from .weather_routes import weather_bp
from .traffic_routes import traffic_bp
from .insights_routes import insights_bp
from .dashboard_routes import dashboard_bp
from .sim_routes import sim_bp

def register_all_routes(app):
    """Register all blueprints with the Flask app"""
    print("🔵 Starting route registration...")
    app.register_blueprint(energy_bp, url_prefix='/api/energy')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(traffic_bp, url_prefix='/api/traffic')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(sim_bp, url_prefix='/api/sim')
    print("✅ Registered sim_bp at /api/sim")
    print(f"✅ Total blueprints registered: {len(app.blueprints)}")