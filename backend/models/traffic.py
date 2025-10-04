from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class TrafficIntersection:
    """Traffic intersection data model"""
    name: str
    latitude: float
    longitude: float
    streets: List[str]
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'streets': self.streets
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TrafficIntersection':
        return TrafficIntersection(
            id=data.get('id'),
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            streets=data['streets'],
            created_at=data.get('created_at')
        )

@dataclass
class TrafficData:
    """Traffic data reading model"""
    intersection_id: int
    reading_timestamp: str  # ISO format datetime
    time_period: str
    total_vehicle_count: int
    average_speed: float
    congestion_level: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'intersection_id': self.intersection_id,
            'reading_timestamp': self.reading_timestamp,
            'time_period': self.time_period,
            'total_vehicle_count': self.total_vehicle_count,
            'average_speed': self.average_speed,
            'congestion_level': self.congestion_level
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TrafficData':
        return TrafficData(
            id=data.get('id'),
            intersection_id=data['intersection_id'],
            reading_timestamp=data['reading_timestamp'],
            time_period=data['time_period'],
            total_vehicle_count=data['total_vehicle_count'],
            average_speed=data['average_speed'],
            congestion_level=data['congestion_level'],
            created_at=data.get('created_at')
        )