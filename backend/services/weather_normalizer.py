import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
from utils.supabase_client import SupabaseClient
from config import Config
import logging

logger = logging.getLogger(__name__)

class WeatherNormalizer:
    """Weather-normalize energy data like MassEnergyInsight"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
        self.config = Config
    
    def normalize_energy_usage(
        self, 
        building_id: int, 
        start_date: str, 
        end_date: str
    ) -> Dict:
        """Weather-normalize energy usage for a building"""
        try:
            logger.info(f"Normalizing energy usage for building {building_id}")
            
            # Get energy readings
            energy_response = self.db.table('energy_readings')\
                .select('*')\
                .eq('building_id', building_id)\
                .gte('reading_date', start_date)\
                .lte('reading_date', end_date)\
                .execute()
            
            if not energy_response.data:
                logger.warning(f"No energy data found for building {building_id}")
                return {
                    'error': 'No energy data available',
                    'normalized_usage': 0,
                    'original_usage': 0
                }
            
            # Get weather data for same period
            weather_response = self.db.table('weather_data')\
                .select('*')\
                .gte('reading_date', start_date)\
                .lte('reading_date', end_date)\
                .execute()
            
            if not weather_response.data:
                logger.warning("No weather data found for the period")
                return {
                    'error': 'No weather data available',
                    'normalized_usage': sum(r['usage'] for r in energy_response.data),
                    'original_usage': sum(r['usage'] for r in energy_response.data)
                }
            
            # Convert to DataFrames
            energy_df = pd.DataFrame(energy_response.data)
            weather_df = pd.DataFrame(weather_response.data)
            
            # Aggregate energy by date (sum all fuel types)
            energy_daily = energy_df.groupby('reading_date').agg({
                'usage': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Merge energy and weather data
            merged = energy_daily.merge(
                weather_df,
                left_on='reading_date',
                right_on='reading_date',
                how='inner'
            )
            
            if len(merged) < 10:
                logger.warning("Insufficient data points for normalization")
                return {
                    'error': 'Insufficient data for normalization',
                    'normalized_usage': energy_daily['usage'].sum(),
                    'original_usage': energy_daily['usage'].sum()
                }
            
            # Calculate total degree days
            merged['total_degree_days'] = merged['heating_degree_days'] + merged['cooling_degree_days']
            
            # Perform linear regression: usage = base_load + factor * degree_days
            X = merged['total_degree_days'].values
            y = merged['usage'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
            
            # Calculate normalized usage (remove weather effect)
            avg_degree_days = X.mean()
            weather_effect = slope * (X - avg_degree_days)
            normalized_usage = y - weather_effect
            
            # Calculate metrics
            original_total = y.sum()
            normalized_total = normalized_usage.sum()
            weather_impact_percent = ((original_total - normalized_total) / original_total * 100) if original_total > 0 else 0
            
            r_squared = r_value ** 2
            confidence = 'high' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'low'
            
            result = {
                'building_id': building_id,
                'original_usage': round(original_total, 2),
                'normalized_usage': round(normalized_total, 2),
                'weather_impact_percent': round(weather_impact_percent, 2),
                'r_squared': round(r_squared, 3),
                'p_value': round(p_value, 4),
                'confidence': confidence,
                'base_load': round(intercept, 2),
                'weather_sensitivity': round(slope, 4),
                'data_points': len(merged)
            }
            
            logger.info(f"Weather normalization completed: {weather_impact_percent:.1f}% impact")
            return result
            
        except Exception as e:
            logger.error(f"Error normalizing energy usage: {str(e)}")
            return {
                'error': str(e),
                'normalized_usage': 0,
                'original_usage': 0
            }
    
    def calculate_degree_days(self, avg_temp: float, base_temp: float = None) -> Dict[str, int]:
        """Calculate heating and cooling degree days"""
        if base_temp is None:
            base_temp = self.config.WEATHER_BASE_TEMP
        
        if avg_temp < base_temp:
            hdd = base_temp - avg_temp
            cdd = 0
        else:
            hdd = 0
            cdd = avg_temp - base_temp
        
        return {
            'hdd': int(hdd),
            'cdd': int(cdd)
        }
    
    def get_weather_summary(self, start_date: str, end_date: str) -> Dict:
        """Get weather summary for a date range"""
        try:
            weather_response = self.db.table('weather_data')\
                .select('*')\
                .gte('reading_date', start_date)\
                .lte('reading_date', end_date)\
                .execute()
            
            if not weather_response.data:
                return {'error': 'No weather data available'}
            
            df = pd.DataFrame(weather_response.data)
            
            summary = {
                'avg_temperature': round(df['temp_avg'].mean(), 1),
                'min_temperature': round(df['temp_min'].min(), 1),
                'max_temperature': round(df['temp_max'].max(), 1),
                'total_heating_degree_days': int(df['heating_degree_days'].sum()),
                'total_cooling_degree_days': int(df['cooling_degree_days'].sum()),
                'total_precipitation': round(df['precipitation'].sum(), 2),
                'avg_humidity': round(df['humidity'].mean(), 1),
                'avg_wind_speed': round(df['wind_speed'].mean(), 1),
                'days': len(df)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating weather summary: {str(e)}")
            return {'error': str(e)}