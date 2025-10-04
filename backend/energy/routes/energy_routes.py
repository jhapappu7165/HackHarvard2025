from flask import Blueprint, jsonify, request
from utils.supabase_client import supabase_client
from data_generator import EnergyDataGenerator
from config import Config

energy_bp = Blueprint('energy', __name__)
generator = EnergyDataGenerator()

@energy_bp.route('/generate-data', methods=['POST'])
def generate_data():
    """Generate and populate synthetic energy data"""
    try:
        # Generate buildings
        buildings = generator.generate_buildings()
        
        # Insert buildings into Supabase
        building_records = []
        for building in buildings:
            response = supabase_client.table('buildings').insert(building.to_dict()).execute()
            building_records.append(response.data[0])
        
        # Generate energy readings for each building
        all_readings = []
        for building_record in building_records:
            readings = generator.generate_energy_readings(
                building_record['id'],
                building_record['square_feet'],
                building_record['year_built']
            )
            
            # Add some anomalies
            readings = generator.create_anomalies(readings)
            
            # Insert readings
            for reading in readings:
                all_readings.append(reading.to_dict())
        
        # Batch insert readings
        if all_readings:
            supabase_client.table('energy_readings').insert(all_readings).execute()
        
        return jsonify({
            'success': True,
            'buildings_created': len(building_records),
            'readings_created': len(all_readings),
            'message': 'Energy data generated successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/buildings', methods=['GET'])
def get_buildings():
    """Get all buildings"""
    try:
        response = supabase_client.table('buildings').select('*').execute()
        return jsonify({'success': True, 'data': response.data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/buildings/<int:building_id>/readings', methods=['GET'])
def get_building_readings(building_id):
    """Get energy readings for a specific building"""
    try:
        response = supabase_client.table('energy_readings')\
            .select('*')\
            .eq('building_id', building_id)\
            .order('year', desc=False)\
            .order('month', desc=False)\
            .execute()
        
        return jsonify({'success': True, 'data': response.data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@energy_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Get all buildings
        buildings_response = supabase_client.table('buildings').select('*').execute()
        buildings = buildings_response.data
        
        # Get total energy usage
        readings_response = supabase_client.table('energy_readings').select('*').execute()
        readings = readings_response.data
        
        # Calculate totals
        total_usage = sum([r['usage'] for r in readings])
        total_cost = sum([r['cost'] for r in readings])
        
        # Group by fuel type
        fuel_breakdown = {}
        for reading in readings:
            fuel = reading['fuel_type']
            if fuel not in fuel_breakdown:
                fuel_breakdown[fuel] = {'usage': 0, 'cost': 0}
            fuel_breakdown[fuel]['usage'] += reading['usage']
            fuel_breakdown[fuel]['cost'] += reading['cost']
        
        return jsonify({
            'success': True,
            'data': {
                'total_buildings': len(buildings),
                'total_usage': round(total_usage, 2),
                'total_cost': round(total_cost, 2),
                'fuel_breakdown': fuel_breakdown,
                'buildings': buildings
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500