from flask import Blueprint, request, jsonify
from services.energy_generator import EnergyDataGenerator
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
energy_bp = Blueprint('energy', __name__)
db = SupabaseClient()

@energy_bp.route('/buildings', methods=['GET'])
def get_buildings():
    """Get all buildings with optional filters"""
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 100))
        
        query = db.get_client().table('energy_buildings').select('*')
        
        if category:
            query = query.eq('category', category)
        
        response = query.limit(limit).order('name').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'buildings': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching buildings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/buildings/<int:building_id>', methods=['GET'])
def get_building(building_id):
    """Get specific building details"""
    try:
        response = db.get_client().table('energy_buildings')\
            .select('*')\
            .eq('id', building_id)\
            .single()\
            .execute()
        
        return jsonify({
            'success': True,
            'building': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching building {building_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404

@energy_bp.route('/buildings/<int:building_id>/readings', methods=['GET'])
def get_building_readings(building_id):
    """Get energy readings for a specific building"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        fuel_type = request.args.get('fuel_type')
        
        query = db.get_client().table('energy_readings')\
            .select('*')\
            .eq('building_id', building_id)
        
        if start_date:
            query = query.gte('reading_date', start_date)
        if end_date:
            query = query.lte('reading_date', end_date)
        if fuel_type:
            query = query.eq('fuel_type', fuel_type)
        
        response = query.order('reading_date').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'readings': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching readings for building {building_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/readings', methods=['GET'])
def get_all_readings():
    """Get all energy readings with optional filters"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        fuel_type = request.args.get('fuel_type')
        limit = int(request.args.get('limit', 1000))
        
        query = db.get_client().table('energy_readings').select('*')
        
        if start_date:
            query = query.gte('reading_date', start_date)
        if end_date:
            query = query.lte('reading_date', end_date)
        if fuel_type:
            query = query.eq('fuel_type', fuel_type)
        
        response = query.limit(limit).order('reading_date').execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'readings': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching readings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get aggregated dashboard metrics for energy"""
    try:
        # Get all buildings
        buildings_response = db.get_client().table('energy_buildings').select('*').execute()
        buildings = buildings_response.data
        
        # Get all readings
        readings_response = db.get_client().table('energy_readings').select('*').execute()
        readings = readings_response.data
        
        # Calculate aggregated metrics
        total_usage = sum(r['usage'] for r in readings)
        total_cost = sum(r['cost'] for r in readings)
        
        # Group by fuel type
        fuel_breakdown = {}
        for reading in readings:
            fuel_type = reading['fuel_type']
            if fuel_type not in fuel_breakdown:
                fuel_breakdown[fuel_type] = {'usage': 0, 'cost': 0, 'count': 0}
            fuel_breakdown[fuel_type]['usage'] += reading['usage']
            fuel_breakdown[fuel_type]['cost'] += reading['cost']
            fuel_breakdown[fuel_type]['count'] += 1
        
        # Calculate average usage per building
        avg_usage_per_building = total_usage / len(buildings) if buildings else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_buildings': len(buildings),
                'total_usage': round(total_usage, 2),
                'total_cost': round(total_cost, 2),
                'avg_usage_per_building': round(avg_usage_per_building, 2),
                'fuel_breakdown': fuel_breakdown,
                'buildings_by_category': self._group_by_category(buildings)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _group_by_category(buildings):
    """Helper to group buildings by category"""
    categories = {}
    for building in buildings:
        cat = building['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    return categories

@energy_bp.route('/generate-data', methods=['POST'])
def generate_energy_data():
    """Generate synthetic energy data for all buildings"""
    try:
        logger.info("Starting energy data generation...")
        generator = EnergyDataGenerator()
        
        # Generate buildings and readings
        buildings = generator.generate_buildings()
        readings = generator.generate_readings_for_all_buildings()
        
        logger.info(f"Generated {len(buildings)} buildings and {len(readings)} readings")
        
        return jsonify({
            'success': True,
            'message': 'Energy data generated successfully',
            'buildings_created': len(buildings),
            'readings_created': len(readings)
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating energy data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of building categories"""
    from config import Config
    return jsonify({
        'success': True,
        'categories': Config.BUILDING_CATEGORIES
    }), 200

@energy_bp.route('/fuel-types', methods=['GET'])
def get_fuel_types():
    """Get list of fuel types"""
    from config import Config
    return jsonify({
        'success': True,
        'fuel_types': Config.FUEL_TYPES
    }), 200