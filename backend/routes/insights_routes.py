from flask import Blueprint, request, jsonify
from services.insights_engine import InsightsEngine
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
insights_bp = Blueprint('insights', __name__)
db = SupabaseClient()

@insights_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get all insights with optional filters"""
    try:
        insight_type = request.args.get('type')
        priority = request.args.get('priority')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        limit = int(request.args.get('limit', 100))
        
        query = db.get_client().table('insights').select('*')
        
        if insight_type:
            query = query.eq('insight_type', insight_type)
        if priority:
            query = query.eq('priority', priority)
        if entity_type:
            query = query.eq('entity_type', entity_type)
        if entity_id:
            query = query.eq('entity_id', int(entity_id))
        
        response = query.limit(limit).order('created_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'insights': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insights_bp.route('/insights/<int:insight_id>', methods=['GET'])
def get_insight(insight_id):
    """Get specific insight"""
    try:
        response = db.get_client().table('insights')\
            .select('*')\
            .eq('id', insight_id)\
            .single()\
            .execute()
        
        return jsonify({
            'success': True,
            'insight': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching insight {insight_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404

@insights_bp.route('/insights/building/<int:building_id>', methods=['GET'])
def get_building_insights(building_id):
    """Get insights for specific building"""
    try:
        response = db.get_client().table('insights')\
            .select('*')\
            .eq('entity_type', 'building')\
            .eq('entity_id', building_id)\
            .order('priority')\
            .order('created_at', desc=True)\
            .execute()
        
        return jsonify({
            'success': True,
            'count': len(response.data),
            'insights': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching insights for building {building_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insights_bp.route('/generate-insights', methods=['POST'])
def generate_insights():
    """Generate AI insights for all buildings"""
    try:
        logger.info("Starting insights generation...")
        
        # Get request parameters - handle both JSON and empty body
        building_id = None
        
        # Only try to parse JSON if content is present
        if request.content_length and request.content_length > 0:
            try:
                data = request.get_json(silent=True) or {}
                building_id = data.get('building_id')
            except:
                pass
        
        # Also check query parameters
        if not building_id and request.args.get('building_id'):
            building_id = int(request.args.get('building_id'))
        
        engine = InsightsEngine()
        
        if building_id:
            # Generate insights for specific building
            insights = engine.generate_comprehensive_insights(building_id)
            message = f'Insights generated for building {building_id}'
        else:
            # Generate insights for all buildings
            buildings_response = db.get_client().table('energy_buildings')\
                .select('id')\
                .execute()
            
            all_insights = []
            for building in buildings_response.data:
                building_insights = engine.generate_comprehensive_insights(building['id'])
                all_insights.extend(building_insights)
            
            insights = all_insights
            message = 'Insights generated for all buildings'
        
        logger.info(f"Generated {len(insights)} insights")
        
        return jsonify({
            'success': True,
            'message': message,
            'count': len(insights),
            'insights': insights
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insights_bp.route('/priorities', methods=['GET'])
def get_priorities():
    """Get list of insight priorities"""
    from config import Config
    return jsonify({
        'success': True,
        'priorities': Config.INSIGHT_PRIORITIES
    }), 200

@insights_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of insight categories"""
    from config import Config
    return jsonify({
        'success': True,
        'categories': Config.INSIGHT_CATEGORIES
    }), 200

@insights_bp.route('/summary', methods=['GET'])
def get_insights_summary():
    """Get summary of insights by priority and type"""
    try:
        response = db.get_client().table('insights').select('*').execute()
        insights = response.data
        
        if not insights:
            return jsonify({
                'success': True,
                'message': 'No insights available'
            }), 200
        
        # Group by priority
        by_priority = {}
        for insight in insights:
            priority = insight['priority']
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        # Group by type
        by_type = {}
        for insight in insights:
            itype = insight['insight_type']
            by_type[itype] = by_type.get(itype, 0) + 1
        
        # Calculate total potential savings
        total_savings = sum(
            insight.get('potential_savings', 0) or 0 
            for insight in insights
        )
        
        summary = {
            'total_insights': len(insights),
            'by_priority': by_priority,
            'by_type': by_type,
            'total_potential_savings': round(total_savings, 2)
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating insights summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500