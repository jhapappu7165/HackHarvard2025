from flask import Blueprint, request, jsonify
from services.insights_engine import InsightsEngine
from utils.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
insights_bp = Blueprint('insights', __name__)
db = SupabaseClient()

@insights_bp.route('/', methods=['GET'])
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

@insights_bp.route('/<int:insight_id>', methods=['GET'])
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

@insights_bp.route('/building/<int:building_id>', methods=['GET'])
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

@insights_bp.route('/suggestions', methods=['POST'])
def generate_city_optimization_suggestions():
    """Generate city-wide optimization suggestions using Gemini API"""
    try:
        import google.generativeai as genai
        import os
        import json
        
        # Configure Gemini API
        from config import Config
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            return jsonify({'success': False, 'error': 'GEMINI_API_KEY not configured'}), 500
        
        # Try to use Gemini API, fallback to mock data if it fails
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            use_gemini = True
        except Exception as e:
            logger.warning(f"Gemini API not available, using mock data: {str(e)}")
            use_gemini = False
        
        logger.info("Fetching city-wide data for optimization suggestions...")
        
        # Get all energy buildings data
        buildings_response = db.get_client().table('energy_buildings').select('*').execute()
        buildings = buildings_response.data if buildings_response.data else []
        
        # Get recent energy consumption data
        energy_response = db.get_client().table('energy_readings')\
            .select('*')\
            .order('reading_date', desc=True)\
            .limit(1000)\
            .execute()
        energy_data = energy_response.data if energy_response.data else []
        
        # Get recent traffic data
        traffic_response = db.get_client().table('traffic_data')\
            .select('*')\
            .order('reading_timestamp', desc=True)\
            .limit(1000)\
            .execute()
        traffic_data = traffic_response.data if traffic_response.data else []
        
        # Calculate city-wide statistics
        total_buildings = len(buildings)
        total_energy_usage = sum(r.get('usage', 0) for r in energy_data)
        total_energy_cost = sum(r.get('cost', 0) for r in energy_data)
        avg_energy_per_building = total_energy_usage / max(total_buildings, 1)
        
        # Analyze traffic patterns
        traffic_by_period = {}
        for reading in traffic_data:
            period = reading.get('time_period', 'unknown')
            congestion = reading.get('congestion_level', 'unknown')
            if period not in traffic_by_period:
                traffic_by_period[period] = []
            traffic_by_period[period].append(congestion)
        
        # Create detailed prompt for Gemini
        # Create detailed prompt for Gemini
        prompt = f"""
You are an expert smart city consultant providing ACTIONABLE SOLUTIONS for Boston's municipal infrastructure optimization from given data.

ANALYSIS CONTEXT:
You are analyzing real data from Boston's municipal infrastructure to provide specific, implementable solutions to real problems that city government can take action on immediately.

CITY DATA SUMMARY:
- Total Municipal Buildings: {total_buildings}
- Total Energy Consumption: {total_energy_usage:,.2f} kWh
- Total Energy Cost: ${total_energy_cost:,.2f}
- Average Energy per Building: {avg_energy_per_building:,.2f} kWh
- Energy Data Points Analyzed: {len(energy_data)}
- Traffic Data Points Analyzed: {len(traffic_data)}

TRAFFIC PATTERNS BY TIME PERIOD:
{json.dumps(traffic_by_period, indent=2)}

BUILDING PORTFOLIO:
{json.dumps([b.get('category', 'Unknown') for b in buildings[:10]], indent=2)}

TASK:
Generate 3-5 SPECIFIC ACTIONABLE SUGGESTIONS that Boston city government can implement to optimize energy consumption and traffic flow mentioning the identified problem. Each solution should be:

1. A concrete action the city can take
2. Specific to particular buildings, locations, or intersections
3. Solving a problem based on the data patterns provided
4. Realistic and implementable

SOLUTION FORMAT REQUIREMENTS:
Each solution must follow this exact structure:

- "title": Answer with an Suggesting tone and describe WHAT TO DO, WHERE TO DO IT. Examples:
  * "Install motion sensors at City Hall to reduce after-hours lighting costs"
  * "Implement dynamic traffic signals at Mass Ave intersection during peak hours"
  * "Upgrade HVAC systems in Community Center to reduce energy waste"

- "why": Explain the problem statement - WHY this solution will help solve the problem, necessarily including data evidence

EXAMPLE FORMAT:
{{
  "title": "Install programmable thermostats in Central Library to optimize heating schedules",
  "why": "Building shows 40% higher energy usage during off-hours compared to similar facilities causing energy wastage and 20% cost increase",
  "category": "Energy",
  "priority": "high",
  "estimated_impact": "15-20% reduction in heating costs",
  "implementation_timeline": "Short-term",
  "estimated_cost": "Low"
}}

CRITICAL INSTRUCTIONS:
1. START each title with an Suggesting tone but mention clear actionable solution
2. Be LOCATION-SPECIFIC (mention exact buildings, intersections, or areas)
3. Focus on SOLUTIONS along with problems and the why behind them
4. Base solutions on the actual data patterns provided
5. Make solutions realistic and implementable by city government
6. Order by priority: HIGH first, then MEDIUM, then LOW

Return your response as a JSON array with this exact structure:
[
    {{
        "title": "[ACTION VERB] [SPECIFIC SOLUTION] at [SPECIFIC LOCATION]",
        "why": "Problem explanation based on data evidence",
        "category": "Energy" or "Traffic" or "Cross-Sector",
        "priority": "high" or "medium" or "low",
        "estimated_impact": "Brief description of expected benefit",
        "implementation_timeline": "Short-term" or "Medium-term" or "Long-term",
        "estimated_cost": "Low" or "Medium" or "High" or "TBD"
    }}
]

IMPORTANT: Return ONLY valid JSON, no markdown formatting. Focus on ACTIONABLE SOLUTIONS, not problem identification.
"""
        
        if use_gemini:
            # Call Gemini API
            logger.info("Calling Gemini API for city optimization suggestions...")
            try:
                response = model.generate_content(prompt)
                
                # Parse response
                try:
                    # Remove markdown code blocks if present
                    text = response.text.strip()
                    if text.startswith('```'):
                        text = text.replace('```json', '').replace('```', '').strip()
                    
                    suggestions = json.loads(text)
                    
                    logger.info(f"Generated {len(suggestions)} city optimization suggestions via Gemini")
                    
                    return jsonify({
                        'success': True,
                        'message': f'Generated {len(suggestions)} AI-powered city optimization suggestions',
                        'count': len(suggestions),
                        'suggestions': suggestions,
                        'data_summary': {
                            'total_buildings': total_buildings,
                            'total_energy_usage': total_energy_usage,
                            'total_energy_cost': total_energy_cost,
                            'data_points_analyzed': len(energy_data) + len(traffic_data)
                        }
                    }), 200
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini response: {str(e)}")
                    logger.error(f"Response was: {response.text[:500]}")
                    # Fall through to mock data
                    use_gemini = False
                    
            except Exception as e:
                logger.error(f"Gemini API call failed: {str(e)}")
                use_gemini = False
        
        if not use_gemini:
            # Return error if Gemini API is not available
            logger.error("Gemini API is not available and no fallback is provided")
            return jsonify({
                'success': False,
                'error': 'AI service unavailable. Please check Gemini API configuration.',
                'message': 'To enable AI-powered suggestions, please configure a valid GEMINI_API_KEY in your .env file'
            }), 503
        
    except Exception as e:
        logger.error(f"Error generating city optimization suggestions: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'An unexpected error occurred while generating suggestions'
        }), 500