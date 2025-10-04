import random
from datetime import datetime, timedelta
from typing import List, Dict
from config import Config
from models.traffic import TrafficIntersection, TrafficData
from utils.supabase_client import SupabaseClient
from utils.helpers import generate_random_coords, generate_date_range
import logging

logger = logging.getLogger(__name__)

class TrafficDataGenerator:
    """Generate synthetic traffic data"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
        self.config = Config
    
    def generate_intersections(self) -> List[Dict]:
        """Generate traffic intersections"""
        logger.info(f"Generating {self.config.NUM_TRAFFIC_INTERSECTIONS} intersections...")
        
        street_names = [
            "Massachusetts Ave", "Boylston St", "Commonwealth Ave", "Beacon St",
            "Tremont St", "Washington St", "Congress St", "Summer St",
            "Atlantic Ave", "Huntington Ave"
        ]
        
        intersections = []
        
        for i in range(self.config.NUM_TRAFFIC_INTERSECTIONS):
            lat, lng = generate_random_coords(self.config.BOSTON_BOUNDS)
            
            # Generate intersection name from two streets
            street1 = random.choice(street_names)
            street2 = random.choice([s for s in street_names if s != street1])
            
            intersection = TrafficIntersection(
                name=f"{street1} & {street2}",
                latitude=lat,
                longitude=lng,
                streets=[street1, street2]
            )
            
            response = self.db.table('traffic_intersections').insert(intersection.to_dict()).execute()
            intersection_data = response.data[0]
            intersections.append(intersection_data)
            
            logger.info(f"Created intersection: {intersection.name} (ID: {intersection_data['id']})")
        
        return intersections
    
    def generate_traffic_data_for_all_intersections(self) -> List[Dict]:
        """Generate traffic data for all intersections"""
        logger.info("Generating traffic data for all intersections...")
        
        intersections_response = self.db.table('traffic_intersections').select('*').execute()
        intersections = intersections_response.data
        
        all_traffic_data = []
        
        for intersection in intersections:
            traffic_data = self._generate_traffic_data_for_intersection(intersection)
            all_traffic_data.extend(traffic_data)
        
        logger.info(f"Generated {len(all_traffic_data)} total traffic readings")
        return all_traffic_data
    
    def _generate_traffic_data_for_intersection(self, intersection: Dict) -> List[Dict]:
        """Generate traffic data for a single intersection"""
        traffic_data = []
        
        # Generate hourly readings for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = generate_date_range(start_date, end_date, freq='H')
        
        for timestamp in dates:
            hour = timestamp.hour
            
            # Determine time period and traffic characteristics
            time_period, base_vehicles, base_speed = self._get_traffic_characteristics(hour)
            
            # Add randomness
            vehicle_count = int(base_vehicles + random.uniform(-base_vehicles * 0.3, base_vehicles * 0.3))
            vehicle_count = max(0, vehicle_count)
            
            avg_speed = base_speed + random.uniform(-5, 5)
            avg_speed = max(5, min(50, avg_speed))  # Clamp between 5-50 mph
            
            # Determine congestion level
            congestion_level = self._determine_congestion_level(vehicle_count, avg_speed)
            
            traffic_reading = TrafficData(
                intersection_id=intersection['id'],
                reading_timestamp=timestamp.isoformat(),
                time_period=time_period,
                total_vehicle_count=vehicle_count,
                average_speed=round(avg_speed, 2),
                congestion_level=congestion_level
            )
            
            response = self.db.table('traffic_data').insert(traffic_reading.to_dict()).execute()
            traffic_data.append(response.data[0])
        
        logger.info(f"Generated {len(traffic_data)} readings for intersection {intersection['name']}")
        return traffic_data
    
    def _get_traffic_characteristics(self, hour: int) -> tuple:
        """Get traffic characteristics based on time of day"""
        if 7 <= hour < 9:  # Morning peak
            return 'morning_peak', 200, 20
        elif 9 <= hour < 15:  # Midday
            return 'midday', 100, 30
        elif 15 <= hour < 18:  # Afternoon peak
            return 'afternoon_peak', 250, 18
        elif 18 <= hour < 22:  # Evening
            return 'evening', 80, 32
        else:  # Night
            return 'night', 30, 40
    
    def _determine_congestion_level(self, vehicle_count: int, avg_speed: float) -> str:
        """Determine congestion level based on volume and speed"""
        if vehicle_count > 200 or avg_speed < 15:
            return 'severe'
        elif vehicle_count > 150 or avg_speed < 22:
            return 'high'
        elif vehicle_count > 80 or avg_speed < 28:
            return 'moderate'
        else:
            return 'low'