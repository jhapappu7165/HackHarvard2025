import random
from datetime import datetime, timedelta
from typing import List, Dict
from config import Config
from models.energy import EnergyBuilding, EnergyReading
from utils.supabase_client import SupabaseClient
from utils.helpers import generate_random_coords, generate_date_range
import logging

logger = logging.getLogger(__name__)

class EnergyDataGenerator:
    """Generate synthetic energy data for buildings"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
        self.config = Config
    
    def generate_buildings(self) -> List[Dict]:
        """Generate energy buildings"""
        logger.info(f"Generating {self.config.NUM_BUILDINGS} buildings...")
        
        building_names = [
            "City Hall", "Central Library", "North High School", "South Elementary",
            "Fire Station #1", "Police Headquarters", "Public Works Facility",
            "Community Center", "Recreation Center", "Municipal Court",
            "Senior Center", "Youth Center", "Health Department", 
            "Parks Department", "Water Treatment Plant"
        ]
        
        buildings = []
        
        for i in range(self.config.NUM_BUILDINGS):
            lat, lng = generate_random_coords(self.config.BOSTON_BOUNDS)
            
            building = EnergyBuilding(
                name=building_names[i % len(building_names)] + f" #{i+1}" if i >= len(building_names) else building_names[i],
                address=f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple', 'Washington'])} St",
                city="Boston",
                latitude=lat,
                longitude=lng,
                square_feet=random.randint(5000, 100000),
                category=random.choice(self.config.BUILDING_CATEGORIES),
                year_built=random.randint(1950, 2020)
            )
            
            # Insert into database
            response = self.db.table('energy_buildings').insert(building.to_dict()).execute()
            building_data = response.data[0]
            buildings.append(building_data)
            
            logger.info(f"Created building: {building.name} (ID: {building_data['id']})")
        
        return buildings
    
    def generate_readings_for_all_buildings(self) -> List[Dict]:
        """Generate energy readings for all buildings"""
        logger.info("Generating energy readings for all buildings...")
        
        # Get all buildings
        buildings_response = self.db.table('energy_buildings').select('*').execute()
        buildings = buildings_response.data
        
        all_readings = []
        
        for building in buildings:
            readings = self._generate_readings_for_building(building)
            all_readings.extend(readings)
        
        logger.info(f"Generated {len(all_readings)} total energy readings")
        return all_readings
    
    def _generate_readings_for_building(self, building: Dict) -> List[Dict]:
        """Generate energy readings for a single building"""
        readings = []
        
        # Generate monthly readings for the past 24 months
        dates = generate_date_range(
            self.config.DATA_START_DATE,
            self.config.DATA_END_DATE,
            freq='M'
        )
        
        # Base consumption based on building size
        base_consumption = building['square_feet'] * 0.5  # kWh per sq ft per month
        
        for date in dates[:self.config.NUM_MONTHS]:
            # Add seasonal variation
            month = date.month
            seasonal_factor = 1.0
            
            # Higher usage in summer (cooling) and winter (heating)
            if month in [12, 1, 2]:  # Winter
                seasonal_factor = 1.3
            elif month in [6, 7, 8]:  # Summer
                seasonal_factor = 1.2
            
            # Generate readings for each fuel type
            for fuel_type in self.config.FUEL_TYPES:
                # Not all buildings use all fuel types
                if random.random() < 0.7:  # 70% chance to use this fuel type
                    
                    fuel_factor = {
                        'electricity': 1.0,
                        'natural_gas': 0.6,
                        'oil': 0.3,
                        'propane': 0.2
                    }.get(fuel_type, 0.5)
                    
                    usage = base_consumption * fuel_factor * seasonal_factor
                    usage += random.uniform(-usage * 0.1, usage * 0.1)  # Add noise
                    usage = max(0, usage)  # Ensure non-negative
                    
                    # Calculate cost
                    cost = usage * self.config.ENERGY_COSTS[fuel_type]
                    
                    reading = EnergyReading(
                        building_id=building['id'],
                        reading_date=date.strftime('%Y-%m-%d'),
                        fuel_type=fuel_type,
                        usage=round(usage, 2),
                        cost=round(cost, 2)
                    )
                    
                    # Insert into database
                    response = self.db.table('energy_readings').insert(reading.to_dict()).execute()
                    readings.append(response.data[0])
        
        logger.info(f"Generated {len(readings)} readings for building {building['name']}")
        return readings