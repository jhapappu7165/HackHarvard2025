from flask import Blueprint, request, jsonify
from services.weather_generator import WeatherDataGenerator
from utils.supabase_client import SupabaseClient
import httpx
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)
weather_bp = Blueprint('weather', __name__)
db = SupabaseClient()

# Boston coordinates for OpenMeteo API
LAT = 42.3601
LON = -71.0589


@weather_bp.route('/openmeteo_current', methods=['GET'])
def get_current_weather_openmeteo():
    """
    Get current weather from OpenMeteo API with comprehensive data:
    - is_day
    - cloudcover
    - shortwave_radiation (solar intensity)
    - temperature_2m
    - precipitation_probability (from current forecast hour)
    - rain
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            f"&current=is_day,cloudcover,shortwave_radiation,temperature_2m,precipitation,rain"
            f"&hourly=precipitation_probability"
            f"&forecast_days=1"
        )
        
        with httpx.Client() as client:
            r = client.get(url)
            if r.status_code != 200:
                raise Exception(f"OpenMeteo API error: {r.status_code}")
            data = r.json()

        current = data.get("current", {})
        
        # Get current hour's precipitation probability from hourly data
        hourly = data.get("hourly", {})
        current_precip_prob = None
        if hourly.get("precipitation_probability"):
            # Take the first hour's precipitation probability as current
            current_precip_prob = hourly["precipitation_probability"][0]

        normalized = {
            "timestamp": current.get("time"),
            "is_day": current.get("is_day"),
            "cloudcover_percent": current.get("cloudcover"),
            "shortwave_radiation_wm2": current.get("shortwave_radiation"),
            "temperature_c": current.get("temperature_2m"),
            "precip_prob_percent": current_precip_prob,
            "rain_mm": current.get("rain"),
        }
        
        return jsonify({
            'success': True,
            'data': normalized
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching current weather from OpenMeteo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/openmeteo_forecast', methods=['GET'])
def get_forecast_openmeteo():
    """
    Get hourly forecast from OpenMeteo API with essential fields:
    - is_day
    - cloudcover
    - shortwave_radiation (solar intensity)
    - temperature_2m
    - precipitation_probability
    - rain
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            f"&hourly=is_day,cloudcover,shortwave_radiation,temperature_2m,precipitation_probability,rain"
            f"&forecast_days=1"
        )

        with httpx.Client() as client:
            r = client.get(url)
            if r.status_code != 200:
                raise Exception(f"OpenMeteo API error: {r.status_code}")
            data = r.json()

        h = data.get("hourly", {})
        times = h.get("time", [])

        results = []
        for i, t in enumerate(times):
            results.append({
                "timestamp": t,
                "is_day": h.get("is_day", [None])[i] if i < len(h.get("is_day", [])) else None,
                "cloudcover_percent": h.get("cloudcover", [None])[i] if i < len(h.get("cloudcover", [])) else None,
                "shortwave_radiation_wm2": h.get("shortwave_radiation", [None])[i] if i < len(h.get("shortwave_radiation", [])) else None,
                "temperature_c": h.get("temperature_2m", [None])[i] if i < len(h.get("temperature_2m", [])) else None,
                "precip_prob_percent": h.get("precipitation_probability", [None])[i] if i < len(h.get("precipitation_probability", [])) else None,
                "rain_mm": h.get("rain", [None])[i] if i < len(h.get("rain", [])) else None,
            })

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching forecast from OpenMeteo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500