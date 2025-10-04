from flask import Blueprint, jsonify
from utils.supabase_client import supabase_client
from insights_engine import InsightsEngine

insights_bp = Blueprint('insights', __name__)
insights_engine = InsightsEngine()

@insights_bp.route('/generate-insights', methods=['POST'])
def generate_insights():
    """Generate AI insights for all buildings"""
    try:
        # Get all buildings
        buildings_response = supabase_client.table('buildings').select('*').execute()
        buildings = buildings_response.data
        
        # Get all readings
        readings_response = supabase_client.table('energy_readings').select('*').execute()
        all_readings_list = readings_response.data
        
        # Group readings by building
        readings_by_building = {}
        for reading in all_readings_list:
            bid = reading['building_id']
            if bid not in readings_by_building:
                readings_by_building[bid] = []
            readings_by_building[bid].append(reading)
        
        # Generate insights for each building
        all_insights = []
        for building in buildings:
            building_readings = readings_by_building.get(building['id'], [])
            if building_readings:
                insights = insights_engine.generate_insights(building, building_readings)
                all_insights.extend(insights)
        
        # Generate portfolio-level insights
        portfolio_insights = insights_engine.generate_portfolio_insights(
            buildings, 
            readings_by_building
        )
        all_insights.extend(portfolio_insights)
        
        # Clear old insights
        supabase_client.table('insights').delete().neq('id', 0).execute()
        
        # Insert new insights
        insights_data = [insight.to_dict() for insight in all_insights]
        if insights_data:
            supabase_client.table('insights').insert(insights_data).execute()
        
        return jsonify({
            'success': True,
            'insights_generated': len(all_insights),
            'message': 'AI insights generated successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@insights_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get all insights"""
    try:
        response = supabase_client.table('insights')\
            .select('*')\
            .order('priority', desc=False)\
            .execute()
        
        # Sort by priority (high, medium, low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_insights = sorted(
            response.data, 
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        
        return jsonify({'success': True, 'data': sorted_insights}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@insights_bp.route('/insights/building/<int:building_id>', methods=['GET'])
def get_building_insights(building_id):
    """Get insights for a specific building"""
    try:
        response = supabase_client.table('insights')\
            .select('*')\
            .eq('building_id', building_id)\
            .execute()
        
        return jsonify({'success': True, 'data': response.data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500