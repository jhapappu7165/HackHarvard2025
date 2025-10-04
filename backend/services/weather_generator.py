import random
from datetime import datetime, timedelta
from typing import List, Dict
from config import Config
from models.weather import WeatherStation, WeatherData
from utils.supabase_client import SupabaseClient
from utils.helpers import generate_random_coords, generate_date_range
import logging

logger = logging.getLogger(__name__)

class WeatherDataGenerator:
    """Generate synthetic weather data"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
        self.config = Config
    
    def generate_stations(self) -> List[Dict]:
        """Generate weather stations"""
        logger.info(f"Generating {self.config.NUM_WEATHER_STATIONS} weather stations...")
        
        station_names = [
            "Logan Airport Weather Station",
            "Boston Common Station",
            "Charles River Station"
        ]
        
        stations = []
        
        for i in range(self.config.NUM_WEATHER_STATIONS):
            lat, lng = generate_random_coords(self.config.BOSTON_BOUNDS)
            
            station = WeatherStation(
                name=station_names[i] if i < len(station_names) else f"Weather Station #{i+1}",
                latitude=lat,
                longitude=lng
            )
            
            response = self.db.table('weather_stations').insert(station.to_dict()).execute()
            station_data = response.data[0]
            stations.append(station_data)
            
            logger.info(f"Created weather station: {station.name} (ID: {station_data['id']})")
        
        return stations
    
    def generate_weather_data_for_all_stations(self) -> List[Dict]:
        """Generate weather data for all stations"""
        logger.info("Generating weather data for all stations...")
        
        stations_response = self.db.table('weather_stations').select('*').execute()
        stations = stations_response.data
        
        all_weather_data = []
        
        for station in stations:
            weather_data = self._generate_weather_data_for_station(station)
            all_weather_data.extend(weather_data)
        
        logger.info(f"Generated {len(all_weather_data)} total weather readings")
        return all_weather_data
    
    def _generate_weather_data_for_station(self, station: Dict) -> List[Dict]:
        """Generate weather data for a single station"""
        weather_data = []
        
        # Generate daily readings
        dates = generate_date_range(
            self.config.DATA_START_DATE,
            self.config.DATA_END_DATE,
            freq='D'
        )
        
        for date in dates:
            # Generate realistic temperature based on season
            month = date.month
            
            # Boston seasonal temperatures (°F)
            base_temps = {
                1: 30, 2: 32, 3: 40, 4: 50, 5: 60, 6: 70,
                7: 75, 8: 74, 9: 67, 10: 57, 11: 47, 12: 35
            }
            
            base_temp = base_temps[month]
            temp_avg = base_temp + random.uniform(-10, 10)
            temp_min = temp_avg - random.uniform(5, 15)
            temp_max = temp_avg + random.uniform(5, 15)
            
            # Calculate degree days
            hdd, cdd = self._calculate_degree_days(temp_avg)
            
            # Generate other weather variables
            precipitation = max(0, random.gauss(0.1, 0.15))  # inches
            wind_speed = max(0, random.gauss(10, 5))  # mph
            humidity = random.uniform(40, 90)  # percent
            
            weather_reading = WeatherData(
                station_id=station['id'],
                reading_date=date.strftime('%Y-%m-%d'),
                temp_avg=round(temp_avg, 1),
                temp_min=round(temp_min, 1),
                temp_max=round(temp_max, 1),
                heating_degree_days=hdd,
                cooling_degree_days=cdd,
                precipitation=round(precipitation, 2),
                wind_speed=round(wind_speed, 1),
                humidity=round(humidity, 1)
            )
            
            response = self.db.table('weather_data').insert(weather_reading.to_dict()).execute()
            weather_data.append(response.data[0])
        
        logger.info(f"Generated {len(weather_data)} readings for station {station['name']}")
        return weather_data
    
    def _calculate_degree_days(self, temp_avg: float) -> tuple:
        """Calculate heating and cooling degree days"""
        base_temp = self.config.WEATHER_BASE_TEMP
        
        if temp_avg < base_temp:
            hdd = int(base_temp - temp_avg)
            cdd = 0
        else:
            hdd = 0
            cdd = int(temp_avg - base_temp)
        
        return hdd, cdd