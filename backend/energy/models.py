from datetime import datetime
from typing import Optional, List

class Building:
    def __init__(self, name: str, category: str, square_feet: int, year_built: int):
        self.name = name
        self.category = category
        self.square_feet = square_feet
        self.year_built = year_built
    
    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'square_feet': self.square_feet,
            'year_built': self.year_built,
            'created_at': datetime.utcnow().isoformat()
        }

class EnergyReading:
    def __init__(self, building_id: int, fuel_type: str, usage: float, 
                 cost: float, month: str, year: int):
        self.building_id = building_id
        self.fuel_type = fuel_type
        self.usage = usage  # kWh or gallons or therms
        self.cost = cost
        self.month = month
        self.year = year
    
    def to_dict(self):
        return {
            'building_id': self.building_id,
            'fuel_type': self.fuel_type,
            'usage': self.usage,
            'cost': self.cost,
            'month': self.month,
            'year': self.year,
            'created_at': datetime.utcnow().isoformat()
        }

class Insight:
    def __init__(self, building_id: Optional[int], insight_type: str, 
                 title: str, description: str, priority: str, 
                 potential_savings: Optional[float] = None):
        self.building_id = building_id
        self.insight_type = insight_type
        self.title = title
        self.description = description
        self.priority = priority
        self.potential_savings = potential_savings
    
    def to_dict(self):
        return {
            'building_id': self.building_id,
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'potential_savings': self.potential_savings,
            'generated_at': datetime.utcnow().isoformat()
        }