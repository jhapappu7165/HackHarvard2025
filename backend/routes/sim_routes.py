from flask import Blueprint, jsonify
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)

sim_bp = Blueprint('sim', __name__)

@sim_bp.route('/weather', methods=['GET'])
def get_weather_data():
    """
    GET /api/sim/weather
    Fetch all weather data from the Weather table for simulation
    """
    try:
        db = SupabaseClient()
        supabase = db.get_client()
        
        response = supabase.table('Weather').select('*').order('id', desc=False).execute()
        
        if response.data:
            logger.info(f"Successfully fetched {len(response.data)} weather records for simulation")
            return jsonify({
                'success': True,
                'data': response.data
            }), 200
        else:
            logger.warning('No weather data found')
            return jsonify({
                'success': False,
                'error': 'No weather data found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sim_bp.route('/weather/<int:weather_id>', methods=['GET'])
def get_weather_by_id(weather_id):
    """
    GET /api/sim/weather/:id
    Fetch specific weather entry by id
    """
    try:
        db = SupabaseClient()
        supabase = db.get_client()
        
        response = supabase.table('Weather').select('*').eq('id', weather_id).single().execute()
        
        if response.data:
            logger.info(f"Successfully fetched weather record {weather_id}")
            return jsonify({
                'success': True,
                'data': response.data
            }), 200
        else:
            logger.warning(f'Weather data with id {weather_id} not found')
            return jsonify({
                'success': False,
                'error': 'Weather data not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching weather data {weather_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500