"""
Email Automation API with Brevo Integration
File: api/emails.py
"""

from flask import Blueprint, request, jsonify
from utils.save_load import data_manager
import pandas as pd
import uuid
from datetime import datetime
import os

emails_bp = Blueprint('emails', __name__)

# Load emails data
emails_df = data_manager.load_emails()

# Brevo configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@techrealm.com')
FROM_NAME = os.getenv('FROM_NAME', 'TechRealm')

# Initialize Brevo client if API key is available
brevo_client = None
BREVO_AVAILABLE = False

try:
    if BREVO_API_KEY:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        brevo_client = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        BREVO_AVAILABLE = True
        print("✓ Brevo email service initialized")
except Exception as e:
    print(f"Brevo not available: {e}")

def send_brevo_email(to_email, subject, html_content, program_data=None):
    """Send email via Brevo API"""
    global emails_df
    
    try:
        if not BREVO_AVAILABLE:
            # Mock email sending for development
            print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            return {
                'success': True,
                'message_id': f'mock-{uuid.uuid4()}',
                'mock': True
            }
        
        # Prepare email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": FROM_NAME, "email": FROM_EMAIL},
            subject=subject,
            html_content=html_content
        )
        
        # Send via Brevo
        api_response = brevo_client.send_transac_email(send_smtp_email)
        
        return {
            'success': True,
            'message_id': api_response.message_id,
            'mock': False
        }
        
    except Exception as e:
        print(f"Email error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def log_email(program_id, to_email, subject, status, message_id=None):
    """Log email to DataFrame"""
    global emails_df
    
    email_record = {
        'email_id': str(uuid.uuid4()),
        'program_id': program_id,
        'to': to_email,
        'subject': subject,
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'message_id': message_id or 'N/A'
    }
    
    new_email = pd.DataFrame([email_record])
    emails_df = pd.concat([emails_df, new_email], ignore_index=True)
    data_manager.save_emails(emails_df)
    
    return email_record

@emails_bp.route('/emails/send', methods=['POST'])
def send_email():
    """Send a custom email"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['to', 'subject', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        to_email = data['to']
        subject = data['subject']
        content = data['content']
        program_id = data.get('program_id', 'N/A')
        
        # Send email
        result = send_brevo_email(to_email, subject, content)
        
        # Log email
        status = 'sent' if result['success'] else 'failed'
        email_record = log_email(
            program_id, 
            to_email, 
            subject, 
            status,
            result.get('message_id')
        )
        
        return jsonify({
            'message': 'Email sent successfully' if result['success'] else 'Email failed',
            'email': email_record,
            'mock': result.get('mock', False)
        }), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emails_bp.route('/emails/send-application', methods=['POST'])
def send_application_email():
    """Send application confirmation email"""
    try:
        data = request.get_json()
        
        if 'to' not in data or 'program_name' not in data:
            return jsonify({'error': 'to and program_name required'}), 400
        
        to_email = data['to']
        program_name = data['program_name']
        university = data.get('university', 'the university')
        program_id = data.get('program_id', 'N/A')
        
        # Create email content
        subject = f"Application Confirmation - {program_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Application Confirmation</h2>
                
                <p>Dear Applicant,</p>
                
                <p>Thank you for your interest in <strong>{program_name}</strong> at {university}.</p>
                
                <p>We have received your application and it is now being processed. Here's what happens next:</p>
                
                <ul>
                    <li>Our admissions team will review your application</li>
                    <li>You will receive updates via email</li>
                    <li>Additional documents may be requested</li>
                </ul>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Program Details</h3>
                    <p><strong>Program:</strong> {program_name}</p>
                    <p><strong>University:</strong> {university}</p>
                    <p><strong>Application Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <p>If you have any questions, please don't hesitate to contact us.</p>
                
                <p>Best regards,<br>
                <strong>TechRealm Team</strong></p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                This is an automated message. Please do not reply directly to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        result = send_brevo_email(to_email, subject, html_content)
        
        # Log email
        status = 'sent' if result['success'] else 'failed'
        email_record = log_email(
            program_id,
            to_email,
            subject,
            status,
            result.get('message_id')
        )
        
        return jsonify({
            'message': 'Application email sent' if result['success'] else 'Email failed',
            'email': email_record,
            'mock': result.get('mock', False)
        }), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emails_bp.route('/emails', methods=['GET'])
def get_emails():
    """Get all sent emails"""
    try:
        program_id = request.args.get('program_id')
        
        filtered_emails = emails_df.copy()
        
        if program_id:
            filtered_emails = filtered_emails[filtered_emails['program_id'] == program_id]
        
        return jsonify({
            'emails': filtered_emails.to_dict(orient='records'),
            'total': len(filtered_emails)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emails_bp.route('/emails/<email_id>', methods=['GET'])
def get_email(email_id):
    """Get a specific email"""
    try:
        email = emails_df[emails_df['email_id'] == email_id]
        
        if len(email) == 0:
            return jsonify({'error': 'Email not found'}), 404
        
        return jsonify({
            'email': email.iloc[0].to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emails_bp.route('/emails/stats', methods=['GET'])
def get_email_stats():
    """Get email statistics"""
    try:
        if len(emails_df) == 0:
            return jsonify({
                'total_emails': 0,
                'by_status': {},
                'by_program': {}
            }), 200
        
        # Group by status
        by_status = emails_df['status'].value_counts().to_dict()
        
        # Group by program
        by_program = emails_df['program_id'].value_counts().head(10).to_dict()
        
        # Time-based stats
        emails_copy = emails_df.copy()
        emails_copy['timestamp'] = pd.to_datetime(emails_copy['timestamp'])
        emails_copy['date'] = emails_copy['timestamp'].dt.date
        
        emails_by_date = emails_copy.groupby('date').size().to_dict()
        emails_by_date = {str(k): v for k, v in emails_by_date.items()}
        
        return jsonify({
            'total_emails': len(emails_df),
            'by_status': by_status,
            'by_program': by_program,
            'emails_by_date': emails_by_date
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emails_bp.route('/emails/test', methods=['POST'])
def send_test_email():
    """Send a test email"""
    try:
        data = request.get_json()
        
        if 'to' not in data:
            return jsonify({'error': 'Recipient email required'}), 400
        
        to_email = data['to']
        
        subject = "TechRealm - Test Email"
        html_content = """
        <html>
        <body>
            <h2>Test Email from TechRealm</h2>
            <p>This is a test email to verify the email integration is working correctly.</p>
            <p>If you received this, the email system is functioning properly!</p>
        </body>
        </html>
        """
        
        result = send_brevo_email(to_email, subject, html_content)
        
        return jsonify({
            'message': 'Test email sent' if result['success'] else 'Test email failed',
            'result': result
        }), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500