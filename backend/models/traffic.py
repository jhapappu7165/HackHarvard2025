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
    """Traffic data reading model with directional counts"""
    intersection_id: int
    reading_timestamp: str  # ISO format datetime
    time_period: str
    
    # Directional vehicle counts
    northbound_left: int
    northbound_thru: int
    northbound_right: int
    southbound_left: int
    southbound_thru: int
    southbound_right: int
    
    # Summary fields (calculated from directional counts)
    total_vehicle_count: int
    average_speed: float
    congestion_level: str
    
    # Optional fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'intersection_id': self.intersection_id,
            'reading_timestamp': self.reading_timestamp,
            'time_period': self.time_period,
            'northbound_left': self.northbound_left,
            'northbound_thru': self.northbound_thru,
            'northbound_right': self.northbound_right,
            'southbound_left': self.southbound_left,
            'southbound_thru': self.southbound_thru,
            'southbound_right': self.southbound_right,
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
            northbound_left=data['northbound_left'],
            northbound_thru=data['northbound_thru'],
            northbound_right=data['northbound_right'],
            southbound_left=data['southbound_left'],
            southbound_thru=data['southbound_thru'],
            southbound_right=data['southbound_right'],
            total_vehicle_count=data['total_vehicle_count'],
            average_speed=data['average_speed'],
            congestion_level=data['congestion_level'],
            created_at=data.get('created_at')
        )