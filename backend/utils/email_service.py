import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL')
        self.client = SendGridAPIClient(self.api_key)
    
    def send_poop_alert(self, user_email, user_name, tamagotchi_name, custom_message=None):
        """Send an email alert when tamagotchi needs to poop or traffic alert is triggered"""
        
        # Use custom message if provided, otherwise default poop message
        if custom_message:
            subject = f'🚨 Traffic Alert: {tamagotchi_name}'
            main_message = custom_message
            action_text = 'Check Traffic Conditions'
        else:
            subject = f'🚨 {tamagotchi_name} needs to go!'
            main_message = f'Your Tamagotchi <strong>{tamagotchi_name}</strong> needs to poop!'
            action_text = f'Take Care of {tamagotchi_name}'
        
        message = Mail(
            from_email=self.from_email,
            to_emails=user_email,
            subject=subject,
            html_content=f'''
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #ff6b6b;">⚠️ Alert!</h1>
                    <p>Hi {user_name},</p>
                    <p style="font-size: 18px;">
                        {main_message}
                    </p>
                    <a href="http://localhost:3000" 
                       style="display: inline-block; background-color: #ef4444; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 5px; 
                              margin-top: 20px;">
                        {action_text}
                    </a>
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        This is an automated alert from your monitoring system.
                    </p>
                </div>
            </div>
            '''
        )
        
        try:
            response = self.client.send(message)
            print(f"Email sent! Status code: {response.status_code}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False