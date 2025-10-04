import requests
from config import Config
import logging

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Interface for external weather data APIs"""
    
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_API_URL
    
    def get_current_weather(self, lat: float, lon: float) -> dict:
        """Fetch current weather data for coordinates"""
        if not self.api_key:
            logger.warning("Weather API key not configured, using mock data")
            return self._get_mock_weather()
        
        try:
            endpoint = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return self._get_mock_weather()
    
    def get_historical_weather(self, lat: float, lon: float, date: str) -> dict:
        """Fetch historical weather data"""
        # Note: Historical weather requires paid API plan
        # For now, return mock data
        return self._get_mock_weather()
    
    def _get_mock_weather(self) -> dict:
        """Generate mock weather data"""
        import random
        return {
            'main': {
                'temp': random.uniform(30, 85),
                'temp_min': random.uniform(25, 75),
                'temp_max': random.uniform(35, 90),
                'humidity': random.uniform(40, 90)
            },
            'wind': {
                'speed': random.uniform(0, 20)
            },
            'weather': [
                {'description': random.choice(['clear', 'cloudy', 'rainy', 'snowy'])}
            ]
        }