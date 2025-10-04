import random
import numpy as np
from datetime import datetime, timedelta
from typing import List
from models import Building, EnergyReading
from config import Config

class EnergyDataGenerator:
    
    BUILDING_NAMES = [
        "Sampleville High School", "Evergreen School", "Primary School",
        "Sampleville Middle School", "East School",
        "Sampleville Library", "Town Center Library",
        "Police Station", "Town Center", "Salt Barn",
        "Sunnyside Rec", "Old Fire Station", "Kennel",
        "Public Works", "Administration Building"
    ]
    
    def __init__(self):
        self.buildings = []
        self.energy_readings = []
    
    def generate_buildings(self) -> List[Building]:
        """Generate synthetic building data"""
        buildings = []
        
        for i, name in enumerate(self.BUILDING_NAMES[:Config.NUM_BUILDINGS]):
            # Assign category
            if "School" in name:
                category = "School"
                sq_ft = random.randint(50000, 150000)
            elif "Library" in name:
                category = "Library"
                sq_ft = random.randint(10000, 30000)
            elif "Police" in name or "Fire" in name:
                category = "Public Safety"
                sq_ft = random.randint(15000, 40000)
            elif "Works" in name or "Salt" in name or "Kennel" in name:
                category = "Public Works"
                sq_ft = random.randint(5000, 25000)
            else:
                category = "Administration"
                sq_ft = random.randint(8000, 35000)
            
            year_built = random.randint(1950, 2015)
            
            buildings.append(Building(name, category, sq_ft, year_built))
        
        self.buildings = buildings
        return buildings
    
    def generate_energy_readings(self, building_id: int, building_sq_ft: int, 
                                building_year: int) -> List[EnergyReading]:
        """Generate synthetic energy readings for a building"""
        readings = []
        
        # Base efficiency based on building age
        age_factor = max(0.7, 1 - (datetime.now().year - building_year) / 100)
        
        # Size factor (larger buildings use more energy)
        size_factor = building_sq_ft / 50000
        
        current_year = datetime.now().year
        start_year = current_year - 2
        
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        for year in range(start_year, current_year + 1):
            for month_idx, month in enumerate(months):
                # Skip future months
                if year == current_year and month_idx > datetime.now().month:
                    break
                
                # Seasonal variation
                seasonal_factor = 1 + 0.4 * np.sin((month_idx - 3) * np.pi / 6)
                
                # Electricity (kWh)
                if random.random() > 0.1:  # 90% of buildings have electricity
                    base_electric = 20000 * size_factor * seasonal_factor
                    electric_usage = base_electric * age_factor * random.uniform(0.85, 1.15)
                    electric_cost = electric_usage * random.uniform(0.12, 0.18)  # $/kWh
                    
                    readings.append(EnergyReading(
                        building_id, 'electricity', round(electric_usage, 2),
                        round(electric_cost, 2), month, year
                    ))
                
                # Natural Gas (therms) - heating season
                if month_idx in [0, 1, 2, 3, 10, 11] and random.random() > 0.3:
                    base_gas = 5000 * size_factor * seasonal_factor
                    gas_usage = base_gas * age_factor * random.uniform(0.8, 1.2)
                    gas_cost = gas_usage * random.uniform(0.9, 1.3)  # $/therm
                    
                    readings.append(EnergyReading(
                        building_id, 'natural_gas', round(gas_usage, 2),
                        round(gas_cost, 2), month, year
                    ))
                
                # Oil (gallons) - for older buildings in winter
                if building_year < 1980 and month_idx in [0, 1, 2, 11] and random.random() > 0.6:
                    base_oil = 800 * size_factor
                    oil_usage = base_oil * random.uniform(0.7, 1.3)
                    oil_cost = oil_usage * random.uniform(3.5, 4.5)  # $/gallon
                    
                    readings.append(EnergyReading(
                        building_id, 'oil', round(oil_usage, 2),
                        round(oil_cost, 2), month, year
                    ))
        
        return readings
    
    def create_anomalies(self, readings: List[EnergyReading]) -> List[EnergyReading]:
        """Inject some anomalies for the AI to detect"""
        if len(readings) > 12:
            # Create a spike in one random month
            anomaly_idx = random.randint(6, len(readings) - 1)
            readings[anomaly_idx].usage *= random.uniform(1.8, 2.5)
            readings[anomaly_idx].cost *= random.uniform(1.8, 2.5)
        
        return readings