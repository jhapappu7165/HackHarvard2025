import pandas as pd
import numpy as np
from typing import Dict, List
from scipy import stats
from utils.supabase_client import SupabaseClient
from utils.helpers import calculate_haversine_distance
import logging

logger = logging.getLogger(__name__)

class CorrelationAnalyzer:
    """Analyze correlations between energy, weather, and traffic"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
    
    def analyze_traffic_energy_correlation(self, building_id: int) -> Dict:
        """Find correlation between nearby traffic and energy usage"""
        try:
            logger.info(f"Analyzing traffic-energy correlation for building {building_id}")
            
            # Get building location
            building_response = self.db.table('energy_buildings')\
                .select('*')\
                .eq('id', building_id)\
                .single()\
                .execute()
            
            if not building_response.data:
                return {'error': 'Building not found', 'correlation': 0}
            
            building = building_response.data
            
            # Find nearby intersections (within 0.5 mile)
            intersections_response = self.db.table('traffic_intersections')\
                .select('*')\
                .execute()
            
            nearby_intersections = []
            for intersection in intersections_response.data:
                distance = calculate_haversine_distance(
                    building['latitude'], building['longitude'],
                    intersection['latitude'], intersection['longitude']
                )
                if distance < 0.5:  # Within 0.5 miles
                    nearby_intersections.append(intersection['id'])
            
            if not nearby_intersections:
                logger.warning(f"No nearby traffic intersections found for building {building_id}")
                return {
                    'correlation': 0,
                    'insight': 'No nearby traffic data',
                    'nearby_intersections': 0
                }
            
            # Get energy data
            energy_response = self.db.table('energy_readings')\
                .select('reading_date, usage')\
                .eq('building_id', building_id)\
                .execute()
            
            if not energy_response.data:
                return {'error': 'No energy data', 'correlation': 0}
            
            # Get traffic data (aggregate by date)
            traffic_response = self.db.table('traffic_data')\
                .select('reading_timestamp, total_vehicle_count')\
                .in_('intersection_id', nearby_intersections)\
                .execute()
            
            if not traffic_response.data:
                return {
                    'correlation': 0,
                    'insight': 'No traffic data available',
                    'nearby_intersections': len(nearby_intersections)
                }
            
            # Process traffic data
            traffic_df = pd.DataFrame(traffic_response.data)
            traffic_df['date'] = pd.to_datetime(traffic_df['reading_timestamp']).dt.date
            daily_traffic = traffic_df.groupby('date')['total_vehicle_count'].sum().reset_index()
            
            # Process energy data
            energy_df = pd.DataFrame(energy_response.data)
            energy_df['date'] = pd.to_datetime(energy_df['reading_date']).dt.date
            daily_energy = energy_df.groupby('date')['usage'].sum().reset_index()
            
            # Merge datasets
            merged = daily_energy.merge(daily_traffic, on='date', how='inner')
            
            if len(merged) < 10:
                return {
                    'correlation': 0,
                    'insight': 'Insufficient overlapping data',
                    'nearby_intersections': len(nearby_intersections),
                    'data_points': len(merged)
                }
            
            # Calculate correlation
            correlation, p_value = stats.pearsonr(
                merged['usage'],
                merged['total_vehicle_count']
            )
            
            result = {
                'building_id': building_id,
                'correlation': round(correlation, 3),
                'p_value': round(p_value, 4),
                'significance': 'significant' if p_value < 0.05 else 'not significant',
                'nearby_intersections': len(nearby_intersections),
                'data_points': len(merged),
                'insight': self._interpret_correlation(correlation, p_value)
            }
            
            logger.info(f"Correlation analysis: r={correlation:.3f}, p={p_value:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing traffic-energy correlation: {str(e)}")
            return {'error': str(e), 'correlation': 0}
    
    def analyze_weather_energy_correlation(self, building_id: int) -> Dict:
        """Analyze correlation between weather and energy usage"""
        try:
            logger.info(f"Analyzing weather-energy correlation for building {building_id}")
            
            # Get energy data
            energy_response = self.db.table('energy_readings')\
                .select('*')\
                .eq('building_id', building_id)\
                .execute()
            
            if not energy_response.data:
                return {'error': 'No energy data', 'correlation': 0}
            
            # Get weather data
            weather_response = self.db.table('weather_data')\
                .select('*')\
                .execute()
            
            if not weather_response.data:
                return {'error': 'No weather data', 'correlation': 0}
            
            # Convert to DataFrames
            energy_df = pd.DataFrame(energy_response.data)
            weather_df = pd.DataFrame(weather_response.data)
            
            # Aggregate energy by date
            daily_energy = energy_df.groupby('reading_date').agg({
                'usage': 'sum'
            }).reset_index()
            
            # Merge
            merged = daily_energy.merge(
                weather_df,
                left_on='reading_date',
                right_on='reading_date',
                how='inner'
            )
            
            if len(merged) < 10:
                return {'error': 'Insufficient data', 'correlation': 0}
            
            # Calculate total degree days
            merged['total_degree_days'] = merged['heating_degree_days'] + merged['cooling_degree_days']
            
            # Calculate correlations
            temp_corr, temp_p = stats.pearsonr(merged['usage'], merged['temp_avg'])
            dd_corr, dd_p = stats.pearsonr(merged['usage'], merged['total_degree_days'])
            
            result = {
                'building_id': building_id,
                'temperature_correlation': round(temp_corr, 3),
                'temperature_p_value': round(temp_p, 4),
                'degree_days_correlation': round(dd_corr, 3),
                'degree_days_p_value': round(dd_p, 4),
                'data_points': len(merged),
                'insight': self._interpret_weather_correlation(dd_corr, dd_p)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing weather-energy correlation: {str(e)}")
            return {'error': str(e), 'correlation': 0}
    
    def _interpret_correlation(self, r: float, p_value: float) -> str:
        """Interpret correlation coefficient"""
        if p_value >= 0.05:
            return "No statistically significant correlation detected"
        
        abs_r = abs(r)
        if abs_r > 0.7:
            strength = "strong"
        elif abs_r > 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if r > 0 else "negative"
        
        return f"{strength.capitalize()} {direction} correlation between traffic and energy usage"
    
    def _interpret_weather_correlation(self, r: float, p_value: float) -> str:
        """Interpret weather-energy correlation"""
        if p_value >= 0.05:
            return "No statistically significant weather impact detected"
        
        abs_r = abs(r)
        if abs_r > 0.7:
            strength = "strong"
        elif abs_r > 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        return f"{strength.capitalize()} weather dependency detected - consider insulation improvements"
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points (wrapper for helper function)"""
        return calculate_haversine_distance(lat1, lon1, lat2, lon2)