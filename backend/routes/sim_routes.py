from flask import Blueprint, jsonify, request
from utils.supabase_client import SupabaseClient
from utils.email_service import EmailService
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)
sim_bp = Blueprint('sim', __name__)
email_service = EmailService()

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
@sim_bp.route('/poop-alert', methods=['POST'])
def trigger_poop_alert():
    """
    POST /api/sim/poop-alert
    Trigger poop alert and send email to user
    Expected body: { "user_id": "123", "user_email": "user@example.com", "user_name": "John", "tamagotchi_name": "Pookie", "custom_message": "alert text" }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'user_email']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        user_id = data['user_id']
        user_email = data['user_email']
        user_name = data.get('user_name', 'User')
        tamagotchi_name = data.get('tamagotchi_name', 'Traffic Alert')
        custom_message = data.get('custom_message')
        
        db = SupabaseClient()
        supabase = db.get_client()
        
        # Check if we should send email (rate limiting - once per hour)
        email_check = supabase.table('poop_alerts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        
        should_send_email = True
        if email_check.data:
            last_alert = email_check.data[0]
            last_alert_time = datetime.fromisoformat(last_alert['created_at'].replace('Z', '+00:00'))
            time_since_last = datetime.now(last_alert_time.tzinfo) - last_alert_time
            
            if time_since_last < timedelta(hours=1):
                should_send_email = False
                logger.info(f"Skipping email for user {user_id} - last alert was {time_since_last.total_seconds() / 60:.1f} minutes ago")
        
        email_sent = False
        if should_send_email:
            # Send email
            email_sent = email_service.send_poop_alert(
                user_email=user_email,
                user_name=user_name,
                tamagotchi_name=tamagotchi_name,
                custom_message=custom_message
            )
            
            # Log the alert in database
            supabase.table('poop_alerts').insert({
                'user_id': user_id,
                'email_sent': email_sent,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            logger.info(f"Poop alert triggered for user {user_id}, email sent: {email_sent}")
        
        return jsonify({
            'success': True,
            'email_sent': email_sent,
            'message': 'Poop alert triggered' if email_sent else 'Alert logged but email not sent (rate limited)'
        }), 200
        
    except Exception as e:
        logger.error(f"Error triggering poop alert: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sim_bp.route('/poop-alert/<user_id>', methods=['GET'])
def get_poop_alerts(user_id):
    """
    GET /api/sim/poop-alert/:user_id
    Get poop alert history for a user
    """
    try:
        db = SupabaseClient()
        supabase = db.get_client()
        
        response = supabase.table('poop_alerts').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'data': response.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching poop alerts for user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500