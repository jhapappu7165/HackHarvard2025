from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class WeatherStation:
    """Weather station data model"""
    name: str
    latitude: float
    longitude: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'WeatherStation':
        return WeatherStation(
            id=data.get('id'),
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            created_at=data.get('created_at')
        )

@dataclass
class WeatherData:
    """Weather data reading model"""
    station_id: int
    reading_date: str  # ISO format date
    temp_avg: float
    temp_min: float
    temp_max: float
    heating_degree_days: int
    cooling_degree_days: int
    precipitation: float
    wind_speed: float
    humidity: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'station_id': self.station_id,
            'reading_date': self.reading_date,
            'temp_avg': self.temp_avg,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'heating_degree_days': self.heating_degree_days,
            'cooling_degree_days': self.cooling_degree_days,
            'precipitation': self.precipitation,
            'wind_speed': self.wind_speed,
            'humidity': self.humidity
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'WeatherData':
        return WeatherData(
            id=data.get('id'),
            station_id=data['station_id'],
            reading_date=data['reading_date'],
            temp_avg=data['temp_avg'],
            temp_min=data['temp_min'],
            temp_max=data['temp_max'],
            heating_degree_days=data['heating_degree_days'],
            cooling_degree_days=data['cooling_degree_days'],
            precipitation=data['precipitation'],
            wind_speed=data['wind_speed'],
            humidity=data['humidity'],
            created_at=data.get('created_at')
        )