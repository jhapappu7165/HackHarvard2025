from flask import Blueprint, request, jsonify
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)
db = SupabaseClient()

@dashboard_bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """Get complete dashboard overview with all data types"""
    try:
        # Get counts
        buildings = db.get_client().table('energy_buildings').select('id').execute()
        weather_stations = db.get_client().table('weather_stations').select('id').execute()
        intersections = db.get_client().table('traffic_intersections').select('id').execute()
        insights = db.get_client().table('insights').select('id').execute()
        
        # Get recent energy data
        recent_energy = db.get_client().table('energy_readings')\
            .select('*')\
            .order('reading_date', desc=True)\
            .limit(100)\
            .execute()
        
        # Calculate energy totals
        total_usage = sum(r['usage'] for r in recent_energy.data)
        total_cost = sum(r['cost'] for r in recent_energy.data)
        
        # Get high priority insights
        high_priority_insights = db.get_client().table('insights')\
            .select('*')\
            .eq('priority', 'high')\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()
        
        overview = {
            'counts': {
                'buildings': len(buildings.data),
                'weather_stations': len(weather_stations.data),
                'traffic_intersections': len(intersections.data),
                'total_insights': len(insights.data)
            },
            'energy_summary': {
                'total_usage': round(total_usage, 2),
                'total_cost': round(total_cost, 2),
                'avg_usage_per_building': round(
                    total_usage / len(buildings.data), 2
                ) if buildings.data else 0
            },
            'high_priority_insights': high_priority_insights.data
        }
        
        return jsonify({
            'success': True,
            'overview': overview
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get statistics for dashboard cards"""
    try:
        # Energy stats
        energy_readings = db.get_client().table('energy_readings')\
            .select('*')\
            .order('reading_date', desc=True)\
            .limit(1000)\
            .execute()
        
        energy_data = energy_readings.data
        total_energy_usage = sum(r['usage'] for r in energy_data)
        total_energy_cost = sum(r['cost'] for r in energy_data)
        
        # Weather stats
        weather_data_response = db.get_client().table('weather_data')\
            .select('*')\
            .order('reading_date', desc=True)\
            .limit(100)\
            .execute()
        
        weather_data = weather_data_response.data
        avg_temp = sum(w['temp_avg'] for w in weather_data) / len(weather_data) if weather_data else 0
        total_hdd = sum(w['heating_degree_days'] for w in weather_data)
        total_cdd = sum(w['cooling_degree_days'] for w in weather_data)
        
        # Traffic stats
        traffic_data_response = db.get_client().table('traffic_data')\
            .select('*')\
            .order('reading_timestamp', desc=True)\
            .limit(1000)\
            .execute()
        
        traffic_data = traffic_data_response.data
        total_vehicles = sum(t['total_vehicle_count'] for t in traffic_data)
        avg_speed = sum(t['average_speed'] for t in traffic_data) / len(traffic_data) if traffic_data else 0
        
        # Insights stats
        insights_response = db.get_client().table('insights').select('*').execute()
        insights = insights_response.data
        
        high_priority_count = sum(1 for i in insights if i['priority'] == 'high')
        total_savings = sum(i.get('potential_savings', 0) or 0 for i in insights)
        
        stats = {
            'energy': {
                'total_usage': round(total_energy_usage, 2),
                'total_cost': round(total_energy_cost, 2),
                'unit': 'kWh'
            },
            'weather': {
                'avg_temperature': round(avg_temp, 1),
                'heating_degree_days': total_hdd,
                'cooling_degree_days': total_cdd
            },
            'traffic': {
                'total_vehicles': total_vehicles,
                'avg_speed': round(avg_speed, 2)
            },
            'insights': {
                'total': len(insights),
                'high_priority': high_priority_count,
                'potential_savings': round(total_savings, 2)
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/map-data', methods=['GET'])
def get_map_data():
    """Get all location data for map visualization"""
    try:
        # Get all buildings with locations
        buildings = db.get_client().table('energy_buildings')\
            .select('id, name, latitude, longitude, category')\
            .execute()
        
        # Get all weather stations with locations
        weather_stations = db.get_client().table('weather_stations')\
            .select('id, name, latitude, longitude')\
            .execute()
        
        # Get all traffic intersections with locations
        intersections = db.get_client().table('traffic_intersections')\
            .select('id, name, latitude, longitude')\
            .execute()
        
        map_data = {
            'buildings': buildings.data,
            'weather_stations': weather_stations.data,
            'intersections': intersections.data
        }
        
        return jsonify({
            'success': True,
            'map_data': map_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching map data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/generate-all-data', methods=['POST'])
def generate_all_data():
    """Generate all synthetic data (energy, weather, traffic, insights)"""
    try:
        logger.info("Starting generation of all data types...")
        
        from services.energy_generator import EnergyDataGenerator
        from services.weather_generator import WeatherDataGenerator
        from services.traffic_generator import TrafficDataGenerator
        from services.insights_engine import InsightsEngine
        
        results = {}
        
        # Generate energy data
        logger.info("Generating energy data...")
        energy_gen = EnergyDataGenerator()
        buildings = energy_gen.generate_buildings()
        energy_readings = energy_gen.generate_readings_for_all_buildings()
        results['energy'] = {
            'buildings': len(buildings),
            'readings': len(energy_readings)
        }
        
        # Generate weather data
        logger.info("Generating weather data...")
        weather_gen = WeatherDataGenerator()
        stations = weather_gen.generate_stations()
        weather_data = weather_gen.generate_weather_data_for_all_stations()
        results['weather'] = {
            'stations': len(stations),
            'readings': len(weather_data)
        }
        
        # Generate traffic data
        logger.info("Generating traffic data...")
        traffic_gen = TrafficDataGenerator()
        intersections = traffic_gen.generate_intersections()
        traffic_data = traffic_gen.generate_traffic_data_for_all_intersections()
        results['traffic'] = {
            'intersections': len(intersections),
            'readings': len(traffic_data)
        }
        
        # Generate insights
        logger.info("Generating insights...")
        insights_engine = InsightsEngine()
        all_insights = []
        for building in buildings:
            building_insights = insights_engine.generate_comprehensive_insights(building['id'])
            all_insights.extend(building_insights)
        results['insights'] = len(all_insights)
        
        logger.info("All data generation completed successfully")
        
        return jsonify({
            'success': True,
            'message': 'All data generated successfully',
            'results': results
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating all data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/clear-all-data', methods=['DELETE'])
def clear_all_data():
    """Clear all data from database (use with caution)"""
    try:
        logger.warning("Clearing all data from database...")
        
        # Delete in reverse order of dependencies
        db.get_client().table('insights').delete().neq('id', 0).execute()
        db.get_client().table('traffic_data').delete().neq('id', 0).execute()
        db.get_client().table('weather_data').delete().neq('id', 0).execute()
        db.get_client().table('energy_readings').delete().neq('id', 0).execute()
        db.get_client().table('traffic_intersections').delete().neq('id', 0).execute()
        db.get_client().table('weather_stations').delete().neq('id', 0).execute()
        db.get_client().table('energy_buildings').delete().neq('id', 0).execute()
        
        logger.info("All data cleared successfully")
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500