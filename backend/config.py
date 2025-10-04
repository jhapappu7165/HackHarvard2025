import os
from datetime import datetime, timedelta

class Config:
    """Unified configuration for all services"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv(
        'SUPABASE_URL', 
        'https://xewxswcnymeeyrykvrnz.supabase.co'
    )
    SUPABASE_KEY = os.getenv(
        'SUPABASE_KEY',
        'No'
    )
    
    # Data Generation Settings
    NUM_BUILDINGS = 15
    NUM_WEATHER_STATIONS = 3
    NUM_TRAFFIC_INTERSECTIONS = 10
    DATA_START_DATE = datetime(2023, 1, 1)
    DATA_END_DATE = datetime.now()
    NUM_MONTHS = 24
    
    # Boston Geographic Bounds
    BOSTON_BOUNDS = {
        'lat_min': 42.2279,
        'lat_max': 42.3969,
        'lng_min': -71.1912,
        'lng_max': -70.9231
    }
    
    # Energy Configuration
    FUEL_TYPES = ['electricity', 'natural_gas', 'oil', 'propane']
    BUILDING_CATEGORIES = [
        'School', 
        'Library', 
        'Administration', 
        'Public Works', 
        'Public Safety',
        'Recreation Center',
        'Community Center'
    ]
    
    # Energy Cost per Unit ($/kWh or $/therm)
    ENERGY_COSTS = {
        'electricity': 0.15,  # $/kWh
        'natural_gas': 0.95,  # $/therm
        'oil': 3.50,          # $/gallon
        'propane': 2.80       # $/gallon
    }
    
    # Weather Configuration
    WEATHER_BASE_TEMP = 65  # Base temperature for degree days (°F)
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')  # Optional: real weather data
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5'
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Traffic Configuration
    TRAFFIC_TIME_PERIODS = [
        'morning_peak',      # 7-9 AM
        'midday',            # 9 AM - 3 PM
        'afternoon_peak',    # 3-6 PM
        'evening',           # 6-10 PM
        'night'              # 10 PM - 7 AM
    ]
    
    TRAFFIC_CONGESTION_LEVELS = ['low', 'moderate', 'high', 'severe']
    
    # Insights Configuration
    INSIGHT_PRIORITIES = ['low', 'medium', 'high', 'critical']
    INSIGHT_CATEGORIES = [
        'Efficiency',
        'Cost Savings',
        'Sustainability',
        'Maintenance',
        'Weather Impact',
        'Traffic Impact',
        'Cross-Domain'
    ]
    
    MIN_CONFIDENCE_THRESHOLD = 60  # Minimum confidence to show insight (0-100)
    MIN_SAVINGS_THRESHOLD = 5000   # Minimum $ to flag as savings opportunity
    ANOMALY_ZSCORE_THRESHOLD = 2.5
    WEATHER_CORRELATION_THRESHOLD = 0.7  # R² for weather impact
    TRAFFIC_CORRELATION_THRESHOLD = 0.6  # R² for traffic impact
    
    # API Settings
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 25
    REQUEST_TIMEOUT = 30
    
    # CORS Settings
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://localhost:5174'
    ]