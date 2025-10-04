from flask import Blueprint, request, jsonify
from services.weather_generator import WeatherDataGenerator
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
weather_bp = Blueprint('weather', __name__)
db = SupabaseClient()

@weather_bp.route('/stations', methods=['GET'])
def get_weather_stations():
    """Get all weather stations"""
    try:
        response = db.get_client().table('weather_stations')\
            .select('*')\
            .execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'stations': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching weather stations: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@weather_bp.route('/stations/<int:station_id>', methods=['GET'])
def get_weather_station(station_id):
    """Get specific weather station"""
    try:
        response = db.get_client().table('weather_stations')\
            .select('*')\
            .eq('id', station_id)\
            .single()\
            .execute()
        
        return jsonify({
            'success': True,
            'station': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching weather station {station_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404

@weather_bp.route('/data', methods=['GET'])
def get_weather_data():
    """Get weather data with optional filters"""
    try:
        station_id = request.args.get('station_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 1000))
        
        query = db.get_client().table('weather_data').select('*')
        
        if station_id:
            query = query.eq('station_id', int(station_id))
        if start_date:
            query = query.gte('reading_date', start_date)
        if end_date:
            query = query.lte('reading_date', end_date)
        
        response = query.limit(limit).order('reading_date').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'data': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@weather_bp.route('/stations/<int:station_id>/data', methods=['GET'])
def get_station_data(station_id):
    """Get weather data for specific station"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = db.get_client().table('weather_data')\
            .select('*')\
            .eq('station_id', station_id)
        
        if start_date:
            query = query.gte('reading_date', start_date)
        if end_date:
            query = query.lte('reading_date', end_date)
        
        response = query.order('reading_date').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'data': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching data for station {station_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@weather_bp.route('/generate-data', methods=['POST'])
def generate_weather_data():
    """Generate synthetic weather data"""
    try:
        logger.info("Starting weather data generation...")
        generator = WeatherDataGenerator()
        
        stations = generator.generate_stations()
        weather_data = generator.generate_weather_data_for_all_stations()
        
        logger.info(f"Generated {len(stations)} stations and {len(weather_data)} readings")
        
        return jsonify({
            'success': True,
            'message': 'Weather data generated successfully',
            'stations_created': len(stations),
            'readings_created': len(weather_data)
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating weather data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@weather_bp.route('/summary', methods=['GET'])
def get_weather_summary():
    """Get weather summary statistics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = db.get_client().table('weather_data').select('*')
        
        if start_date:
            query = query.gte('reading_date', start_date)
        if end_date:
            query = query.lte('reading_date', end_date)
        
        response = query.execute()
        data = response.data
        
        if not data:
            return jsonify({
                'success': True,
                'message': 'No weather data available'
            }), 200
        
        # Calculate summary statistics
        temps = [d['temp_avg'] for d in data]
        hdds = [d['heating_degree_days'] for d in data]
        cdds = [d['cooling_degree_days'] for d in data]
        
        summary = {
            'avg_temperature': round(sum(temps) / len(temps), 2),
            'min_temperature': min(d['temp_min'] for d in data),
            'max_temperature': max(d['temp_max'] for d in data),
            'total_heating_degree_days': sum(hdds),
            'total_cooling_degree_days': sum(cdds),
            'total_precipitation': round(sum(d['precipitation'] for d in data), 2),
            'records_count': len(data)
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating weather summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500