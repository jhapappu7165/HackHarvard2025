import random
import string
from datetime import datetime, timedelta
from typing import List, Tuple
import numpy as np

def generate_random_string(length: int = 10) -> str:
    """Generate random alphanumeric string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_coords(bounds: dict) -> Tuple[float, float]:
    """Generate random coordinates within Boston bounds"""
    lat = random.uniform(bounds['lat_min'], bounds['lat_max'])
    lng = random.uniform(bounds['lng_min'], bounds['lng_max'])
    return round(lat, 6), round(lng, 6)

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles using Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 3959  # Earth radius in miles
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def generate_date_range(start_date: datetime, end_date: datetime, freq: str = 'D') -> List[datetime]:
    """Generate list of dates between start and end"""
    dates = []
    current = start_date
    
    if freq == 'D':  # Daily
        delta = timedelta(days=1)
    elif freq == 'M':  # Monthly
        delta = timedelta(days=30)
    elif freq == 'H':  # Hourly
        delta = timedelta(hours=1)
    else:
        delta = timedelta(days=1)
    
    while current <= end_date:
        dates.append(current)
        current += delta
    
    return dates

def calculate_z_score(value: float, mean: float, std: float) -> float:
    """Calculate z-score for anomaly detection"""
    if std == 0:
        return 0
    return (value - mean) / std

def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-1 range"""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def round_to_nearest(value: float, nearest: float = 0.01) -> float:
    """Round value to nearest specified increment"""
    return round(value / nearest) * nearest

def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"

def format_large_number(num: float) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return f"{num:.0f}"