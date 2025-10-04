from flask import Blueprint, request, jsonify
from services.traffic_generator import TrafficDataGenerator
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
traffic_bp = Blueprint('traffic', __name__)
db = SupabaseClient()

@traffic_bp.route('/intersections', methods=['GET'])
def get_intersections():
    """Get all traffic intersections"""
    try:
        limit = int(request.args.get('limit', 100))
        
        response = db.get_client().table('traffic_intersections')\
            .select('*')\
            .limit(limit)\
            .execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'intersections': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching intersections: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@traffic_bp.route('/intersections/<int:intersection_id>', methods=['GET'])
def get_intersection(intersection_id):
    """Get specific intersection details"""
    try:
        response = db.get_client().table('traffic_intersections')\
            .select('*')\
            .eq('id', intersection_id)\
            .single()\
            .execute()
        
        return jsonify({
            'success': True,
            'intersection': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching intersection {intersection_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404

@traffic_bp.route('/data', methods=['GET'])
def get_traffic_data():
    """Get traffic data with optional filters"""
    try:
        intersection_id = request.args.get('intersection_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        time_period = request.args.get('time_period')
        limit = int(request.args.get('limit', 1000))
        
        query = db.get_client().table('traffic_data').select('*')
        
        if intersection_id:
            query = query.eq('intersection_id', int(intersection_id))
        if start_time:
            query = query.gte('reading_timestamp', start_time)
        if end_time:
            query = query.lte('reading_timestamp', end_time)
        if time_period:
            query = query.eq('time_period', time_period)
        
        response = query.limit(limit).order('reading_timestamp').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'data': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching traffic data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@traffic_bp.route('/intersections/<int:intersection_id>/data', methods=['GET'])
def get_intersection_data(intersection_id):
    """Get traffic data for specific intersection"""
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        query = db.get_client().table('traffic_data')\
            .select('*')\
            .eq('intersection_id', intersection_id)
        
        if start_time:
            query = query.gte('reading_timestamp', start_time)
        if end_time:
            query = query.lte('reading_timestamp', end_time)
        
        response = query.order('reading_timestamp').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'data': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching data for intersection {intersection_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@traffic_bp.route('/generate-data', methods=['POST'])
def generate_traffic_data():
    """Generate synthetic traffic data"""
    try:
        logger.info("Starting traffic data generation...")
        generator = TrafficDataGenerator()
        
        intersections = generator.generate_intersections()
        traffic_data = generator.generate_traffic_data_for_all_intersections()
        
        logger.info(f"Generated {len(intersections)} intersections and {len(traffic_data)} readings")
        
        return jsonify({
            'success': True,
            'message': 'Traffic data generated successfully',
            'intersections_created': len(intersections),
            'readings_created': len(traffic_data)
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating traffic data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@traffic_bp.route('/summary', methods=['GET'])
def get_traffic_summary():
    """Get traffic summary statistics"""
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        query = db.get_client().table('traffic_data').select('*')
        
        if start_time:
            query = query.gte('reading_timestamp', start_time)
        if end_time:
            query = query.lte('reading_timestamp', end_time)
        
        response = query.execute()
        data = response.data
        
        if not data:
            return jsonify({
                'success': True,
                'message': 'No traffic data available'
            }), 200
        
        # Calculate summary statistics
        total_vehicles = sum(d['total_vehicle_count'] for d in data)
        avg_speed = sum(d['average_speed'] for d in data) / len(data)
        
        # Count by congestion level
        congestion_counts = {}
        for d in data:
            level = d['congestion_level']
            congestion_counts[level] = congestion_counts.get(level, 0) + 1
        
        summary = {
            'total_vehicle_count': total_vehicles,
            'average_speed': round(avg_speed, 2),
            'congestion_distribution': congestion_counts,
            'records_count': len(data)
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating traffic summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@traffic_bp.route('/time-periods', methods=['GET'])
def get_time_periods():
    """Get list of time periods"""
    from config import Config
    return jsonify({
        'success': True,
        'time_periods': Config.TRAFFIC_TIME_PERIODS
    }), 200