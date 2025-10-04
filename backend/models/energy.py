from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class EnergyBuilding:
    """Energy building data model"""
    name: str
    address: str
    city: str
    latitude: float
    longitude: float
    square_feet: int
    category: str
    year_built: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'square_feet': self.square_feet,
            'category': self.category,
            'year_built': self.year_built
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'EnergyBuilding':
        """Create instance from dictionary"""
        return EnergyBuilding(
            id=data.get('id'),
            name=data['name'],
            address=data['address'],
            city=data['city'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            square_feet=data['square_feet'],
            category=data['category'],
            year_built=data['year_built'],
            created_at=data.get('created_at')
        )

@dataclass
class EnergyReading:
    """Energy reading data model"""
    building_id: int
    reading_date: str  # ISO format date
    fuel_type: str
    usage: float
    cost: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'building_id': self.building_id,
            'reading_date': self.reading_date,
            'fuel_type': self.fuel_type,
            'usage': self.usage,
            'cost': self.cost
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'EnergyReading':
        """Create instance from dictionary"""
        return EnergyReading(
            id=data.get('id'),
            building_id=data['building_id'],
            reading_date=data['reading_date'],
            fuel_type=data['fuel_type'],
            usage=data['usage'],
            cost=data['cost'],
            created_at=data.get('created_at')
        )